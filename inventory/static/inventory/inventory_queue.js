document.addEventListener('DOMContentLoaded', function() {
    // Toggle Sections
    const toggleSections = document.querySelectorAll('.toggle-section h3');
    
    toggleSections.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            content.style.display = content.style.display === 'none' ? 'block' : 'none';
            this.classList.toggle('expanded');
        });
    });

    // Move products between stages
    const unstagedProductsTable = document.querySelector('.unstaged-products-table tbody');
    const stagingProductsTable = document.querySelector('.staging-products-table tbody');
    const stagedProductsTable = document.querySelector('.staged-products-table tbody');

    // Move product to Staging
    function moveProductToStaging(productRow) {
        stagingProductsTable.appendChild(productRow);
    }

    // Move product to Staged Products
    function moveProductToStaged(productRow) {
        stagedProductsTable.appendChild(productRow);
    }

    // Function to collect data and move to staged products
    function collectData(productRow, productId) {
        console.log(`Collecting data for Product ID: ${productId}`);
        // Trigger data collection process here (e.g., open modal for weight, image, etc.)
        // Simulate data collection
        setTimeout(() => {
            console.log(`Data collected for Product ID: ${productId}`);
            moveProductToStaged(productRow); // Move to staged products once data is collected
        }, 1000);
    }

    // Add event listener for Staging Products
    stagingProductsTable.addEventListener('click', function(event) {
        const collectButton = event.target.closest('.collect-data-button');
        if (collectButton) {
            const productRow = collectButton.closest('tr');
            const productId = productRow.dataset.productId;
            collectData(productRow, productId); // Collect data and move to staged
            event.stopPropagation(); // Prevents further event handling
        }
    });

    // Add hover functionality for Unstaged Products
    unstagedProductsTable.addEventListener('click', function(event) {
        const moveButton = event.target.closest('.stage-button');
        if (moveButton) {
            const productRow = moveButton.closest('tr');
            moveProductToStaging(productRow); // Move to staging products
            event.stopPropagation(); // Prevent row click event
        }
    });

    // Event listener for row clicks (load visuals for selected product)
    function addRowClickListener(tableBody) {
        tableBody.addEventListener('click', function(event) {
            const clickedRow = event.target.closest('tr');
            if (clickedRow && !event.target.closest('.stage-button, .collect-data-button')) {
                const productId = clickedRow.dataset.productId;
                console.log(`Loading data visuals for product ID: ${productId}`);
                loadLineItems(productId); // Load the line items for the selected product
            }
        });
    }

    addRowClickListener(unstagedProductsTable);
    addRowClickListener(stagingProductsTable);

    console.log('Staging JavaScript initialized.');
});

// Function to load line items for the selected product
function loadLineItems(productId) {
    fetch(`/inventory/queue/load_line_items/?product_id=${productId}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('line-item-table-body');
            tableBody.innerHTML = ''; // Clear the table

            data.line_items.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.line_item_id}</td>
                    <td>${item.item_description}</td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                    <td>${item.price}</td>
                    <td>${item.invoice_receipt_date}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading line items:', error));
}