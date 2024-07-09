document.addEventListener('DOMContentLoaded', function() {
    const glLevel1Select = document.getElementById('gl_level_1');
    const glLevel2Select = document.getElementById('gl_level_2');
    const glLevel3Select = document.getElementById('gl_level_3');
    const gl3TableBody = document.getElementById('gl3-table-body');

    // Populate GL Level 2 based on GL Level 1 selection
    glLevel1Select.addEventListener('change', function() {
        const gl1Id = this.value;
        if (gl1Id) {
            fetch(`/inventory/get_gl_level_2/?gl1_id=${gl1Id}`)
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
                });
        } else {
            glLevel2Select.innerHTML = '<option value="">Select GL Level 2</option>';
            glLevel2Select.disabled = true;
            glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
            glLevel3Select.disabled = true;
            updateGL3Table([]);
        }
    });

    // Populate GL Level 3 based on GL Level 2 selection
    glLevel2Select.addEventListener('change', function() {
        const gl2Id = this.value;
        if (gl2Id) {
            fetch(`/inventory/get_gl_level_3/?gl2_id=${gl2Id}`)
                .then(response => response.json())
                .then(data => {
                    glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item.id;
                        option.textContent = item.name;
                        glLevel3Select.appendChild(option);
                    });
                    glLevel3Select.disabled = false;
                    updateGL3Table(data);
                });
        } else {
            glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
            glLevel3Select.disabled = true;
            updateGL3Table([]);
        }
    });

    // Function to update the GL Level 3 table
    function updateGL3Table(data) {
        gl3TableBody.innerHTML = '';
        data.forEach(item => {
            const row = document.createElement('tr');
            const idCell = document.createElement('td');
            const nameCell = document.createElement('td');
            idCell.textContent = item.id;
            nameCell.textContent = item.name;
            row.appendChild(idCell);
            row.appendChild(nameCell);
            gl3TableBody.appendChild(row);
        });
    }
});