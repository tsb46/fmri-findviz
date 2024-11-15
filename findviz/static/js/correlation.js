// correlation.js
import ColorBar from './colorbar.js';
import TimeSlider from './timeslider.js';
import { VisualizationOptions } from './user.js';
import NiftiViewer from './nifti.js';
import GiftiViewer from './gifti.js';

class Correlate {
    constructor(
      plotData
    ) {
        // Set text in visualization card
        document.getElementById('fmri-visualization-title').textContent = 'Correlation Map'
        document.getElementById('time-slider-title').textContent = 'Lag:'
        // set attributes based on nifti or gifti file input
        if (plotData.plot_type == 'nifti') {
            // initialize nifti viewer
            this.viewer = new NiftiViewer(
                plotData.file_key,
                plotData.anat_key,
                plotData.mask_key,
                plotData.slice_len[0]
            );
            // set colorbar div
            this.colorbarDiv = 'colorbar_container_nii'
        } else if (plotData.plot_type == 'gifti') {
            // initialize gifti viewer
            this.viewer = new GiftiViewer(
                plotData.left_key,
                plotData.right_key,
                plotData.vertices_left,
                plotData.faces_left,
                plotData.vertices_right,
                plotData.faces_right,
            );
            // set colorbar div
            this.colorbarDiv = 'colorbar_container_gii'
        }
        // set plot type
        this.plotType = plotData.plot_type;
        // Initialize colormap as Viridis
        this.colormap = 'Viridis';
        // Set time point as zero for initial plot
        this.timePoint = 0;
        // Initilialize global min and global max values
        this.globalMin = plotData.global_min;
        this.globalMax = plotData.global_max;
        // Initialize color min and color max based on Global min and max (for intial plot)
        this.colorMin = this.globalMin;
        this.colorMax = this.globalMax;
        // Initialize thresholds (set to [0,0] for no threshold by default)
        this.thresholdMin = 0;
        this.thresholdMax = 0;
        // Initialize hover text state
        this.hoverTextOn = true;
        // Initialize Preprocess state as false (not used, just for consistency with API)
        this.preprocState = false;

        // Initialize TimeSlider class
        this.timeSlider = new TimeSlider(plotData.timepoints);

        // Initialize VisualizationOptions class
        this.visualizationOptions = new VisualizationOptions(
            this.globalMin, this.globalMax, this.plotType,
            this.attachVizOptionListeners
        );

        // Initialize colorbar class
        this.colorBar = new ColorBar(
            this.colorbarDiv, this.globalMin, this.globalMax, 'Correlation'
        );

    }

    // initialize initial plot
    init() {
        // Plot brain image
        this.viewer.plot(
            this.timePoint,
            this.colormap,
            this.colorMin,
            this.colorMax,
            this.thresholdMin,
            this.thresholdMax,
            this.hoverTextOn,
            this.preprocState,
            true // update voxel coordinate labels (only for nifti)
        ).then(() => {
            // Weird layout of first plot for niftis, initiate resize to fix
            if (this.plotType == 'nifti') {
                this.viewer.onWindowResize()
            }
            // Plot colorbar
            this.colorBar.plotColorbar(this.colormap);
            // set listener for time slider change
            this.listenForTimeSliderChange();
            // Register click handlers
            this.registerClickHandlers();
        }).catch(error => {
            console.error('Error during initialization:', error);
        });
    }

