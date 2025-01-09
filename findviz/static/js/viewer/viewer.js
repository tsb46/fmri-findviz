// viewer.js
import { FILE_TYPES, DOM_IDS, CONTAINER_IDS, DEFAULTS, API_ENDPOINTS } from './constants.js';
import { EVENT_TYPES } from './EventTypes.js';
import { Types } from './types.js';
import ColorBar from './colorbar.js';
import Distance from '../analytics/distance.js';
import TimeCourse from './timecourse.js';
import TimeSlider from './timeslider.js';
import { VisualizationOptions, PreprocessingOptions } from './user.js';
import NiftiViewer from './nifti.js';
import GiftiViewer from './gifti.js';

/**
 * @typedef {import('./types.js').ViewerData} ViewerData
 * @typedef {import('./types.js').VisualizationParams} VisualizationParams
 * @typedef {import('./types.js').TimeCourseData} TimeCourseData
 */


/**
 * MainViewer class handles the primary visualization logic for neuroimaging data
 * @class
 */
class MainViewer{
    /**
     * Creates a new MainViewer instance
     * @param {ViewerData} viewerData - Data object containing visualization parameters and file information
     * @throws {Error} If viewerData format is invalid
     */
    constructor(
        viewerData
      ) {
        if (!Types.isViewerData(viewerData)) {
            throw new Error('Invalid viewer data format');
        }
        // Set file type and common properties
        /** @type {string} Type of plot ('nifti' or 'gifti') */
        this.plotType = viewerData.file_type;
        
        /** @type {number[]} Array of timepoint indices */
        this.timepoints = viewerData.timepoints;
        
        /** @type {number} Global minimum value across dataset */
        this.globalMin = viewerData.global_min;
        
        /** @type {number} Global maximum value across dataset */
        this.globalMax = viewerData.global_max;
        
        /** @type {boolean} Whether timeseries visualization is enabled */
        this.tsEnabled = viewerData.ts_enabled;
        
        /** @type {boolean} Whether task design visualization is enabled */
        this.taskEnabled = viewerData.task_enabled;

        // set title of time slider
        document.getElementById(DOM_IDS.TIME_SLIDER_TITLE).textContent = 'Time Point:';

        this.initializeViewer(viewerData);
        this.initializeVisualizationParams();
        this.initializeComponents(viewerData);
        
        // Set up fmri time course event listeners
        this.timeCourseListeners();
    }

    /**
     * Initializes all viewer components (TimeSlider, VisualizationOptions, etc.)
     * @private
     * @param {ViewerData} viewerData - Data for component initialization
     */
    initializeComponents(viewerData) {
        /** @type {TimeSlider} Time slider component */
        this.timeSlider = new TimeSlider(
            this.timepoints,
            'Time Point: '
        );

        /** @type {VisualizationOptions} Visualization options component */
        this.visualizationOptions = new VisualizationOptions(
            this.globalMin,
            this.globalMax,
            this.plotType,
            this.sliceLen,
            this.attachVizOptionListeners
        );

        /** @type {PreprocessingOptions} Preprocessing options component */
        this.preprocessOptions = new PreprocessingOptions(
            this.plotType,
            this.attachPreprocListeners,
            viewerData.mask_input
        );

         /** @type {ColorBar} Color bar component */
         this.colorBar = new ColorBar(
            this.colorbarDiv,
            this.globalMin,
            this.globalMax,
            'Intensity'
        );

        // initialize time course
        this.initializeTimeCourse(viewerData);

        /** @type {Distance} Distance computation component */
        this.distance = new Distance(true, this.timeSlider.sliderElement);
    }

