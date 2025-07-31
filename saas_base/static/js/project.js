class WeddingFormManager {
    constructor() {
        this.apiBaseUrl = '/wedding/api/';
        this.brandingCache = new Map();
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeDynamicFormsets();
            this.setupUrlPreview();
            this.setupBrandingDetection();
        });
    }

    /**
     * Initialize dynamic formset management for social media and registry forms
     */
    initializeDynamicFormsets() {
        this.setupDynamicFormset('social', 'Social Media Link');
        this.setupDynamicFormset('registry', 'Wedding Registry');
    }

    /**
     * Setup dynamic formset functionality for a specific formset type
     * @param {string} formsetType - The type of formset (social or registry)
     * @param {string} displayName - Human-readable name for the formset
     */
    setupDynamicFormset(formsetType, displayName) {
        const formsetContainer = document.getElementById(`${formsetType}-formset`);
        if (!formsetContainer) return;

        // Setup delete buttons for existing forms
        this.setupDeleteButtons(formsetType);
    }

    /**
     * Setup delete buttons for existing forms
     * @param {string} formsetType - The type of formset
     */
    setupDeleteButtons(formsetType) {
        const forms = document.querySelectorAll(`[id^="${formsetType}-form-"]:not(#${formsetType}-empty-form)`);
        forms.forEach(form => {
            if (!form.querySelector('.formset-delete-btn')) {
                const deleteButton = this.createDeleteButton(form, formsetType);
                form.appendChild(deleteButton);
            }
        });
    }

    /**
     * Create a delete button for a form
     * @param {HTMLElement} formElement - The form element
     * @param {string} formsetType - The type of formset
     * @returns {HTMLElement} The created delete button
     */
    createDeleteButton(formElement, formsetType) {
        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn btn-outline-danger btn-sm mt-2 formset-delete-btn';
        deleteButton.innerHTML = '<i class="bi bi-trash"></i> Remove';
        deleteButton.onclick = () => this.removeFormsetForm(formElement, formsetType);
        return deleteButton;
    }

    /**
     * Remove a form from the formset
     * @param {HTMLElement} formElement - The form element to remove
     * @param {string} formsetType - The type of formset
     */
    removeFormsetForm(formElement, formsetType) {
        const deleteInput = formElement.querySelector(`input[name*="DELETE"]`);
        const idInput = formElement.querySelector(`input[name*="id"]`);

        if (deleteInput && idInput && idInput.value) {
            // Mark existing object for deletion
            deleteInput.checked = true;
            formElement.style.display = 'none';
        } else {
            // Remove new form completely
            formElement.remove();
            this.reindexFormset(formsetType);
        }
    }

    /**
     * Reindex formset after removal
     * @param {string} formsetType - The type of formset
     */
    reindexFormset(formsetType) {
        const forms = document.querySelectorAll(`[id^="${formsetType}-form-"]:not(#${formsetType}-empty-form)`);
        const totalFormsInput = document.querySelector(`input[name="${formsetType}-TOTAL_FORMS"]`);
        
        let visibleIndex = 0;
        forms.forEach((form) => {
            if (form.style.display !== 'none') {
                this.updateFormIndices(form, visibleIndex);
                visibleIndex++;
            }
        });
        
        totalFormsInput.value = visibleIndex;
    }

    /**
     * Update form element indices
     * @param {HTMLElement} form - The form element
     * @param {number} index - New index for the form
     */
    updateFormIndices(form, index) {
        const elements = form.querySelectorAll('input, select, textarea, label');
        elements.forEach(element => {
            ['name', 'id', 'for', 'htmlFor'].forEach(attr => {
                const value = element[attr] || element.getAttribute(attr);
                if (value && value.includes('-')) {
                    const updated = value.replace(/\d+/, index);
                    if (element[attr] !== undefined) {
                        element[attr] = updated;
                    } else {
                        element.setAttribute(attr, updated);
                    }
                }
            });
        });
    }

    /**
     * Setup branding detection for URL fields
     */
    setupBrandingDetection() {
        // Setup for existing forms
        document.querySelectorAll('.url-field').forEach(urlField => {
            this.setupBrandingForField(urlField);
        });
    }

    /**
     * Setup branding detection for a specific URL field
     * @param {HTMLElement} urlField - The URL input field
     */
    setupBrandingForField(urlField) {
        urlField.addEventListener('blur', async () => {
            const url = urlField.value.trim();
            if (!url) return;

            const form = urlField.closest('.social-form, .registry-form');
            if (!form) return;

            const formsetType = form.classList.contains('social-form') ? 'social' : 'registry';
            await this.detectAndApplyBranding(urlField, formsetType);
        });

        urlField.addEventListener('input', () => {
            // Clear previous branding indicators on input
            this.clearBrandingIndicator(urlField);
        });
    }

    /**
     * Simple branding detection and application
     * @param {HTMLElement} urlField - The URL input field
     * @param {string} formsetType - Type of formset (social or registry)
     */
    async detectAndApplyBranding(urlField, formsetType) {
        const url = urlField.value.trim();
        const form = urlField.closest('.social-form, .registry-form');
        
        if (!url || !form) return;

        // Check cache first
        const cacheKey = `${formsetType}-${url}`;
        if (this.brandingCache.has(cacheKey)) {
            this.applyBrandingData(form, this.brandingCache.get(cacheKey), formsetType);
            return;
        }

        // Show loading indicator
        this.showBrandingLoading(urlField);

        try {
            const response = await fetch(`${this.apiBaseUrl}detect-branding/?url=${encodeURIComponent(url)}&type=${formsetType}`);
            const data = await response.json();
            
            if (response.ok && data.success && data.branding.detected) {
                // Cache the result
                this.brandingCache.set(cacheKey, data.branding);
                
                // Apply branding
                this.applyBrandingData(form, data.branding, formsetType);
                
                // Show success indicator
                this.showBrandingIndicator(urlField, data.branding, 'success');
            } else {
                this.showBrandingIndicator(urlField, { name: 'Unknown', type: 'other' }, 'warning');
            }
        } catch (error) {
            console.error('Error detecting branding:', error);
            this.showBrandingIndicator(urlField, null, 'error');
        }
    }

    /**
     * Apply detected branding data to form
     * @param {HTMLElement} form - The form element
     * @param {Object} brandingData - Branding information from API
     * @param {string} formsetType - Type of formset
     */
    applyBrandingData(form, brandingData, formsetType) {
        if (formsetType === 'social') {
            const displayNameField = form.querySelector('input[name*="display_name"]');
            
            // Auto-fill display name if available and field is empty
            if (displayNameField && !displayNameField.value && brandingData.suggestions?.display_name) {
                displayNameField.value = brandingData.suggestions.display_name;
            }
        } else {
            const registryNameField = form.querySelector('input[name*="registry_name"]');
            const descriptionField = form.querySelector('textarea[name*="description"]');
            
            // Auto-fill registry name if available and field is empty
            if (registryNameField && !registryNameField.value && brandingData.suggestions?.display_name) {
                registryNameField.value = brandingData.suggestions.display_name;
            }
            
            // Auto-fill description if available and field is empty
            if (descriptionField && !descriptionField.value && brandingData.description) {
                descriptionField.value = brandingData.description;
            }
        }
    }

    /**
     * Show branding detection indicator
     * @param {HTMLElement} urlField - The URL field
     * @param {Object} brandingData - Branding data
     * @param {string} type - Type of indicator (success, warning, error)
     */
    showBrandingIndicator(urlField, brandingData, type) {
        this.clearBrandingIndicator(urlField);
        
        const indicator = document.createElement('div');
        indicator.className = `branding-indicator alert alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'danger'} alert-sm mt-1`;
        
        let content = '';
        if (type === 'success' && brandingData) {
            const icon = brandingData.icon || 'bi-check-circle';
            const color = brandingData.color || '#28a745';
            content = `
                <i class="${icon}" style="color: ${color};"></i> 
                <strong>${brandingData.name}</strong> detected automatically
            `;
        } else if (type === 'warning') {
            content = `<i class="bi bi-exclamation-triangle"></i> Platform not recognized`;
        } else {
            content = `<i class="bi bi-exclamation-circle"></i> Could not detect platform`;
        }
        
        indicator.innerHTML = content;
        urlField.parentNode.appendChild(indicator);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.remove();
            }
        }, 5000);
    }

    /**
     * Show loading indicator for branding detection
     * @param {HTMLElement} urlField - The URL field
     */
    showBrandingLoading(urlField) {
        this.clearBrandingIndicator(urlField);
        
        const indicator = document.createElement('div');
        indicator.className = 'branding-indicator alert alert-info alert-sm mt-1';
        indicator.innerHTML = '<i class="bi bi-hourglass-split"></i> Detecting platform...';
        
        urlField.parentNode.appendChild(indicator);
    }

    /**
     * Clear branding indicator
     * @param {HTMLElement} urlField - The URL field
     */
    clearBrandingIndicator(urlField) {
        const existing = urlField.parentNode.querySelector('.branding-indicator');
        if (existing) {
            existing.remove();
        }
    }

    /**
     * Setup URL preview functionality for wedding page URL
     */
    setupUrlPreview() {
        const previewField = document.getElementById('url-preview');
        if (!previewField) return;

        const updatePreview = () => {
            const name1 = document.getElementById('id_partner_1_name')?.value || '';
            const name2 = document.getElementById('id_partner_2_name')?.value || '';
            const date = document.getElementById('id_wedding_date')?.value || '';
            
            if (name1 && name2) {
                const cleanName1 = name1.replace(/[^a-zA-Z0-9]/g, '').toLowerCase().substring(0, 15);
                const cleanName2 = name2.replace(/[^a-zA-Z0-9]/g, '').toLowerCase().substring(0, 15);
                
                let dateStr = 'tbd';
                if (date) {
                    const dateObj = new Date(date);
                    dateStr = String(dateObj.getMonth() + 1).padStart(2, '0') + 
                             String(dateObj.getDate()).padStart(2, '0') + 
                             String(dateObj.getFullYear()).substr(-2);
                }
                
                const slug = `${cleanName1}${cleanName2}${dateStr}`;
                previewField.value = `yoursite.com/wedding/${slug}/`;
            } else {
                previewField.value = 'Enter names to see your custom URL...';
            }
        };

        // Attach listeners to name and date fields
        ['partner_1_name', 'partner_2_name'].forEach(fieldName => {
            const field = document.getElementById(`id_${fieldName}`);
            if (field) {
                field.addEventListener('input', updatePreview);
            }
        });

        const dateField = document.getElementById('id_wedding_date');
        if (dateField) {
            dateField.addEventListener('change', updatePreview);
        }

        // Initial update
        updatePreview();
    }

    /**
     * Show alert message
     * @param {string} message - Alert message
     * @param {string} type - Alert type (success, warning, danger, info)
     */
    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alert, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

