// static/js/image_classifier.js

document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.getElementById('id_image');
    const imagePreviewContainer = document.getElementById('image-preview');
    const imagePreview = document.getElementById('preview-image');
    const classificationResults = document.getElementById('classification-results');

    imageInput.addEventListener('change', function (event) {
        const files = event.target.files;
        if (files && files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                imagePreview.alt = "Preview of uploaded image";
                imagePreviewContainer.style.display = 'block';  // Ensure preview container stays visible
            };
            reader.readAsDataURL(files[0]);
        } else {
            imagePreviewContainer.style.display = 'none';  // Hide preview container if no image
            imagePreview.src = ''; // Clear preview
            imagePreview.alt = ''; 
        }
    });
});