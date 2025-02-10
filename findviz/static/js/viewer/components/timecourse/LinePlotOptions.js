// LinePlotOptions.js - Options for line plot (timecourse plot)
import {initializeSingleSlider } from '../sliders';
import { EVENT_TYPES } from '../../constants/EventTypes';
import eventBus from '../../events/ViewerEvents';
import { 
    getTaskConditions,
    getTimeCourseLabels
} from '../../api/data';
import { 
    getTaskDesignPlotOptions,
    getTimeCoursePlotOptions, 
    getTimeMarkerPlotOptions,
    updateTaskDesignPlotOptions,
    updateTimeCoursePlotOptions,
    updateTimeMarkerPlotOptions,
    updateTimeCourseScale
} from '../../api/plot';

class LinePlotOptions {
    /**
     * Constructor for LinePlotOptions
     * @param {string} timeCourseSelectMenuId - ID of the time course select menu
     * @param {string} timeCourseOpacitySliderId - ID of the opacity slider
     * @param {string} timeCourseLineWidthSliderId - ID of the line width slider
     * @param {string} timeCourseSelectColorId - ID of the color picker
     * @param {string} timeCourseSelectModeId - ID of the time course select mode (lines, markers, lines+markers)
     * @param {string} timeMarkerWidthSliderId - ID of the time marker width slider
     * @param {string} timeMarkerOpacitySliderId - ID of the time marker opacity slider
     * @param {string} timeMarkerSelectShapeId - ID of the time marker shape select (solid, dashed, dotted)
     * @param {string} timeMarkerSelectColorId - ID of the time marker color picker
     * @param {string} toggleConvolutionId - ID of the toggle convolution checkbox
     * @param {string} taskIncreaseScaleId - ID of the task increase scale button
     * @param {string} taskDecreaseScaleId - ID of the task decrease scale button
     * @param {number} taskScaleChangeUnit - The unit of change for the task plot scale change
     */
    constructor(
        timeCourseSelectMenuId,
        timeCourseOpacitySliderId,
        timeCourseLineWidthSliderId,
        timeCourseSelectColorId,
        timeCourseSelectModeId,
        timeMarkerWidthSliderId,
        timeMarkerOpacitySliderId,
        timeMarkerSelectColorId,
        toggleConvolutionId,
        scaleIncreaseId,
        scaleDecreaseId,
    ) {
        // get div elements
        this.timeCourseSelectMenu = $(`#${timeCourseSelectMenuId}`);
        this.timeCourseOpacitySlider = $(`#${timeCourseOpacitySliderId}`);
        this.timeCourseLineWidthSlider = $(`#${timeCourseLineWidthSliderId}`);
        this.timeCourseSelectColor = $(`#${timeCourseSelectColorId}`);
        this.timeCourseSelectMode = $(`#${timeCourseSelectModeId}`);
        this.timeMarkerWidthSlider = $(`#${timeMarkerWidthSliderId}`);
        this.timeMarkerOpacitySlider = $(`#${timeMarkerOpacitySliderId}`);
        this.timeMarkerSelectColor = $(`#${timeMarkerSelectColorId}`);
        this.timeMarkerSelectShape = $(`#${timeMarkerSelectShapeId}`);
        this.toggleConvolution = $(`#${toggleConvolutionId}`);
        this.scaleIncrease = $(`#${scaleIncreaseId}`);
        this.scaleDecrease = $(`#${scaleDecreaseId}`);

        // set state variables
        this.timeMarkerPlotState = true;
        this.selectedTimeCourse = null;
        this.timeCourseType = {}
        

        // get time course and task labels and initialize components
        this.getPlotLabels((labels) => {
            this.initializeTimeCourseSelectMenu(labels, true);
            // initialize plot components for the first time course
            this.initializeLinePlotComponents(this.selectedTimeCourse);
            // initialize time marker plot components
            this.initializeTimeMarkerPlotComponents();
        });

        // attach listeners
        this.attachListeners();
    }

