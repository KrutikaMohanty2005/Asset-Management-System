document.addEventListener('DOMContentLoaded', () => {
    initCharts();
});

let categoryChart = null;
let statusChart = null;

async function initCharts() {
    const categoryCtx = document.getElementById('categoryChart');
    const statusCtx = document.getElementById('statusChart');
    
    if (!categoryCtx || !statusCtx) return;
    
    try {
        const response = await fetch('/api/dashboard/chart-data');
        const data = await response.json();
        
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const textColor = isDark ? '#94a3b8' : '#64748b';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
        
        // 1. Doughnut Chart: Assets by Category
        categoryChart = new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: data.categories.labels,
                datasets: [{
                    data: data.categories.counts,
                    backgroundColor: [
                        '#818cf8', // Indigo
                        '#22d3ee', // Cyan
                        '#34d399', // Emerald
                        '#fb7185', // Rose
                        '#fbbf24', // Amber
                        '#c084fc'  // Purple
                    ],
                    borderWidth: isDark ? 2 : 1,
                    borderColor: isDark ? '#09081a' : '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor,
                            font: { family: 'Inter', size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: isDark ? 'rgba(15, 13, 45, 0.9)' : 'rgba(255, 255, 255, 0.95)',
                        titleColor: isDark ? '#e2e8f0' : '#0f172a',
                        bodyColor: isDark ? '#94a3b8' : '#475569',
                        borderColor: 'var(--border-color)',
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 6
                    }
                },
                cutout: '70%'
            }
        });
        
        // 2. Bar Chart: Assets by Status
        statusChart = new Chart(statusCtx, {
            type: 'bar',
            data: {
                labels: data.status.labels,
                datasets: [{
                    label: 'Assets Count',
                    data: data.status.counts,
                    backgroundColor: [
                        '#34d399', // Available (Emerald)
                        '#60a5fa', // Assigned (Blue)
                        '#fbbf24', // Maintenance (Amber)
                        '#f87171'  // Retired (Red)
                    ],
                    borderRadius: 8,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: isDark ? 'rgba(15, 13, 45, 0.9)' : 'rgba(255, 255, 255, 0.95)',
                        titleColor: isDark ? '#e2e8f0' : '#0f172a',
                        bodyColor: isDark ? '#94a3b8' : '#475569',
                        borderColor: 'var(--border-color)',
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 6
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: textColor,
                            font: { family: 'Inter', size: 11 }
                        }
                    },
                    y: {
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor,
                            font: { family: 'Inter', size: 11 },
                            stepSize: 1
                        }
                    }
                }
            }
        });
        
        // Listen to theme changes to dynamically re-style chart labels
        window.addEventListener('themechanged', (e) => {
            const currentTheme = e.detail.theme;
            const updatedColor = currentTheme === 'dark' ? '#94a3b8' : '#64748b';
            const updatedGrid = currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
            const borderVal = currentTheme === 'dark' ? '#09081a' : '#ffffff';
            const borderWidthVal = currentTheme === 'dark' ? 2 : 1;
            
            if (categoryChart) {
                categoryChart.options.plugins.legend.labels.color = updatedColor;
                categoryChart.data.datasets[0].borderColor = borderVal;
                categoryChart.data.datasets[0].borderWidth = borderWidthVal;
                categoryChart.update();
            }
            
            if (statusChart) {
                statusChart.options.scales.x.ticks.color = updatedColor;
                statusChart.options.scales.y.ticks.color = updatedColor;
                statusChart.options.scales.y.grid.color = updatedGrid;
                statusChart.update();
            }
        });
        
    } catch (error) {
        console.error('Error fetching dashboard chart data:', error);
    }
}
