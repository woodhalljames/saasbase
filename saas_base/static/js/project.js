/* Project specific Javascript goes here. */
/**
 * Wedding Form Management
 * Handles dynamic formsets, URL detection, and branding for wedding page creation
 */

class WeddingFormManager {
    constructor() {
        this.apiBaseUrl = '/wedding/api/';
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeDynamicFormsets();
            this.setupUrlDetection();
            this.setupUrlPreview();
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
            alert(`Maximum ${maxForms} ${displayName.toLowerCase()}s allowed.`);
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

        // Setup URL blur detection
        urlField.addEventListener('blur', () => {
            if (formsetType === 'social') {
                this.detectPlatformFromUrl(urlField);
            } else {
                this.detectRegistryFromUrl(urlField);
            }
        });

        // Setup select field change handlers
        const selectField = formElement.querySelector(`.${formsetType}-select`);
        if (selectField) {
            selectField.addEventListener('change', () => {
                if (formsetType === 'social') {
                    this.updatePlatformFields(selectField);
                } else {
                    this.updateRegistryFields(selectField);
                }
            });
        }
    }

    /**
     * Detect social media platform from URL
     * @param {HTMLElement} urlField - The URL input field
     */
    async detectPlatformFromUrl(urlField) {
        const url = urlField.value.trim();
        if (!url) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}detect-branding/?url=${encodeURIComponent(url)}&type=social`);
            const data = await response.json();
            
            if (data.platform && data.platform !== 'other') {
                const form = urlField.closest('[id*="-form-"]');
                const platformSelect = form.querySelector('.platform-select');
                
                if (platformSelect) {
                    platformSelect.value = data.platform;
                    this.updatePlatformFields(platformSelect);
                    
                    // Auto-fill display name if empty
                    const displayNameField = form.querySelector('input[name*="display_name"]');
                    if (displayNameField && !displayNameField.value) {
                        displayNameField.value = this.extractUsernameFromUrl(url, data.platform);
                    }
                    
                    this.addBrandingIndicator(form, data);
                }
            }
        } catch (error) {
            console.error('Error detecting platform:', error);
        }
    }

    /**
     * Detect registry type from URL
     * @param {HTMLElement} urlField - The URL input field
     */
    async detectRegistryFromUrl(urlField) {
        const url = urlField.value.trim();
        if (!url) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}detect-branding/?url=${encodeURIComponent(url)}&type=registry`);
            const data = await response.json();
            
            if (data.type && data.type !== 'other') {
                const form = urlField.closest('[id*="-form-"]');
                const registrySelect = form.querySelector('.registry-select');
                
                if (registrySelect) {
                    registrySelect.value = data.type;
                    this.updateRegistryFields(registrySelect);
                    
                    // Auto-fill display name if empty
                    const displayNameField = form.querySelector('input[name*="display_name"]');
                    if (displayNameField && !displayNameField.value && data.name) {
                        displayNameField.value = `${data.name} Registry`;
                    }
                    
                    this.addBrandingIndicator(form, data);
                }
            }
        } catch (error) {
            console.error('Error detecting registry:', error);
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
     * Add visual branding indicator to form
     * @param {HTMLElement} form - The form element
     * @param {Object} brandingData - Branding information from API
     */
    addBrandingIndicator(form, brandingData) {
        const urlField = form.querySelector('.url-field');
        const existingIndicator = form.querySelector('.brand-indicator');
        
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        if (brandingData.name && brandingData.type !== 'other') {
            const indicator = document.createElement('small');
            indicator.className = 'brand-indicator text-muted ms-2';
            indicator.innerHTML = `<i class="${brandingData.icon || 'bi-check-circle'}"></i> ${brandingData.name} detected`;
            indicator.style.color = brandingData.color || '#6c757d';
            
            urlField.parentNode.appendChild(indicator);
        }
    }

    /**
     * Extract username from social media URL
     * @param {string} url - The social media URL
     * @param {string} platform - The detected platform
     * @returns {string} The extracted username or empty string
     */
    extractUsernameFromUrl(url, platform) {
        try {
            const urlObj = new URL(url);
            const pathname = urlObj.pathname;
            
            switch (platform) {
                case 'instagram':
                case 'facebook':
                case 'twitter':
                case 'tiktok':
                    const match = pathname.match(/^\/([^\/\?]+)/);
                    return match ? `@${match[1]}` : '';
                default:
                    return '';
            }
        } catch (error) {
            return '';
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
}

// Initialize the wedding form manager
const weddingFormManager = new WeddingFormManager();