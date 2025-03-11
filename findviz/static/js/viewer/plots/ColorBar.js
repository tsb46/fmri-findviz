// ColorBar.js - Plot colorbar
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import ContextManager from '../api/ContextManager.js';


class ColorBar {
    /**
     * Constructor for ColorBar
     * @param {string} containerId - The ID of the container
     * @param {string} colorbarTitle - The title of the colorbar
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(containerId, colorbarTitle, eventBus, contextManager) {
        this.containerId = containerId;
        this.colorbarTitle=colorbarTitle;
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // initialize colorbar state
        this.colorbarState = null;

        // attach event listeners
        this.attachEventListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Plot colorbar on initialization of gifti or nifti plot
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.INIT_GIFTI_VIEWER,
                EVENT_TYPES.VISUALIZATION.FMRI.INIT_NIFTI_VIEWER,
            ],
            () => {
                this.initPlot();
            }
        );

        // Toggle colorbar
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_COLORBAR, 
            (colorbarState) => {
                if (colorbarState.colorbarState) {
                    console.log('initializing colorbar');
                    this.initPlot();
                } else {
                    console.log('removing colorbar');
                    this.removePlot();
                }
        });

        // Listen for color slider changes and update colorbar min and max
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.COLOR_SLIDER_CHANGE, 
            (colorSliderValues) => {
                if (this.colorbarState) {
                    console.log('updating colorbar min and max');
                    const color_min = colorSliderValues[0];
                    const color_max = colorSliderValues[1];
                    this.updateColorRange(color_min, color_max);
                }
            }
        );

        // Listen for colormap change and update colorbar
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.COLOR_MAP_CHANGE, 
            (color_map) => {
                console.log('updating colormap selection');
                this.updateColormap(color_map.colormap);
            }
        );

        // Listen for reverse colorbar toggle and update colorbar
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_REVERSE_COLORBAR, 
            (reverseColormapState) => {
                console.log('reversing colormap');
                this.updateReverseColormap(reverseColormapState.reverseColormapState);
            }
        );

        // Listen for preprocess submit and reset - replot with new data
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS,
                EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_RESET,
            ],
            () => {
                console.log('replotting colorbar for new preprocessed data');
                this.initPlot();
            }
        );
    }

    /**
     * Initialize colorbar plot
     */
    async initPlot() {
        const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
        this.colorbarState = true;
        const colorbarData = [{
            z: [[1]],  // Small data for colorbar
            type: 'heatmap',
            colorscale: plotOptions.color_map,  // Colormap to match the main plots
            showscale: true,  // Enable colorbar
            zmin: plotOptions.color_min,  // Set minimum of the color scale
            zmax: plotOptions.color_max,  // Set maximum of the color scale
            colorbar: {
                title: this.colorbarTitle,  // Title for the colorbar
                titleside: 'top',
                titlefont: {
                    size: 12,
                    color: '#000'
                },
                // tick values at min, mid, max
                tickvals: [
                    plotOptions.color_min, 
                    (plotOptions.color_min + plotOptions.color_max) / 2, 
                    plotOptions.color_max
                ], 
                // tick labels at min, mid, max
                ticktext: [
                    `${plotOptions.color_min.toFixed(2)}`, 
                    `${((plotOptions.color_min + plotOptions.color_max) / 2).toFixed(2)}`, 
                    `${plotOptions.color_max.toFixed(2)}`
                ], 
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

    /**
     * Remove colorbar plot
     */
    removePlot() {
        console.log('removing colorbar');
        this.colorbarState = false;
        Plotly.purge(this.containerId);
    }

    /**
     * Update reverse colorbar
     * @param {boolean} reverseColormap - Whether the colormap is reversed
     */
    updateReverseColormap(reverseColormap) {
        Plotly.restyle(this.containerId, { reversescale: reverseColormap });
    }

    /**
     * Update colormap
     * @param {string} color_map - The colormap to update to
     */
    updateColormap(color_map) {
        const colorbarUpdate = {
            colorscale: color_map
        };
        Plotly.restyle(this.containerId, colorbarUpdate);
    }

    /**
     * Update colorbar min and max
     * @param {number} color_min - The minimum color value
     * @param {number} color_max - The maximum color value
     */
    updateColorRange(color_min, color_max) {
        const colorbarUpdate = {
            zmin: [color_min],  // Array for first trace
            zmax: [color_max],
            'colorbar.tickvals': [[
                color_min,
                (color_min + color_max) / 2,
                color_max
            ]],
            'colorbar.ticktext': [[
                `${color_min.toFixed(2)}`,
                `${((color_min + color_max) / 2).toFixed(2)}`,
                `${color_max.toFixed(2)}`
            ]]
        }
        Plotly.restyle(this.containerId, colorbarUpdate);
    }
}

export default ColorBar;
