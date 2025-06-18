# image_processing/views.py
import json
import logging
from urllib.parse import quote
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone

from usage_limits.decorators import usage_limit_required
from usage_limits.tier_config import TierLimits
from .models import UserImage, PromptTemplate, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, ImageRating, RatingTag, Favorite
from .forms import ImageUploadForm, BulkImageUploadForm, ImageProcessingForm, CollectionForm
from .tasks import process_image_async

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Main dashboard for image processing"""
    # Get user's recent images
    recent_images = UserImage.objects.filter(user=request.user)[:6]
    
    # Get recent processing jobs
    recent_jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    )[:5]
    
    # Get user's limits
    max_prompts = TierLimits.get_user_max_prompts(request.user)
    
    # Get usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    context = {
        'recent_images': recent_images,
        'recent_jobs': recent_jobs,
        'max_prompts': max_prompts,
        'usage_data': usage_data,
    }
    
    return render(request, 'image_processing/dashboard.html', context)


@login_required
def upload_image(request):
    """Combined single and bulk wedding photo upload"""
    if request.method == 'POST':
        # Check if it's a bulk upload (multiple files)
        files = request.FILES.getlist('images') if 'images' in request.FILES else []
        single_file = request.FILES.get('image')
        
        uploaded_count = 0
        errors = []
        
        # Handle single file upload
        if single_file and not files:
            try:
                # Validate single file
                if not single_file.content_type.startswith('image/'):
                    errors.append('Please upload an image file.')
                elif single_file.size > 5 * 1024 * 1024:  # 5MB limit
                    errors.append('Image is too large. Maximum size is 5MB.')
                else:
                    user_image = UserImage(
                        user=request.user,
                        image=single_file,
                        original_filename=single_file.name
                    )
                    user_image.save()
                    uploaded_count = 1
            except Exception as e:
                errors.append(f'Failed to upload {single_file.name}: {str(e)}')
        
        # Handle bulk upload
        elif files:
            # MVP limit: 10 files max
            files_to_process = files[:10]
            if len(files) > 10:
                errors.append('Only the first 10 images were processed. Please upload remaining photos separately.')
            
            for f in files_to_process:
                try:
                    # Validate each file
                    if not f.content_type.startswith('image/'):
                        errors.append(f'"{f.name}" is not an image file - skipped.')
                        continue
                    if f.size > 5 * 1024 * 1024:  # 5MB limit
                        errors.append(f'"{f.name}" is too large (max 5MB) - skipped.')
                        continue
                    
                    user_image = UserImage(
                        user=request.user,
                        image=f,
                        original_filename=f.name
                    )
                    user_image.save()
                    uploaded_count += 1
                except Exception as e:
                    errors.append(f'Failed to upload "{f.name}": {str(e)}')
        
        # Show results with wedding-friendly messaging
        if uploaded_count > 0:
            if uploaded_count == 1:
                messages.success(request, 'Your wedding photo has been uploaded successfully! Ready to visualize different styles.')
            else:
                messages.success(request, f'Successfully uploaded {uploaded_count} wedding photos! Ready to create your dream wedding vision.')
        
        if errors:
            for error in errors:
                messages.warning(request, error)
        
        if uploaded_count > 0:
            return redirect('image_processing:image_gallery')
        
        # If no files were uploaded successfully, stay on upload page
        if not uploaded_count and errors:
            messages.error(request, 'No photos were uploaded. Please check the requirements and try again.')
    
    # For GET requests, show the combined upload form
    single_form = ImageUploadForm()
    bulk_form = BulkImageUploadForm()
    
    return render(request, 'image_processing/upload.html', {
        'single_form': single_form,
        'bulk_form': bulk_form
    })


# Remove the separate bulk_upload view since we're combining them


@login_required
def image_gallery(request):
    """Display user's uploaded images"""
    images = UserImage.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(images, 12)  # Show 12 images per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_images': images.count(),
    }
    
    return render(request, 'image_processing/gallery.html', context)


