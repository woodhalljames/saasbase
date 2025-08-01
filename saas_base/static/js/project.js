/**
 * ============================================
 * DREAMWEDAI COMPLETE JAVASCRIPT
 * ============================================
 */

/**
 * Wedding Form Manager
 * Handles dynamic formsets and branding detection
 */
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

    initializeDynamicFormsets() {
        this.setupDynamicFormset('social', 'Social Media Link');
        this.setupDynamicFormset('weddinglink', 'Wedding Link');
        this.setupDynamicFormset('registry', 'Wedding Registry');
    }

    setupDynamicFormset(formsetType, displayName) {
        const formsetContainer = document.getElementById(`${formsetType}-formset`);
        if (!formsetContainer) return;
        this.setupDeleteButtons(formsetType);
    }

    setupDeleteButtons(formsetType) {
        const forms = document.querySelectorAll(`[id^="${formsetType}-form-"]:not(#${formsetType}-empty-form)`);
        forms.forEach(form => {
            if (!form.querySelector('.formset-delete-btn')) {
                const deleteButton = this.createDeleteButton(form, formsetType);
                form.appendChild(deleteButton);
            }
        });
    }

    createDeleteButton(formElement, formsetType) {
        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn btn-outline-danger btn-sm mt-2 formset-delete-btn';
        deleteButton.innerHTML = '<i class="bi bi-trash"></i> Remove';
        deleteButton.onclick = () => this.removeFormsetForm(formElement, formsetType);
        return deleteButton;
    }

    removeFormsetForm(formElement, formsetType) {
        const deleteInput = formElement.querySelector(`input[name*="DELETE"]`);
        const idInput = formElement.querySelector(`input[name*="id"]`);

        if (deleteInput && idInput && idInput.value) {
            deleteInput.checked = true;
            formElement.style.display = 'none';
        } else {
            formElement.remove();
            this.reindexFormset(formsetType);
        }
    }

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

    setupBrandingDetection() {
        document.querySelectorAll('.url-field').forEach(urlField => {
            this.setupBrandingForField(urlField);
        });
    }

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
            this.clearBrandingIndicator(urlField);
        });
    }

    async detectAndApplyBranding(urlField, formsetType) {
        const url = urlField.value.trim();
        const form = urlField.closest('.social-form, .registry-form');
        
        if (!url || !form) return;

        const cacheKey = `${formsetType}-${url}`;
        if (this.brandingCache.has(cacheKey)) {
            this.applyBrandingData(form, this.brandingCache.get(cacheKey), formsetType);
            return;
        }

        this.showBrandingLoading(urlField);

        try {
            const response = await fetch(`${this.apiBaseUrl}detect-branding/?url=${encodeURIComponent(url)}&type=${formsetType}`);
            const data = await response.json();
            
            if (response.ok && data.success && data.branding.detected) {
                this.brandingCache.set(cacheKey, data.branding);
                this.applyBrandingData(form, data.branding, formsetType);
                this.showBrandingIndicator(urlField, data.branding, 'success');
            } else {
                this.showBrandingIndicator(urlField, { name: 'Unknown', type: 'other' }, 'warning');
            }
        } catch (error) {
            console.error('Error detecting branding:', error);
            this.showBrandingIndicator(urlField, null, 'error');
        }
    }

    applyBrandingData(form, brandingData, formsetType) {
        if (formsetType === 'social') {
            const displayNameField = form.querySelector('input[name*="display_name"]');
            if (displayNameField && !displayNameField.value && brandingData.suggestions?.display_name) {
                displayNameField.value = brandingData.suggestions.display_name;
            }
        } else {
            const registryNameField = form.querySelector('input[name*="registry_name"]');
            const descriptionField = form.querySelector('textarea[name*="description"]');
            
            if (registryNameField && !registryNameField.value && brandingData.suggestions?.display_name) {
                registryNameField.value = brandingData.suggestions.display_name;
            }
            
            if (descriptionField && !descriptionField.value && brandingData.description) {
                descriptionField.value = brandingData.description;
            }
        }
    }

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
        
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.remove();
            }
        }, 5000);
    }

    showBrandingLoading(urlField) {
        this.clearBrandingIndicator(urlField);
        
        const indicator = document.createElement('div');
        indicator.className = 'branding-indicator alert alert-info alert-sm mt-1';
        indicator.innerHTML = '<i class="bi bi-hourglass-split"></i> Detecting platform...';
        
        urlField.parentNode.appendChild(indicator);
    }

    clearBrandingIndicator(urlField) {
        const existing = urlField.parentNode.querySelector('.branding-indicator');
        if (existing) {
            existing.remove();
        }
    }

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

        updatePreview();
    }

    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alert, container.firstChild);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

