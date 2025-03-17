// NiftiViewer.js
// Handles all plotting and click events for nifti visualization
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import ContextManager from '../api/ContextManager.js';

class NiftiViewer {
    /**
     * @param {string} niftiPlotContainerId - The ID of the nifti plot container
     * @param {string} slice1ContainerId - The ID of the first slice container
     * @param {string} slice2ContainerId - The ID of the second slice container
     * @param {string} slice3ContainerId - The ID of the third slice container
     * @param {string} colorbarContainerId - The ID of the colorbar container
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        niftiPlotContainerId,
        slice1ContainerId,
        slice2ContainerId,
        slice3ContainerId,
        colorbarContainerId,
        eventBus,
        contextManager
    ) {
        this.niftiPlotContainerId = niftiPlotContainerId;
        this.slice1ContainerId = slice1ContainerId;
        this.slice2ContainerId = slice2ContainerId;
        this.slice3ContainerId = slice3ContainerId;
        this.colorbarContainerId = colorbarContainerId;
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // define slice name to container id converter
        this.sliceName2ContainerId = {
            slice_1: slice1ContainerId,
            slice_2: slice2ContainerId,
            slice_3: slice3ContainerId,
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
            slice_1: null,
            slice_2: null,
            slice_3: null,
            slice_1_coords: null,
            slice_2_coords: null,
            slice_3_coords: null,
            slice_1_anat: null,
            slice_2_anat: null,
            slice_3_anat: null,
        };

        // initialize anatomical plot state as false
        this.anatomicalInput = false;

        // initialize hover text state as true
        this.hoverTextOn = true;

        // initialize crosshair state as true
        this.crosshairOn = true;

        // Add event listeners
        this.attachEventListeners();
    }

    /**
     * Attach event listeners for plot updates
     */
    attachEventListeners() {
        // Handle time slider change - update slice data and re-plot
        // Handle montage slice direction change - replot with new slice indices
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE
            ], 
            async () => {
                console.log('replotting nifti plot - time slider change');
                const viewer_data = await this.contextManager.data.getFMRIData();
                this.sliceData = {
                    slice_1: viewer_data.data.func.slice_1,
                    slice_2: viewer_data.data.func.slice_2,
                    slice_3: viewer_data.data.func.slice_3,
                    slice_1_coords: viewer_data.data.coords.slice_1,
                    slice_2_coords: viewer_data.data.coords.slice_2,
                    slice3_coords: viewer_data.data.coords.slice_3,
                };
                this.plotNiftiDataUpdate(
                    this.slice1ContainerId, 
                    this.sliceData.slice_1, 
                    this.sliceData.slice_1_coords
                );
                this.plotNiftiDataUpdate(
                    this.slice2ContainerId, 
                    this.sliceData.slice_2, 
                    this.sliceData.slice_2_coords
                );
                this.plotNiftiDataUpdate(
                    this.slice3ContainerId, 
                    this.sliceData.slice_3, 
                    this.sliceData.slice_3_coords
                );
            }
        );

        // Handle click event - update slice data and re-plot, if crosshair is enabled, re-plot crosshairs
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, 
            async () => {
                const viewer_data = await this.contextManager.data.getFMRIData();
                this.sliceData = {
                    slice_1: viewer_data.data.func.slice_1,
                    slice_2: viewer_data.data.func.slice_2,
                    slice_3: viewer_data.data.func.slice_3,
                    slice_1_coords: viewer_data.data.coords.slice_1,
                    slice_2_coords: viewer_data.data.coords.slice_2,
                    slice_3_coords: viewer_data.data.coords.slice_3,
                    slice_1_anat: viewer_data.data.anat.slice_1,
                    slice_2_anat: viewer_data.data.anat.slice_2,
                    slice_3_anat: viewer_data.data.anat.slice_3,
                };
                this.plotNiftiDataUpdate(
                    this.slice1ContainerId, 
                    this.sliceData.slice_1, 
                    this.sliceData.slice_1_coords,
                    this.sliceData.slice_1_anat
                );
                this.plotNiftiDataUpdate(
                    this.slice2ContainerId, 
                    this.sliceData.slice_2, 
                    this.sliceData.slice_2_coords,
                    this.sliceData.slice_2_anat
                );
                this.plotNiftiDataUpdate(
                    this.slice3ContainerId, 
                    this.sliceData.slice_3, 
                    this.sliceData.slice_3_coords,
                    this.sliceData.slice_3_anat
                );
                // re-plot crosshairs
                if (this.crosshairOn) {
                    const crosshairCoords = await this.contextManager.data.getCrosshairCoords();
                    this.plotCrosshairs(this.slice1ContainerId, crosshairCoords.slice_1);
                    this.plotCrosshairs(this.slice2ContainerId, crosshairCoords.slice_2);
                    this.plotCrosshairs(this.slice3ContainerId, crosshairCoords.slice_3);
                }
            }
        );

        // Handle view state change and/or montage slice direction change and perform full plot update
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.VIEW_TOGGLE, 
                EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_DIRECTION_CHANGE
            ], 
            async (viewState) => {
                // change plot width
                this.changeViewPlotWidth(viewState.view_state);
                const viewer_data = await this.contextManager.data.getFMRIData();
                console.log('initializing nifti plot');
                // store temporary slice data
                this.sliceData = {
                    slice_1: viewer_data.data.func.slice_1,
                    slice_2: viewer_data.data.func.slice_2,
                    slice_3: viewer_data.data.func.slice_3,
                    slice_1_coords: viewer_data.data.coords.slice_1,
                    slice_2_coords: viewer_data.data.coords.slice_2,
                    slice_3_coords: viewer_data.data.coords.slice_3,
                    slice_1_anat: viewer_data.data.anat.slice_1,
                    slice_2_anat: viewer_data.data.anat.slice_2,
                    slice_3_anat: viewer_data.data.anat.slice_3,
                };
                // full plot update
                this.plotNiftiFullUpdate(viewer_data.plot_options);
            }
        );

        // Handle montage slice index change - replot with new slice indices
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_CHANGE, 
            async (sliceParams) => {
                const sliceName = sliceParams.slice_name;
                const sliceIdx = sliceParams.slice_idx;
                const viewer_data = await this.contextManager.data.getFMRIData();
                console.log('replotting nifti plot - montage slice index change');
                // only update slices that have changed
                this.sliceData[sliceName] = viewer_data.data.func[sliceName];
                this.sliceData[sliceName + '_coords'] = viewer_data.data.coords[sliceName];
                this.plotNiftiDataUpdate(
                    this.sliceName2ContainerId[sliceName], 
                    this.sliceData[sliceName], 
                    this.sliceData[sliceName + '_coords']
                );
            }
        );

        // Handle any color changes
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.COLOR_MAP_CHANGE, 
                EVENT_TYPES.VISUALIZATION.FMRI.OPACITY_SLIDER_CHANGE,
                EVENT_TYPES.VISUALIZATION.FMRI.COLOR_SLIDER_CHANGE,
            ], 
            async () => {
                console.log('replotting nifti plot - color slider or color map change');
                const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
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
            }
        );

        // Handle threshold change
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.THRESHOLD_SLIDER_CHANGE, 
            async () => {
                console.log('replotting nifti plot - threshold slider change');
                const viewer_data = await this.contextManager.data.getFMRIData();
                this.sliceData = {
                    slice_1: viewer_data.data.func.slice_1,
                    slice_2: viewer_data.data.func.slice_2,
                    slice_3: viewer_data.data.func.slice_3,
                    slice_1_coords: viewer_data.data.coords.slice_1,
                    slice_2_coords: viewer_data.data.coords.slice_2,
                    slice_3_coords: viewer_data.data.coords.slice_3,
                };
                this.plotNiftiDataUpdate(
                    this.slice1ContainerId, 
                    this.sliceData.slice_1, 
                    this.sliceData.slice_1_coords
                );
                this.plotNiftiDataUpdate(
                    this.slice2ContainerId, 
                    this.sliceData.slice_2, 
                    this.sliceData.slice_2_coords
                );
                this.plotNiftiDataUpdate(
                    this.slice3ContainerId, 
                    this.sliceData.slice_3, 
                    this.sliceData.slice_3_coords
                );
            }
        );

        // Handle reset of color sliders - update for change of threshold and update plot color properties
        // Handle preprocess submit and reset - replot with new data
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.RESET_COLOR_SLIDERS,
                EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS,
                EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_RESET,
            ],
            async () => {
                console.log('replotting nifti plot - reset color sliders, or preprocess submit/reset');
                const viewer_data = await this.contextManager.data.getFMRIData();
                this.sliceData = {
                    slice_1: viewer_data.data.func.slice_1,
                    slice_2: viewer_data.data.func.slice_2,
                    slice_3: viewer_data.data.func.slice_3,
                    slice_1_coords: viewer_data.data.coords.slice_1,
                    slice_2_coords: viewer_data.data.coords.slice_2,
                    slice_3_coords: viewer_data.data.coords.slice_3,
                };
                this.plotNiftiDataUpdate(
                    this.slice1ContainerId, 
                    this.sliceData.slice_1, 
                    this.sliceData.slice_1_coords
                );
                this.plotNiftiDataUpdate(
                    this.slice2ContainerId, 
                    this.sliceData.slice_2, 
                    this.sliceData.slice_2_coords
                );
                this.plotNiftiDataUpdate(
                    this.slice3ContainerId, 
                    this.sliceData.slice_3, 
                    this.sliceData.slice_3_coords
                );
                // update plot color properties
                const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
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
            }
        );

        // Handle crosshair change
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_CROSSHAIR, 
            async (crosshairState) => {
                console.log('plotting crosshairs on nifti plot');
                this.crosshairOn = crosshairState.crosshairState;
                if (this.crosshairOn) {
                    const crosshairCoords = await this.contextManager.data.getCrosshairCoords();
                    this.plotCrosshairs(this.slice1ContainerId, crosshairCoords.slice_1);
                    this.plotCrosshairs(this.slice2ContainerId, crosshairCoords.slice_2);
                    this.plotCrosshairs(this.slice3ContainerId, crosshairCoords.slice_3);
                } else {
                    this.removeCrosshairs();
                }
            }
        );

        // Handle direction marker change
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_DIRECTION_MARKER, 
            async (directionMarkerState) => {
                console.log('plotting direction markers on nifti plot');
                if (directionMarkerState.directionMarkerState) {
                    const directionMarkerCoords = await this.contextManager.data.getDirectionLabelCoords();
                    this.plotDirectionMarkers(this.slice1ContainerId, directionMarkerCoords.slice_1);
                    this.plotDirectionMarkers(this.slice2ContainerId, directionMarkerCoords.slice_2);
                    this.plotDirectionMarkers(this.slice3ContainerId, directionMarkerCoords.slice_3);
                } else {
                    this.removeDirectionMarkers();
                }
            }
        );

        // Handle hover text toggle
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.HOVER_TEXT_TOGGLE, 
            (hoverState) => {
                console.log('plotting hover text on nifti plot');
                this.plotNiftiDataUpdate(
                    this.slice1ContainerId,
                    this.sliceData.slice_1, 
                    this.sliceData.slice_1_coords,
                    null, 
                    hoverState.hoverState
                );
                this.plotNiftiDataUpdate(
                    this.slice2ContainerId,
                    this.sliceData.slice_2, 
                    this.sliceData.slice_2_coords,
                    null, 
                    hoverState.hoverState
                );
                this.plotNiftiDataUpdate(
                    this.slice3ContainerId,
                    this.sliceData.slice_3, 
                    this.sliceData.slice_3_coords,
                    null, 
                    hoverState.hoverState
                );
            }
        );

        // Handle reverse colorbar toggle
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_REVERSE_COLORBAR, 
            (reverseColormapState) => {
                console.log('reversing colormap on nifti plot');
                this.plotReverseColormap(
                    reverseColormapState.reverseColormapState
                );
            }
        );

        // resize window on colorbar toggle
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_COLORBAR, 
            () => {
                this.onWindowResize();
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
        console.log('creating nifti plot containers');
        // Append the row container to the surface container in the DOM
        const slicesContainer = document.getElementById(niftiPlotContainerId);
        if (slicesContainer) {
            slicesContainer.innerHTML = `
                <div id="${slice1ContainerId}" class="plot-slice-container"></div>
                <div id="${slice2ContainerId}" class="plot-slice-container"></div>
                <div id="${slice3ContainerId}" class="plot-slice-container"></div>
                <div id="${colorbarContainerId}" class="plot-colorbar-container"></div>
            `;
            slicesContainer.style.display = 'block';
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
    async initPlot() {
        // get fMRI data
        const viewer_data = await this.contextManager.data.getFMRIData();
        console.log('initializing nifti plot');
        // store temporary slice data
        this.sliceData = {
            slice_1: viewer_data.data.func.slice_1,
            slice_2: viewer_data.data.func.slice_2,
            slice_3: viewer_data.data.func.slice_3,
            slice_1_coords: viewer_data.data.coords.slice_1,
            slice_2_coords: viewer_data.data.coords.slice_2,
            slice_3_coords: viewer_data.data.coords.slice_3,
            slice_1_anat: viewer_data.data.anat.slice_1,
            slice_2_anat: viewer_data.data.anat.slice_2,
            slice_3_anat: viewer_data.data.anat.slice_3,
        };
        // full plot update
        this.plotNiftiFullUpdate(viewer_data.plot_options);
        // TODO: this is a workaround for a bug where the plot is not resized 
        //  after the plot is initialized and the plot is not displayed correctly
        this.onWindowResize();
        // emit event to indicate initialization of plot is complete
        this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.INIT_NIFTI_VIEWER);
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
    async plotNiftiFullUpdate(plotOptions) {
        // plot three slices individually
        this.plotSliceData(
            this.slice1ContainerId,
            'slice_1', 
            plotOptions.color_map, 
            plotOptions.color_min, 
            plotOptions.color_max, 
            plotOptions.opacity,
            plotOptions.hover_text_on,
            plotOptions.reverse_colormap
        );
        this.plotSliceData(
            this.slice2ContainerId,
             'slice_2',
            plotOptions.color_map, 
            plotOptions.color_min, 
            plotOptions.color_max, 
            plotOptions.opacity,
            plotOptions.hover_text_on,
            plotOptions.reverse_colormap
        )
        this.plotSliceData(
            this.slice3ContainerId, 
            'slice_3',
            plotOptions.color_map, 
            plotOptions.color_min, 
            plotOptions.color_max, 
            plotOptions.opacity,
            plotOptions.hover_text_on,
            plotOptions.reverse_colormap
        );

        // plot crosshairs if enabled
        if (this.crosshairOn) {
            const crosshairCoords = await this.contextManager.data.getCrosshairCoords();
            // plot crosshairs for each slice
            this.plotCrosshairs(this.slice1ContainerId, crosshairCoords.slice_1);
            this.plotCrosshairs(this.slice2ContainerId, crosshairCoords.slice_2);
            this.plotCrosshairs(this.slice3ContainerId, crosshairCoords.slice_3);
        }

        // plot direction markers if enabled
        if (plotOptions.direction_markers_on) {
            const directionMarkerCoords = await this.contextManager.data.getDirectionLabelCoords();
            this.plotDirectionMarkers(this.slice1ContainerId, directionMarkerCoords.slice_1);
            this.plotDirectionMarkers(this.slice2ContainerId, directionMarkerCoords.slice_2);
            this.plotDirectionMarkers(this.slice3ContainerId, directionMarkerCoords.slice_3);
        }
    }

    /**
     * Partial plot update of nifti data across slices
     * @param {string} plotContainerId - The plot container ID
     * @param {object} sliceData - The slice data
     * @param {object} sliceCoords - The slice coordinates
     * @param {object} sliceAnat - The slice anatomical data
     * @param {boolean} hoverTextOn - Whether hover text is enabled
     */
    plotNiftiDataUpdate(plotContainerId, sliceData, sliceCoords, sliceAnat=null, hoverTextOn=null) {
        // update functional slice with new nifti data
        if (hoverTextOn !== null) {
            this.hoverTextOn = hoverTextOn;
        }
        let sliceUpdate = {
            z: [sliceData],
            text: [sliceCoords],
            hoverinfo: this.hoverTextOn ? 'all' : 'none',
            hovertemplate: this.hoverTextOn ? 'Intensity: %{z}<br> %{text}<extra></extra>': null
        }
        // functional data is second trace (0-indexed) if anatomical input is enabled
        let traceIndex
        if (this.anatomicalInput) {
            traceIndex = 1;
        } else {
            traceIndex = 0;
        }
        Plotly.restyle(plotContainerId, sliceUpdate, [traceIndex]);
        // update anatomical slice with new nifti data
        if (sliceAnat && this.anatomicalInput) {
            sliceUpdate = {
                z: [sliceAnat],
            }
            Plotly.restyle(plotContainerId, sliceUpdate, 0);
        }
    }

    /**
     * Plot a single slice (functional and anatomical - optional)
     * @param {string} plotContainerId - The plot container ID
     * @param {string} axisLabel - The axis label
     * @param {string} colorMap - The color map
     * @param {number} colorMin - The color minimum
     * @param {number} colorMax - The color maximum
     * @param {number} opacity - The opacity
     * @param {object} hoverTextOn - Whether hover text is enabled
     * @param {boolean} reverseColormap - Whether the colormap is reversed
     */
    plotSliceData(
        plotContainerId,
        sliceName,
        colorMap,
        colorMin,
        colorMax,
        opacity,
        hoverTextOn,
        reverseColormap
    ) {
        // plot functional data
        const data = [{
            z: this.sliceData[sliceName],
            name: 'fMRI',
            type: 'heatmap',
            colorscale: colorMap,
            zmin: colorMin,
            zmax: colorMax,
            opacity: opacity,
            showscale: false,
            hoverinfo: hoverTextOn ? 'all' : 'none',
            reversescale: reverseColormap,
            // Display voxel coordinates
            text: this.sliceData[sliceName + '_coords'],
            hovertemplate: hoverTextOn ? 'Intensity: %{z}<br> %{text}<extra></extra>': null
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
                visible: false,  
                showgrid: false, 
                zeroline: false, 
                showline: false, 
                showticklabels: false,
            },
            yaxis: {
                fixedrange: true,
                visible: false,  
                showgrid: false, 
                zeroline: false, 
                showline: false, 
                showticklabels: false, 
            },
            margin: { l: 0, r: 0, t: 0, b: 0 },  // Remove any margins
        };
        // add anatomical data if available
        if (this.sliceData[sliceName + '_anat']) {
            this.anatomicalInput = true;
            // Add the anatomical image as a background layer
            data.unshift({
                z: this.sliceData[sliceName + '_anat'],
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
        const colorUpdate = {};
        if (colorMap) {
            colorUpdate.colorscale = [colorMap];
        }
        if (colorMin) {
            colorUpdate.zmin = [colorMin];
        }
        if (colorMax) {
            colorUpdate.zmax = [colorMax];
        }
        if (opacity) {
            colorUpdate.opacity = [opacity];
        }
        // functional data is second trace (0-indexed) if anatomical input is enabled
        let traceIndex
        if (this.anatomicalInput) {
            traceIndex = 1;
        } else {
            traceIndex = 0;
        }
        Plotly.restyle(plotContainerId, colorUpdate, [traceIndex]);
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
                x1: crosshairCoords.len_x,
                y1: crosshairCoords.y,
                line: { color: crosshairColor, width: crosshairWidth }
            },
            {
                type: 'line',
                x0: crosshairCoords.x,
                y0: 0,
                x1: crosshairCoords.x,
                y1: crosshairCoords.len_y,
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
     * Plot hover text
     * @param {boolean} hoverTextOn - Whether hover text is enabled
     */
    plotHoverText(hoverTextOn) {
        // Plot hover text
        // Plot data update using restyle (functional data is always second trace - zero-indexed)
        Plotly.restyle(
            this.slice1ContainerId, 
            { hoverinfo: hoverTextOn ? 'all' : 'none' },
            1
        );
        Plotly.restyle(
            this.slice2ContainerId, 
            { hoverinfo: hoverTextOn ? 'all' : 'none' }, 
            1
        );
        Plotly.restyle(
            this.slice3ContainerId, 
            { hoverinfo: hoverTextOn ? 'all' : 'none' }, 
            1
        );
    }

    /**
     * Plot reverse colorbar
     * @param {boolean} reverseColormap - Whether the colormap is reversed
     */
    plotReverseColormap(reverseColormap) {
        // functional data is second trace (0-indexed) if anatomical input is enabled
        let traceIndex
        if (this.anatomicalInput) {
            traceIndex = 1;
        } else {
            traceIndex = 0;
        }
        Plotly.restyle(this.slice1ContainerId, { reversescale: reverseColormap }, traceIndex);
        Plotly.restyle(this.slice2ContainerId, { reversescale: reverseColormap }, traceIndex);
        Plotly.restyle(this.slice3ContainerId, { reversescale: reverseColormap }, traceIndex);
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
