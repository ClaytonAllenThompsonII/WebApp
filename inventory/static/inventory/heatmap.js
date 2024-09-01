document.addEventListener('DOMContentLoaded', function() {
    // Heatmap rendering
    const heatMapData = JSON.parse(document.getElementById('heat-map').dataset.heatMapData || '[]');
    renderHeatMap(heatMapData);
});

// Function to render the heatmap
function renderHeatMap(heatMapData) {
    const ctx = document.getElementById('heat-map').getContext('2d');
    
    const labels = heatMapData.map(data => data.product_name);
    const data = heatMapData.map(data => data.total_spend);

    const backgroundColors = data.map(value => {
        // Here you could apply a gradient or different colors based on the value
        return `rgba(75, 192, 192, ${value / Math.max(...data)})`;
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Top 50% Spend',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}