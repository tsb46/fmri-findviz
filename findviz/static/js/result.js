// correlation.js
import ColorBar from './colorbar.js';
import Distance from './distance.js';
import TimeSlider from './timeslider.js';
import { VisualizationOptions } from './user.js';
import NiftiViewer from './nifti.js';
import GiftiViewer from './gifti.js';

class Result {
    constructor(
      plotData,
      plotTitle
    ) {
        // Set text in visualization card
        document.getElementById('time-slider-title').textContent = plotTitle['timeSliderTitle'];
        // set attributes based on nifti or gifti file input
        if (plotData.plot_type == 'nifti') {
            // handle null string of anat
            let anatKey
            if (plotData.anat_key == 'null') {
                anatKey = null;
            } else {
                anatKey = plotData.anat_key;
            }
            // initialize nifti viewer
            this.viewer = new NiftiViewer(
                plotData.file_key,
                anatKey,
                plotData.mask_key,
                plotData.slice_len
            );
            // set colorbar div
            this.colorbarDiv = 'colorbar_container_nii'
        } else if (plotData.plot_type == 'gifti') {
            // handle null string of left or right key
            let leftKey
            if (plotData.left_key == 'null') {
                leftKey = null;
            } else {
                leftKey = plotData.left_key;
            }
            let rightKey
            if (plotData.right_key == 'null') {
                rightKey = null;
            } else {
                rightKey = plotData.right_key;
            }
            // initialize gifti viewer
            this.viewer = new GiftiViewer(
                leftKey,
                rightKey,
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
        // Initialize color opacity
        this.opacity = 1;
        // Initialize hover text state
        this.hoverTextOn = true;
        // Initialize Preprocess state as false (not used, just for consistency with API)
        this.preprocState = false;

        // Initialize TimeSlider class
        this.timeSlider = new TimeSlider(
            plotData.timepoints,
            `${plotTitle['timeSliderTitle']} `
        );

        // Initialize VisualizationOptions class
        // pass slice length if nifti
        if (this.plotType == 'nifti') {
            this.sliceLen = plotData.slice_len
        } else {
            this.sliceLen = null
        }
        // Initialize VisualizationOptions class
        this.visualizationOptions = new VisualizationOptions(
            this.globalMin, this.globalMax, this.plotType,
            this.sliceLen, this.attachVizOptionListeners
        );

        // Initialize colorbar class
        this.colorBar = new ColorBar(
            this.colorbarDiv, this.globalMin, this.globalMax, 'Correlation'
        );

        // initialize distance class - not used
        this.distance = new Distance(false);

        // disable 'enable time course' switch
        $('#enable-time-course').prop('disabled', true);

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
            this.opacity,
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
                this.opacity,
                this.hoverTextOn,
                this.preprocState,
                false, // do not update coordinates
                true // update layout only
            );
            // Update colorbar
            this.colorBar.plotColorbar(this.colormap)

        };
        document.addEventListener(
            'colormapChange',  this.colormapChangeListener
        );
        // Listen for color range slider change
        $(document).on('colorSliderChange', (event) => {
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
                  this.opacity,
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
        $(document).on('thresholdSliderChange', (event) => {
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
                this.opacity,
                this.hoverTextOn,
                this.preprocState
            );
        });
        // Listen for opacity slider change
        $(document).on('opacitySliderChange', (event) => {
            const opacityValue = event.detail.newValue;
            this.opacity = opacityValue;
            // Plot brain map with new thresholds
            this.viewer.plot(
                this.timePoint,
                this.colormap,
                this.colorMin,
                this.colorMax,
                this.thresholdMin,
                this.thresholdMax,
                this.opacity,
                this.hoverTextOn,
                this.preprocState
            );
        });

        // Listen for hover toggle click
        $(document).on('toggleHoverChange', (event) => {
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
                this.opacity,
                this.hoverTextOn,
                this.preprocState
            );
        });

        // attach nifti specific visualization options
        if (this.plotType == 'nifti') {
            // Listen for view toggle click
            $(document).on('toggleViewChange', (event) => {
                // Change view state (ortho <-> montage)
                this.viewer.changeViewState(
                    true,
                    event.detail.sliceDirection,
                    event.detail.sliceIndices,
                )
                // plot with new view
                this.viewer.plot(
                    this.timePoint,
                    this.colormap,
                    this.colorMin,
                    this.colorMax,
                    this.thresholdMin,
                    this.thresholdMax,
                    this.opacity,
                    this.hoverTextOn,
                    this.preprocState
                );
            });

            // Listen for change to montage direction
            $(document).on('montageSliceDirectionChange', (event) => {
                // Change view state (ortho <-> montage)
                this.viewer.changeViewState(
                    false,
                    event.detail.sliceDirection,
                    event.detail.sliceIndices,
                )
                if (this.viewer.viewerState == 'montage') {
                    // plot with new view
                    this.viewer.plot(
                        this.timePoint,
                        this.colormap,
                        this.colorMin,
                        this.colorMax,
                        this.thresholdMin,
                        this.thresholdMax,
                        this.opacity,
                        this.hoverTextOn,
                        this.preprocState
                    );
                };
            });

            // Listen for change to slice indices for montage for each slice
            const sliceSliders = ['slice1Slider', 'slice2Slider', 'slice3Slider'];
            sliceSliders.forEach((sliceDiv, index) => {
                $(document).on(`${sliceDiv}Change`, (event) => {
                    // Change view state (ortho <-> montage)
                    this.viewer.changeViewState(
                        false,
                        event.detail.sliceDirection,
                        event.detail.sliceIndices
                    );
                    if (this.viewer.viewerState == 'montage') {
                        // plot with new view
                        this.viewer.plot(
                            this.timePoint,
                            this.colormap,
                            this.colorMin,
                            this.colorMax,
                            this.thresholdMin,
                            this.thresholdMax,
                            this.opacity,
                            this.hoverTextOn,
                            this.preprocState
                        );
                    };
                });
            });

            // Listen for crosshair toggle click
            $(document).on('toggleCrosshairChange', (event) => {
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
                    this.opacity,
                    this.hoverTextOn,
                    this.preprocState
                );
            });

            // Listen for hover toggle click
            $(document).on('toggleDirectionMarkerChange', (event) => {
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
                    this.opacity,
                    this.hoverTextOn,
                    this.preprocState
                );
            });
        }
    }

    // Update plot for changes in time point from the time slider
    listenForTimeSliderChange() {
        $(document).on('timeSliderChange', (event) => {
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
                this.opacity,
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
                this.opacity,
                this.hoverTextOn,
                this.preprocState,
                true, // update coordinate labels (only for nifti)
            )
        }
    }
}

export default Result;


