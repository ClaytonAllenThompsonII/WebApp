document.addEventListener('DOMContentLoaded', function() {
    var sizeInput = document.getElementById('sizeInput');
    var unitSelect = document.getElementById('unitSelect');
    var hiddenSize = document.getElementById('hidden_size');
    var hiddenUnit = document.getElementById('hidden_unit');

    sizeInput.addEventListener('input', function() {
        updateDisplay();
    });

    unitSelect.addEventListener('change', function() {
        updateDisplay();
    });

    function updateDisplay() {
        var weight = parseFloat(sizeInput.value).toFixed(2);
        var unit = unitSelect.value;

        if (hiddenSize && hiddenUnit) {
            hiddenSize.value = isNaN(weight) ? '' : weight;
            hiddenUnit.value = unit;
        }

        var weightDisplay = document.getElementById('digital-weight-display');
        var unitDisplay = document.getElementById('digital-unit-display');

        weightDisplay.textContent = isNaN(weight) ? '00.00' : weight;
        unitDisplay.textContent = unit;
    }

    updateDisplay();
});