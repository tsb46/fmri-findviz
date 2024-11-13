class ColorBar {
    constructor(containerId, globalMin, globalMax, colorbarTitle) {
        this.containerId = containerId;
        this.globalMin = globalMin;
        this.globalMax = globalMax;
        this.colorbarTitle=colorbarTitle;
    }

    plotColorbar(colorscaleUser='Viridis', globalMin=null, globalMax=null) {
        // Define minimal data setup to create the colorbar without showing actual data
        // if global min and global max is passed as parameters update class
        if ((globalMin !== null) && (globalMax !== null)) {
            this.globalMin = globalMin
            this.globalMax = globalMax
        }
        const colorbarData = [{
            z: [[1]],  // Small data for colorbar
            type: 'heatmap',
            colorscale: colorscaleUser,  // Colormap to match the main plots
            showscale: true,  // Enable colorbar
            zmin: this.globalMin,  // Set minimum of the color scale
            zmax: this.globalMax,  // Set maximum of the color scale
            colorbar: {
                title: this.colorbarTitle,  // Title for the colorbar
                titleside: 'top',
                tickvals: [this.globalMin, (this.globalMin + this.globalMax) / 2, this.globalMax],  // Custom tick values
                ticktext: [`${this.globalMin.toFixed(2)}`, `${((this.globalMin + this.globalMax) / 2).toFixed(2)}`, `${this.globalMax.toFixed(2)}`],  // Custom tick labels
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

    // Rescale min and max of colorbar
    rescaleMinMax(newGlobalMin, newGlobalMax) {
        this.globalMin = newGlobalMin
        this.globalMax = newGlobalMax
    }
}

export default ColorBar;
