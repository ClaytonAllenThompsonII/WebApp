document.addEventListener('DOMContentLoaded', function() {
    const glLevel1Select = document.getElementById('gl_level_1');
    const glLevel2Select = document.getElementById('gl_level_2');
    const glTableBody = document.querySelector('#gl_table tbody');

    // Function to filter the table based on GL Level 1 and GL Level 2 selections
    function filterTable(gl1Id, gl2Id) {
        let url = '/invoice/gl_level_3_by_gl1/';
        if (gl1Id && gl2Id) {
            url = `/invoice/gl_level_3_by_gl2/?gl1_id=${gl1Id}&gl2_id=${gl2Id}`;
        } else if (gl1Id) {
            url = `/invoice/gl_level_3_by_gl1/?gl1_id=${gl1Id}`;
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                glTableBody.innerHTML = '';
                data.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.gl_level_1_name}</td>
                        <td>${item.gl_level_2_name}</td>
                        <td>${item.gl_level_3_name}</td>
                    `;
                    glTableBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching GL Level 3 data:', error));
    }

    glLevel1Select.addEventListener('change', function() {
        const gl1Id = this.value;
        if (gl1Id) {
            // Fetch and populate GL Level 2 options based on GL Level 1 selection
            fetch(`/invoice/gl_level_2_by_gl1/?gl1_id=${gl1Id}`)
                .then(response => response.json())
                .then(data => {
                    glLevel2Select.innerHTML = '<option value="">Select GL Level 2</option>';
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = item.name;
                        glLevel2Select.appendChild(option);
                    });
                    glLevel2Select.disabled = false;

                    // Reset GL Level 2 selection and filter table based on GL Level 1
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
        filterTable(gl1Id, gl2Id);
    });
});