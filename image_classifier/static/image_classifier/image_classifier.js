document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.querySelector('input[type="file"]');
    const uploadArea = document.getElementById('upload-area');
    const imagePreviewContainer = document.getElementById('image-preview');
    const imagePreview = document.getElementById('preview-image');
    const classificationResults = document.getElementById('classification-results');
    const resultsList = document.getElementById('results-list');
    const loadingBar = document.getElementById('loading-bar');

    uploadArea.addEventListener('click', function () {
        imageInput.click();
    });

    imageInput.addEventListener('change', function (event) {
        const files = event.target.files;
        if (files && files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                imagePreview.alt = "Preview of uploaded image";
                imagePreviewContainer.style.display = 'block';
                uploadArea.style.display = 'none';

                startLoadingBar();

                const formData = new FormData();
                formData.append('image', files[0]);

                fetch('/image-classifier/classify/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    stopLoadingBar();

                    resultsList.innerHTML = '';
                    if (data.results && data.results.length > 0) {
                        classificationResults.style.display = 'block';
                        data.results.forEach((result, index) => {
                            const li = document.createElement('li');
                            li.innerHTML = `
                                <div class="result-item">
                                    <span class="label">${result.label}</span>
                                </div>
                                <div class="bar-container">
                                    <div class="confidence-bar" style="width: ${result.score * 100}%"></div>
                                    <span class="score">${result.score.toFixed(3)}</span>
                                </div>
                            `;
                            resultsList.appendChild(li);

                            setTimeout(() => {
                                li.classList.add('visible');
                            }, index * 200);
                        });
                    } else {
                        classificationResults.innerHTML = '<p>No results found.</p>';
                    }
                })
                .catch(error => {
                    console.error('Error during classification:', error);
                    stopLoadingBar();
                    classificationResults.innerHTML = '<p>An error occurred while classifying the image.</p>';
                });
            };
            reader.readAsDataURL(files[0]);
        } else {
            imagePreviewContainer.style.display = 'none';
            imagePreview.src = '';
            imagePreview.alt = '';
            uploadArea.style.display = 'block';
        }
    });

    function startLoadingBar() {
        loadingBar.style.display = 'block';
        loadingBar.style.width = '100%';
    }

    function stopLoadingBar() {
        loadingBar.style.display = 'none';
    }
});