/**
 * Enhanced Homepage Manager
 * Handles all homepage interactions and animations
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
            this.setupInteractiveDemo();
            this.setupCountUpAnimations();
            this.setupThemeCardInteractions();
            this.setupSmoothScrolling();
            this.setupParallaxEffects();
            this.setupHoverEffects();
            this.addAnimationStyles();
        });
    }

    addAnimationStyles() {
        if (!document.getElementById('homepage-animations')) {
            const style = document.createElement('style');
            style.id = 'homepage-animations';
            style.textContent = `
                .animate-in {
                    opacity: 1 !important;
                    transform: translateY(0) !important;
                }
                
                @keyframes sparkleFloat {
                    0% { 
                        opacity: 0; 
                        transform: translateY(0) scale(0.5); 
                    }
                    50% { 
                        opacity: 1; 
                        transform: translateY(-20px) scale(1); 
                    }
                    100% { 
                        opacity: 0; 
                        transform: translateY(-40px) scale(0.5); 
                    }
                }
                
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    setupInteractiveDemo() {
        const demoContainer = document.querySelector('.before-after-container');
        if (!demoContainer) return;

        let isTransformed = false;
        
        demoContainer.addEventListener('click', () => {
            const arrow = demoContainer.querySelector('.transform-arrow');
            const beforeImg = demoContainer.querySelector('.before-image');
            const afterImg = demoContainer.querySelector('.after-image');
            
            if (!isTransformed) {
                this.performTransformation(arrow, beforeImg, afterImg);
                isTransformed = true;
            } else {
                this.resetTransformation(arrow, beforeImg, afterImg);
                isTransformed = false;
            }
        });

        demoContainer.style.cursor = 'pointer';
        demoContainer.title = 'Click to see AI transformation magic!';
    }

    performTransformation(arrow, beforeImg, afterImg) {
        arrow.innerHTML = '<i class="bi bi-hourglass-split rotating"></i>';
        arrow.style.background = 'var(--gradient-cyan)';
        
        beforeImg.style.filter = 'brightness(0.7) saturate(0.8)';
        afterImg.style.filter = 'brightness(1.2) saturate(1.3)';
        
        setTimeout(() => {
            arrow.innerHTML = '<i class="bi bi-check-circle"></i>';
            arrow.style.background = '#28a745';
            this.addSparkleEffect(beforeImg.parentElement);
        }, 1500);
    }

    resetTransformation(arrow, beforeImg, afterImg) {
        arrow.innerHTML = '<i class="bi bi-arrow-right"></i>';
        arrow.style.background = 'var(--gradient-rose)';
        beforeImg.style.filter = '';
        afterImg.style.filter = '';
    }

    addSparkleEffect(container) {
        for (let i = 0; i < 6; i++) {
            setTimeout(() => {
                const sparkle = document.createElement('div');
                sparkle.innerHTML = '✨';
                sparkle.style.position = 'absolute';
                sparkle.style.left = Math.random() * 100 + '%';
                sparkle.style.top = Math.random() * 100 + '%';
                sparkle.style.fontSize = '1.5rem';
                sparkle.style.animation = 'sparkleFloat 2s ease-out forwards';
                sparkle.style.pointerEvents = 'none';
                sparkle.style.zIndex = '20';
                
                container.appendChild(sparkle);
                
                setTimeout(() => {
                    if (sparkle.parentNode) {
                        sparkle.parentNode.removeChild(sparkle);
                    }
                }, 2000);
            }, i * 300);
        }
    }

    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        const animateElements = document.querySelectorAll(
            '.theme-card, .tool-card, .testimonial-card, .step-card, .section-title, .section-subtitle'
        );
        
        animateElements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s ease';
            el.style.transitionDelay = `${(index % 3) * 0.1}s`;
            observer.observe(el);
        });
    }

    setupCountUpAnimations() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        const countUp = (element, target) => {
            const increment = target / 60;
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    element.textContent = this.formatStatNumber(target);
                    clearInterval(timer);
                } else {
                    element.textContent = this.formatStatNumber(Math.floor(current));
                }
            }, 16);
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

    formatStatNumber(num) {
        if (num >= 1000) {
            return Math.floor(num / 1000) + 'k+';
        }
        return num + '+';
    }

    setupThemeCardInteractions() {
        document.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-15px) scale(1.02)';
                
                const preview = card.querySelector('.theme-preview');
                if (preview) {
                    preview.style.boxShadow = '0 0 30px rgba(255, 255, 255, 0.3)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
                
                const preview = card.querySelector('.theme-preview');
                if (preview) {
                    preview.style.boxShadow = '';
                }
            });

            card.addEventListener('click', (e) => {
                this.createRippleEffect(e, card);
            });
        });
    }

    createRippleEffect(e, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s linear';
        ripple.style.pointerEvents = 'none';
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }

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

    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('.floating-element');
        
        if (parallaxElements.length === 0) return;
        
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset;
            
            parallaxElements.forEach((element, index) => {
                const speed = 0.3 + (index * 0.1);
                const yPos = -(scrollTop * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    setupHoverEffects() {
        document.querySelectorAll('.hero-cta-primary, .hero-cta-secondary').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-3px) scale(1.05)';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0) scale(1)';
            });

            btn.addEventListener('click', (e) => {
                btn.style.transform = 'translateY(0) scale(0.95)';
                setTimeout(() => {
                    btn.style.transform = 'translateY(-3px) scale(1.05)';
                }, 150);
            });
        });

        document.querySelectorAll('.tool-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                const icon = card.querySelector('.tool-icon');
                if (icon) {
                    icon.style.transform = 'scale(1.2) rotate(5deg)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                const icon = card.querySelector('.tool-icon');
                if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                }
            });
        });

        document.querySelectorAll('.step-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                const number = card.querySelector('.step-number');
                const icon = card.querySelector('.step-icon');
                
                if (number) {
                    number.style.transform = 'translateX(-50%) scale(1.2)';
                }
                if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(5deg)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                const number = card.querySelector('.step-number');
                const icon = card.querySelector('.step-icon');
                
                if (number) {
                    number.style.transform = 'translateX(-50%) scale(1)';
                }
                if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                }
            });
        });
    }
}

/**
 * Form Enhancements
 * General form functionality and enhancements
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
            this.setupFormsetManagement();
        });
    }

    setupFormsetManagement() {
        let socialFormCount = this.getFormsetCount('social');
        let weddingLinkFormCount = this.getFormsetCount('weddinglink');

        document.addEventListener('click', (e) => {
            if (e.target.matches('#add-social-btn')) {
                e.preventDefault();
                this.addFormToFormset('social', socialFormCount++);
                this.updateTotalForms('social', socialFormCount);
            }
            
            if (e.target.matches('#add-wedding-link-btn')) {
                e.preventDefault();
                this.addFormToFormset('weddinglink', weddingLinkFormCount++);
                this.updateTotalForms('weddinglink', weddingLinkFormCount);
            }
            
            if (e.target.matches('.delete-form-btn')) {
                e.preventDefault();
                this.handleFormDelete(e.target);
            }
        });

        ['id_partner_1_name', 'id_partner_2_name', 'id_wedding_date'].forEach(id => {
            const field = document.getElementById(id);
            if (field) {
                field.addEventListener('input', this.updateUrlPreview);
                field.addEventListener('change', this.updateUrlPreview);
            }
        });
    }

    getFormsetCount(prefix) {
        const totalFormsInput = document.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
        return totalFormsInput ? parseInt(totalFormsInput.value) : 0;
    }

    updateTotalForms(prefix, count) {
        const totalFormsInput = document.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
        if (totalFormsInput) {
            totalFormsInput.value = count;
        }
    }

    addFormToFormset(formsetType, formIndex) {
        const formsetDiv = document.getElementById(`${formsetType}-formset`);
        if (!formsetDiv) return;

        const newForm = document.createElement('div');
        newForm.className = `${formsetType === 'social' ? 'social' : 'wedding-link'}-form border rounded p-3 mb-3`;
        newForm.setAttribute('data-form-index', formIndex);
        
        if (formsetType === 'social') {
            newForm.innerHTML = this.getSocialFormHTML(formIndex);
        } else {
            newForm.innerHTML = this.getWeddingLinkFormHTML(formIndex);
        }
        
        formsetDiv.appendChild(newForm);
        
        // Setup delete button
        const deleteBtn = newForm.querySelector('.delete-form-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleFormDelete(e.target);
            });
        }
        
        // Setup link type change handler for wedding links
        if (formsetType === 'weddinglink') {
            const linkTypeSelect = newForm.querySelector('select[name*="link_type"]');
            if (linkTypeSelect && window.updateLinkPlaceholders) {
                linkTypeSelect.addEventListener('change', function() {
                    window.updateLinkPlaceholders(this);
                });
                window.updateLinkPlaceholders(linkTypeSelect);
            }
        }
        
        // Animate in
        newForm.style.opacity = '0';
        newForm.style.transform = 'translateY(10px)';
        setTimeout(() => {
            newForm.style.transition = 'all 0.3s ease';
            newForm.style.opacity = '1';
            newForm.style.transform = 'translateY(0)';
        }, 10);
    }

    getSocialFormHTML(index) {
        return `
            <div class="row">
                <div class="col-lg-3 mb-2">
                    <label class="form-label">Belongs To</label>
                    <select name="social-${index}-owner" class="form-select">
                        <option value="partner_1">Partner 1</option>
                        <option value="partner_2">Partner 2</option>
                        <option value="shared" selected>Both/Shared</option>
                    </select>
                    <div class="form-text">Who does this social media account belong to?</div>
                </div>
                <div class="col-lg-4 mb-2">
                    <label class="form-label">Social Media URL</label>
                    <input type="url" name="social-${index}-url" class="form-control url-field" 
                           placeholder="https://instagram.com/yourusername">
                    <div class="form-text">We'll automatically detect the platform</div>
                </div>
                <div class="col-lg-4 mb-2">
                    <label class="form-label">Display Name</label>
                    <input type="text" name="social-${index}-display_name" class="form-control" 
                           placeholder="@yourusername or Your Page Name">
                    <div class="form-text">How this link should appear on your wedding page</div>
                </div>
                <div class="col-lg-1 mb-2 d-flex align-items-end">
                    <button type="button" class="btn btn-outline-danger btn-sm delete-form-btn" data-form-type="social">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <input type="hidden" name="social-${index}-DELETE" value="">
            <input type="hidden" name="social-${index}-id" value="">
        `;
    }

    getWeddingLinkFormHTML(index) {
        return `
            <div class="row">
                <div class="col-lg-3 mb-2">
                    <label class="form-label">Link Type</label>
                    <select name="weddinglink-${index}-link_type" class="form-select" onchange="updateLinkPlaceholders(this)">
                        <option value="registry">Wedding Registry</option>
                        <option value="rsvp">RSVP Site</option>
                        <option value="livestream">Live Stream</option>
                        <option value="photos">Wedding Photos</option>
                        <option value="website">Wedding Website</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="col-lg-5 mb-2">
                    <label class="form-label">URL</label>
                    <input type="url" name="weddinglink-${index}-url" class="form-control url-field" 
                           placeholder="https://example.com/your-link">
                    <div class="form-text">We'll automatically detect the service from your URL</div>
                </div>
                <div class="col-lg-3 mb-2">
                    <label class="form-label">Title <span class="text-danger">*</span></label>
                    <input type="text" name="weddinglink-${index}-title" class="form-control" 
                           placeholder="Link Title" required>
                    <div class="form-text">A friendly name for this link</div>
                </div>
                <div class="col-lg-1 mb-2 d-flex align-items-end">
                    <button type="button" class="btn btn-outline-danger btn-sm delete-form-btn" data-form-type="wedding-link">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="row">
                <div class="col-12 mb-2">
                    <label class="form-label">Description</label>
                    <textarea name="weddinglink-${index}-description" class="form-control" rows="2" 
                              placeholder="Additional details about this link (optional)"></textarea>
                    <div class="form-text">Additional details about this link (optional)</div>
                </div>
            </div>
            <input type="hidden" name="weddinglink-${index}-DELETE" value="">
            <input type="hidden" name="weddinglink-${index}-id" value="">
        `;
    }

    handleFormDelete(button) {
        const form = button.closest('.social-form, .wedding-link-form');
        const deleteInput = form.querySelector('input[name$="-DELETE"]');
        
        if (deleteInput) {
            if (deleteInput.value === 'on') {
                deleteInput.value = '';
                form.classList.remove('marked-for-deletion');
                form.style.opacity = '';
                button.innerHTML = '<i class="bi bi-trash"></i>';
                button.classList.remove('btn-outline-success');
                button.classList.add('btn-outline-danger');
            } else {
                deleteInput.value = 'on';
                form.classList.add('marked-for-deletion');
                form.style.opacity = '0.5';
                button.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i>';
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-outline-success');
            }
        } else {
            form.remove();
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
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('focus', () => {
                input.parentNode.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentNode.classList.remove('focused');
                }
            });
            
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
 * Studio Manager
 * Handles image processing and studio functionality
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
        document.querySelectorAll('.venue-thumbnail').forEach(t => {
            t.classList.remove('selected');
        });
        
        thumbnail.classList.add('selected');
        
        const imageId = thumbnail.dataset.imageId;
        const imageUrl = thumbnail.dataset.imageUrl;
        const imageName = thumbnail.dataset.imageName;
        
        this.showImagePreview(imageUrl, imageName);
        this.updateTransformButton(true);
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
        const processingJobs = document.querySelectorAll('.processing-status');
        if (processingJobs.length > 0) {
            this.checkJobStatuses();
            setInterval(() => this.checkJobStatuses(), 30000);
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
 * Handles dashboard functionality
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
        const upgradeButtons = document.querySelectorAll('[href*="pricing"]');
        upgradeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                console.log('User clicked upgrade button');
            });
        });
    }
}

/**
 * Newsletter Functionality
 */