    /**
     * Attaches listeners to the time course(s) and time marker
     */
    attachListeners() {
        // attach listeners to the time course(s)
        this.timeCourseSelectColor.on(
            'change', this.handleTimeCourseColorChangeListener.bind(this)
        );
        this.timeCourseLineWidthSlider.on(
            'change', this.handleTimeCourseLineWidthSliderChangeListener.bind(this)
        );
        this.timeCourseOpacitySlider.on(
            'change', this.handleTimeCourseOpacitySliderChangeListener.bind(this)
        );
        this.timeCourseSelectMenu.on(
            'change', this.handleTimeCourseSelectMenuChangeListener.bind(this)
        );
        this.timeCourseSelectMode.on(
            'change', this.handleTimeCourseSelectModeChangeListener.bind(this)
        );
        // attach listeners to the time marker
        this.timeMarkerSelectColor.on(
            'change', this.handleTimeMarkerColorChangeListener.bind(this)
        );
        this.timeMarkerSelectShape.on(
            'change', this.handleTimeMarkerShapeChangeListener.bind(this)
        );
        this.timeMarkerOpacitySlider.on(
            'change', this.handleTimeMarkerOpacitySliderChangeListener.bind(this)
        );
        this.timeMarkerWidthSlider.on(
            'change', this.handleTimeMarkerWidthSliderChangeListener.bind(this)
        );
        // toggle convolution of task design listener
        this.toggleConvolution.on(
            'click', this.handleToggleConvolutionChangeListener.bind(this)
        );

        // attach listeners to the scale change buttons
        this.scaleIncrease.on(
            'click', this.handleTimeCourseScaleChangeListener.bind(this, 'increase')
        );
        this.scaleDecrease.on(
            'click', this.handleTimeCourseScaleChangeListener.bind(this, 'decrease')
        );

        // attache listener for fmri time course added or removed from plot
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE
            ],
            this.handleFmriTimecourseChangeListener.bind(this)
        );
    }

    /**
     * Get plot labels from all time courses and/or tasks
     * @param {Function} callback - Callback function to handle successful response
     * @returns {Array} labels - The labels for the time courses and/or tasks
     */
    async getPlotLabels(callback=null) {
        // clear time course types object
        this.timeCourseType = {};
        const labels = [];
        await getTaskConditions((conditions) => {
            for (const condition of conditions) {
                this.timeCourseType[condition] = 'task';
                labels.push(condition);
            }
        });
        await getTimeCourseLabels((labels) => {
            for (const label of labels) {
                this.timeCourseType[label] = 'timecourse';
                labels.push(label);
            }
        });
        if (callback) {
            callback(labels);
        }
        return labels;
    }
   
    /**
     * Initializes the components for a given time course
     * @param {string} timeCourse - The time course to initialize components for
     */
    initializeLinePlotComponents(timeCourse) {
        // Initialize task plot options
        if (this.timeCourseType[timeCourse] === 'task') {
            getTaskDesignPlotOptions(timeCourse, (plotOptions) => {
                this.initializePlotSliders(
                    plotOptions.opacity,
                    plotOptions.width
                );
                // initialize time course color select
                this.timeCourseSelectColor.val(plotOptions.color);
                // initialize time course mode select
                this.timeCourseSelectMode.val(plotOptions.mode);
            });
        } else {
            // Initialize time course plot options
            getTimeCoursePlotOptions(timeCourse, (plotOptions) => {
                this.initializePlotSliders(
                    plotOptions.opacity,
                    plotOptions.width
                );
                // initialize time course color select
                this.timeCourseSelectColor.val(plotOptions.color);
                // initialize time course mode select
                this.timeCourseSelectMode.val(plotOptions.mode);
            });
        }

    }

    /**
     * Initialize time marker plot components
     */
    initializeTimeMarkerPlotComponents() {
        // Initialize time marker plot options
        getTimeMarkerPlotOptions((plotOptions) => {
            this.initializeTimeMarkerPlotSliders(
                plotOptions.width,
                plotOptions.opacity
            );
            // initialize time marker color select
            this.timeMarkerSelectColor.val(plotOptions.color);
            // initialize time marker shape select
            this.timeMarkerSelectShape.val(plotOptions.shape);
        });
    }

    /**
     * Initializes the plot options sliders for the time course(s) and/or task(s)
     * @param {number} timeCourseOpacityValue - Opacity value for the time course
     * @param {number} timeCourseLineWidthValue - Line width value for the time course
     */
    initializePlotSliders(
        timeCourseOpacityValue,
        timeCourseLineWidthValue
    ) {
        console.log('initializeTimeCoursePlotSliders');
        initializeSingleSlider(
            this.timeCourseOpacitySlider, 
            timeCourseOpacityValue,
            [0, 1],
            0.01
        );
        initializeSingleSlider(
            this.timeCourseLineWidthSlider, 
            timeCourseLineWidthValue,
            [0.5, 10],
            0.1
        );
    }

    /**
     * Initializes the time course select menu
     * @param {Array} labels - The labels for the time course
     * @param {boolean} firstInit - Whether this is the first initialization
     */
    initializeTimeCourseSelectMenu(labels, firstInit = false) {
        this.timeCourseSelectMenu.empty();
        for (const label of labels) {
            this.timeCourseSelectMenu.append(
                `<option value="${label}">${label}</option>`
            );
        }
        // if first initialization, select the first label as the selected time course
        if (firstInit) {
            this.timeCourseSelectMenu.val(labels[0]);
            this.selectedTimeCourse = labels[0];
        }
    }


    /**
     * Initializes the plot options sliders for the time marker
     * @param {number} timeMarkerWidthValue - Width value for the time marker
     * @param {number} timeMarkerOpacityValue - Opacity value for the time marker
     */
    initializeTimeMarkerPlotSliders(
        timeMarkerWidthValue,
        timeMarkerOpacityValue,
    ) {
        console.log('initializeTimeMarkerPlotSliders');
        initializeSingleSlider(
            this.timeMarkerWidthSlider, 
            timeMarkerWidthValue, 
            [0.5, 10], 
            0.1
        );
        initializeSingleSlider(
            this.timeMarkerOpacitySlider, 
            timeMarkerOpacityValue, 
            [0, 1], 
            0.01
        );
    }

    /**
     * Handles the fmri time course added to plot listener
     */
    handleFmriTimecourseChangeListener() {
        // if time course is added to the plot, update time course select menu
        this.getPlotLabels((labels) => {
            this.initializeTimeCourseSelectMenu(labels, false);
            this.initializeLinePlotComponents(this.selectedTimeCourse);
        });
        
    }


    /**
     * Handles the color change listener for the time course(s) and time marker
     */
    handleTimeCourseColorChangeListener() {
        console.log('timeCourseSelectColor change');
        const callback = () => {
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_COLOR_CHANGE,
                { label: this.selectedTimeCourse, color: this.timeCourseSelectColor.val() }
            );
        };
        if (this.timeCourseType[this.selectedTimeCourse] === 'task') {
            updateTaskDesignPlotOptions(
                this.selectedTimeCourse,
                { color: this.timeCourseSelectColor.val() },
                callback
            );
        } else {
            updateTimeCoursePlotOptions(
                this.selectedTimeCourse,
                { color: this.timeCourseSelectColor.val() },
                callback
            );
        }
        
    }

    /**
     * Handles the line width slider change listener for the time course(s)
     */
    handleTimeCourseLineWidthSliderChangeListener() {
        console.log('timeCourseLineWidthSlider change');
        const callback = () => {
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_LINE_WIDTH_SLIDER_CHANGE,
                { label: this.selectedTimeCourse, width: this.timeCourseLineWidthSlider.val() }
            );
        };
        if (this.timeCourseType[this.selectedTimeCourse] === 'task') {
            updateTaskDesignPlotOptions(
                this.selectedTimeCourse,
                { width: this.timeCourseLineWidthSlider.val() },
                callback
            );
        } else {
            updateTimeCoursePlotOptions(
                this.selectedTimeCourse,
                { width: this.timeCourseLineWidthSlider.val() },
                callback
            );
        }
    }

        /**
     * Handles task plot scale change
     * @param {string} changeType - The type of change (increase or decrease)
     */
        handleTimeCourseScaleChangeListener(changeType) {
            updateTimeCourseScale(
               this.selectedTimeCourse,
               this.timeCourseType[this.selectedTimeCourse],
               changeType,
               () => {
                   eventBus.publish(
                       EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_SCALE_CHANGE,
                       { label: this.selectedTimeCourse, changeType: changeType }
                   );
               }
           );
       }

    /**
     * Handles the opacity slider change listener for the time course(s)
     */
    handleTimeCourseOpacitySliderChangeListener() {
        console.log('timeCourseOpacitySlider change');
        const callback = () => {
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_OPACITY_SLIDER_CHANGE,
                { label: this.selectedTimeCourse, opacity: this.timeCourseOpacitySlider.val() }
            );
        };
        if (this.timeCourseType[this.selectedTimeCourse] === 'task') {
            updateTaskDesignPlotOptions(
                this.selectedTimeCourse,
                { opacity: this.timeCourseOpacitySlider.val() },
                callback
            );
        } else {
            updateTimeCoursePlotOptions(
                this.selectedTimeCourse,
                { opacity: this.timeCourseOpacitySlider.val() },
                callback
            );
        }
    }

    /**
     * Handles the time course select menu change listener
     */
    handleTimeCourseSelectMenuChangeListener() {
        console.log('timeCourseSelectMenu change');
        this.selectedTimeCourse = this.timeCourseSelectMenu.val();
        this.initializeLinePlotComponents(this.selectedTimeCourse);
    }

    /**
     * Handles the time course mode change listener
     */
    handleTimeCourseSelectModeChangeListener() {
        console.log('timeCourseSelectMode change');
        if (this.timeCourseType[this.selectedTimeCourse] === 'task') {
            updateTaskDesignPlotOptions(
                this.selectedTimeCourse,
                { mode: this.timeCourseSelectMode.val() },
                () => {
                    eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_MODE_CHANGE,
                        { mode: this.timeCourseSelectMode.val() }
                    );
                }
            );
        } else {
            updateTimeCoursePlotOptions(
                this.selectedTimeCourse,
                { mode: this.timeCourseSelectMode.val() },
                () => {
                    eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_MODE_CHANGE,
                        { mode: this.timeCourseSelectMode.val() }
                    );
                }
            );
        }
    }

    /**
     * Handles the color change listener for the time marker
     */
    handleTimeMarkerColorChangeListener() {
        console.log('timeMarkerSelectColor change');
        updateTimeMarkerPlotOptions(
            { color: this.timeMarkerSelectColor.val() },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_COLOR_CHANGE,
                    { color: this.timeMarkerSelectColor.val() }
                );
            }
        );
    }

    /**
     * Handles the shape change listener for the time marker
     */
    handleTimeMarkerShapeChangeListener() {
        console.log('timeMarkerSelectShape change');
        updateTimeMarkerPlotOptions(
            { shape: this.timeMarkerSelectShape.val() },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_SHAPE_CHANGE,
                    { shape: this.timeMarkerSelectShape.val() }
                );
            }
        );
    }

    /**
     * Handles the opacity slider change listener for the time marker
     */
    handleTimeMarkerOpacitySliderChangeListener() {
        console.log('timeMarkerOpacitySlider change');
        updateTimeMarkerPlotOptions(
            { opacity: this.timeMarkerOpacitySlider.val() },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_OPACITY_SLIDER_CHANGE,
                    { opacity: this.timeMarkerOpacitySlider.val() }
                );
            }
        );
    }

    /**
     * Handles the width slider change listener for the time marker
     */
    handleTimeMarkerWidthSliderChangeListener() {
        console.log('timeMarkerWidthSlider change');
        updateTimeMarkerPlotOptions(
            { width: this.timeMarkerWidthSlider.val() },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_WIDTH_SLIDER_CHANGE,
                    { width: this.timeMarkerWidthSlider.val() }
                );
            }
        );
    }

    /**
     * Handles the toggle convolution change listener
     */
    handleToggleConvolutionChangeListener() {
        console.log('toggleConvolution change');
        updateTaskDesignPlotOptions(
            { convolution: this.toggleConvolution.val() },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION,
                    { convolution: this.toggleConvolution.val() }
                );
            }
        );
    }
}

export default LinePlotOptions;
