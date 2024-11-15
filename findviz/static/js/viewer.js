// viewer.js
import ColorBar from './colorbar.js';
import TimeCourse from './timecourse.js';
import TimeSlider from './timeslider.js';
import { VisualizationOptions, PreprocessingOptions } from './user.js';
import NiftiViewer from './nifti.js';
import GiftiViewer from './gifti.js';
import Correlate from './correlation.js'

class MainViewer{
    constructor(
        plotData,
        plotType
      ) {
        // Set text in visualization card
        document.getElementById('fmri-visualization-title').textContent = 'FMRI Visualization'
        document.getElementById('time-slider-title').textContent = 'Time Point:'

        // set attributes based on nifti or gifti file input
        if (plotType == 'nifti') {
            // initialize nifti viewer
            this.viewer = new NiftiViewer(
                plotData.file_key,
                plotData.anat_key,
                plotData.mask_key,
                plotData.slice_len
            );
            // set colorbar div
            this.colorbarDiv = 'colorbar_container_nii'
        } else if (plotType == 'gifti') {
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
        this.plotType = plotType;
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
        // Initialize Preprocess state as false
        this.preprocState = false;

        // Initialize TimeSlider class
        this.timeSlider = new TimeSlider(plotData.timepoints);

        // Initialize VisualizationOptions class
        this.visualizationOptions = new VisualizationOptions(
            this.globalMin, this.globalMax, this.plotType,
            this.attachVizOptionListeners
        );

        // Initialize PreprocessingOptions class (pass mask, if nifti)
        let maskKey = null;
        if (plotType == 'nifti') {
            maskKey = plotData.mask_key;
        }
        this.preprocessOptions = new PreprocessingOptions(
            plotType, this.attachPreprocListeners, maskKey
        );

        // Initialize colorbar class
        this.colorBar = new ColorBar(
            this.colorbarDiv, this.globalMin, this.globalMax, 'Intensity'
        );

        // Initialize the TimeCourse class (with input time series, optional)
        if (plotData.timeCourses.ts.length > 0 || plotData.taskConditions !== null) {
            this.timeCourse = new TimeCourse(
                plotData.timepoints.length,
                plotData.timeCourses.ts,
                plotData.timeCourses.tsLabels,
                plotData.taskConditions
            );
        }
        else {
            this.timeCourse = new TimeCourse(plotData.timepoints.length)
        }

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
            // Plot time courses, if any
            this.timeCourse.plotTimeCourses(this.timePoint);
            // Register click handlers
            this.registerClickHandlers();
            // Listen for correlation submit event
            $('#correlationForm').on('correlationSubmit', (event, data) => {
                this.initiateCorrelation(event, data)
            });
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

    // Listeners to pass to PreprocessingOptions class
    attachPreprocListeners = () => {
        // Listen for preprocessing submission
        $('#submit-preprocess').on('preprocessSubmit', (event, data) => {
            // Set preprocess state to true
            this.preprocState = true
            // Start spinner to indicate loading of files
            let spinnerOverlayDiv = document.getElementById(
              'preproc-spinner-overlay'
            )
            spinnerOverlayDiv.style.display = 'block'
            let spinnerDiv = document.getElementById('preproc-load-spinner')
            spinnerDiv.style.display = 'block'
            // fetch preprocessed data
            this.viewer.fetchPreprocessed(
                data.detail,
                this.preprocessOptions.normSwitchEnabled,
                this.preprocessOptions.filterSwitchEnabled,
                this.preprocessOptions.smoothSwitchEnabled,
            ).then(data => {
                // Revised global min and global max
                this.globalMin = data.global_min;
                this.globalMax = data.global_max;
                this.colorMin = data.global_min;
                this.colorMax = data.global_max;
                // reset threshold to zero
                this.thresholdMin = 0;
                this.thresholdMax = 0;

                // Plot colorbar with new data and update color min and max
                this.colorBar.plotColorbar(
                    this.colormap, this.globalMin, this.globalMax
                );
                // modify visualization option sliders
                this.visualizationOptions.modifyVizOptions(
                    this.globalMin, this.globalMax
                )
                // Replot slices with preprocessed data
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

                // turn off spinner
                let spinnerOverlayDiv = document.getElementById(
                    'preproc-spinner-overlay'
                )
                let spinnerDiv = document.getElementById('preproc-load-spinner')
                // end spinner to indicate loading of files
                spinnerOverlayDiv.style.display = 'none'
                spinnerDiv.style.display = 'none'
            })

        });

        // Listen for preprocessing reset
        $('#reset-preprocess-button').on('preprocessReset', () => {
            // set preprocess state to false
            this.preprocState = false;
            // fetch original data
            this.viewer.fetchPreprocessed(null, null, null, null, true)
                .then(data => {
                    // Revised global min and global max
                    this.globalMin = data.global_min;
                    this.globalMax = data.global_max;
                    this.colorMin = data.global_min;
                    this.colorMax = data.global_max;
                    // reset threshold to zero
                    this.thresholdMin = 0;
                    this.thresholdMax = 0;

                    // Plot colorbar with new data and update color min and max
                    this.colorBar.plotColorbar(
                        this.colormap, this.globalMin, this.globalMax
                    );
                    // modify visualization option sliders
                    this.visualizationOptions.modifyVizOptions(
                        this.globalMin, this.globalMax
                    )
                    // Replot slices with preprocessed data
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

                })
        });
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

            // update time course plot
            this.timeCourse.plotTimeCourses(this.timePoint);
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
        // Update time course, if fmri time course plotting enabled
        if (this.timeCourse.fmriEnabled) {
            this.viewer.fetchTimeCourse(this.preprocState)
            .then(({ label, timeCourse }) => {
                // update fmri time course in the TimeCourse class
                this.timeCourse.updatefMRITimeCourse(timeCourse, label);
            });
        }
    }

    // package up input to pass to cross-correlation routes
    initiateCorrelation(event, data) {
        // define error display function
        function raiseError(errorDiv, errorMessage) {
            errorDiv.textContent = errorMessage;
            errorDiv.style.display = 'block';
            // Clear error message after 5 seconds
            setTimeout(function() {
                errorDiv.style.display = 'none';
            }, 5000);
        }
        // get error placeholder
        const errorDiv = document.getElementById(
            'error-message-correlation'
        );
        let errorMessage
        // raise error if mask is not provided for nifti file
        if (!this.viewer.maskKey && this.plotType == 'nifti') {
            errorMessage = 'a brain mask must be supplied (in file upload) to perform correlation analysis';
            raiseError(errorDiv, errorMessage);
            return
        }
        // get lag inputs
        const negativeLag = document.getElementById('correlateNegativeLag').value;
        const positiveLag = document.getElementById('correlatePositiveLag').value;
        // get half of time length for checking lag bounds
        const timeLengthMid = Math.floor(this.timeCourse.timeLength / 2);
        // check lags do not exceed zero
        if (negativeLag > 0) {
            errorMessage = 'negative lag must be less than or equal to zero';
            raiseError(errorDiv, errorMessage);
        }
        if (positiveLag < 0) {
            errorMessage = 'positive lag must be greater than or equal to zero';
            raiseError(errorDiv, errorMessage);
        }
        // check lags do not exceed half of time legnth
        if (negativeLag < -timeLengthMid) {
            errorMessage = `negative lag must not be less than ${timeLengthMid} (half the length of time course) `;
            raiseError(errorDiv, errorMessage);
        }
        if (positiveLag > timeLengthMid) {
            errorMessage = `positive lag must not be greater than ${timeLengthMid} (half the length of time course) `;
            raiseError(errorDiv, errorMessage);
        }
        // initialize form data to pass in POST route
        let formData = new FormData();
        // Add parameters and input to formData
        formData.append('ts', JSON.stringify(data['ts']))
        formData.append('negative_lag', negativeLag);
        formData.append('positive_lag', positiveLag);
        formData.append('label', data['label']);
        formData.append('use_preprocess', this.preprocState);
        let fetchURL
        if (this.plotType == 'nifti') {
            formData.append('file_key', this.viewer.fileKey);
            formData.append('mask_key', this.viewer.maskKey);
            formData.append('anat_key', this.viewer.anatKey);
            fetchURL = '/compute_corr_nii'
        } else if (this.plotType == 'gifti') {
            formData.append('left_key', this.viewer.leftKey);
            formData.append('right_key', this.viewer.rightKey);
            fetchURL = '/compute_corr_gii'
        }
        // initiate spinner
        let spinnerOverlayDiv = document.getElementById(
              'correlate-spinner-overlay'
            )
        spinnerOverlayDiv.style.display = 'block'
        let spinnerDiv = document.getElementById('correlate-spinner')
        spinnerDiv.style.display = 'block'

        fetch(fetchURL, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error in response from server during correlation analysis')
            }
            // open correlation window
            window.open('/correlation', '_blank');
            // turn off spinner
            let spinnerOverlayDiv = document.getElementById(
                'correlate-spinner-overlay'
            )
            let spinnerDiv = document.getElementById('correlate-spinner')
            // end spinner to indicate loading of files
            spinnerOverlayDiv.style.display = 'none'
            spinnerDiv.style.display = 'none'
        }).catch(error => {
            console.error('Error during correlation analysis:', error);
        });
    }

}

export default MainViewer;