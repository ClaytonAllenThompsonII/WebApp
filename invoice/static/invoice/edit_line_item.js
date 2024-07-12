document.addEventListener('DOMContentLoaded', function() {
    const glLevel1Select = document.getElementById('gl_level_1');
    const glLevel2Select = document.getElementById('gl_level_2');
    const glLevel3Select = document.getElementById('gl_level_3');
    const glTableBody = document.querySelector('#gl_table tbody');

    function filterTable(gl1Id, gl2Id, gl3Id) {
        let url = '/invoice/gl_level_3_by_gl1/';
        if (gl1Id && gl2Id && gl3Id) {
            url = `/invoice/gl_level_3_by_gl3/?gl1_id=${gl1Id}&gl2_id=${gl2Id}&gl3_id=${gl3Id}`;
        } else if (gl1Id && gl2Id) {
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
                        option.value = item.gl_level_2_id;
                        option.textContent = item.gl_level_2_name;
                        glLevel2Select.appendChild(option);
                    });
                    glLevel2Select.disabled = false;

                    // Reset GL Level 2 and GL Level 3 selection and filter table based on GL Level 1
                    glLevel2Select.value = '';
                    glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
                    glLevel3Select.disabled = true;
                    filterTable(gl1Id, '', '');
                })
                .catch(error => console.error('Error fetching GL Level 2 data:', error));
        } else {
            glLevel2Select.innerHTML = '<option value="">Select GL Level 2</option>';
            glLevel2Select.disabled = true;
            glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
            glLevel3Select.disabled = true;
            filterTable('', '', '');
        }
    });

    glLevel2Select.addEventListener('change', function() {
        const gl1Id = glLevel1Select.value;
        const gl2Id = this.value;
        console.log('GL Level 2 changed:', gl2Id); // Debugging line
        if (gl2Id) {
            fetch(`/invoice/gl_level_3_by_gl2/?gl1_id=${gl1Id}&gl2_id=${gl2Id}`)
                .then(response => response.json())
                .then(data => {
                    console.log('GL Level 3 data:', data); // Debugging line
                    glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.gl_level_3_id;
                        option.textContent = item.gl_level_3_name;
                        glLevel3Select.appendChild(option);
                    });
                    glLevel3Select.disabled = false;
                    filterTable(gl1Id, gl2Id, '');
                })
                .catch(error => console.error('Error fetching GL Level 3 data:', error));
        } else {
            glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
            glLevel3Select.disabled = true;
            filterTable(gl1Id, '', '');
        }
    });

    glLevel3Select.addEventListener('change', function() {
        const gl1Id = glLevel1Select.value;
        const gl2Id = glLevel2Select.value;
        const gl3Id = this.value;
        console.log('GL Level 3 changed:', gl3Id); // Debugging line
        filterTable(gl1Id, gl2Id, gl3Id);
    });
});