/**
 * Modern Homepage Enhancement Manager
 * Handles scroll animations, interactive elements, and enhanced UX
 */
class HomepageManager {
    constructor() {
        this.isHomepage = document.querySelector('.homepage') !== null;
        if (this.isHomepage) {
            this.init();
        }
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupScrollAnimations();
            this.setupInteractiveElements();
            this.setupSmoothScrolling();
            this.setupCountUpAnimations();
            this.setupParallaxEffects();
            this.setupDemoInteractions();
        });
    }

    /**
     * Setup scroll-triggered animations using Intersection Observer
     */
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements for animation
        const animateElements = document.querySelectorAll(
            '.feature-card, .theme-card, .tool-card, .testimonial-card, .step-card'
        );
        
        animateElements.forEach((el, index) => {
            el.classList.add(`stagger-${(index % 4) + 1}`);
            observer.observe(el);
        });
    }

    /**
     * Setup interactive demo elements
     */
    setupDemoInteractions() {
        const beforeAfterContainer = document.querySelector('.before-after-container');
        if (beforeAfterContainer) {
            let isTransformed = false;
            
            beforeAfterContainer.addEventListener('click', () => {
                const arrow = beforeAfterContainer.querySelector('.transform-arrow');
                const beforeImg = beforeAfterContainer.querySelector('.before-image');
                const afterImg = beforeAfterContainer.querySelector('.after-image');
                
                if (!isTransformed) {
                    // Add transformation effect
                    beforeAfterContainer.style.filter = 'brightness(1.1) saturate(1.2)';
                    arrow.innerHTML = '<i class="bi bi-check-circle"></i>';
                    arrow.style.background = 'linear-gradient(135deg, #00F5FF 0%, #0099CC 100%)';
                    
                    // Show loading state briefly
                    arrow.innerHTML = '<i class="bi bi-hourglass-split rotating"></i>';
                    setTimeout(() => {
                        arrow.innerHTML = '<i class="bi bi-check-circle"></i>';
                    }, 1500);
                    
                    isTransformed = true;
                } else {
                    // Reset
                    beforeAfterContainer.style.filter = '';
                    arrow.innerHTML = '<i class="bi bi-arrow-right"></i>';
                    arrow.style.background = 'var(--gradient-rose)';
                    isTransformed = false;
                }
            });

            // Add cursor pointer
            beforeAfterContainer.style.cursor = 'pointer';
            
            // Add tooltip
            beforeAfterContainer.title = 'Click to see AI transformation in action!';
        }
    }

    /**
     * Setup smooth scrolling for anchor links
     */
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Setup count-up animations for statistics
     */
    setupCountUpAnimations() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        const countUp = (element, target) => {
            const increment = target / 60; // 60 frames for 1 second
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    element.textContent = this.formatStatNumber(target);
                    clearInterval(timer);
                } else {
                    element.textContent = this.formatStatNumber(Math.floor(current));
                }
            }, 16); // ~60fps
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const text = element.textContent;
                    const target = parseInt(text.replace(/[^\d]/g, ''));
                    
                    if (target && !element.classList.contains('counted')) {
                        element.classList.add('counted');
                        countUp(element, target);
                        observer.unobserve(element);
                    }
                }
            });
        });

        statNumbers.forEach(stat => observer.observe(stat));
    }

    /**
     * Format stat numbers with appropriate suffixes
     */
    formatStatNumber(num) {
        if (num >= 1000) {
            return Math.floor(num / 1000) + 'K+';
        }
        return num + '+';
    }

    /**
     * Setup subtle parallax effects
     */
    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('.floating-element');
        
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset;
            
            parallaxElements.forEach((element, index) => {
                const speed = 0.5 + (index * 0.1);
                const yPos = -(scrollTop * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    /**
     * Setup interactive elements with enhanced feedback
     */
    setupInteractiveElements() {
        // Enhanced button interactions
        document.querySelectorAll('.hero-cta-primary, .hero-cta-secondary').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-2px) scale(1.02)';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Theme card interactions
        document.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Add click effects to interactive elements
        document.querySelectorAll('.tool-card, .feature-card').forEach(card => {
            card.addEventListener('click', () => {
                card.style.transform = 'translateY(-5px) scale(0.98)';
                setTimeout(() => {
                    card.style.transform = 'translateY(-5px) scale(1)';
                }, 150);
            });
        });
    }

    /**
     * Add loading states for CTA buttons
     */
    addLoadingState(button, loadingText = 'Loading...') {
        const originalText = button.innerHTML;
        button.innerHTML = `<i class="bi bi-hourglass-split rotating me-2"></i>${loadingText}`;
        button.disabled = true;
        
        // Simulate loading (remove in production)
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    }

    /**
     * Show notification toast
     */
    showNotification(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed`;
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.style.minWidth = '300px';
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 4000);
    }
}

/**
 * Enhanced Form Interactions
 */
class FormEnhancements {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupFormValidation();
            this.setupInputEnhancements();
            this.setupImagePreview();
            this.setupDeleteConfirmations();
            this.setupCollectionActions();
            this.setupFavoriteHearts();
            this.setupFormsetManagement();
        });
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        return isValid;
    }

    showFieldError(input, message) {
        this.clearFieldError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        
        input.classList.add('is-invalid');
        input.parentNode.appendChild(errorDiv);
    }

    clearFieldError(input) {
        input.classList.remove('is-invalid');
        const existingError = input.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    setupInputEnhancements() {
        // Add floating label effect
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('focus', () => {
                input.parentNode.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentNode.classList.remove('focused');
                }
            });
            
            // Check initial state
            if (input.value) {
                input.parentNode.classList.add('focused');
            }
        });
    }

    setupImagePreview() {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        // Find existing preview or create new one
                        let preview = input.parentNode.querySelector('.image-preview');
                        if (!preview) {
                            preview = document.createElement('div');
                            preview.className = 'image-preview mt-2';
                            input.parentNode.appendChild(preview);
                        }
                        
                        preview.innerHTML = `
                            <img src="${e.target.result}" 
                                 class="img-thumbnail" 
                                 style="max-width: 200px; max-height: 200px;" 
                                 alt="Preview">
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            });
        });
    }

    setupDeleteConfirmations() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.confirm-delete, .confirm-delete *')) {
                const button = e.target.closest('.confirm-delete');
                const message = button.dataset.message || 'Are you sure you want to delete this?';
                
                if (!confirm(message)) {
                    e.preventDefault();
                }
            }
        });
    }

    setupCollectionActions() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-collection')) {
                e.preventDefault();
                const button = e.target;
                const imageId = button.dataset.imageId;
                const imageType = button.dataset.imageType || 'processed';
                
                this.addToCollection(imageId, imageType);
            }
        });
    }

    async addToCollection(imageId, imageType) {
        try {
            const formData = new FormData();
            formData.append(`${imageType}_image_id`, imageId);
            formData.append('use_default', 'true');
            
            const response = await fetch('/studio/collections/add/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                this.showToast(data.message, 'success');
            } else {
                this.showToast(data.message || 'Failed to add to collection', 'warning');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Network error', 'error');
        }
    }

    setupFavoriteHearts() {
        // Favorite heart functionality is already in the CSS/HTML component
        // This ensures it works properly with dynamic content
        document.addEventListener('click', (e) => {
            if (e.target.closest('.favorite-heart-btn')) {
                e.preventDefault();
                e.stopPropagation();
                
                const button = e.target.closest('.favorite-heart-btn');
                const processedImageId = button.dataset.processedImageId;
                const isCurrentlyFavorited = button.dataset.isFavorited === 'true';
                
                this.toggleFavorite(processedImageId, button);
            }
        });
    }

    async toggleFavorite(processedImageId, button) {
        button.disabled = true;
        
        try {
            const formData = new FormData();
            formData.append('processed_image_id', processedImageId);
            
            const response = await fetch('/studio/favorites/toggle/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                const icon = button.querySelector('i');
                if (data.is_favorited) {
                    icon.className = 'bi bi-heart-fill';
                    button.classList.add('favorited');
                    button.classList.remove('not-favorited');
                    button.title = 'Remove from favorites';
                } else {
                    icon.className = 'bi bi-heart';
                    button.classList.remove('favorited');
                    button.classList.add('not-favorited');
                    button.title = 'Add to favorites';
                }
                button.dataset.isFavorited = data.is_favorited.toString();
                this.showToast(data.message, 'success');
            } else {
                this.showToast(data.error || 'Error updating favorite', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Network error', 'error');
        } finally {
            button.disabled = false;
        }
    }

    setupFormsetManagement() {
        // Global form counters
        let socialFormCount = 0;
        let registryFormCount = 0;

        // Initialize counters if management forms exist
        const socialTotalForms = document.getElementById('id_social-TOTAL_FORMS');
        const registryTotalForms = document.getElementById('id_registry-TOTAL_FORMS');
        
        if (socialTotalForms) {
            socialFormCount = parseInt(socialTotalForms.value);
        }
        if (registryTotalForms) {
            registryFormCount = parseInt(registryTotalForms.value);
        }

        // Add form handlers
        document.addEventListener('click', (e) => {
            if (e.target.matches('#add-social-btn')) {
                e.preventDefault();
                this.addFormToFormset('social', socialFormCount++);
                if (socialTotalForms) socialTotalForms.value = socialFormCount;
            }
            
            if (e.target.matches('#add-registry-btn')) {
                e.preventDefault();
                this.addFormToFormset('registry', registryFormCount++);
                if (registryTotalForms) registryTotalForms.value = registryFormCount;
            }
            
            if (e.target.matches('.delete-form-btn')) {
                e.preventDefault();
                this.handleFormDelete(e.target);
            }
        });

        // URL preview update
        ['id_partner_1_name', 'id_partner_2_name', 'id_wedding_date'].forEach(id => {
            const field = document.getElementById(id);
            if (field) {
                field.addEventListener('input', this.updateUrlPreview);
                field.addEventListener('change', this.updateUrlPreview);
            }
        });
    }

    addFormToFormset(formsetType, formIndex) {
        const formsetDiv = document.getElementById(`${formsetType}-formset`);
        if (!formsetDiv) return;

        const newForm = document.createElement('div');
        newForm.className = `${formsetType}-form border rounded p-3 mb-3`;
        newForm.setAttribute('data-form-index', formIndex);
        
        if (formsetType === 'social') {
            newForm.innerHTML = this.getSocialFormHTML(formIndex);
        } else {
            newForm.innerHTML = this.getRegistryFormHTML(formIndex);
        }
        
        formsetDiv.appendChild(newForm);
    }

    getSocialFormHTML(index) {
        return `
            <div class="row">
                <div class="col-lg-5 mb-2">
                    <label class="form-label">Social Media URL</label>
                    <input type="url" name="social-${index}-url" class="form-control url-field" 
                           placeholder="https://instagram.com/yourusername">
                    <div class="form-text">We'll automatically detect the platform</div>
                </div>
                <div class="col-lg-5 mb-2">
                    <label class="form-label">Display Name</label>
                    <input type="text" name="social-${index}-display_name" class="form-control" 
                           placeholder="@yourusername">
                    <div class="form-text">How this appears on your page</div>
                </div>
                <div class="col-lg-2 mb-2 d-flex align-items-end">
                    <button type="button" class="btn btn-outline-danger btn-sm delete-form-btn">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    getRegistryFormHTML(index) {
        return `
            <div class="row">
                <div class="col-lg-4 mb-2">
                    <label class="form-label">Registry URL</label>
                    <input type="url" name="registry-${index}-url" class="form-control url-field" 
                           placeholder="https://amazon.com/wedding/registry">
                    <div class="form-text">We'll detect the store automatically</div>
                </div>
                <div class="col-lg-4 mb-2">
                    <label class="form-label">Registry Name <span class="text-danger">*</span></label>
                    <input type="text" name="registry-${index}-registry_name" class="form-control" 
                           placeholder="Our Home Registry" required>
                </div>
                <div class="col-lg-4 mb-2 d-flex align-items-end">
                    <button type="button" class="btn btn-outline-danger btn-sm delete-form-btn">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="row">
                <div class="col-12 mb-2">
                    <label class="form-label">Description</label>
                    <textarea name="registry-${index}-description" class="form-control" rows="2" 
                              placeholder="Kitchen appliances, home decor..."></textarea>
                </div>
            </div>
        `;
    }

    handleFormDelete(button) {
        const form = button.closest('.social-form, .registry-form');
        const deleteInput = form.querySelector('input[name$="-DELETE"]');
        
        if (deleteInput) {
            // Mark for deletion
            deleteInput.checked = true;
            form.classList.add('marked-for-deletion');
            button.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i>';
            button.classList.remove('btn-outline-danger');
            button.classList.add('btn-outline-success');
            button.onclick = () => this.restoreForm(button);
        } else {
            // Remove new form
            form.remove();
        }
    }

    restoreForm(button) {
        const form = button.closest('.social-form, .registry-form');
        const deleteInput = form.querySelector('input[name$="-DELETE"]');
        
        if (deleteInput) {
            deleteInput.checked = false;
            form.classList.remove('marked-for-deletion');
            button.innerHTML = '<i class="bi bi-trash"></i>';
            button.classList.remove('btn-outline-success'); 
            button.classList.add('btn-outline-danger');
            button.onclick = () => this.handleFormDelete(button);
        }
    }

    updateUrlPreview() {
        const previewField = document.getElementById('url-preview');
        if (!previewField) return;

        const name1 = document.getElementById('id_partner_1_name')?.value || '';
        const name2 = document.getElementById('id_partner_2_name')?.value || '';
        const date = document.getElementById('id_wedding_date')?.value || '';
        
        if (name1 && name2) {
            const clean1 = name1.replace(/[^a-zA-Z0-9]/g, '').toLowerCase().substring(0, 15);
            const clean2 = name2.replace(/[^a-zA-Z0-9]/g, '').toLowerCase().substring(0, 15);
            
            let dateStr = 'tbd';
            if (date) {
                // Parse date manually to avoid timezone issues
                const dateParts = date.split('-');
                if (dateParts.length === 3) {
                    const month = dateParts[1].padStart(2, '0');
                    const day = dateParts[2].padStart(2, '0');
                    const year = dateParts[0].slice(-2);
                    dateStr = month + day + year;
                }
            }
            
            const slug = clean1 + clean2 + dateStr;
            previewField.value = `yoursite.com/wedding/${slug}/`;
        } else {
            previewField.value = 'yoursite.com/wedding/[your-custom-url]/';
        }
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
        return csrfToken;
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'warning'} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 3000);
    }
}

/**
 * Studio & Image Processing Manager
 */
class StudioManager {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupFileUpload();
            this.setupImageSelection();
            this.setupProcessingForms();
            this.setupStatusChecking();
        });
    }

    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        const dropZone = document.getElementById('dropZone');
        
        if (!fileInput || !uploadBtn || !dropZone) return;
        
        uploadBtn.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('click', () => fileInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    }

    async handleFileUpload(file) {
        if (!file.type.startsWith('image/')) {
            this.showToast('Please select an image file', 'error');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) {
            this.showToast('File too large (max 10MB)', 'error');
            return;
        }
        
        this.showUploadProgress();
        
        try {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());
            
            const response = await fetch('/studio/upload/', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                this.handleUploadSuccess(data);
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast(error.message || 'Upload failed', 'error');
            this.showUploadArea();
        }
    }

    handleUploadSuccess(data) {
        this.addImageToRecent(data);
        this.selectImage(data.image_id, data);
        this.showToast('Image uploaded successfully!', 'success');
    }

    addImageToRecent(data) {
        const container = document.getElementById('recentImagesContainer');
        if (!container) return;
        
        const newThumbnail = this.createThumbnailElement(data);
        container.insertBefore(newThumbnail, container.firstChild);
        
        // Remove excess thumbnails
        const thumbnails = container.querySelectorAll('.col-4');
        if (thumbnails.length > 3) {
            thumbnails[3].remove();
        }
    }

    createThumbnailElement(data) {
        const div = document.createElement('div');
        div.className = 'col-4';
        div.innerHTML = `
            <div class="venue-thumbnail" 
                 data-image-id="${data.image_id}"
                 data-image-url="${data.image_url}"
                 data-thumbnail-url="${data.thumbnail_url}"
                 data-image-name="${data.image_name}">
                <img src="${data.thumbnail_url}" 
                     class="card-img-top" 
                     style="height: 80px; object-fit: cover; border-radius: 0.25rem;" 
                     alt="${data.image_name}">
            </div>
        `;
        
        div.querySelector('.venue-thumbnail').addEventListener('click', () => {
            this.selectImageFromThumbnail(div.querySelector('.venue-thumbnail'));
        });
        
        return div;
    }

    setupImageSelection() {
        document.querySelectorAll('.venue-thumbnail').forEach(thumbnail => {
            thumbnail.addEventListener('click', () => {
                this.selectImageFromThumbnail(thumbnail);
            });
        });
    }

    selectImageFromThumbnail(thumbnail) {
        // Clear previous selections
        document.querySelectorAll('.venue-thumbnail').forEach(t => {
            t.classList.remove('selected');
        });
        
        thumbnail.classList.add('selected');
        
        const imageId = thumbnail.dataset.imageId;
        const imageUrl = thumbnail.dataset.imageUrl;
        const imageName = thumbnail.dataset.imageName;
        
        // Update preview
        this.showImagePreview(imageUrl, imageName);
        this.updateTransformButton(true);
        
        // Store selected image ID
        this.selectedImageId = imageId;
    }

    selectImage(imageId, data) {
        this.selectedImageId = imageId;
        this.showImagePreview(data.image_url, data.image_name);
        this.updateTransformButton(true);
    }

    showUploadProgress() {
        const uploadArea = document.getElementById('uploadArea');
        const uploadProgress = document.getElementById('uploadProgress');
        const imagePreview = document.getElementById('imagePreview');
        
        if (uploadArea) uploadArea.classList.add('d-none');
        if (imagePreview) imagePreview.classList.add('d-none');
        if (uploadProgress) {
            uploadProgress.classList.remove('d-none');
            uploadProgress.classList.add('d-flex');
        }
    }

    showImagePreview(imageUrl, imageName) {
        const uploadArea = document.getElementById('uploadArea');
        const uploadProgress = document.getElementById('uploadProgress');
        const imagePreview = document.getElementById('imagePreview');
        const selectedImage = document.getElementById('selectedImage');
        const selectedImageName = document.getElementById('selectedImageName');
        
        if (uploadArea) uploadArea.classList.add('d-none');
        if (uploadProgress) {
            uploadProgress.classList.add('d-none');
            uploadProgress.classList.remove('d-flex');
        }
        if (imagePreview) {
            imagePreview.classList.remove('d-none');
            imagePreview.classList.add('d-flex');
        }
        
        if (selectedImage) selectedImage.src = imageUrl;
        if (selectedImageName) selectedImageName.textContent = imageName;
    }

    showUploadArea() {
        const uploadArea = document.getElementById('uploadArea');
        const uploadProgress = document.getElementById('uploadProgress');
        const imagePreview = document.getElementById('imagePreview');
        
        if (imagePreview) imagePreview.classList.add('d-none');
        if (uploadProgress) {
            uploadProgress.classList.add('d-none');
            uploadProgress.classList.remove('d-flex');
        }
        if (uploadArea) uploadArea.classList.remove('d-none');
    }

    setupProcessingForms() {
        const transformBtn = document.getElementById('transformBtn');
        if (!transformBtn) return;
        
        transformBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.processImage();
        });
        
        // Setup form change listeners
        ['wedding-theme', 'space-type'].forEach(id => {
            const field = document.getElementById(id);
            if (field) {
                field.addEventListener('change', () => {
                    this.updateTransformButton();
                    this.showSmartSuggestions();
                });
            }
        });
    }

    updateTransformButton(hasImage = null) {
        const transformBtn = document.getElementById('transformBtn');
        if (!transformBtn) return;
        
        const hasSelectedImage = hasImage !== null ? hasImage : !!this.selectedImageId;
        const hasTheme = document.getElementById('wedding-theme')?.value;
        const hasSpace = document.getElementById('space-type')?.value;
        
        transformBtn.disabled = !(hasSelectedImage && hasTheme && hasSpace);
    }

    showSmartSuggestions() {
        const theme = document.getElementById('wedding-theme')?.value;
        const space = document.getElementById('space-type')?.value;
        const suggestionsDiv = document.getElementById('smartSuggestions');
        
        if (!theme || !space || !suggestionsDiv) return;
        
        const suggestions = this.getSuggestions(theme, space);
        if (suggestions) {
            document.getElementById('suggestionText').textContent = suggestions;
            suggestionsDiv.style.display = 'block';
        } else {
            suggestionsDiv.style.display = 'none';
        }
    }

    getSuggestions(theme, space) {
        const suggestionMap = {
            'rustic_reception_area': 'Medium guest count, moderate budget, fall season, earth tones',
            'rustic_barn': 'Intimate to medium guests, string lights, warm colors',
            'modern_ballroom': 'Large guest count, luxury budget, evening time, monochrome colors',
            'garden_wedding_ceremony': 'Any size, spring/summer, afternoon, natural colors',
            'beach_wedding_ceremony': 'Medium guests, summer, sunset time, coastal colors',
            'vintage_reception_area': 'Medium guests, moderate to luxury budget, pastels',
            'classic_ballroom': 'Large to grand, luxury budget, evening, neutral palette'
        };
        
        return suggestionMap[`${theme}_${space}`];
    }

    async processImage() {
        if (!this.selectedImageId) {
            this.showToast('Please select an image first', 'error');
            return;
        }
        
        const theme = document.getElementById('wedding-theme')?.value;
        const space = document.getElementById('space-type')?.value;
        
        if (!theme || !space) {
            this.showToast('Please select both wedding style and space type', 'error');
            return;
        }
        
        this.showProcessingStatus();
        
        const data = {
            wedding_theme: theme,
            space_type: space,
            guest_count: document.getElementById('guest-count')?.value || '',
            budget_level: document.getElementById('budget-level')?.value || '',
            season: document.getElementById('season')?.value || '',
            time_of_day: document.getElementById('time-of-day')?.value || '',
            color_scheme: document.getElementById('color-scheme')?.value || '',
            custom_colors: document.getElementById('custom-colors')?.value || '',
            additional_details: document.getElementById('additional-details')?.value || ''
        };
        
        try {
            const response = await fetch(`/studio/image/${this.selectedImageId}/process/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                this.showToast('✨ Transformation started! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = result.redirect_url;
                }, 2000);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Processing error:', error);
            this.showToast('Error: ' + error.message, 'error');
            this.hideProcessingStatus();
        }
    }

    showProcessingStatus() {
        const statusDiv = document.getElementById('processingStatus');
        const transformBtn = document.getElementById('transformBtn');
        
        if (statusDiv) statusDiv.style.display = 'block';
        if (transformBtn) {
            transformBtn.disabled = true;
            transformBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Creating Magic...';
        }
    }

    hideProcessingStatus() {
        const statusDiv = document.getElementById('processingStatus');
        const transformBtn = document.getElementById('transformBtn');
        
        if (statusDiv) statusDiv.style.display = 'none';
        if (transformBtn) {
            transformBtn.disabled = false;
            transformBtn.innerHTML = '<i class="bi bi-magic"></i> <span class="fs-5">Transform Space</span>';
            this.updateTransformButton();
        }
    }

    setupStatusChecking() {
        // Auto-refresh processing jobs
        const processingJobs = document.querySelectorAll('.processing-status');
        if (processingJobs.length > 0) {
            this.checkJobStatuses();
            setInterval(() => this.checkJobStatuses(), 30000); // Check every 30 seconds
        }
    }

    async checkJobStatuses() {
        const processingJobs = document.querySelectorAll('[data-job-id]');
        
        for (const jobElement of processingJobs) {
            const jobId = jobElement.dataset.jobId;
            if (jobId) {
                try {
                    const response = await fetch(`/studio/job/${jobId}/status/`);
                    const data = await response.json();
                    
                    if (data.status === 'completed' || data.status === 'failed') {
                        // Reload page to show updated status
                        window.location.reload();
                        break;
                    }
                } catch (error) {
                    console.error('Error checking job status:', error);
                }
            }
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
}

/**
 * Dashboard Manager
 */
class DashboardManager {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupUsageDisplay();
            this.setupQuickActions();
            this.setupSubscriptionManagement();
        });
    }

    setupUsageDisplay() {
        // Update usage indicators with smooth animations
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 500);
        });
    }

    setupQuickActions() {
        // Add hover effects to quick action buttons
        document.querySelectorAll('.btn-outline-primary, .btn-outline-secondary, .btn-outline-danger').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-2px)';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
            });
        });
    }

    setupSubscriptionManagement() {
        // Handle subscription upgrade prompts
        const upgradeButtons = document.querySelectorAll('[href*="pricing"]');
        upgradeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Could add analytics tracking here
                console.log('User clicked upgrade button');
            });
        });
    }
}