function initializeNewsletter() {
    const newsletterForm = document.getElementById('newsletter-form');
    const emailInput = document.getElementById('newsletter-email');
    const submitBtn = document.getElementById('newsletter-submit-btn');
    const icon = document.getElementById('newsletter-icon');
    const spinner = document.getElementById('newsletter-spinner');
    const messagesDiv = document.getElementById('newsletter-messages');
    
    if (!newsletterForm) return;
    
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        if (!email) {
            showMessage('Please enter your email address.', 'error');
            return;
        }
        
        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }
        
        setLoadingState(true);
        clearMessages();
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
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
                emailInput.value = '';
                
                emailInput.disabled = true;
                submitBtn.disabled = true;
                
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
    
    emailInput.addEventListener('input', function() {
        if (messagesDiv.innerHTML) {
            setTimeout(clearMessages, 500);
        }
    });
}

/**
 * Global Utility Functions
 */
window.updateLinkPlaceholders = function(selectElement) {
    const linkType = selectElement.value;
    const form = selectElement.closest('.wedding-link-form');
    const urlField = form.querySelector('input[name*="url"]');
    const titleField = form.querySelector('input[name*="title"]');
    const descriptionField = form.querySelector('textarea[name*="description"]');
    
    const placeholders = {
        'registry': {
            url: 'https://amazon.com/wedding/your-registry',
            title: 'Our Home Registry',
            description: 'Kitchen appliances, home decor, and everyday essentials'
        },
        'rsvp': {
            url: 'https://rsvpify.com/your-event',
            title: 'RSVP for Our Wedding', 
            description: 'Please let us know if you can attend'
        },
        'livestream': {
            url: 'https://zoom.us/j/your-meeting-id',
            title: 'Wedding Ceremony Live Stream',
            description: 'Watch our ceremony live online'
        },
        'photos': {
            url: 'https://photos.google.com/share/your-album',
            title: 'Wedding Photo Gallery',
            description: 'View and download our wedding photos'
        },
        'website': {
            url: 'https://ourweddingwebsite.com',
            title: 'Our Wedding Website',
            description: 'More details about our special day'
        },
        'other': {
            url: 'https://example.com',
            title: 'Custom Link',
            description: 'Additional wedding information'
        }
    };
    
    const config = placeholders[linkType] || placeholders['other'];
    if (urlField) urlField.placeholder = config.url;
    if (titleField) titleField.placeholder = config.title;
    if (descriptionField) descriptionField.placeholder = config.description;
};

