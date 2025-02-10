// ColorBar.js - Plot colorbar

class ColorBar {
    /**
     * Constructor for ColorBar
     * @param {string} containerId - The ID of the container
     * @param {string} colorbarTitle - The title of the colorbar
     */
    constructor(containerId, colorbarTitle) {
        this.containerId = containerId;
        this.colorbarTitle=colorbarTitle;
    }

    /**
     * Plot colorbar
     * @param {string} colormap - The colormap
     * @param {number} colorMin - The global minimum
     * @param {number} colorMax - The global maximum
     */
    plotColorbar(colormap='Viridis', colorMin=null, colorMax=null) {
        const colorbarData = [{
            z: [[1]],  // Small data for colorbar
            type: 'heatmap',
            colorscale: colormap,  // Colormap to match the main plots
            showscale: true,  // Enable colorbar
            zmin: colorMin,  // Set minimum of the color scale
            zmax: colorMax,  // Set maximum of the color scale
            colorbar: {
                title: this.colorbarTitle,  // Title for the colorbar
                titleside: 'top',
                tickvals: [colorMin, (colorMin + colorMax) / 2, colorMax],  // Custom tick values
                ticktext: [`${colorMin.toFixed(2)}`, `${((colorMin + colorMax) / 2).toFixed(2)}`, `${colorMax.toFixed(2)}`],  // Custom tick labels
                len: 1,  // Full height of the plot
                thickness: 20,  // Thickness of the colorbar
                outlinewidth: 0,  // No border around the colorbar
                ticks: 'outside',  // Show tick marks outside the colorbar
                tickfont: {
                    size: 10,
                    color: '#000'
                }
            },
            hoverinfo: 'none', // Disable hover information to avoid showing dummy data
            opacity: 0 // Ensure the data is invisible but the colorbar is displayed,
        }];

        const layout = {
            autosize: false,
            responsive: true, // Make the plot responsive
            width: 150,  // Narrow width for the colorbar container
            height: 300,  // Adjust height as needed
            margin: { l: 0, r: 0, b: 0, t: 0 },  // No margin around colorbar
            xaxis: {
                visible: false,  // Hide the X-axis
                fixedrange: true,  // Prevent zooming/panning
            },
            yaxis: {
                visible: false,  // Hide the Y-axis
                fixedrange: true,  // Prevent zooming/panning
            },
            showlegend: false,  // Hide any legends
            paper_bgcolor: 'rgba(0,0,0,0)',  // Transparent background
            plot_bgcolor: 'rgba(0,0,0,0)'
        };
        // Plotly to plot just the colorbar
        Plotly.newPlot(this.containerId, colorbarData, layout);
    }
}

export default ColorBar;
