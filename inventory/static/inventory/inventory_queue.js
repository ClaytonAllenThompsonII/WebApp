// ===========================
// Timer Functions
// ===========================

let timerInterval = null;
let cycleStartTime = null;

function startTimerFromOffset(startTimeStr) {
    if (!startTimeStr) return; // No active cycle start provided
    cycleStartTime = new Date(startTimeStr);
    const timerElement = document.getElementById('inventory-timer');
    timerElement.classList.remove('hidden'); // Make sure timer is visible
    timerInterval = setInterval(() => {
        const now = new Date();
        const elapsedMs = now - cycleStartTime;
        const totalSeconds = Math.floor(elapsedMs / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        const displayMinutes = minutes.toString().padStart(2, '0');
        const displaySeconds = seconds.toString().padStart(2, '0');
        timerElement.innerHTML = `<span class="clock-emoji">⏱️</span>${displayMinutes}:${displaySeconds}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    // Optionally hide the timer:
    // document.getElementById('inventory-timer').classList.add('hidden');
}

// ===========================
// Product Movement Functions
// ===========================

// Global function to move product to Staging and update the button to "+Add Data"
function moveProductToStaging(button) {
    const productRow = button.closest('tr');  // Get the row that contains the button
    const stagingProductsTable = document.querySelector('.staging-products-table tbody');
    stagingProductsTable.appendChild(productRow);  // Move the product row to the staging table

    // Update the button text and class to "+Add Data" and ensure correct event
    const collectDataButton = productRow.querySelector('button');  // Get the button in the product row
    collectDataButton.textContent = '+Add Data';  // Change the button text
    collectDataButton.classList.remove('stage-button');  // Remove the stage-button class
    collectDataButton.classList.add('collect-data-button');  // Add the collect-data-button class
    collectDataButton.onclick = function(event) {
        const productId = productRow.dataset.productId;
        collectData(productId);  // Call the collectData function when clicked
        event.stopPropagation();  // Prevent event bubbling
    };
}

// Global function to move product to Staged Products
function moveProductToStaged(productRow) {
    const stagedProductsTable = document.querySelector('.staged-products-table tbody');
    stagedProductsTable.appendChild(productRow);  // Move product row to the staged table
}

// Global function to move product to Unstaged Products
function moveProductToUnstaged(productRow) {
    const unstagedProductsTable = document.querySelector('.unstaged-products-table tbody');
    unstagedProductsTable.appendChild(productRow);  // Move product row to the unstaged table

    // Change the +Add Data button back to Stage Product button
    const addDataButton = productRow.querySelector('.collect-data-button');
    if (addDataButton) {
        addDataButton.classList.remove('collect-data-button');
        addDataButton.classList.add('stage-button');
        addDataButton.textContent = 'Stage Product';
        addDataButton.setAttribute('onclick', 'moveProductToStaging(this); event.stopPropagation();');
    }
}

// ===========================
// Collect and Submit Data
// ===========================
/**
 * Function to collect product data (size, unit, image) and send it to the server.
 * @param {number} productId - The ID of the product to collect data for.
 */
function collectData(productId) {
    const productRow = document.querySelector(`tr[data-product-id="${productId}"]`);
    
    // Get inputs for size, unit, and image
    const sizeInput = document.querySelector('input[name="size"]').value;
    const unitInput = document.querySelector('select[name="unit"]').value;
    const imageInput = document.querySelector('input[type="file"]').files[0];  // Assuming a file input

    if (!sizeInput || !unitInput || !imageInput) {
        alert("Please provide all required data (size, unit, and image).");
        return;
    }

    // Create FormData to send to the server
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('size', sizeInput);
    formData.append('unit', unitInput);
    formData.append('image', imageInput);

    // Send the collected data to the server
    fetch('/inventory/queue/save_inventory_data/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // CSRF protection
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Data successfully saved.') {
            moveProductToStaged(productRow);  // After saving data, move to the staged products section
            resetFormFields();  // Reset the form fields after staging
        }
    })
    .catch(error => {
        console.error('Error saving data:', error);
        alert("Error saving data. Please try again.");
    });
}

/**
 * Function to reset form fields after data collection.
 */
function resetFormFields() {
    document.querySelector('input[name="size"]').value = '';
    document.querySelector('select[name="unit"]').value = '';
    document.querySelector('input[type="file"]').value = '';
}

// ===========================
// Event Handling for Sections
// ===========================
document.addEventListener('DOMContentLoaded', function() {
    // Toggle expandable/collapsible sections
    const toggleSections = document.querySelectorAll('.toggle-section h3');
    
    toggleSections.forEach(header => {
        header.addEventListener('click', function(event) {
            const clickedButton = event.target.closest('button');
            if (!clickedButton) {
                const content = this.nextElementSibling;
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
                this.classList.toggle('expanded');
            }
        });
    });

    // Handling product actions
    const unstagedProductsTable = document.querySelector('.unstaged-products-table tbody');
    const stagingProductsTable = document.querySelector('.staging-products-table tbody');
    const stagedProductsTable = document.querySelector('.staged-products-table tbody');

    // Adding row click event listeners for product selections
    addRowClickListener(unstagedProductsTable);
    addRowClickListener(stagingProductsTable);

    // Handling click events for Staging Products
    stagingProductsTable.addEventListener('click', function(event) {
        const collectButton = event.target.closest('.collect-data-button');
        if (collectButton) {
            const productRow = collectButton.closest('tr');
            const productId = productRow.dataset.productId;
            collectData(productId); // Collect data and move to staged products
            event.stopPropagation();
        }
    });

    // Handling click events for Unstaged Products
    unstagedProductsTable.addEventListener('click', function(event) {
        const stageButton = event.target.closest('.stage-button');
        if (stageButton) {
            const productRow = stageButton.closest('tr');
            moveProductToStaging(productRow); // Move product to Staging
            event.stopPropagation();
        }
    });

    // --- Timer Initialization for Mid-Cycle Refresh ---
    const timerElement = document.getElementById('inventory-timer');
    const cycleStartStr = timerElement.dataset.cycleStart; // Should be set by the template if there's an active cycle
    if (cycleStartStr) {
        startTimerFromOffset(cycleStartStr);
    }

    console.log('Staging JavaScript initialized.');
});

/**
 * Add row click event listeners for product selections in tables.
 * @param {Element} tableBody - The table body element to add the listener to.
 */
function addRowClickListener(tableBody) {
    tableBody.addEventListener('click', function(event) {
        const clickedRow = event.target.closest('tr');
        if (clickedRow && !event.target.closest('.stage-button, .collect-data-button')) {
            const productId = clickedRow.dataset.productId;
            loadLineItems(productId); // Load the line items for the selected product
        }
    });
}

// ===========================
// Inventory Cycle Actions
// ===========================
/**
 * Function to start a new inventory cycle.
 */
document.getElementById('start-cycle-button').addEventListener('click', function() {
    fetch('/inventory/queue/start_cycle/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Cycle started successfully!');
            // Reload page so the new cycle_start is injected into the timer element
            location.reload();
        } else {
            alert('Error starting cycle.');
        }
    })
    .catch(error => console.error('Error starting cycle:', error));
});

/**
 * Function to commit the current inventory cycle.
 */
document.getElementById('stage-cycle-button').addEventListener('click', function() {
    fetch('/inventory/queue/commit_cycle/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Cycle committed successfully!');
            // Stop the timer and refresh the page so staged items are hidden
            stopTimer();
            location.reload();
        } else {
            alert('Error committing cycle.');
        }
    })
    .catch(error => console.error('Error committing cycle:', error));
});

/**
 * Function to unstage all products in a section.
 * @param {string} sectionId - The ID of the section to unstage products from.
 */
function unstageAll(sectionId) {
    const sectionTableBody = document.querySelector(`#${sectionId} tbody`);
    const products = sectionTableBody.querySelectorAll('tr');

    products.forEach(productRow => {
        if (sectionId === 'staging-products') {
            moveProductToUnstaged(productRow);  // Move product back to Unstaged Products
        } else if (sectionId === 'staged-products') {
            moveProductToStaging(productRow);  // Move product back to Staging Products
        }
    });
}

// ===========================
// Loading Line Items
// ===========================
/**
 * Load line items based on product selection.
 * @param {number} productId - The ID of the selected product.
 */
function loadLineItems(productId) {
    fetch(`/inventory/queue/load_line_items/?product_id=${productId}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('line-item-table-body');
            tableBody.innerHTML = '';  // Clear the table

            // Append new rows with updated fields
            data.line_items.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.pack ?? 'N/A'}</td>
                    <td>${item.size ?? 'N/A'}</td>
                    <td>${item.weight ?? 'N/A'}</td>
                    <td>${item.line_item_id}</td>
                    <td>${item.item_description}</td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                    <td>${item.price}</td>
                    <td>${item.unit_price ?? 'N/A'}</td> <!-- Added unit price -->
                    <td>${item.invoice_receipt_date}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading line items:', error));
}