window.confirmDelete = function(id, name, type = 'item') {
    return confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`);
};

window.showToast = function(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `${message} <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
};

/**
 * Enhanced Wedding Form Management Setup
 */
function setupWeddingFormManagement() {
    console.log('Setting up wedding form management...');
    
    document.querySelectorAll('.delete-form-btn').forEach(btn => {
        if (!btn.hasAttribute('data-setup')) {
            btn.setAttribute('data-setup', 'true');
            btn.addEventListener('click', handleDeleteClick);
        }
    });
    
    const addSocialBtn = document.getElementById('add-social-btn');
    const addWeddingLinkBtn = document.getElementById('add-wedding-link-btn');
    
    if (addSocialBtn && !addSocialBtn.hasAttribute('data-setup')) {
        addSocialBtn.setAttribute('data-setup', 'true');
        addSocialBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.formEnhancements) {
                const currentCount = window.formEnhancements.getFormsetCount('social');
                window.formEnhancements.addFormToFormset('social', currentCount);
                window.formEnhancements.updateTotalForms('social', currentCount + 1);
            }
        });
    }
    
    if (addWeddingLinkBtn && !addWeddingLinkBtn.hasAttribute('data-setup')) {
        addWeddingLinkBtn.setAttribute('data-setup', 'true');
        addWeddingLinkBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.formEnhancements) {
                const currentCount = window.formEnhancements.getFormsetCount('weddinglink');
                window.formEnhancements.addFormToFormset('weddinglink', currentCount);
                window.formEnhancements.updateTotalForms('weddinglink', currentCount + 1);
            }
        });
    }
    
    document.querySelectorAll('select[name*="link_type"]').forEach(select => {
        if (window.updateLinkPlaceholders) {
            window.updateLinkPlaceholders(select);
        }
    });
}

function handleDeleteClick(e) {
    e.preventDefault();
    if (window.formEnhancements) {
        window.formEnhancements.handleFormDelete(e.target);
    }
}

/**
 * Main Initialization
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all managers
    window.weddingFormManager = new WeddingFormManager();
    window.homepageManager = new HomepageManager();
    window.formEnhancements = new FormEnhancements();
    window.studioManager = new StudioManager();
    window.dashboardManager = new DashboardManager();
    
    // Initialize newsletter
    initializeNewsletter();
    
    // Enhanced form setup for wedding management page
    if (document.getElementById('social-formset') || document.getElementById('weddinglink-formset')) {
        setupWeddingFormManagement();
    }
});