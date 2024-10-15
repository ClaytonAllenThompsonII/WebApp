document.addEventListener('DOMContentLoaded', function() {
    const glLevel1Select = document.getElementById('gl_level_1');
    const glLevel2Select = document.getElementById('gl_level_2');
    const glTableBody = document.querySelector('#gl_table tbody');

    // Function to handle GL3 selection
    function selectGL3(row, gl3Name, gl3Id) {
        document.getElementById('selected-gl3-name').textContent = gl3Name;
        document.getElementById('selected-gl3').style.display = 'block';
        document.getElementById('id_gl3_id').value = parseInt(gl3Id); // Ensure the value is an integer

        // Remove the 'selected' class from all rows
        const rows = document.querySelectorAll('#gl_table tbody tr');
        rows.forEach(r => r.classList.remove('selected'));

        // Add the 'selected' class to the clicked row
        row.classList.add('selected');
    }

    // Attach row click handlers to existing rows (if any)
    function attachRowClickHandlers() {
        const rows = document.querySelectorAll('#gl_table tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', function() {
                const gl3Name = this.querySelector('td:last-child').textContent;
                const gl3Id = this.dataset.gl3Id; // Retrieve the GL3 ID from the data attribute
                selectGL3(this, gl3Name, gl3Id);
            });
        });
    }

    function filterTable(gl1Id, gl2Id) {
        let url = '/invoice/gl_level_3_by_gl1/';
        if (gl1Id && gl2Id) {
            url = `/invoice/gl_level_3_by_gl2/?gl1_id=${gl1Id}&gl2_id=${gl2Id}`;
        } else if (gl1Id) {
            url = `/invoice/gl_level_3_by_gl1/?gl1_id=${gl1Id}`;
        }
        // If neither gl1Id nor gl2Id is provided, url remains '/invoice/gl_level_3_by_gl1/'
    
        console.log('Fetching URL:', url); // Debugging line
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    // If response is not OK, throw an error
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || 'Unknown error');
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Data received:', data); // Debugging line
    
                // Ensure data is an array
                if (!Array.isArray(data)) {
                    throw new Error('Invalid data format received from server.');
                }
    
                glTableBody.innerHTML = '';
                data.sort((a, b) => a.gl3_name.localeCompare(b.gl3_name)); // Sort by GL Level 3 name A-Z
                data.forEach(item => {
                    const row = document.createElement('tr');
                    row.dataset.gl3Id = item.gl3_id; // Adding data attribute for GL3 ID
                    row.innerHTML = `
                        <td>${item.gl1_name ? item.gl1_name : 'N/A'}</td>
                        <td>${item.gl2_name ? item.gl2_name : 'N/A'}</td>
                        <td>${item.gl3_name ? item.gl3_name : 'N/A'}</td>
                    `;
                    // Attach click handler to the row
                    row.addEventListener('click', function() {
                        selectGL3(this, item.gl3_name, item.gl3_id);
                    });
                    glTableBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching GL Level 3 data:', error));
    }

    glLevel1Select.addEventListener('change', function() {
        const gl1Id = this.value;
        console.log('GL Level 1 changed:', gl1Id); // Debugging line
        if (gl1Id) {
            // Fetch and populate GL Level 2 options based on GL Level 1 selection
            fetch(`/invoice/gl_level_2_by_gl1/?gl1_id=${gl1Id}`)
                .then(response => response.json())
                .then(data => {
                    console.log('GL Level 2 data:', data); // Debugging line
                    glLevel2Select.innerHTML = '<option value="">Select GL Level 2</option>';
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.gl2_id;
                        option.textContent = item.gl2_name;
                        glLevel2Select.appendChild(option);
                    });
                    glLevel2Select.disabled = false;

                    // Reset GL Level 2 and GL Level 3 selection and filter table based on GL Level 1
                    glLevel2Select.value = '';
                    filterTable(gl1Id, '');
                })
                .catch(error => console.error('Error fetching GL Level 2 data:', error));
        } else {
            glLevel2Select.innerHTML = '<option value="">Select GL Level 2</option>';
            glLevel2Select.disabled = true;
            filterTable('', '');
        }
    });

    glLevel2Select.addEventListener('change', function() {
        const gl1Id = glLevel1Select.value;
        const gl2Id = this.value;
        console.log('GL Level 2 changed:', gl2Id); // Debugging line
        if (gl2Id) {
            filterTable(gl1Id, gl2Id);
        } else {
            filterTable(gl1Id, '');
        }
    });

    // Initial fetch to populate table sorted by GL Level 3 name
    filterTable('', '');

    // Attach click handlers to existing rows on page load
    attachRowClickHandlers();

    // Attach the click handlers again if the table is updated dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                attachRowClickHandlers();
            }
        });
    });

    observer.observe(glTableBody, {
        childList: true,
        subtree: true
    });

    // AI-related code (commented out)
    /*
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
        const resultElement = document.getElementById('ai-product-name');
        showGenerating(resultElement);
        // Simulate fetching AI result
        setTimeout(() => {
            const aiProductName = 'Beef Strip-loin';
            typeEffect(resultElement, aiProductName);
        }, 1000);
    });

    document.getElementById('generate-ai-product-details').addEventListener('click', function() {
        const resultElement = document.getElementById('ai-product-details');
        showGenerating(resultElement);
        // Simulate fetching AI result
        setTimeout(() => {
            const aiProductDetails = 'Beef Strip-loin, 13# Average, Premium Quality';
            typeEffect(resultElement, aiProductDetails);
        }, 1000);
    });
    */
});