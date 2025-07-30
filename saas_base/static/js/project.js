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

// Initialize all managers
document.addEventListener('DOMContentLoaded', function() {
    window.weddingFormManager = new WeddingFormManager();
    window.homepageManager = new HomepageManager();
    window.formEnhancements = new FormEnhancements();
});