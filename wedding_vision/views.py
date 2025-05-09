# wedding_vision/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from usage_limits.decorators import usage_limit_required
from usage_limits.usage_tracker import UsageTracker

from .models import VenueImage, ThemeTemplate, GeneratedImage
from .services import StabilityAIService




@login_required
def venue_list(request):
    """Display list of user's venue images"""
    venues = VenueImage.objects.filter(user=request.user)
    return render(request, 'wedding_vision/venue_list.html', {'venues': venues})

@login_required
def venue_upload(request):
    """Upload a new venue image"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        
        if not title or not image:
            messages.error(request, "Title and image are required.")
            return render(request, 'wedding_vision/venue_upload.html')
        
        # Validate image format
        if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            messages.error(request, "Only JPG, PNG and WEBP files are allowed.")
            return render(request, 'wedding_vision/venue_upload.html')
            
        # Validate file size (5MB limit)
        if image.size > 5 * 1024 * 1024:
            messages.error(request, "Image size must be under 5MB.")
            return render(request, 'wedding_vision/venue_upload.html')
        
        venue = VenueImage.objects.create(
            user=request.user,
            title=title,
            description=description,
            image=image
        )
        
        messages.success(request, "Venue image uploaded successfully!")
        return redirect('wedding_vision:venue_detail', venue_id=venue.id)
    
    return render(request, 'wedding_vision/venue_upload.html')

@login_required
def venue_detail(request, venue_id):
    """View venue details and generated images"""
    venue = get_object_or_404(VenueImage, id=venue_id, user=request.user)
    generated_images = GeneratedImage.objects.filter(venue_image=venue)
    return render(request, 'wedding_vision/venue_detail.html', {
        'venue': venue,
        'generated_images': generated_images
    })

@login_required
def theme_selection(request, venue_id):
    """Select theme for image generation"""
    venue = get_object_or_404(VenueImage, id=venue_id, user=request.user)
    themes = ThemeTemplate.objects.filter(active=True)
    
    return render(request, 'wedding_vision/theme_selection.html', {
        'venue': venue,
        'themes': themes
    })

@login_required
def generate_image(request, venue_id, theme_id):
    """Generate image with selected theme"""
    venue = get_object_or_404(VenueImage, id=venue_id, user=request.user)
    theme = get_object_or_404(ThemeTemplate, id=theme_id, active=True)
    
    # Call Stability AI service
    result = StabilityAIService.image_to_image(venue, theme)
    
    if result["success"]:
        # Create a new generated image record
        generated_image = GeneratedImage.objects.create(
            user=request.user,
            venue_image=venue,
            theme=theme,
            image_data=result["image_data"],
            prompt=result.get("prompt", ""),
            seed=result.get("seed"),
            status='completed',
            tokens_used=theme.token_cost
        )
        
        messages.success(request, "Image generated successfully!")
        return redirect('wedding_vision:preview_image', generation_id=generated_image.id)
    else:
        messages.error(request, f"Image generation failed: {result.get('error')}")
        return redirect('wedding_vision:theme_selection', venue_id=venue.id)

@login_required
def preview_image(request, generation_id):
    """View generated image details"""
    generation = get_object_or_404(GeneratedImage, id=generation_id, user=request.user)
    
    # Convert binary image data to base64 for display if needed
    image_base64 = None
    if generation.image_data and not generation.image:
        import base64
        image_base64 = base64.b64encode(generation.image_data).decode('utf-8')
    
    return render(request, 'wedding_vision/preview_image.html', {
        'generation': generation,
        'image_base64': image_base64
    })

@login_required
def save_image(request, generation_id):
    """Save generated image permanently"""
    generation = get_object_or_404(GeneratedImage, id=generation_id, user=request.user)
    
    if request.method == 'POST':
        # Save the image if not already saved
        if not generation.is_saved:
            generation.is_saved = True
            
            # If we have image_data but no image file, create one
            if generation.image_data and not generation.image:
                from django.core.files.base import ContentFile
                image_name = f"generated_{generation.id}.png"
                generation.image.save(image_name, ContentFile(generation.image_data), save=False)
            
            generation.save()
            messages.success(request, "Image saved to your gallery!")
        
        return redirect('wedding_vision:gallery')
    
    return redirect('wedding_vision:preview_image', generation_id=generation.id)

@login_required
def gallery(request):
    """View user's gallery of generated images"""
    generated_images = GeneratedImage.objects.filter(
        user=request.user,
        is_saved=True
    ).select_related('venue_image', 'theme')
    
    return render(request, 'wedding_vision/gallery.html', {
        'generated_images': generated_images
    })

@login_required
def image_feedback(request, generation_id):
    """Submit feedback for generated image"""
    generation = get_object_or_404(GeneratedImage, id=generation_id, user=request.user)
    
    if request.method == 'POST':
        feedback_type = request.POST.get('feedback_type')
        comment = request.POST.get('comment', '')
        
        if feedback_type in ('positive', 'negative'):
            ImageFeedback.objects.update_or_create(
                generated_image=generation,
                defaults={
                    'feedback_type': feedback_type,
                    'comment': comment
                }
            )
            messages.success(request, "Thank you for your feedback!")
        
    return redirect('wedding_vision:preview_image', generation_id=generation.id)