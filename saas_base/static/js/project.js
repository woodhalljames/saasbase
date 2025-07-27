/* Enhanced Project specific Javascript with Wedding Branding Detection */

/**
 * Enhanced Wedding Form Management
 * Handles dynamic formsets, URL detection, and enhanced branding for wedding page creation
 */

class WeddingFormManager {
    constructor() {
        this.apiBaseUrl = '/wedding/api/';
        this.brandingCache = new Map(); // Cache branding results
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeDynamicFormsets();
            this.setupUrlDetection();
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

        // Create and configure add button
        const addButton = this.createAddButton(formsetType, displayName);
        formsetContainer.parentNode.insertBefore(addButton, formsetContainer.nextSibling);

        // Setup delete buttons for existing forms
        this.setupDeleteButtons(formsetType);
    }

    /**
     * Create the "Add Another" button for formsets
     * @param {string} formsetType - The type of formset
     * @param {string} displayName - Human-readable name for the formset
     * @returns {HTMLElement} The created button element
     */
    createAddButton(formsetType, displayName) {
        const addButton = document.createElement('button');
        addButton.type = 'button';
        addButton.className = 'btn btn-outline-primary btn-sm mt-2';
        addButton.innerHTML = `<i class="bi bi-plus-circle"></i> Add Another ${displayName}`;
        addButton.onclick = () => this.addFormsetForm(formsetType, displayName);
        return addButton;
    }

    /**
     * Add a new form to the formset
     * @param {string} formsetType - The type of formset
     * @param {string} displayName - Human-readable name for the formset
     */
    addFormsetForm(formsetType, displayName) {
        const formsetContainer = document.getElementById(`${formsetType}-formset`);
        const totalFormsInput = document.querySelector(`input[name="${formsetType}-TOTAL_FORMS"]`);
        
        if (!formsetContainer || !totalFormsInput) return;

        const currentFormCount = parseInt(totalFormsInput.value);
        const maxForms = parseInt(document.querySelector(`input[name="${formsetType}-MAX_NUM_FORMS"]`).value);

        if (currentFormCount >= maxForms) {
            this.showAlert(`Maximum ${maxForms} ${displayName.toLowerCase()}s allowed.`, 'warning');
            return;
        }

        // Clone and configure the empty form template
        const emptyForm = document.getElementById(`${formsetType}-empty-form`);
        if (!emptyForm) {
            console.error(`Empty form template not found for ${formsetType}`);
            return;
        }

        const newForm = this.createNewFormFromTemplate(emptyForm, formsetType, currentFormCount);
        const addButton = formsetContainer.nextElementSibling;
        formsetContainer.parentNode.insertBefore(newForm, addButton);

        // Update total forms count and setup functionality
        totalFormsInput.value = currentFormCount + 1;
        this.setupUrlDetectionForForm(newForm, formsetType);

        // Focus on first input of new form
        const firstInput = newForm.querySelector('input, select');
        if (firstInput) firstInput.focus();
    }