    // Listeners to pass to VisualizationOptions class
    attachVizOptionListeners = () => {
        // Listen for colormap change
        this.colormapChangeListener = (event) => {
            this.colormap = event.detail.selectedValue;
            // Plot brain map with new color
            this.viewer.plot(
                this.timePoint,
                this.colormap,
                this.colorMin,
                this.colorMax,
                this.thresholdMin,
                this.thresholdMax,
                this.hoverTextOn,
                this.preprocState,
                false, // do not update coordinates
                true // update layout only
            );
            // Update colorbar
            this.colorBar.plotColorbar(this.colormap)

        };
        document.querySelector('.custom-dropdown .dropdown-menu').addEventListener(
                'colormapChange',  this.colormapChangeListener
      );
      // Listen for color range slider change
        $('#colorRangeSlider').on('colorSliderChange', (event) => {
            const colorRange = event.detail.newValue
            this.colorMin = colorRange[0]
            this.colorMax = colorRange[1]
            // plot brain map with new color range
            this.viewer.plot(
                  this.timePoint,
                  this.colormap,
                  this.colorMin,
                  this.colorMax,
                  this.thresholdMin,
                  this.thresholdMax,
                  this.hoverTextOn,
                  this.preprocState,
                  false, // do not update coordinates
                  true // update layout only
            );
            // plot colorbar with new color range
            this.colorBar.plotColorbar(
                this.colormap, this.colorMin, this.colorMax
            );
        });
        // Listen for threshold slider change
        $('#thresholdSlider').on('thresholdSliderChange', (event) => {
            const thresholdRange = event.detail.newValue;
            this.thresholdMin = thresholdRange[0];
            this.thresholdMax = thresholdRange[1];
            // Plot brain map with new thresholds
            this.viewer.plot(
                this.timePoint,
                this.colormap,
                this.colorMin,
                this.colorMax,
                this.thresholdMin,
                this.thresholdMax,
                this.hoverTextOn,
                this.preprocState
            );
        });

        // Listen for hover toggle click
        $('#toggle-hover').on('toggleHoverChange', (event) => {
            // if checked
            this.hoverTextOn = !this.hoverTextOn
            // plot with or without hover text
            this.viewer.plot(
                this.timePoint,
                this.colormap,
                this.colorMin,
                this.colorMax,
                this.thresholdMin,
                this.thresholdMax,
                this.hoverTextOn,
                this.preprocState
            );
        });

        // attach nifti specific visualization options
        if (this.plotType == 'nifti') {
            // Listen for crosshair toggle click
            $('#toggle-crosshair').on('toggleCrosshairChange', (event) => {
                // if checked
                this.viewer.crosshairOn = !this.viewer.crosshairOn
                // plot with or without crosshair
                this.viewer.plot(
                    this.timePoint,
                    this.colormap,
                    this.colorMin,
                    this.colorMax,
                    this.thresholdMin,
                    this.thresholdMax,
                    this.hoverTextOn,
                    this.preprocState
                );
            });

            // Listen for hover toggle click
            $('#toggle-direction').on('toggleDirectionMarkerChange', (event) => {
                // if checked
                this.viewer.directionMarkerOn = !this.viewer.directionMarkerOn
                // plot with or without direction marker labels
                this.viewer.plot(
                    this.timePoint,
                    this.colormap,
                    this.colorMin,
                    this.colorMax,
                    this.thresholdMin,
                    this.thresholdMax,
                    this.hoverTextOn,
                    this.preprocState
                );
            });
        }
    }

    // Update plot for changes in time point from the time slider
    listenForTimeSliderChange() {
        $('#time_slider').on('timeSliderChange', (event) => {
            // Access the timeIndex from event.detail and update viewer
            this.timePoint = event.detail.timeIndex;
            // update brain plot and time course plot
            this.viewer.plot(
                this.timePoint,
                this.colormap,
                this.colorMin,
                this.colorMax,
                this.thresholdMin,
                this.thresholdMax,
                this.hoverTextOn,
                this.preprocState
            );
        });
    }

    // Register click handlers that update views based on click
    registerClickHandlers() {
        // bind context to master class for updating brain map on click
        const boundClickCallBack = this.clickHandlerCallBack.bind(this);
        this.viewer.plotlyClickHandler(boundClickCallBack);
    }

    // method passed as callback to viewer click handlers
    clickHandlerCallBack() {
        // only update nifti (due to slice index change)
        if (this.plotType == 'nifti') {
            // Plot the updated data from the server
            this.viewer.plot(
                this.timePoint,
                this.colormap,
                this.colorMin,
                this.colorMax,
                this.thresholdMin,
                this.thresholdMax,
                this.hoverTextOn,
                this.preprocState,
                true, // update coordinate labels (only for nifti)
            )
        }
    }
}

export default Correlate;


