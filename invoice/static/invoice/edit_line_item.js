document.addEventListener('DOMContentLoaded', function() {
    const glLevel1Select = document.getElementById('gl_level_1');
    const glLevel2Select = document.getElementById('gl_level_2');
    const glTableBody = document.querySelector('#gl_table tbody');

    function filterTable(gl1Id, gl2Id) {
        let url = '/invoice/gl_level_3_by_gl1/';
        if (gl1Id && gl2Id) {
            url = `/invoice/gl_level_3_by_gl2/?gl1_id=${gl1Id}&gl2_id=${gl2Id}`;
        } else if (gl1Id) {
            url = `/invoice/gl_level_3_by_gl1/?gl1_id=${gl1Id}`;
        }

        console.log('Fetching URL:', url); // Debugging line
        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('Data received:', data); // Debugging line
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
                    row.addEventListener('click', function() {
                        selectGL3(this, item.gl3_name, item.gl3_id);
                    });
                    glTableBody.appendChild(row);
                });
                attachRowClickHandlers(); // Re-attach row click handlers after updating table
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

    // Function to handle GL3 selection
    function selectGL3(row, gl3Name, gl3Id) {
        document.getElementById('selected-gl3-name').textContent = gl3Name;
        document.getElementById('selected-gl3').style.display = 'block';
        document.getElementById('id_gl3_id').value = parseInt(gl3Id); // Ensure the value is an integer
        document.getElementById('id_gl3_name').value = gl3Name; // Set the hidden field value

        // Remove the 'selected' class from all rows
        const rows = document.querySelectorAll('#gl_table tbody tr');
        rows.forEach(r => r.classList.remove('selected'));

        // Add the 'selected' class to the clicked row
        row.classList.add('selected');
    }

    // Attach row click handlers
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

    // Initial fetch to populate table sorted by GL Level 3 name
    filterTable('', '');

    attachRowClickHandlers();

    // Attach the click handlers again if the table is updated
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                attachRowClickHandlers();
            }
        });
    });

    observer.observe(document.getElementById('gl_table').getElementsByTagName('tbody')[0], {
        childList: true,
        subtree: true
    });
});