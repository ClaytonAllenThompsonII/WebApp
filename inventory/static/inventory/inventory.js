document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    const glLevel1Select = document.getElementById('gl-level-1');
    const glLevel2Select = document.getElementById('gl-level-2');
    const glLevel3Select = document.getElementById('gl-level-3');
    const productSelect = document.getElementById('product');

    console.log('GL Level 1 Select Element:', glLevel1Select);
    console.log('GL Level 2 Select Element:', glLevel2Select);
    console.log('GL Level 3 Select Element:', glLevel3Select);
    console.log('Product Select Element:', productSelect);

    if (glLevel1Select) {
        glLevel1Select.addEventListener('change', function() {
            const gl1Id = this.value;
            document.getElementById('gl_level_1_id').value = gl1Id;
            document.getElementById('gl_level_1_name').value = glLevel1Select.options[glLevel1Select.selectedIndex].text;

            console.log('GL Level 1 changed:', gl1Id);

            if (gl1Id) {
                const fetchUrl = `/get_gl_level_2/?gl1_id=${gl1Id}`;
                console.log('Fetch URL:', fetchUrl);

                fetch(fetchUrl)
                    .then(response => {
                        console.log('Response status:', response.status);
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('GL Level 2 data:', data);
                        glLevel2Select.innerHTML = '<option value="">-- Select GL Level 2 --</option>';
                        data.forEach(item => {
                            const option = document.createElement('option');
                            option.value = item.id;
                            option.textContent = item.name;
                            glLevel2Select.appendChild(option);
                        });
                        glLevel2Select.disabled = false;

                        // Reset GL Level 3 and product selections
                        glLevel3Select.innerHTML = '<option value="">-- Select GL Level 3 --</option>';
                        glLevel3Select.disabled = true;
                        productSelect.innerHTML = '<option value="">-- Select a Product --</option>';
                        productSelect.disabled = true;
                    })
                    .catch(error => console.error('Error fetching GL Level 2 data:', error));
            } else {
                glLevel2Select.innerHTML = '<option value="">-- Select GL Level 2 --</option>';
                glLevel2Select.disabled = true;
                glLevel3Select.innerHTML = '<option value="">-- Select GL Level 3 --</option>';
                glLevel3Select.disabled = true;
                productSelect.innerHTML = '<option value="">-- Select a Product --</option>';
                productSelect.disabled = true;
            }
        });

        glLevel2Select.addEventListener('change', function() {
            const gl2Id = this.value;
            document.getElementById('gl_level_2_id').value = gl2Id;
            document.getElementById('gl_level_2_name').value = glLevel2Select.options[glLevel2Select.selectedIndex].text;
            console.log('GL Level 2 changed:', gl2Id);

            if (gl2Id) {
                const fetchUrl = `/get_gl_level_3/?gl2_id=${gl2Id}`;
                console.log('Fetch URL:', fetchUrl);

                fetch(fetchUrl)
                    .then(response => {
                        console.log('Response status:', response.status);
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('GL Level 3 data:', data);
                        glLevel3Select.innerHTML = '<option value="">-- Select GL Level 3 --</option>';
                        data.forEach(item => {
                            const option = document.createElement('option');
                            option.value = item.id;
                            option.textContent = item.name;
                            glLevel3Select.appendChild(option);
                        });
                        glLevel3Select.disabled = false;

                        // Reset product selection
                        productSelect.innerHTML = '<option value="">-- Select a Product --</option>';
                        productSelect.disabled = true;
                    })
                    .catch(error => console.error('Error fetching GL Level 3 data:', error));
            } else {
                glLevel3Select.innerHTML = '<option value="">-- Select GL Level 3 --</option>';
                glLevel3Select.disabled = true;
                productSelect.innerHTML = '<option value="">-- Select a Product --</option>';
                productSelect.disabled = true;
            }
        });

        glLevel3Select.addEventListener('change', function() {
            const gl3Id = this.value;
            document.getElementById('gl_level_3_id').value = gl3Id;
            document.getElementById('gl_level_3_name').value = glLevel3Select.options[glLevel3Select.selectedIndex].text;
            console.log('GL Level 3 changed:', gl3Id);

            if (gl3Id) {
                const fetchUrl = `/get_products/?gl3_id=${gl3Id}`;
                console.log('Fetch URL:', fetchUrl);

                fetch(fetchUrl)
                    .then(response => {
                        console.log('Response status:', response.status);
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Product data:', data);
                        productSelect.innerHTML = '<option value="">-- Select a Product --</option>';
                        data.forEach(item => {
                            const option = document.createElement('option');
                            option.value = item.id;
                            option.textContent = item.name;
                            productSelect.appendChild(option);
                        });
                        productSelect.disabled = false;
                    })
                    .catch(error => console.error('Error fetching product data:', error));
            } else {
                productSelect.innerHTML = '<option value="">-- Select a Product --</option>';
                productSelect.disabled = true;
            }
        });

        productSelect.addEventListener('change', function() {
            const productId = this.value;
            document.getElementById('product_id').value = productId;
            document.getElementById('product_name').value = productSelect.options[productSelect.selectedIndex].text;
        });
    } else {
        console.error('GL Level 1 Select Element not found');
    }
});