@login_required
def image_detail(request, pk):
    """Display single image with processing options"""
    user_image = get_object_or_404(UserImage, pk=pk, user=request.user)
    
    # Get available prompts
    prompts = PromptTemplate.objects.filter(is_active=True)
    
    # Get user's prompt limit
    max_prompts = TierLimits.get_user_max_prompts(request.user)
    
    # Get processing history for this image
    processing_jobs = ImageProcessingJob.objects.filter(
        user_image=user_image
    ).order_by('-created_at')
    
    context = {
        'user_image': user_image,
        'prompts': prompts,
        'max_prompts': max_prompts,
        'processing_jobs': processing_jobs,
    }
    
    return render(request, 'image_processing/image_detail.html', context)


@login_required
@require_POST
@usage_limit_required(tokens=1)  # Each processing job uses 1 token
def process_image(request, pk):
    """Process an image with selected prompts"""
    user_image = get_object_or_404(UserImage, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        prompt_ids = data.get('prompt_ids', [])
        
        if not prompt_ids:
            return JsonResponse({'error': 'No prompts selected'}, status=400)
        
        # Check user's prompt limit
        max_prompts = TierLimits.get_user_max_prompts(request.user)
        if len(prompt_ids) > max_prompts:
            return JsonResponse({
                'error': f'You can only select up to {max_prompts} prompts. Upgrade your subscription for more prompts.'
            }, status=400)
        
        # Validate prompts exist
        prompts = PromptTemplate.objects.filter(id__in=prompt_ids, is_active=True)
        if prompts.count() != len(prompt_ids):
            return JsonResponse({'error': 'Some selected prompts are invalid'}, status=400)
        
        # Create processing job
        with transaction.atomic():
            job = ImageProcessingJob.objects.create(
                user_image=user_image,
                cfg_scale=data.get('cfg_scale', 7.0),
                steps=data.get('steps', 50),
                seed=data.get('seed') if data.get('seed') else None
            )
            job.prompts.set(prompts)
        
        # Process asynchronously
        process_image_async.delay(job.id)
        
        return JsonResponse({
            'success': True,
            'job_id': job.id,
            'message': f'Processing started with {len(prompt_ids)} prompts'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return JsonResponse({'error': 'Processing failed'}, status=500)


@login_required
def job_status(request, job_id):
    """Get status of a processing job"""
    job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
    
    data = {
        'job_id': job.id,
        'status': job.status,
        'created_at': job.created_at.isoformat(),
        'prompt_count': job.prompt_count,
    }
    
    if job.status == 'completed':
        data['completed_at'] = job.completed_at.isoformat()
        data['processed_images'] = [
            {
                'id': img.id,
                'prompt_name': img.prompt_template.name,
                'image_url': img.processed_image.url,
                'seed': img.stability_seed,
            }
            for img in job.processed_images.all()
        ]
    elif job.status == 'failed':
        data['error_message'] = job.error_message
    
    return JsonResponse(data)


@login_required
def processing_history(request):
    """View all processing jobs for the user"""
    jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'image_processing/processing_history.html', context)


@login_required
def processed_image_detail(request, pk):
    """View details of a processed image"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    context = {
        'processed_image': processed_image,
    }
    
    return render(request, 'image_processing/processed_image_detail.html', context)


@login_required
def themes_list(request):
    """Display available themes by category"""
    themes = PromptTemplate.objects.filter(is_active=True).order_by('category', 'name')
    
    # Group by category
    themes_by_category = {}
    for theme in themes:
        category = theme.get_category_display()
        if category not in themes_by_category:
            themes_by_category[category] = []
        themes_by_category[category].append(theme)
    
    max_prompts = TierLimits.get_user_max_prompts(request.user)
    
    context = {
        'themes_by_category': themes_by_category,
        'max_prompts': max_prompts,
    }
    
    return render(request, 'image_processing/themes_list.html', context)



@login_required
def collections_list(request):
    """Display user's collections"""
    collections = Collection.objects.filter(user=request.user)
    recent_favorites = Favorite.objects.filter(user=request.user)[:6]
    
    context = {
        'collections': collections,
        'recent_favorites': recent_favorites,
    }
    
    return render(request, 'image_processing/collections_list.html', context)


@login_required
@require_POST
def create_collection(request):
    """Create a new collection"""
    form = CollectionForm(request.POST, user=request.user)
    if form.is_valid():
        collection = form.save(commit=False)
        collection.user = request.user
        collection.save()
        messages.success(request, f'Collection "{collection.name}" created successfully!')
        return redirect('image_processing:collections_list')
    else:
        messages.error(request, 'Error creating collection. Please check your input.')
        return redirect('image_processing:collections_list')


@login_required
def collection_detail(request, collection_id):
    """View collection details"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    items = collection.items.all().order_by('order', '-added_at')
    
    context = {
        'collection': collection,
        'items': items,
    }
    
    return render(request, 'image_processing/collection_detail.html', context)


@login_required
@require_POST
def add_to_collection(request):
    """Add image to collection via AJAX"""
    collection_id = request.POST.get('collection_id')
    user_image_id = request.POST.get('user_image_id')
    processed_image_id = request.POST.get('processed_image_id')
    
    try:
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        
        # Check if adding user image or processed image
        if user_image_id:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                user_image=user_image
            )
        elif processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage, 
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                processed_image=processed_image
            )
        else:
            return JsonResponse({'success': False, 'message': 'No image specified'})
        
        if created:
            return JsonResponse({'success': True, 'message': f'Added to "{collection.name}"'})
        else:
            return JsonResponse({'success': False, 'message': 'Already in collection'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def remove_from_collection(request):
    """Remove image from collection"""
    collection_id = request.POST.get('collection_id')
    item_id = request.POST.get('item_id')
    
    try:
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        item = get_object_or_404(CollectionItem, id=item_id, collection=collection)
        item.delete()
        
        return JsonResponse({'success': True, 'message': 'Removed from collection'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def rate_image(request):
    """Rate a processed image"""
    processed_image_id = request.POST.get('processed_image_id')
    rating = request.POST.get('rating')
    tags = request.POST.getlist('tags[]')
    
    try:
        processed_image = get_object_or_404(
            ProcessedImage,
            id=processed_image_id,
            processing_job__user_image__user=request.user
        )
        
        # Create or update rating
        image_rating, created = ImageRating.objects.update_or_create(
            user=request.user,
            processed_image=processed_image,
            defaults={'rating': rating}
        )
        
        # Add tags for thumbs down ratings
        if rating == 'down' and tags:
            # Clear existing tags
            image_rating.tags.all().delete()
            # Add new tags
            for tag in tags:
                RatingTag.objects.create(rating=image_rating, tag=tag)
        
        # Get updated counts
        thumbs_up_count = processed_image.ratings.filter(rating='up').count()
        thumbs_down_count = processed_image.ratings.filter(rating='down').count()
        
        return JsonResponse({
            'success': True,
            'message': 'Rating submitted',
            'thumbs_up_count': thumbs_up_count,
            'thumbs_down_count': thumbs_down_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorite status for an image"""
    user_image_id = request.POST.get('user_image_id')
    processed_image_id = request.POST.get('processed_image_id')
    
    try:
        if user_image_id:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                user_image=user_image
            )
        elif processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage,
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                processed_image=processed_image
            )
        else:
            return JsonResponse({'success': False, 'error': 'No image specified'})
        
        if not created:
            # Remove favorite
            favorite.delete()
            is_favorited = False
            message = 'Removed from favorites'
        else:
            # Added to favorites
            is_favorited = True
            message = 'Added to favorites'
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def favorites_list(request):
    """Display user's favorite images"""
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'image_processing/favorites_list.html', context)


@login_required
def share_image(request, image_type, image_id):
    """Generate sharing URL for an image"""
    if image_type == 'user':
        image = get_object_or_404(UserImage, id=image_id, user=request.user)
        image_url = request.build_absolute_uri(image.image.url)
    elif image_type == 'processed':
        image = get_object_or_404(
            ProcessedImage,
            id=image_id,
            processing_job__user_image__user=request.user
        )
        image_url = request.build_absolute_uri(image.processed_image.url)
    else:
        messages.error(request, 'Invalid image type')
        return redirect('image_processing:dashboard')
    
    context = {
        'image': image,
        'image_url': image_url,
        'image_type': image_type,
    }
    
    return render(request, 'image_processing/share_image.html', context)