// Global functions for compatibility with existing form HTML
window.detectBrandingFromUrl = function(urlField) {
    if (window.weddingFormManager) {
        const form = urlField.closest('.social-form, .registry-form');
        if (form) {
            const formsetType = form.classList.contains('social-form') ? 'social' : 'registry';
            window.weddingFormManager.detectAndApplyBranding(urlField, formsetType);
        }
    }
};

// Global confirmation function
window.confirmDelete = function(id, name, type = 'item') {
    return confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`);
};

// Global toast function
window.showToast = function(message, type = 'info') {
    if (window.formEnhancements) {
        window.formEnhancements.showToast(message, type);
    } else {
        // Fallback toast
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.innerHTML = `${message} <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
};

// Initialize all managers
document.addEventListener('DOMContentLoaded', function() {
    window.weddingFormManager = new WeddingFormManager();
    window.homepageManager = new HomepageManager();
    window.formEnhancements = new FormEnhancements();
    window.studioManager = new StudioManager();
    window.dashboardManager = new DashboardManager();
});



document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.getElementById('newsletter-form');
    const emailInput = document.getElementById('newsletter-email');
    const submitBtn = document.getElementById('newsletter-submit-btn');
    const icon = document.getElementById('newsletter-icon');
    const spinner = document.getElementById('newsletter-spinner');
    const messagesDiv = document.getElementById('newsletter-messages');
    
    if (!newsletterForm) return; // Exit if form not found
    
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        if (!email) {
            showMessage('Please enter your email address.', 'error');
            return;
        }
        
        // Validate email format
        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }
        
        // Show loading state
        setLoadingState(true);
        clearMessages();
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Submit via AJAX
        fetch('/newsletter/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                email: email
            })
        })
        .then(response => response.json())
        .then(data => {
            setLoadingState(false);
            
            if (data.success) {
                showMessage(data.message, 'success');
                emailInput.value = ''; // Clear the form
                
                // Disable form temporarily
                emailInput.disabled = true;
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds
                setTimeout(() => {
                    emailInput.disabled = false;
                    submitBtn.disabled = false;
                    clearMessages();
                }, 5000);
                
            } else {
                showMessage(data.message || 'Something went wrong. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Newsletter signup error:', error);
            setLoadingState(false);
            showMessage('Network error. Please check your connection and try again.', 'error');
        });
    });
    
    function setLoadingState(loading) {
        if (loading) {
            submitBtn.disabled = true;
            icon.classList.add('d-none');
            spinner.classList.remove('d-none');
        } else {
            submitBtn.disabled = false;
            icon.classList.remove('d-none');
            spinner.classList.add('d-none');
        }
    }
    
    function showMessage(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const iconClass = type === 'success' ? 'bi-check-circle' : 'bi-exclamation-circle';
        
        messagesDiv.innerHTML = `
            <div class="alert ${alertClass} alert-sm py-2 px-3 small" role="alert">
                <i class="${iconClass} me-1"></i>
                ${message}
            </div>
        `;
        
        // Auto-hide success messages after 4 seconds
        if (type === 'success') {
            setTimeout(() => {
                clearMessages();
            }, 4000);
        }
    }
    
    function clearMessages() {
        messagesDiv.innerHTML = '';
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Clear messages when user starts typing again
    emailInput.addEventListener('input', function() {
        if (messagesDiv.innerHTML) {
            setTimeout(clearMessages, 500);
        }
    });
});
