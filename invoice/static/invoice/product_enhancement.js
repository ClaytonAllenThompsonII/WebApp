document.addEventListener('DOMContentLoaded', function() {
    // Function to sort the table by the specified column
    function sortTable(n) {
        const table = document.getElementById('product-table');
        let switching = true;
        let dir = 'asc'; // Set the sorting direction to ascending
        let switchcount = 0;

        while (switching) {
            switching = false;
            const rows = table.rows;
            let shouldSwitch = false;

            for (let i = 1; i < rows.length - 1; i++) {
                let x = rows[i].getElementsByTagName('TD')[n];
                let y = rows[i + 1].getElementsByTagName('TD')[n];
                let cmp = 0;

                // Compare numerical values if both cells contain numbers
                if (!isNaN(parseFloat(x.innerHTML)) && !isNaN(parseFloat(y.innerHTML))) {
                    cmp = parseFloat(x.innerHTML) - parseFloat(y.innerHTML);
                } else {
                    // Compare text values
                    cmp = x.innerHTML.toLowerCase().localeCompare(y.innerHTML.toLowerCase());
                }

                if ((dir === 'asc' && cmp > 0) || (dir === 'desc' && cmp < 0)) {
                    shouldSwitch = true;
                    break;
                }
            }

            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount++;
            } else {
                if (switchcount === 0 && dir === 'asc') {
                    dir = 'desc';
                    switching = true;
                }
            }
        }
    }

    // Function to filter the table based on selected criteria
    function filterTable() {
        const filter = document.getElementById('filter-select').value;
        const rows = document.querySelectorAll('#product-table tbody tr');

        rows.forEach(row => {
            const productName = row.children[4].textContent;
            const expiration = row.children[6].textContent;
            row.style.display = ''; // Show all rows by default

            if (filter === 'needs-product-name' && productName !== 'None') {
                row.style.display = 'none';
            } else if (filter === 'needs-expiration' && expiration !== 'None') {
                row.style.display = 'none';
            }
        });
    }

    // Add event listener to the filter dropdown
    document.getElementById('filter-select').addEventListener('change', filterTable);

    // Function to populate the form with selected product data
    function selectProduct(row, productId, productCode, itemDescription, brand, generatedProductName, enhancedDetails, estimatedExpiration) {
        document.getElementById('id_item_description').value = itemDescription;
        document.getElementById('id_brand').value = brand;
        document.getElementById('id_generated_product_name').value = generatedProductName;
        document.getElementById('id_enhanced_details').value = enhancedDetails;
        document.getElementById('id_estimated_expiration').value = estimatedExpiration;
        document.getElementById('id_product_id').value = productId; // Set the hidden field value

        // Highlight the selected row
        const rows = document.querySelectorAll('#product-table tbody tr');
        rows.forEach(r => r.classList.remove('selected'));
        row.classList.add('selected');
    }

    // Attach click handlers to table rows
    const rows = document.querySelectorAll('#product-table tbody tr');
    rows.forEach(row => {
        row.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productCode = this.children[1].textContent;
            const itemDescription = this.children[2].textContent;
            const brand = this.children[3].textContent;
            const generatedProductName = this.children[4].textContent;
            const enhancedDetails = this.children[5].textContent;
            const estimatedExpiration = this.children[6].textContent;

            selectProduct(this, productId, productCode, itemDescription, brand, generatedProductName, enhancedDetails, estimatedExpiration);
        });
    });

    // AI Integration
    function typeEffect(element, text, callback) {
        element.innerHTML = '';
        let i = 0;
        let timer = setInterval(function() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
                if (callback) callback();
            }
        }, 50);
    }

    function showGenerating(element) {
        element.innerHTML = '<div class="generating-container">Generating...</div>';
    }

    document.getElementById('generate-ai-product-name').addEventListener('click', function() {
        const productId = document.getElementById('id_product_id').value;
        const resultElement = document.getElementById('ai-product-name');
        showGenerating(resultElement);
        
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
        });
    });

    document.getElementById('enhance-product-details').addEventListener('click', function() {
        const productId = document.getElementById('id_product_id').value;
        const resultElement = document.getElementById('ai-enhanced-product-details');
        showGenerating(resultElement);
        
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
            if (data.enhanced_product_details) {
                typeEffect(resultElement, data.enhanced_product_details);
            } else {
                resultElement.innerHTML = 'Error enhancing product details';
            }
        });
    });

    // Function to get CSRF token
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

    // Add click event listeners to headers for sorting
    const headers = document.querySelectorAll('#product-table th');
    headers.forEach((header, index) => {
        header.addEventListener('click', function() {
            console.log(`Header clicked: ${header.innerText}`);
            sortTable(index);
        });
    });
});