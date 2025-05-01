document.addEventListener('DOMContentLoaded', function() {
    // Initialize CKEditor on textareas with the rich-editor class
    const editors = document.querySelectorAll('textarea.rich-editor');

    editors.forEach(editor => {
        ClassicEditor
            .create(editor, {
                toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote'],
                heading: {
                    options: [
                        { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                        { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
                        { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
                        { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' },
                    ]
                }
            })
            .catch(error => {
                console.error('Error initializing editor:', error);
            });
    });

    // Initialize tag input with auto-complete
    const tagInput = document.getElementById('tags');
    if (tagInput) {
        // Add event listener for comma input
        tagInput.addEventListener('keyup', function(e) {
            if (e.key === ',') {
                // Remove trailing comma and trim
                this.value = this.value.replace(/,\s*$/, '');
            }
        });
    }
});
