document.addEventListener('DOMContentLoaded', function () {
    // Function to populate the form with selected product data
    function selectProduct(productId, productCode, itemDescription, brand, classificationId) {
        // Display the product code in the relevant field
        document.getElementById('id_product_id').value = productId;
        document.getElementById('product_code_display').textContent = productCode || 'N/A';
        // Set the form fields for item description and brand
        document.getElementById('id_item_description').value = itemDescription || '';
        document.getElementById('id_brand').value = brand || '';
        
        // Display Classification ID or message
        const classificationDisplay = document.getElementById('classification_display');
        if (classificationId && classificationId !== 'null') {
            // If a classification exists, show the classification ID (or name)
            classificationDisplay.textContent = `Classification ID: ${classificationId}`;
        } else {
            // If no classification is present, show a message
            classificationDisplay.textContent = 'Not Classified';
        }

        clearClassificationForm(); // Clear classification form fields
    
        // Fetch and display existing classification details if available
        if (classificationId && classificationId !== 'null') {
            fetch(`/get_classification_details/${classificationId}/`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('ai-product-name').textContent = data.name;
                    document.getElementById('ai-enhanced-product-details').textContent = data.enhanced_details;
                    // Populate form with fetched classification details
                    document.getElementById('classification-select').value = classificationId;
                })
                .catch(error => console.error('Error fetching classification details:', error));
        }
    }

    // Add event listener for classification select dropdown
    document.getElementById('classification-select').addEventListener('change', function () {
        const classificationId = this.value;
        const productId = document.getElementById('id_product_id').value;

        if (!productId || !classificationId) {
            alert('Product ID or Classification not set.');
            return;
        }

        // Submit the form to update the product classification
        const form = document.getElementById('product-classification-form');
        form.submit();
    });

    // Use AI generated product name for classification name
    document.getElementById('populate-classification-name').addEventListener('click', function () {
        const aiProductName = document.getElementById('ai-product-name').textContent;
        const nameField = document.querySelector('input[name="name"]');
        nameField.value = aiProductName;  // Populate classification name field
    
        // Add a log to confirm the value is being set
        console.log(`AI Product Name set to: ${nameField.value}`);
    });

    // Clear classification form fields
    function clearClassificationForm() {
        document.getElementById('ai-product-name').textContent = 'Product name will be generated...';
        document.getElementById('ai-enhanced-product-details').textContent = 'Enhanced details will be generated...';
        document.getElementById('id_storage_guidelines').value = '';
        document.getElementById('id_handling_instructions').value = '';
        document.getElementById('id_allergens').value = '';
        document.getElementById('id_nutritional_info').value = '';
        document.getElementById('id_regulatory_compliance').value = '';
        document.getElementById('id_shelf_life').value = '';
    }

    // Attach click event to table rows
    const rows = document.querySelectorAll('#product-table tbody tr');
    // For each row in the table, add a click event listener
    rows.forEach(row => {
        row.addEventListener('click', function () {
            // Extract values from data attributes on the row
            const productId = row.dataset.productId;
            const productCode = row.dataset.productCode;
            const itemDescription = row.dataset.itemDescription;
            const brand = row.dataset.brand;
            const classificationId = row.dataset.classificationId || null;
            // Call the `selectProduct` function and pass these values as arguments
            selectProduct(productId, productCode, itemDescription, brand, classificationId);
        });
    });

    // Typing effect for AI-generated text
    function typeEffect(element, text, callback) {
        element.innerHTML = '';
        let i = 0;
        let timer = setInterval(function () {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
                if (callback) callback();
            }
        }, 50);
    }

    // Show "Generating..." message during AI request
    function showGenerating(element) {
        element.innerHTML = '<div class="generating-container">Generating...</div>';
    }

    // Generate product name with AI
    document.getElementById('generate-ai-product-name').addEventListener('click', function () {
        const productId = document.getElementById('id_product_id').value;
        const resultElement = document.getElementById('ai-product-name');
        showGenerating(resultElement);

        if (!productId) {
            resultElement.innerHTML = 'Product ID not set.';
            return;
        }

        fetch('/invoice/generate-product-name/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ product_id: productId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.generated_product_name) {
                typeEffect(resultElement, data.generated_product_name);
            } else {
                resultElement.innerHTML = 'Error generating product name';
            }
        })
        .catch(() => {
            resultElement.innerHTML = 'Error generating product name';
        });
    });

    // Enhance product details with AI
    document.getElementById('enhance-product-details').addEventListener('click', function () {
        const productId = document.getElementById('id_product_id').value;
        const resultElement = document.getElementById('ai-enhanced-product-details');
        showGenerating(resultElement);

        if (!productId) {
            resultElement.innerHTML = 'Product ID not set.';
            return;
        }

        fetch('/invoice/enhance-product-details/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ product_id: productId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultElement.innerHTML = data.error;
                return;
            }

            // List of classification fields to populate
            const fields = [
                'enhanced_details',
                'storage_guidelines',
                'handling_instructions',
                'allergens',
                'nutritional_info',
                'regulatory_compliance',
                'shelf_life'
            ];

            // Populate each field with the generated data
            fields.forEach(field => {
                const input = document.getElementById(`id_${field}`);
                if (input && data[field]) {
                    input.value = data[field];
                }
            });

            // Display the enhanced details in the AI result box
            if (data.enhanced_details) {
                typeEffect(resultElement, data.enhanced_details);
            } else {
                resultElement.innerHTML = 'Enhanced details not provided.';
            }
        })
        .catch(() => {
            resultElement.innerHTML = 'Error enhancing product details';
        });
    });

    // Get CSRF token for POST requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Vendor Filter Functionality
    const vendorFilter = document.getElementById('vendor-filter');

    vendorFilter.addEventListener('change', function () {
        filterTableByVendor();
    });

    function filterTableByVendor() {
        const selectedVendor = vendorFilter.value.trim();
        const table = document.getElementById('product-table');
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const vendorShortName = row.dataset.vendorShortName ? row.dataset.vendorShortName.trim() : '';

            if (!selectedVendor || vendorShortName === selectedVendor) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Call filterTableByVendor on page load
    filterTableByVendor();
});