// static/admin/js/tinymce_init.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize TinyMCE for blog content
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: 'textarea.tinymce-editor',
            height: 500,
            menubar: false,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'preview', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | ' +
                'bold italic forecolor | alignleft aligncenter ' +
                'alignright alignjustify | bullist numlist outdent indent | ' +
                'removeformat | help | link image | code preview fullscreen',
            content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, San Francisco, Segoe UI, Roboto, Helvetica Neue, sans-serif; font-size:14px }',
            
            // Image handling
            images_upload_handler: function (blobInfo, success, failure) {
                // For now, just show the base64 data URL
                // In production, you'd upload to your media storage
                const reader = new FileReader();
                reader.onload = function() {
                    success(reader.result);
                };
                reader.readAsDataURL(blobInfo.blob());
            },
            
            // Content filtering for clean HTML
            valid_elements: 'p,br,strong,em,u,s,a[href|title|target],ul,ol,li,h1,h2,h3,h4,h5,h6,img[src|alt|width|height],blockquote,table,thead,tbody,tr,th,td,code,pre',
            
            // Remove unwanted formatting on paste
            paste_as_text: false,
            paste_strip_class_attributes: 'all',
            paste_remove_styles: true,
            paste_remove_styles_if_webkit: true,
            
            // Accessibility
            a11y_advanced_options: true,
            
            // Setup callback
            setup: function(editor) {
                editor.on('change', function() {
                    editor.save(); // Sync content back to textarea
                });
            }
        });
    }
});