    /**
     * Initializes the initial plot and sets up event listeners
     * @public
     * @returns {Promise<void>}
     */
    initializePlot() {
        // change DOM elements of upload after successful upload
        this.afterUpload();
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
            if (this.plotType === FILE_TYPES.NIFTI) {
                this.viewer.onWindowResize();
            }
            // Plot colorbar
            this.colorBar.plotColorbar(this.colormap);
            // set listener for time slider change
            this.listenForTimeSliderChange();
            // Plot time courses, if any
            this.timeCourse.plotTimeCourses(this.timePoint);
            // Register click handlers
            this.registerClickHandlers();
            // Listen for distance computation submit event
            // Listen for correlation submit event
            $(document).on(EVENT_TYPES.ANALYSIS.DISTANCE, (event) => {
                this.initiateDistanceCompute(event)
            });
            // Listen for correlation submit event
            $(document).on(EVENT_TYPES.ANALYSIS.CORRELATION, (event, data) => {
                this.initiateCorrelation(event, data)
            });
            // Listen for window average submit event
            $(document).on(EVENT_TYPES.ANALYSIS.AVERAGE, (event, data) => {
                this.initiateAverage(event, data)
            });
        }).catch(error => {
            console.error('Error during initialization:', error);
        });
    }

    /**
     * Initializes time course visualization
     * @private
     * @param {ViewerData} viewerData - Viewer data containing time course information
     */
    initializeTimeCourse(viewerData) {
        /** @type {TimeCourseData} */
        const timeCourseData = {
            timeseries: viewerData.ts,
            labels: viewerData.ts_labels,
            task: viewerData.task
        };

        /** @type {TimeCourse} Time course visualization component */
        this.timeCourse = new TimeCourse(
            this.timepoints.length,
            timeCourseData.timeseries,
            timeCourseData.labels,
            timeCourseData.task,
            this.timeSlider.sliderElement
        );
    }

    /**
     * Initializes visualization parameters with default values
     * @private
     */
    initializeVisualizationParams() {
        /** @type {VisualizationParams} */
        const params = {
            colormap: DEFAULTS.COLORMAP,
            timePoint: DEFAULTS.TIME_POINT,
            colorMin: this.globalMin,
            colorMax: this.globalMax,
            thresholdMin: DEFAULTS.THRESHOLD.MIN,
            thresholdMax: DEFAULTS.THRESHOLD.MAX,
            opacity: DEFAULTS.OPACITY,
            hoverTextOn: true
        };

        Object.assign(this, params);
    }

    /**
     * Initializes the appropriate viewer based on file type
     * @private
     * @param {ViewerData} viewerData - Viewer initialization data
     */
    initializeViewer(viewerData) {
        if (this.plotType === FILE_TYPES.NIFTI) {
            /** @type {NiftiViewer} NIFTI-specific viewer instance */
            this.viewer = new NiftiViewer(
                viewerData.anat_input,
                viewerData.mask_input,
                viewerData.slice_len
            );
            this.colorbarDiv = CONTAINER_IDS.COLORBAR.NIFTI;
        } else if (this.plotType === FILE_TYPES.GIFTI) {
            /** @type {GiftiViewer} GIFTI-specific viewer instance */
            this.viewer = new GiftiViewer(
                viewerData.left_input,
                viewerData.right_input,
                viewerData.vertices_left,
                viewerData.faces_left,
                viewerData.vertices_right,
                viewerData.faces_right
            );
            this.colorbarDiv = CONTAINER_IDS.COLORBAR.GIFTI;
        }
    }

   /**
     * Handles post-upload initialization tasks
     * @private
     * @returns {void}
     */
    afterUpload(){
        const uploadButton = document.getElementById(DOM_IDS.UPLOAD_BUTTON)
        // Change button color
        uploadButton.classList.add('btn-secondary');
        uploadButton.classList.remove('btn-primary');
        // Change button text to reupload file
        uploadButton.innerHTML = 'Reupload Files'
        // Set listener to refresh page when user clicks reupload files
        uploadButton.addEventListener("click", () => {
            // clear cache
            window.location.href = API_ENDPOINTS.CLEAR_CACHE;
            location.reload()
        });
        // set saveScene button to display
        const saveSceneDisplay = document.getElementById(DOM_IDS.SAVE_SCENE);
        saveSceneDisplay.style.display = 'block';
    }

    /**
     * Attaches visualization option event listeners
     * @private
     * @returns {Promise<void>}
     */
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
            EVENT_TYPES.VISUALIZATION.COLOR_MAP_CHANGE,  this.colormapChangeListener
        );
        // Listen for color range slider change
        $(document).on(EVENT_TYPES.VISUALIZATION.COLOR_SLIDER_CHANGE, (event) => {
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
        $(document).on(EVENT_TYPES.VISUALIZATION.THRESHOLD_SLIDER_CHANGE, (event) => {
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
        $(document).on(EVENT_TYPES.VISUALIZATION.OPACITY_SLIDER_CHANGE, (event) => {
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
        $(document).on(EVENT_TYPES.VISUALIZATION.HOVER_TEXT_TOGGLE, (event) => {
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
            $(document).on(EVENT_TYPES.VISUALIZATION.VIEW_TOGGLE, (event) => {
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
            $(document).on(EVENT_TYPES.VISUALIZATION.MONTAGE_SLICE_DIRECTION_CHANGE, (event) => {
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
                $(document).on(EVENT_TYPES.VISUALIZATION.SLICE_SLIDER[sliceDiv], (event) => {
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
            $(document).on(EVENT_TYPES.VISUALIZATION.TOGGLE_CROSSHAIR, (event) => {
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
            $(document).on(EVENT_TYPES.VISUALIZATION.TOGGLE_DIRECTION_MARKER, (event) => {
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

    /**
     * Attaches preprocessing option event listeners
     * @private
     * @returns {Promise<void>}
     */
    attachPreprocListeners = () => {
        // Listen for preprocessing submission
        $(document).on(EVENT_TYPES.PREPROCESSING.PREPROCESS_SUBMIT, (event, data) => {
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
                    this.opacity,
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
        $(document).on(EVENT_TYPES.PREPROCESSING.PREPROCESS_RESET, () => {
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
                        this.opacity,
                        this.hoverTextOn,
                        this.preprocState
                    );

                })
        });
    }

    /**
     * Sets up time slider change event listener
     * @private
     * @returns {void}
     */    
    listenForTimeSliderChange() {
        $(document).on(EVENT_TYPES.VISUALIZATION.TIME_SLIDER_CHANGE, (event) => {
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

            // update time course plot
            this.timeCourse.plotTimeCourses(this.timePoint);
        });
    }

    /**
     * Sets up time course related event listeners
     * @private
     * @returns {void}
     */
    timeCourseListeners() {
        // Initialize the button to enable/disable time course plotting
        const enableSwitch = document.getElementById(DOM_IDS.ENABLE_TIME_COURSE);
        const freezeButton = document.getElementById(DOM_IDS.FREEZE_TIME_COURSE);
        const undoButton = document.getElementById(DOM_IDS.UNDO_TIME_COURSE);
        const removeButton = document.getElementById(DOM_IDS.REMOVE_TIME_COURSE);

        // enable fmri time course plotting
        enableSwitch.addEventListener('click', () => {
            this.timeCourseEnabled = !this.timeCourseEnabled;
            // If there is no user input time courses, hide the time point container
            if (!this.timeCourse.userInput) {
                this.timeCourse.timeCourseContainer.style.visibility = this.timeCourseEnabled ? 'visible' : 'hidden';
            }

            // enable time course buttons
            if (this.timeCourseEnabled) {
                freezeButton.disabled = false;
                undoButton.disabled = false;
                removeButton.disabled = false;
            } else {
                freezeButton.disabled = true;
                undoButton.disabled = true;
                removeButton.disabled = true;
            }
        });

        // freeze fmri time course
        freezeButton.on('click', () => {
            this.timeCourseFreeze = this.timeCourseFreeze ? false : true;
            // get icon
            const timeCourseFreezeIcon = document.getElementById(DOM_IDS.FREEZE_ICON);
            // change icon based on time course freeze state
            if (this.timeCourseFreeze) {
                timeCourseFreezeIcon.removeClass('fa-unlock').addClass('fa-lock');
            } else {
                timeCourseFreezeIcon.removeClass('fa-lock').addClass('fa-unlock');
            }

        });

        // remove most recently added fmri time course
        undoButton.on('click', () => {
            this.timeCourse.removefMRITimeCourse();
            // plot time courses
            this.timeCourse.plotTimeCourses(this.timePoint);
        })

        // remove all fmri time courses
        removeButton.on('click', () => {
            this.timeCourse.removefMRITimeCourse(true);
            // plot time courses
            this.timeCourse.plotTimeCourses(this.timePoint);
        })

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
        if (this.plotType == FILE_TYPES.NIFTI) {
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
        // Update time course, if fmri time course plotting enabled
        if (this.timeCourseEnabled) {
            this.viewer.fetchTimeCourse(this.preprocState)
            .then(({ label, timeCourse }) => {
                // update fmri time course in the TimeCourse class
                this.timeCourse.updatefMRITimeCourse(timeCourse, label, this.timeCourseFreeze);
            });
        }
    }

    /**
     * Initiates distance computation between time courses
     * @param {Event} event - Form submission event
     * @returns {Promise<void>}
     */
    initiateDistanceCompute(event) {
        // get error placeholder
        const errorDiv = document.getElementById(
            DOM_IDS.ERROR_MESSAGES.DISTANCE
        );
        let errorMessage
        // raise error if mask is not provided for nifti file
        if (!this.viewer.maskKey && this.plotType == 'nifti') {
            errorMessage = 'a brain mask must be supplied (in file upload) to calculate time point distance';
            this.raiseError(errorDiv, errorMessage);
            return
        }

        // initialize form data to pass in POST route
        let formData = new FormData();
        // Add parameters and input to formData
        formData.append('dist_metric', event.detail.distMetric);
        formData.append('time_point', event.detail.timeIndex);
        formData.append('use_preprocess', this.preprocState);
        let fetchURL
        if (this.plotType == FILE_TYPES.NIFTI) {
            formData.append('file_key', this.viewer.fileKey);
            formData.append('mask_key', this.viewer.maskKey);
            fetchURL = API_ENDPOINTS.COMPUTE.DISTANCE_NIFTI
        } else if (this.plotType == FILE_TYPES.GIFTI) {
            formData.append('left_key', this.viewer.leftKey);
            formData.append('right_key', this.viewer.rightKey);
            fetchURL = API_ENDPOINTS.COMPUTE.DISTANCE_GIFTI
        }
        // initiate spinner
        let spinnerOverlayDiv = document.getElementById(
            CONSTANTS.SPINNERS.DISTANCE_OVERLAY
        )
        spinnerOverlayDiv.style.display = 'block'
        let spinnerDiv = document.getElementById(
            CONSTANTS.SPINNERS.DISTANCE_OVERLAY
        )
        spinnerDiv.style.display = 'block'

        fetch(fetchURL, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // plot time distance vector
            this.distance.plotDistance(data.dist_vec, data.time_point);
            // turn off spinner
            let spinnerOverlayDiv = document.getElementById(
                CONSTANTS.SPINNERS.DISTANCE_OVERLAY
            )
            let spinnerDiv = document.getElementById(
                CONSTANTS.SPINNERS.DISTANCE
            )
            // end spinner to indicate loading of files
            spinnerOverlayDiv.style.display = 'none'
            spinnerDiv.style.display = 'none'
            // close modal
            $(`#${DOM_IDS.MODALS.DISTANCE}`).modal('hide');
        }).catch(error => {
            console.error('Error during time point distance analysis:', error);
        });

    }

    /**
     * Initiates average analysis
     * @param {Event} event - Form submission event
     * @param {Object} data - Average analysis parameters
     * @returns {Promise<void>}
     */
    initiateAverage(event, data) {
        // get error placeholder
        const errorDiv = document.getElementById(
            DOM_IDS.ERROR_MESSAGES.AVERAGE
        );
        let errorMessage
        // raise error if mask is not provided for nifti file
        if (!this.viewer.maskKey && this.plotType == FILE_TYPES.NIFTI) {
            errorMessage = 'a brain mask must be supplied (in file upload) to perform windowed average analysis';
            this.raiseError(errorDiv, errorMessage);
            return
        }
        // get lag inputs
        const leftEdge = document.getElementById(DOM_IDS.AVERAGE_LEFT_EDGE).value;
        const rightEdge = document.getElementById(DOM_IDS.AVERAGE_RIGHT_EDGE).value;
        // get half of time length for checking lag bounds
        const timeLengthMid = Math.floor(this.timeCourse.timeLength / 2);
        // check lags do not exceed zero
        if (leftEdge > 0) {
            errorMessage = 'left edge must be less than or equal to zero';
            this.raiseError(errorDiv, errorMessage);
        }
        if (rightEdge < 0) {
            errorMessage = 'right edge must be greater than or equal to zero';
            this.raiseError(errorDiv, errorMessage);
        }
        // check lags do not exceed half of time legnth
        if (leftEdge < -timeLengthMid) {
            errorMessage = `left edge must not be less than ${timeLengthMid} (half the length of time course) `;
            this.raiseError(errorDiv, errorMessage);
        }
        if (rightEdge > timeLengthMid) {
            errorMessage = `right edge must not be greater than ${timeLengthMid} (half the length of time course) `;
            this.raiseError(errorDiv, errorMessage);
        }
        // initialize form data to pass in POST route
        let formData = new FormData();
        // Add parameters and input to formData
        formData.append('markers', JSON.stringify(data['markers']))
        formData.append('left_edge', leftEdge);
        formData.append('right_edge', rightEdge);
        formData.append('use_preprocess', this.preprocState);
        let fetchURL
        if (this.plotType == FILE_TYPES.NIFTI) {
            formData.append('file_key', this.viewer.fileKey);
            formData.append('mask_key', this.viewer.maskKey);
            formData.append('anat_key', this.viewer.anatKey);
            formData.append('slice_len', this.sliceLen);
            fetchURL = API_ENDPOINTS.COMPUTE.AVERAGE_NIFTI
        } else if (this.plotType == FILE_TYPES.GIFTI) {
            formData.append('left_key', this.viewer.leftKey);
            formData.append('right_key', this.viewer.rightKey);
            fetchURL = API_ENDPOINTS.COMPUTE.AVERAGE_GIFTI
        }
        // initiate spinner
        let spinnerOverlayDiv = document.getElementById(
            CONSTANTS.SPINNERS.AVERAGE_OVERLAY
        )
        spinnerOverlayDiv.style.display = 'block'
        let spinnerDiv = document.getElementById(CONSTANTS.SPINNERS.AVERAGE)
        spinnerDiv.style.display = 'block'

        fetch(fetchURL, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error in response from server during window average analysis')
            }
            // open average results window
            window.open('/results_view/average', '_blank');
            // turn off spinner
            let spinnerOverlayDiv = document.getElementById(
                CONSTANTS.SPINNERS.AVERAGE_OVERLAY
            )
            let spinnerDiv = document.getElementById(
                CONSTANTS.SPINNERS.AVERAGE
            )
            // end spinner to indicate loading of files
            spinnerOverlayDiv.style.display = 'none'
            spinnerDiv.style.display = 'none'
            // close modal
            $(`#${DOM_IDS.MODALS.AVERAGE}`).modal('hide');
        }).catch(error => {
            console.error('Error during window average analysis:', error);
        });
    }


    /**
     * Initiates correlation analysis
     * @param {Event} event - Form submission event
     * @param {Object} data - Correlation parameters
     * @returns {Promise<void>}
     */
    initiateCorrelation(event, data) {
        // get error placeholder
        const errorDiv = document.getElementById(
            DOM_IDS.ERROR_MESSAGES.CORRELATION
        );
        let errorMessage
        // raise error if mask is not provided for nifti file
        if (!this.viewer.maskKey && this.plotType == FILE_TYPES.NIFTI) {
            errorMessage = 'a brain mask must be supplied (in file upload) to perform correlation analysis';
            this.raiseError(errorDiv, errorMessage);
            return
        }
        // get lag inputs
        const negativeLag = document.getElementById(DOM_IDS.CORRELATION_LAGS.NEGATIVE).value;
        const positiveLag = document.getElementById(DOM_IDS.CORRELATION_LAGS.POSITIVE).value;
        // get half of time length for checking lag bounds
        const timeLengthMid = Math.floor(this.timeCourse.timeLength / 2);
        // check lags do not exceed zero
        if (negativeLag > 0) {
            errorMessage = 'negative lag must be less than or equal to zero';
            this.raiseError(errorDiv, errorMessage);
        }
        if (positiveLag < 0) {
            errorMessage = 'positive lag must be greater than or equal to zero';
            this.raiseError(errorDiv, errorMessage);
        }
        // check lags do not exceed half of time legnth
        if (negativeLag < -timeLengthMid) {
            errorMessage = `negative lag must not be less than ${timeLengthMid} (half the length of time course) `;
            this.raiseError(errorDiv, errorMessage);
        }
        if (positiveLag > timeLengthMid) {
            errorMessage = `positive lag must not be greater than ${timeLengthMid} (half the length of time course) `;
            this.raiseError(errorDiv, errorMessage);
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
        if (this.plotType == FILE_TYPES.NIFTI) {
            formData.append('file_key', this.viewer.fileKey);
            formData.append('mask_key', this.viewer.maskKey);
            formData.append('anat_key', this.viewer.anatKey);
            fetchURL = API_ENDPOINTS.COMPUTE.CORRELATION_NIFTI
        } else if (this.plotType == FILE_TYPES.GIFTI) {
            formData.append('left_key', this.viewer.leftKey);
            formData.append('right_key', this.viewer.rightKey);
            fetchURL = API_ENDPOINTS.COMPUTE.CORRELATION_GIFTI
        }
        // initiate spinner
        let spinnerOverlayDiv = document.getElementById(
            CONSTANTS.SPINNERS.CORRELATE_OVERLAY
        )
        spinnerOverlayDiv.style.display = 'block'
        let spinnerDiv = document.getElementById(
            CONSTANTS.SPINNERS.CORRELATE
        )
        spinnerDiv.style.display = 'block'

        fetch(fetchURL, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error in response from server during correlation analysis')
            }
            // open correlation results window
            window.open('/results_view/correlate', '_blank');
            // turn off spinner
            let spinnerOverlayDiv = document.getElementById(
                CONSTANTS.SPINNERS.CORRELATE_OVERLAY
            )
            let spinnerDiv = document.getElementById(
                CONSTANTS.SPINNERS.CORRELATE
            )
            // end spinner to indicate loading of files
            spinnerOverlayDiv.style.display = 'none'
            spinnerDiv.style.display = 'none'
            // close modal
            $(`#${DOM_IDS.MODALS.CORRELATION}`).modal('hide');
        }).catch(error => {
            console.error('Error during correlation analysis:', error);
        });
    }

    // utility function to temporarily display error message
    raiseError(errorDiv, errorMessage) {
        errorDiv.textContent = errorMessage;
        errorDiv.style.display = 'block';
        // Clear error message after 5 seconds
        setTimeout(function() {
            errorDiv.style.display = 'none';
        }, 5000);
    }

}

export default MainViewer;