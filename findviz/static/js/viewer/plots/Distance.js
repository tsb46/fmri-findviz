// Distance.js
// Plot distance between timepoint and all other timepoints

import { EVENT_TYPES } from '../constants/EventTypes';
import eventBus from '../events/ViewerEvents';
import { getDistanceData, getTimePoint } from '../api/data';
import { getDistancePlotOptions, removeDistancePlot } from '../api/plot';

class Distance {
    /**
     * Constructor for Distance class
     * @param {string} distancePlotId - ID of the distance plot
     * @param {string} distanceContainerId - ID of the distance container
     */
    constructor(distancePlotId, distanceContainerId){
        this.distancePlotId = distancePlotId;
        this.distanceContainerId = distanceContainerId;
    }

    /**
     * Attaches event listeners to the distance plot
     */
    attachEventListeners() {
        // listen for distance submit event and plot distance vector
        eventBus.subscribe(EVENT_TYPES.ANALYSIS.DISTANCE, 
            async () => {
                const distanceVector = await getDistanceData();
                const timeIndex = await getTimePoint();
                const plotOptions = await getDistancePlotOptions();
                this.plotDistance(distanceVector, timeIndex, plotOptions);
                this.plotTimePointMarker(timeIndex, plotOptions);
                // show container
                document.getElementById(this.distanceContainerId).style.display = 'block';
            }
        );

        // listen for distance remove event and remove distance plot
        eventBus.subscribe(EVENT_TYPES.ANALYSIS.DISTANCE_REMOVE, 
            () => {
                Plotly.purge(this.distancePlotId);
                // hide container
                document.getElementById(this.distanceContainerId).style.display = 'none';
            }
        );

        // listen for time point change event and plot time point marker
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, 
            async (timeIndex) => {
                const plotOptions = await getDistancePlotOptions();
                this.plotTimePointMarker(timeIndex, plotOptions);
            }
        );

        // listen for time marker plot changes and replot time point marker
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_COLOR_MAP_CHANGE,
                EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_WIDTH_CHANGE, 
                EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_OPACITY_CHANGE
            ] , 
            async () => {
                const plotOptions = await getDistancePlotOptions();
                const timeIndex = await getTimePoint();
                this.plotTimePointMarker(timeIndex, plotOptions);
            }
        );

        // listen for window resize event and resize distance plot
        window.addEventListener('resize', () => this.onWindowResize());
    }

    /**
     * Plots the distance vector
     * @param {Array} distanceVector - Distance vector
     * @param {number} timeIndex - Time index
     * @param {Object} plotOptions - Plot options
     */
    plotDistance(distanceVector, timeIndex, plotOptions) {
        const distPlot = [{
            z: [distanceVector],  // Small data for colorbar
            type: 'heatmap',
            zmin: plotOptions['color_min'],
            zmax: plotOptions['color_max'],
            colorscale: plotOptions['color_map'],
            showscale: true,  // Enable colorbar
            hovertemplate: 'Time Point: %{x}<br>Distance: %{z}<extra></extra>',
            colorbar: {
                tickfont: {
                    size: 8  // Set the desired font size here
                }
            }
        }];

        const layout = {
            title: {
                text: `Time Point Distance: ${timeIndex}`
            },
            autosize: true,
            responsive: true, // Make the plot responsive
            height: 80,
            margin: { l: 0, r: 0, b: 0, t: 30 },  // No margin around colorbar
            showlegend: false,  // Hide any legends
            xaxis: {
                visible: false,  // Hide the X-axis
                fixedrange: true,  // Prevent zooming/panning
            },
            yaxis: {
                visible: false,  // Hide the Y-axis
                fixedrange: true,  // Prevent zooming/panning
            }
        }

        Plotly.react(this.distancePlotId, distPlot, layout);
    }

    // resize plotly plots to window resizing
    onWindowResize() {
        Plotly.Plots.resize(document.getElementById(this.distancePlotId));
    }

    /**
     * Plots the time point marker
     * @param {number} timeIndex - Time index
     * @param {Object} plotOptions - Plot options
     */
    plotTimePointMarker(timeIndex, plotOptions) {
        // only plot time point marker if it is enabled
        if (plotOptions['time_marker_on']) {
            const timePointMarkerUpdate = {
                shapes: [
                    {
                        type: 'line',
                        x0: timeIndex,
                        y0: 0,
                        x1: timeIndex,
                        y1: 1,
                        yref: 'paper',
                        opacity: plotOptions['time_marker_opacity'],
                        line: {
                            color: plotOptions['time_marker_color'],
                            width: plotOptions['time_marker_width'],
                        },
                    }
                ]
            }
            Plotly.relayout(this.distancePlotId, timePointMarkerUpdate);
        }
    }
}



export default Distance;
