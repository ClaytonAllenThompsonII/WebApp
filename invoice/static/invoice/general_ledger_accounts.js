document.addEventListener('DOMContentLoaded', function() {
    const glLevel1Select = document.getElementById('gl_level_1');
    const glLevel2Select = document.getElementById('gl_level_2');
    const glLevel3Select = document.getElementById('gl_level_3');
    const gl3TableBody = document.getElementById('gl3_table').querySelector('tbody');

    // Populate GL Level 2 based on GL Level 1 selection
    glLevel1Select.addEventListener('change', function() {
        const gl1Id = this.value;
        glLevel2Select.innerHTML = '<option value="">Select GL Level 2</option>';
        glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
        glLevel2Select.disabled = !gl1Id;
        glLevel3Select.disabled = true;
        
        // Filter GL Level 2 options based on GL Level 1 selection
        const gl2Options = Array.from(document.querySelectorAll('#gl_level_2 option'));
        gl2Options.forEach(option => {
            if (!gl1Id || option.dataset.parent == gl1Id) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        });

        updateTable();
    });

    // Populate GL Level 3 based on GL Level 2 selection
    glLevel2Select.addEventListener('change', function() {
        const gl2Id = this.value;
        glLevel3Select.innerHTML = '<option value="">Select GL Level 3</option>';
        glLevel3Select.disabled = !gl2Id;

        // Filter GL Level 3 options based on GL Level 2 selection
        const gl3Options = Array.from(document.querySelectorAll('#gl_level_3 option'));
        gl3Options.forEach(option => {
            if (!gl2Id || option.dataset.parent == gl2Id) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        });

        updateTable();
    });

    // Update table based on GL Level 3 selection
    glLevel3Select.addEventListener('change', updateTable);

    // Function to update the table based on the selected filters
    function updateTable() {
        const gl1Id = glLevel1Select.value;
        const gl2Id = glLevel2Select.value;
        const gl3Id = glLevel3Select.value;
        const rows = Array.from(gl3TableBody.querySelectorAll('tr'));

        rows.forEach(row => {
            const gl1Match = !gl1Id || row.dataset.gl1 == gl1Id;
            const gl2Match = !gl2Id || row.dataset.gl2 == gl2Id;
            const gl3Match = !gl3Id || row.cells[3].textContent == glLevel3Select.querySelector(`option[value="${gl3Id}"]`).textContent;
            row.style.display = gl1Match && gl2Match && gl3Match ? 'table-row' : 'none';
        });
    }
});