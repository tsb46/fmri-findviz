// NiftiViewer.js
// Handles all plotting and click events for nifti visualization
import { EVENT_TYPES } from '../constants/EventTypes.js';
import eventBus from '../events/ViewerEvents.js';
import { getFMRIData, getCrosshairCoords, getDirectionLabelCoords } from '../api/data.js';
import { getFmriPlotOptions } from '../api/plot.js';

class NiftiViewer {
    /**
     * @param {string} niftiPlotContainerId - The ID of the nifti plot container
     * @param {string} slice1ContainerId - The ID of the first slice container
     * @param {string} slice2ContainerId - The ID of the second slice container
     * @param {string} slice3ContainerId - The ID of the third slice container
     * @param {string} colorbarContainerId - The ID of the colorbar container
     */
    constructor(
        niftiPlotContainerId,
        slice1ContainerId,
        slice2ContainerId,
        slice3ContainerId,
        colorbarContainerId,
    ) {
        this.niftiPlotContainerId = niftiPlotContainerId;
        this.slice1ContainerId = slice1ContainerId;
        this.slice2ContainerId = slice2ContainerId;
        this.slice3ContainerId = slice3ContainerId;
        this.colorbarContainerId = colorbarContainerId;

        // define slice name to container id converter
        this.sliceName2ContainerId = {
            slice1: slice1ContainerId,
            slice2: slice2ContainerId,
            slice3: slice3ContainerId,
        };

        // create container
        this.createContainer(
            niftiPlotContainerId, 
            slice1ContainerId,
            slice2ContainerId, 
            slice3ContainerId, 
            colorbarContainerId
        );

        // temporary slice data storage for quick plot updates
        this.sliceData = {
            slice1: null,
            slice2: null,
            slice3: null,
            slice1Anat: null,
            slice2Anat: null,
            slice3Anat: null,
        };

        // Add event listeners
        this.attachEventListeners();
    }