    /**
     * Create a new form from the empty template
     * @param {HTMLElement} emptyForm - The empty form template
     * @param {string} formsetType - The type of formset
     * @param {number} currentFormCount - Current number of forms
     * @returns {HTMLElement} The new form element
     */
    createNewFormFromTemplate(emptyForm, formsetType, currentFormCount) {
        const newForm = emptyForm.cloneNode(true);
        newForm.id = `${formsetType}-form-${currentFormCount}`;
        newForm.style.display = 'block';

        // Update form indices
        const formRegex = new RegExp(`__prefix__`, 'g');
        newForm.innerHTML = newForm.innerHTML.replace(formRegex, currentFormCount);

        // Add delete button
        const deleteButton = this.createDeleteButton(newForm, formsetType);
        newForm.appendChild(deleteButton);

        return newForm;
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
     * Setup enhanced branding detection for all forms
     */
    setupBrandingDetection() {
        // Setup for existing forms
        document.querySelectorAll('.url-field').forEach(urlField => {
            this.setupBrandingForField(urlField);
        });

        // Setup for platform/registry selects
        document.querySelectorAll('.platform-select, .registry-select').forEach(select => {
            this.setupSelectField(select);
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

            const form = urlField.closest('[id*="-form-"]');
            if (!form) return;

            const formsetType = form.id.includes('social') ? 'social' : 'registry';
            await this.detectAndApplyBranding(urlField, formsetType);
        });

        urlField.addEventListener('input', () => {
            // Clear previous branding indicators on input
            this.clearBrandingIndicator(urlField);
        });
    }

    /**
     * Setup select field change handlers
     * @param {HTMLElement} select - The select element
     */
    setupSelectField(select) {
        select.addEventListener('change', () => {
            const form = select.closest('[id*="-form-"]');
            if (!form) return;

            if (select.classList.contains('platform-select')) {
                this.updatePlatformFields(select);
            } else if (select.classList.contains('registry-select')) {
                this.updateRegistryFields(select);
            }
        });
    }

    /**
     * Enhanced branding detection and application
     * @param {HTMLElement} urlField - The URL input field
     * @param {string} formsetType - Type of formset (social or registry)
     */
    async detectAndApplyBranding(urlField, formsetType) {
        const url = urlField.value.trim();
        const form = urlField.closest('[id*="-form-"]');
        
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
            
            if (response.ok && data.detected) {
                // Cache the result
                this.brandingCache.set(cacheKey, data);
                
                // Apply branding
                this.applyBrandingData(form, data, formsetType);
                
                // Show success indicator
                this.showBrandingIndicator(urlField, data, 'success');
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
            const platformSelect = form.querySelector('.platform-select');
            const displayNameField = form.querySelector('input[name*="display_name"]');
            
            if (platformSelect && brandingData.platform && brandingData.platform !== 'other') {
                platformSelect.value = brandingData.platform;
                this.updatePlatformFields(platformSelect);
            }
            
            if (displayNameField && !displayNameField.value && brandingData.suggested_display_name) {
                displayNameField.value = brandingData.suggested_display_name;
            }
        } else {
            const registrySelect = form.querySelector('.registry-select');
            const displayNameField = form.querySelector('input[name*="display_name"]');
            
            if (registrySelect && brandingData.type && brandingData.type !== 'other') {
                registrySelect.value = brandingData.type;
                this.updateRegistryFields(registrySelect);
            }
            
            if (displayNameField && !displayNameField.value && brandingData.suggested_display_name) {
                displayNameField.value = brandingData.suggested_display_name;
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
            content = `<i class="bi bi-check-circle"></i> ${brandingData.name} detected automatically`;
        } else if (type === 'warning') {
            content = `<i class="bi bi-exclamation-triangle"></i> Platform not recognized - please select manually`;
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
     * Setup URL detection for all forms
     */
    setupUrlDetection() {
        document.querySelectorAll('.url-field').forEach(urlField => {
            const form = urlField.closest('[id*="-form-"]');
            if (form) {
                const formsetType = form.id.includes('social') ? 'social' : 'registry';
                this.setupUrlDetectionForForm(form, formsetType);
            }
        });
    }

    /**
     * Setup URL detection for a specific form
     * @param {HTMLElement} formElement - The form element
     * @param {string} formsetType - The type of formset
     */
    setupUrlDetectionForForm(formElement, formsetType) {
        const urlField = formElement.querySelector('.url-field');
        if (!urlField) return;

        // Setup branding detection
        this.setupBrandingForField(urlField);

        // Setup select field change handlers
        const selectField = formElement.querySelector(`.${formsetType}-select`);
        if (selectField) {
            this.setupSelectField(selectField);
        }
    }

    /**
     * Update platform-specific form fields
     * @param {HTMLElement} selectElement - The platform select element
     */
    updatePlatformFields(selectElement) {
        const form = selectElement.closest('[id*="-form-"]');
        const platformNameField = form.querySelector('.platform-name-field');
        
        if (platformNameField) {
            if (selectElement.value === 'other') {
                platformNameField.style.display = 'block';
                platformNameField.required = true;
            } else {
                platformNameField.style.display = 'none';
                platformNameField.required = false;
                platformNameField.value = '';
            }
        }
    }

    /**
     * Update registry-specific form fields
     * @param {HTMLElement} selectElement - The registry select element
     */
    updateRegistryFields(selectElement) {
        const form = selectElement.closest('[id*="-form-"]');
        const registryNameField = form.querySelector('.registry-name-field');
        
        if (registryNameField) {
            if (selectElement.value === 'other') {
                registryNameField.style.display = 'block';
                registryNameField.required = true;
            } else {
                registryNameField.style.display = 'none';
                registryNameField.required = false;
                registryNameField.value = '';
            }
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
window.detectPlatformFromUrl = function(urlField) {
    if (window.weddingFormManager) {
        const form = urlField.closest('[id*="-form-"]');
        if (form) {
            window.weddingFormManager.detectAndApplyBranding(urlField, 'social');
        }
    }
};

window.detectRegistryFromUrl = function(urlField) {
    if (window.weddingFormManager) {
        const form = urlField.closest('[id*="-form-"]');
        if (form) {
            window.weddingFormManager.detectAndApplyBranding(urlField, 'registry');
        }
    }
};

window.updatePlatformFields = function(selectElement) {
    if (window.weddingFormManager) {
        window.weddingFormManager.updatePlatformFields(selectElement);
    }
};

window.updateRegistryFields = function(selectElement) {
    if (window.weddingFormManager) {
        window.weddingFormManager.updateRegistryFields(selectElement);
    }
};

// Initialize the enhanced wedding form manager
document.addEventListener('DOMContentLoaded', function() {
    window.weddingFormManager = new WeddingFormManager();
});