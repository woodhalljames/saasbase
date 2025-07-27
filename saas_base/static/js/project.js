/* Simplified Wedding Form Management */

/**
 * Simplified Wedding Form Manager
 * Handles dynamic formsets and basic URL detection for wedding page creation
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

// Initialize the wedding form manager
document.addEventListener('DOMContentLoaded', function() {
    window.weddingFormManager = new WeddingFormManager();
});