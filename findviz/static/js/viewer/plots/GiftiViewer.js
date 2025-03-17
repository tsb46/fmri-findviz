// GiftiViewer.js
// Handles all plotting and click events for gifti visualization
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import ContextManager from '../api/ContextManager.js';

class GiftiViewer {
    /**
     * Constructor for GiftiViewer
     * @param {string} giftiPlotContainerId - ID of the gifti plot container
     * @param {string} leftPlotContainerId - ID of the left plot container
     * @param {string} rightPlotContainerId - ID of the right plot container
     * @param {string} colorbarContainerId - ID of the colorbar container
     * @param {EventBus} eventBus - Event bus for communication between components
     * @param {ContextManager} contextManager - Context manager for data and plot options
     */
    constructor(
        giftiPlotContainerId,
        leftPlotContainerId,
        rightPlotContainerId,
        colorbarContainerId,
        eventBus,
        contextManager
    ) {
        this.giftiPlotContainerId = giftiPlotContainerId;
        this.leftPlotContainerId = leftPlotContainerId;
        this.rightPlotContainerId = rightPlotContainerId;
        this.colorbarContainerId = colorbarContainerId;
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // initialize hover text state as true
        this.hoverTextOn = true;

        // attach event listeners
        this.attachEventListeners();
    }

     /**
     * Attach event listeners for plot updates
     */
     attachEventListeners() {
        // Handle time slider change - update slice data and re-plot
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, 
            async () => {
                console.log('replotting gifti plot - time slider change');
                const viewer_data = await this.contextManager.data.getFMRIData();
                this.surfaceData = {
                    left: viewer_data.data.left_hemisphere,
                    right: viewer_data.data.right_hemisphere,
                };
                this.plotGiftiDataUpdate();
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
                console.log('replotting gifti plot - color slider or color map change');
                const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
                this.plotColorUpdate(
                    plotOptions.color_map, plotOptions.color_min, 
                    plotOptions.color_max, plotOptions.opacity
                );
            }
        );