    /**
     * Attach event listeners for plot updates
     */
    attachEventListeners() {
        // Handle time slider change - update slice data and re-plot
        // Handle montage slice direction change - replot with new slice indices
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, 
                EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_DIRECTION_CHANGE
            ], 
            () => {
                getFMRIData((viewer_data) => {
                    this.sliceData = {
                        slice1: viewer_data.data.func.x,
                        slice2: viewer_data.data.func.y,
                        slice3: viewer_data.data.func.z,
                    };
                    this.plotNiftiDataUpdate(this.slice1ContainerId, this.sliceData.slice1);
                    this.plotNiftiDataUpdate(this.slice2ContainerId, this.sliceData.slice2);
                    this.plotNiftiDataUpdate(this.slice3ContainerId, this.sliceData.slice3);
                });
            }
        );

        // Handle click event - update slice data and re-plot, if crosshair is enabled, re-plot crosshairs
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, 
            () => {
                getFMRIData((viewer_data) => {
                    this.sliceData = {
                        slice1: viewer_data.data.func.x,
                        slice2: viewer_data.data.func.y,
                        slice3: viewer_data.data.func.z,
                    };
                    this.plotNiftiDataUpdate(this.slice1ContainerId, this.sliceData.slice1);
                    this.plotNiftiDataUpdate(this.slice2ContainerId, this.sliceData.slice2);
                    this.plotNiftiDataUpdate(this.slice3ContainerId, this.sliceData.slice3);
                });
            }
        );

        // Handle view state change - update plot width and slice data and re-plot
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.VIEW_TOGGLE, 
            (viewState) => {
                this.changeViewPlotWidth(viewState);
                getFMRIData((viewer_data) => {
                    this.sliceData = {
                        slice1: viewer_data.data.func.x,
                        slice2: viewer_data.data.func.y,
                        slice3: viewer_data.data.func.z,
                    };
                    this.plotNiftiDataUpdate(this.slice1ContainerId, this.sliceData.slice1);
                    this.plotNiftiDataUpdate(this.slice2ContainerId, this.sliceData.slice2);
                    this.plotNiftiDataUpdate(this.slice3ContainerId, this.sliceData.slice3);
                });
            }
        );

        // Handle montage slice index change - replot with new slice indices
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_CHANGE, 
            (sliceName, sliceIdx) => {
                getFMRIData((viewer_data) => {
                    // only update slices that have changed
                    this.sliceData[sliceName] = viewer_data.data.func[sliceName];
                    this.plotNiftiDataUpdate(this.sliceName2ContainerId[sliceName], this.sliceData[sliceName]);
                });
            }
        );

        // Handle any color changes
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.COLOR_MAP_CHANGE, 
                EVENT_TYPES.VISUALIZATION.FMRI.OPACITY_SLIDER_CHANGE,
                EVENT_TYPES.VISUALIZATION.FMRI.COLOR_SLIDER_CHANGE,
            ], 
            () => {
                getFmriPlotOptions((plotOptions) => {
                    this.plotColorUpdate(
                        this.slice1ContainerId, plotOptions.color_map, plotOptions.color_min, 
                        plotOptions.color_max, plotOptions.opacity
                    );
                    this.plotColorUpdate(
                        this.slice2ContainerId, plotOptions.color_map, plotOptions.color_min,
                         plotOptions.color_max, plotOptions.opacity
                    );
                    this.plotColorUpdate(
                        this.slice3ContainerId, plotOptions.color_map, plotOptions.color_min,
                        plotOptions.color_max, plotOptions.opacity
                    );
                });
            }
        );

        // Handle threshold change
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.THRESHOLD_SLIDER_CHANGE, 
            () => {
                getFMRIData((viewer_data) => {
                    this.sliceData = {
                        slice1: viewer_data.data.func.x,
                        slice2: viewer_data.data.func.y,
                        slice3: viewer_data.data.func.z,
                    };
                    this.plotNiftiDataUpdate(this.slice1ContainerId, this.sliceData.slice1);
                    this.plotNiftiDataUpdate(this.slice2ContainerId, this.sliceData.slice2);
                    this.plotNiftiDataUpdate(this.slice3ContainerId, this.sliceData.slice3);
                });
            }
        );

        // Handle reset of color sliders - update for change of threshold and update plot color properties
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.RESET_COLOR_SLIDERS,
            () => {
                getFMRIData((viewer_data) => {
                    this.sliceData = {
                        slice1: viewer_data.data.func.x,
                        slice2: viewer_data.data.func.y,
                        slice3: viewer_data.data.func.z,
                    };
                    this.plotNiftiDataUpdate(this.slice1ContainerId, this.sliceData.slice1);
                    this.plotNiftiDataUpdate(this.slice2ContainerId, this.sliceData.slice2);
                    this.plotNiftiDataUpdate(this.slice3ContainerId, this.sliceData.slice3);
                    // update plot color properties
                    getFmriPlotOptions((plotOptions) => {
                        this.plotColorUpdate(
                            this.slice1ContainerId, plotOptions.color_map, plotOptions.color_min, 
                            plotOptions.color_max, plotOptions.opacity
                        );
                        this.plotColorUpdate(
                            this.slice2ContainerId, plotOptions.color_map, plotOptions.color_min, 
                            plotOptions.color_max, plotOptions.opacity
                        );
                        this.plotColorUpdate(
                            this.slice3ContainerId, plotOptions.color_map, plotOptions.color_min, 
                            plotOptions.color_max, plotOptions.opacity
                        );
                    });
                });
            }
        );

        // Handle crosshair change
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_CROSSHAIR, 
            (crosshairState) => {
                if (crosshairState) {
                    getCrosshairCoords((crosshairCoords) => {
                        this.plotCrosshairs(this.slice1ContainerId, crosshairCoords.slice1);
                        this.plotCrosshairs(this.slice2ContainerId, crosshairCoords.slice2);
                        this.plotCrosshairs(this.slice3ContainerId, crosshairCoords.slice3);
                    });
                } else {
                    this.removeCrosshairs();
                }
            }
        );
        // Handle direction marker change
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_DIRECTION_MARKER, 
            (directionMarkerState) => {
                if (directionMarkerState) {
                    getDirectionLabelCoords((directionMarkerCoords) => {
                        this.plotDirectionMarkers(this.slice1ContainerId, directionMarkerCoords.slice1);
                        this.plotDirectionMarkers(this.slice2ContainerId, directionMarkerCoords.slice2);
                        this.plotDirectionMarkers(this.slice3ContainerId, directionMarkerCoords.slice3);
                    });
                } else {
                    this.removeDirectionMarkers();
                }
            }
        );
        // Add event listener for window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    /**
     * Create the nifti plot container
     * @param {string} niftiPlotContainerId - The ID of the nifti plot container
     * @param {string} slice1ContainerId - The ID of the first slice container
     * @param {string} slice2ContainerId - The ID of the second slice container
     * @param {string} slice3ContainerId - The ID of the third slice container
     * @param {string} colorbarContainerId - The ID of the colorbar container
     */
    createContainer(
        niftiPlotContainerId, 
        slice1ContainerId,
        slice2ContainerId, 
        slice3ContainerId, 
        colorbarContainerId
    ) {
        // Append the row container to the surface container in the DOM
        const slicesContainer = document.getElementById(niftiPlotContainerId);
        if (slicesContainer) {
            slicesContainer.innerHTML = `
            <div id="${slice1ContainerId}" class="plot-slice-container"></div>
            <div id="${slice2ContainerId}" class="plot-slice-container"></div>
            <div id="${slice3ContainerId}" class="plot-slice-container"></div>
            <div id="${colorbarContainerId}" class="plot-colorbar-container"></div>
        `;
        slicesContainer.style.display = 'block'
        } else {
            console.error('Parent container for slices visualization not found!');
        }
    }

    /**
     * Change plot slice width based on view state
     * @param {string} viewState - The view state
     */
    changeViewPlotWidth(viewState) {    
        // update montage slice indices if montage state
        if (viewState == 'montage') {
            // distribute slice containers evenly
            document.getElementById(this.slice1ContainerId).style.width = '33%';
            document.getElementById(this.slice2ContainerId).style.width = '33%';
            document.getElementById(this.slice3ContainerId).style.width = '33%';
        } else {
            // if ortho view, give more room to first slice
            document.getElementById(this.slice1ContainerId).style.width = '38%';
            document.getElementById(this.slice2ContainerId).style.width = '31%';
            document.getElementById(this.slice3ContainerId).style.width = '31%';

        }
    }

    /**
     * Initialize the plot
     */
    initPlot() {
        // get fMRI data
        getFMRIData((viewer_data) => {
            // store temporary slice data
            this.sliceData = {
                slice1: viewer_data.data.func.x,
                slice2: viewer_data.data.func.y,
                slice3: viewer_data.data.func.z,
                slice1Anat: viewer_data.data.anat.x,
                slice2Anat: viewer_data.data.anat.y,
                slice3Anat: viewer_data.data.anat.z,
            };
            // full plot update
            this.plotNiftiFullUpdate(viewer_data.plot_options);
        });
    }

    /**
     * Resize plotly plots to window resizing
     */
    onWindowResize() {
        Plotly.Plots.resize(document.getElementById(this.slice1ContainerId));
        Plotly.Plots.resize(document.getElementById(this.slice2ContainerId));
        Plotly.Plots.resize(document.getElementById(this.slice3ContainerId));
        Plotly.Plots.resize(document.getElementById(this.colorbarContainerId));
    }

    /**
     * Full plot update of nifti data across slices
     * @param {object} plotOptions - Nifti plot options
     */
    plotNiftiFullUpdate(plotOptions) {
        // plot three slices individually
        this.plotSliceData(
            this.slice1ContainerId,
            'slice1', 
            plotOptions.color_map, 
            plotOptions.color_min, 
            plotOptions.color_max, 
            plotOptions.opacity
        );
        this.plotSliceData(
            this.slice2ContainerId,
             'slice2',
            plotOptions.color_map, 
            plotOptions.color_min, 
            plotOptions.color_max, 
            plotOptions.opacity
        )
        this.plotSliceData(
            this.slice3ContainerId, 
            'slice3',
            plotOptions.color_map, 
            plotOptions.color_min, 
            plotOptions.color_max, 
            plotOptions.opacity
        );

        // plot crosshairs if enabled
        if (plotOptions.crosshair_on) {
            getCrosshairCoords((crosshairCoords) => {
                // plot crosshairs for each slice
                this.plotCrosshairs(this.slice1ContainerId, crosshairCoords.slice1);
                this.plotCrosshairs(this.slice2ContainerId, crosshairCoords.slice2);
                this.plotCrosshairs(this.slice3ContainerId, crosshairCoords.slice3);
            });
        }

        // plot direction markers if enabled
        if (plotOptions.direction_markers_on) {
            getDirectionLabelCoords((directionMarkerCoords) => {
                this.plotDirectionMarkers(this.slice1ContainerId, directionMarkerCoords.slice1);
                this.plotDirectionMarkers(this.slice2ContainerId, directionMarkerCoords.slice2);
                this.plotDirectionMarkers(this.slice3ContainerId, directionMarkerCoords.slice3);
            });
        }
    }

    /**
     * Partial plot update of nifti data across slices
     * @param {string} plotContainerId - The plot container ID
     * @param {object} sliceData - The slice data
     */
    plotNiftiDataUpdate(plotContainerId, sliceData) {
        // update slice with new nifti data
        let sliceUpdate = {
            z: sliceData
        }
        // Plot data update using restyle (functional data is always second trace - zero-indexed)
        Plotly.restyle(plotContainerId, sliceUpdate, 1);
    }

    /**
     * Plot a single slice (functional and anatomical - optional)
     * @param {string} plotContainerId - The plot container ID
     * @param {string} axisLabel - The axis label
     * @param {string} colorMap - The color map
     * @param {number} colorMin - The color minimum
     * @param {number} colorMax - The color maximum
     * @param {number} opacity - The opacity
     */
    plotSliceData(
        plotContainerId,
        sliceName,
        colorMap,
        colorMin,
        colorMax,
        opacity
    ) {
        const data = [{
            z: this.viewerData[sliceName],
            name: 'fMRI',
            type: 'heatmap',
            colorscale: colorMap,
            zmin: colorMin,
            zmax: colorMax,
            opacity: opacity,
            showscale: false,
            // hoverinfo: hoverTextOn ? 'all' : 'none',
            // Display voxel coordinates
            // text: this.voxelText[axisLabel],
            // hovertemplate: hoverTextOn ? 'Intensity: %{z}<br> %{text}<extra></extra>': null
        }];

        const layout = {
            autosize: true,  // Enable autosizing
            responsive: true, // Make the plot responsive
            uirevision: true, // Keep the plot state consistent
            width: null,
            height: null,
            hovermode: 'closest',
            xaxis: {
                fixedrange: true,
                visible: false,  // Hide the X axis
                showgrid: false, // Hide grid lines
                zeroline: false, // Hide zero lines
                showline: false, // Hide axis lines
                showticklabels: false, // Hide axis tick labels
            },
            yaxis: {
                fixedrange: true,
                visible: false,  // Hide the X axis
                showgrid: false, // Hide grid lines
                zeroline: false, // Hide zero lines
                showline: false, // Hide axis lines
                showticklabels: false, // Hide axis tick labels
            },
            margin: { l: 0, r: 0, t: 0, b: 0 },  // Remove any margins
        };

        if (this.viewerData[sliceName + 'Anat']) {
            // Add the anatomical image as a background layer
            data.unshift({
                z: this.viewerData[sliceName + 'Anat'],
                name: 'anat',
                type: 'heatmap',
                colorscale: 'Greys',  // Use a grayscale colormap for the anatomical brain
                showscale: false,
                opacity: 0.5  // Set opacity for the anatomical background
            });
        }
        // Plot using react
        Plotly.react(plotContainerId, data, layout);
    }

    /**
     * Update plot with color change - color range, opacity
     * @param {string} plotContainerId - The plot container ID
     * @param {string} colorMap - The color map
     * @param {number} colorMin - The color minimum
     * @param {number} colorMax - The color maximum
     * @param {number} opacity - The opacity
     */
    plotColorUpdate(
        plotContainerId, 
        colorMap=null, 
        colorMin=null, 
        colorMax=null, 
        opacity=null
    ) {
        let colorUpdate = {};
        if (colorMap) {
            colorUpdate = {
                colorscale: colorMap,
            };
        }
        else if (colorMin) {
            colorUpdate = {
                zmin: colorMin,
            };
        }
        else if (colorMax) {
            colorUpdate = {
                zmax: colorMax,
            };
        }
        else if (opacity) {
            colorUpdate = {
                opacity: opacity,
            };
        }
        // Plot update using restyle (functional data is always second trace - zero-indexed)
        Plotly.restyle(plotContainerId, colorUpdate, 1);
    }
    /**
     * Plot crosshairs
     * @param {string} plotContainerId - The plot container ID
     * @param {object} crosshairCoords - The crosshair coordinates
     */
    plotCrosshairs(plotContainerId, crosshairCoords) {
        // hardcoded crosshair color and width - TODO: make this dynamic
        const crosshairColor = 'red';
        const crosshairWidth = 1;
        // Plot crosshairs
        // Create crosshair lines
        const crosshairLines = [
            {
                type: 'line',
                x0: 0,
                y0: crosshairCoords.y,
                x1: crosshairCoords.lenX,
                y1: crosshairCoords.y,
                line: { color: crosshairColor, width: crosshairWidth }
            },
            {
                type: 'line',
                x0: crosshairCoords.x,
                y0: 0,
                x1: crosshairCoords.x,
                y1: crosshairCoords.lenY,
                line: { color: crosshairColor, width: crosshairWidth }
            }
        ];
        // crosshair update
        const crossHairRelayout = {
            shapes: crosshairLines,
        };
        // Plot crosshairs with relayout
        Plotly.relayout(plotContainerId, crossHairRelayout);
    }

    /**
     * Plot direction markers
     * @param {string} plotContainerId - The plot container ID
     * @param {object} directionMarkerCoords - The direction marker coordinates
     */
    plotDirectionMarkers(plotContainerId, directionMarkerCoords) {
        // Create direction marker annotations
        const directionMarkerAnnotations = [];
        Object.keys(directionMarkerCoords).forEach((direction) => {
            directionMarkerAnnotations.push({
                    x: directionMarkerCoords[direction].x,
                    y: directionMarkerCoords[direction].y,
                    xref: 'x',
                    yref: 'y',
                    text: direction,
                showarrow: false            
            });
        });
        const directionMarkerRelayout = {
            annotations: directionMarkerAnnotations,
        };
        // Plot direction markers with relayout
        Plotly.relayout(plotContainerId, directionMarkerRelayout);
    }

    /**
     * Remove crosshairs
     */
    removeCrosshairs() {
        // remove crosshairs
        Plotly.relayout(this.slice1ContainerId, { shapes: [] });
        Plotly.relayout(this.slice2ContainerId, { shapes: [] });
        Plotly.relayout(this.slice3ContainerId, { shapes: [] });
    }

    /**
     * Remove direction markers
     */
    removeDirectionMarkers() {
        // remove direction markers
        Plotly.relayout(this.slice1ContainerId, { annotations: [] });
        Plotly.relayout(this.slice2ContainerId, { annotations: [] });
        Plotly.relayout(this.slice3ContainerId, { annotations: [] });
    }

}

export default NiftiViewer;
