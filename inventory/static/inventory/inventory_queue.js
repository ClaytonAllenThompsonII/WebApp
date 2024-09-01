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

    function moveProductToStaging(productRow) {
        stagingProductsTable.appendChild(productRow);
    }

    function moveProductToStaged(productRow) {
        stagedProductsTable.appendChild(productRow);
    }

    unstagedProductsTable.addEventListener('click', function(event) {
        const moveButton = event.target.closest('.stage-button');
        if (moveButton) {
            const productRow = moveButton.closest('tr');
            moveProductToStaging(productRow);
            event.stopPropagation(); // Prevents the row click event from firing
        }
    });

    stagingProductsTable.addEventListener('click', function(event) {
        const moveButton = event.target.closest('.stage-button');
        if (moveButton) {
            const productRow = moveButton.closest('tr');
            moveProductToStaged(productRow);
            event.stopPropagation(); // Prevents the row click event from firing
        }
    });

    // Event listener for row clicks to control data visuals
    unstagedProductsTable.addEventListener('click', function(event) {
        const clickedRow = event.target.closest('tr');
        if (clickedRow && !event.target.closest('.stage-button')) {
            const productId = clickedRow.dataset.productId;
            console.log('Loading data visuals for product ID:', productId);
            loadLineItems(productId); // Load the line items for the selected product
        }
    });

    stagingProductsTable.addEventListener('click', function(event) {
        const clickedRow = event.target.closest('tr');
        if (clickedRow && !event.target.closest('.stage-button')) {
            const productId = clickedRow.dataset.productId;
            console.log('Loading data visuals for product ID:', productId);
            loadLineItems(productId); // Load the line items for the selected product
        }
    });

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