        // Handle threshold change
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.THRESHOLD_SLIDER_CHANGE, 
            async () => {
                console.log('replotting gifti plot - threshold slider change');
                const viewer_data = await this.contextManager.data.getFMRIData();
                this.surfaceData = {
                    left: viewer_data.data.left_hemisphere,
                    right: viewer_data.data.right_hemisphere,
                };
                this.plotGiftiDataUpdate();
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
                console.log('replotting gifti plot - reset color sliders, or preprocess submit/reset');
                const viewer_data = await this.contextManager.data.getFMRIData();
                this.surfaceData = {
                    left: viewer_data.data.left_hemisphere,
                    right: viewer_data.data.right_hemisphere,
                };
                this.plotGiftiDataUpdate();
                // update plot color properties
                const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
                this.plotColorUpdate(
                    plotOptions.color_map, plotOptions.color_min, 
                    plotOptions.color_max, plotOptions.opacity
                );
            }
        );

        // Handle hover text toggle
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.HOVER_TEXT_TOGGLE, 
            (hoverState) => {
                console.log('plotting hover text on gifti plot');
                this.plotGiftiDataUpdate(null, hoverState.hoverState);
            }
        );

        // Handle reverse colorbar toggle
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_REVERSE_COLORBAR, 
            (reverseColormapState) => {
                console.log('reversing colormap on gifti plot');
                this.plotReverseColormap(
                    reverseColormapState.reverseColormapState
                );
            }
        );

        // Handle freeze view toggle
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_FREEZE_VIEW, 
            (freezeViewState) => {
                if (freezeViewState.freezeViewState) {
                    console.log('freezing view on gifti plot');
                    this.freezeView();
                } else {
                    console.log('unfreezing view on gifti plot');
                    this.unfreezeView();
                }
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
     * Freeze zooming and panning of gifti plot
     */
    freezeView() {
        const layoutUpdate = {
            xaxis: {
                fixedrange: true
            },
            yaxis: {
                fixedrange: true
            },
            dragmode: false
        };
        if (this.leftInput) {
            Plotly.relayout(this.leftPlotContainerId, layoutUpdate);
        }
        if (this.rightInput) {
            Plotly.relayout(this.rightPlotContainerId, layoutUpdate);
        }
    }

    /**
     * Get metadata for gifti plot
     */
    async getMetadata() {
        const viewerMetadata = await this.contextManager.data.getViewerMetadata();
        const coordLabels = await this.contextManager.data.getCoordLabels();
        this.leftInput = viewerMetadata.left_input;
        this.rightInput = viewerMetadata.right_input;
        this.verticesLeft = viewerMetadata.vertices_left;
        this.facesLeft = viewerMetadata.faces_left;
        this.verticesRight = viewerMetadata.vertices_right;
        this.facesRight = viewerMetadata.faces_right;
        this.coordLabelsLeft = coordLabels.left_coord_labels;
        this.coordLabelsRight = coordLabels.right_coord_labels;
    }

    /**
     * Initialize containers for gifti plot
     * @param {string} giftiPlotContainerId - ID of the gifti plot container
     * @param {string} leftPlotContainerId - ID of the left plot container
     * @param {string} rightPlotContainerId - ID of the right plot container
     * @param {string} colorbarContainerId - ID of the colorbar container
     */
    initContainers(
        giftiPlotContainerId,
        leftPlotContainerId,
        rightPlotContainerId,
        colorbarContainerId
    ) {
        console.log('creating gifti plot containers');
        // Append the row container to the surface container in the DOM
        const surfaceContainer = document.getElementById(giftiPlotContainerId);

        // create row container
        let rowContainer = document.createElement('div');
        rowContainer.className = 'row';
        rowContainer.style.width = '100%';
        rowContainer.style.height = '100%';
        rowContainer.style.margin = '0';

        // display surface container
        surfaceContainer.style.display = 'block';

        // Left hemisphere
        if (this.leftInput) {
            const leftContainer = document.createElement('div');
            if (!this.rightInput) {
                leftContainer.className = 'col-md-10';
            } else {
                leftContainer.className = 'col-md-5';
            }
            leftContainer.innerHTML = `<div id="${leftPlotContainerId}"></div>`;
            rowContainer.appendChild(leftContainer);
        }

        // Right hemisphere
        if (this.rightInput) {
            const rightContainer = document.createElement('div');
            if (!this.leftInput) {
                rightContainer.className = 'col-md-10';
            } else {
                rightContainer.className = 'col-md-5';
            }
            rightContainer.innerHTML = `<div id="${rightPlotContainerId}"></div>`;
            rowContainer.appendChild(rightContainer);
        }

        // Colorbar
        const colorbarContainer = document.createElement('div');
        colorbarContainer.className = 'col-md-2';
        colorbarContainer.innerHTML = `<div id="${colorbarContainerId}"></div>`;
        rowContainer.appendChild(colorbarContainer);

        // Add container to DOM
        surfaceContainer.appendChild(rowContainer);
    }

    /**
     * Initialize the plot
     */
    async initPlot() {
        // get metadata
        await this.getMetadata();
        // Initialize containers for plots and initialize them properly
        this.initContainers(
            this.giftiPlotContainerId,
            this.leftPlotContainerId,
            this.rightPlotContainerId,
            this.colorbarContainerId
        );
        // get fMRI data
        const viewer_data = await this.contextManager.data.getFMRIData();
        console.log('initializing gifti plot');
        // store temporary surface data
        this.surfaceData = {
            left: viewer_data.data.left_hemisphere,
            right: viewer_data.data.right_hemisphere,
        };
        // full plot update
        this.plotGiftiFullUpdate(viewer_data.plot_options);
        // emit event to indicate initialization of plot is complete
        this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.INIT_GIFTI_VIEWER);
    }

    /**
     * Update plot with color change - color range, opacity
     * @param {string} colorMap - The color map
     * @param {number} colorMin - The color minimum
     * @param {number} colorMax - The color maximum
     * @param {number} opacity - The opacity
     */
    plotColorUpdate(
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
            colorUpdate.cmin = [colorMin];
        }
        if (colorMax) {
            colorUpdate.cmax = [colorMax];
        }
        if (opacity) {
            colorUpdate.opacity = [opacity];
        }
        if (this.leftInput) {
            Plotly.restyle(this.leftPlotContainerId, colorUpdate);
        }
        if (this.rightInput) {
            Plotly.restyle(this.rightPlotContainerId, colorUpdate);
        }
    }

    /**
     * Full plot update of gifti data across slices
     * @param {object} plotOptions - Gifti plot options
     */
    async plotGiftiFullUpdate(plotOptions) {
        // plot hemispheres individually
        if (this.leftInput) {
            this.plotHemisphere(
                this.leftPlotContainerId,
                'left', 
                plotOptions.color_map, 
                plotOptions.color_min, 
                plotOptions.color_max, 
                plotOptions.opacity,
                plotOptions.hover_text_on,
                plotOptions.reverse_colormap
            );
        }
        if (this.rightInput) {
            this.plotHemisphere(
                this.rightPlotContainerId,
                'right',
                plotOptions.color_map, 
                plotOptions.color_min, 
                plotOptions.color_max, 
                plotOptions.opacity,
                plotOptions.hover_text_on,
                plotOptions.reverse_colormap
            );
        }
    }

    /**
     * Partial plot update of gifti data across slices
     * @param {string} hemisphere - The hemisphere to plot
     * @param {boolean} hoverTextOn - Whether hover text is enabled
     */
    plotGiftiDataUpdate(hemisphere=null, hoverTextOn=null) {
        // update functional slice with new nifti data
        if (hoverTextOn !== null) {
            this.hoverTextOn = hoverTextOn;
        }
        if ((hemisphere == 'left') || (hemisphere == null && this.leftInput)) {
            let leftSurfaceUpdate = {
                intensity: [this.surfaceData.left],
                text: [this.formattedCoordLabelsLeft],
                hoverinfo: this.hoverTextOn ? 'all' : 'none',
                hovertemplate: this.hoverTextOn ? 'Intensity: %{intensity:.3f}<br> %{text}<extra></extra>': null
            }
            Plotly.restyle(this.leftPlotContainerId, leftSurfaceUpdate);
        }
        if ((hemisphere == 'right') || (hemisphere == null && this.rightInput)) {
            let rightSurfaceUpdate = {
                intensity: [this.surfaceData.right],
                text: [this.formattedCoordLabelsRight],
                hoverinfo: this.hoverTextOn ? 'all' : 'none',
                hovertemplate: this.hoverTextOn ? 'Intensity: %{intensity:.3f}<br> %{text}<extra></extra>': null
            }
            Plotly.restyle(this.rightPlotContainerId, rightSurfaceUpdate);
        }
    }

    /**
     * Plot a hemisphere of the gifti data
     * @param {string} plotDiv - ID of the plot container
     * @param {string} hemisphere - Hemisphere to plot
     * @param {string} colorMap - Color map to use
     * @param {string} colorMin - Minimum color value
     * @param {string} colorMax - Maximum color value
     * @param {string} opacity - Opacity of the plot
     * @param {string} hoverTextOn - Whether to show hover text
     * @param {string} reverseColormap - Whether to reverse the colormap
     */
    plotHemisphere(
        plotDiv,
        hemisphere,
        colorMap,
        colorMin,
        colorMax,
        opacity,
        hoverTextOn,
        reverseColormap
    ) {
        console.log('plotting hemisphere', hemisphere);
        let plotTitle;
        let vertices;
        let faces;
        let coordLabels;
        // set plot data based on hemisphere
        if (hemisphere == 'left') {
            plotTitle = 'Left Hemisphere';
            vertices = this.verticesLeft;
            faces = this.facesLeft;
            coordLabels = this.coordLabelsLeft;
        } else if (hemisphere == 'right') {
            plotTitle = 'Right Hemisphere';
            vertices = this.verticesRight;
            faces = this.facesRight;
            coordLabels = this.coordLabelsRight;
        }

        // format coord labels
        const formattedCoordLabels = coordLabels.map(label => {
            return `Vertex ${label[0]} (${label[1]})`;
        });

        const intensityData = this.surfaceData[hemisphere];
        const plotData = {
            type: 'mesh3d',
            x: vertices.map(v => v[0]),
            y: vertices.map(v => v[1]),
            z: vertices.map(v => v[2]),
            i: faces.map(f => f[0]),
            j: faces.map(f => f[1]),
            k: faces.map(f => f[2]),
            intensity: intensityData,
            colorscale: colorMap,
            cmin: colorMin,
            cmax: colorMax,
            opacity: opacity,
            showscale: false,
            text: formattedCoordLabels,
            reversescale: reverseColormap,
            hoverinfo: hoverTextOn ? 'all' : 'none',
            hovertemplate: hoverTextOn ? 'Intensity: %{intensity:.3f}<br> %{text}<extra></extra>': null
        };

        let layout = {
            title: plotTitle,
            autosize: true,  // Enable autosizing
            responsive: true, // Make the plot responsive
            uirevision:'true',
            scene: {
                xaxis: {
                    visible: false,  // Hide the X axis
                    showgrid: false, // Hide grid lines
                    zeroline: false, // Hide zero lines
                    showline: false, // Hide axis lines
                    showticklabels: false, // Hide axis tick labels
                },
                yaxis: {
                    visible: false,  // Hide the Y axis
                    showgrid: false, // Hide grid lines
                    zeroline: false, // Hide zero lines
                    showline: false, // Hide axis lines
                    showticklabels: false, // Hide axis tick labels
                },
                zaxis: {
                    visible: false,  // Hide the Z axis
                    showgrid: false, // Hide grid lines
                    zeroline: false, // Hide zero lines
                    showline: false, // Hide axis lines
                    showticklabels: false, // Hide axis tick labels
                },
            },
            margin: { l: 5, r: 5, b: 5, t: 30 },
        };

        // Plot using react
        Plotly.react(plotDiv, [plotData], layout);
    }

    /**
     * Plot reverse colorbar
     * @param {boolean} reverseColormap - Whether the colormap is reversed
     */
    plotReverseColormap(reverseColormap) {
        if (this.leftInput) {
            Plotly.restyle(this.leftPlotContainerId, { reversescale: reverseColormap });
        }
        if (this.rightInput) {
            Plotly.restyle(this.rightPlotContainerId, { reversescale: reverseColormap });
        }
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        if (this.leftInput) {
            Plotly.Plots.resize(document.getElementById(this.leftPlotContainerId));
        }
        if (this.rightInput) {
            Plotly.Plots.resize(document.getElementById(this.rightPlotContainerId));
        }
    }

    /**
     * Allow zooming and panning of gifti plot
     */
    unfreezeView() {
        const layoutUpdate = {
            xaxis: {
                fixedrange: false
            },
            yaxis: {
                fixedrange: false
            },
            dragmode: 'rotate'
        };
        if (this.leftInput) {
            Plotly.relayout(this.leftPlotContainerId, layoutUpdate);
        }
        if (this.rightInput) {
            Plotly.relayout(this.rightPlotContainerId, layoutUpdate);
        }
    }
}

export default GiftiViewer;
