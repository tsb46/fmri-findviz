// LinePlotOptions.js - Options for line plot (timecourse plot)
import {initializeSingleSlider } from '../sliders.js';
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { 
    getTaskConditions,
    getTimeCourseLabels
} from '../../api/data.js';
import { 
    getTaskDesignPlotOptions,
    getTimeCoursePlotOptions, 
    getTimeCourseShiftHistory,
    getTimeMarkerPlotOptions,
    resetTimeCourseShift,
    updateTaskDesignPlotOptions,
    updateTimeCoursePlotOptions,
    updateTimeCourseShift,
    updateTimeMarkerPlotOptions,
} from '../../api/plot.js';

class LinePlotOptions {
    /**
     * Constructor for LinePlotOptions
     * @param {string} timeCourseSelectMenuId - ID of the time course select menu
     * @param {string} timeCourseOpacitySliderId - ID of the opacity slider
     * @param {string} timeCourseLineWidthSliderId - ID of the line width slider
     * @param {string} timeCourseScaleIncreaseId - ID of the time course scale increase button
     * @param {string} timeCourseScaleDecreaseId - ID of the time course scale decrease button
     * @param {string} timeCourseScaleResetId - ID of the time course scale reset button
     * @param {string} timeCourseConstantIncreaseId - ID of the time course constant shift increase button
     * @param {string} timeCourseConstantDecreaseId - ID of the time course constant shift decrease button
     * @param {string} timeCourseConstantResetId - ID of the time course constant shift reset button
     * @param {string} timeCourseSelectColorId - ID of the color picker
     * @param {string} timeCourseSelectModeId - ID of the time course select mode (lines, markers, lines+markers)
     * @param {string} timeMarkerWidthSliderId - ID of the time marker width slider
     * @param {string} timeMarkerOpacitySliderId - ID of the time marker opacity slider
     * @param {string} timeMarkerSelectShapeId - ID of the time marker shape select (solid, dashed, dotted)
     * @param {string} timeMarkerSelectColorId - ID of the time marker color picker
     * @param {string} toggleConvolutionId - ID of the toggle convolution checkbox
     */
    constructor(
        timeCourseSelectMenuId,
        timeCourseOpacitySliderId,
        timeCourseLineWidthSliderId,
        timeCourseScaleIncreaseId,
        timeCourseScaleDecreaseId,
        timeCourseScaleResetId,
        timeCourseConstantIncreaseId,
        timeCourseConstantDecreaseId,
        timeCourseConstantResetId,
        timeCourseSelectColorId,
        timeCourseSelectModeId,
        timeMarkerWidthSliderId,
        timeMarkerOpacitySliderId,
        timeMarkerSelectShapeId,
        timeMarkerSelectColorId,
        toggleConvolutionId
    ) {
        // get ids
        this.timeCourseSelectMenuId = timeCourseSelectMenuId;
        this.timeCourseOpacitySliderId = timeCourseOpacitySliderId;
        this.timeCourseLineWidthSliderId = timeCourseLineWidthSliderId;
        this.timeCourseSelectColorId = timeCourseSelectColorId;
        this.timeCourseSelectModeId = timeCourseSelectModeId;
        this.timeCourseConstantIncreaseId = timeCourseConstantIncreaseId;
        this.timeCourseConstantDecreaseId = timeCourseConstantDecreaseId;
        this.timeCourseConstantResetId = timeCourseConstantResetId;
        this.timeCourseScaleIncreaseId = timeCourseScaleIncreaseId;
        this.timeCourseScaleDecreaseId = timeCourseScaleDecreaseId;
        this.timeCourseScaleResetId = timeCourseScaleResetId;
        this.timeMarkerWidthSliderId = timeMarkerWidthSliderId;
        this.timeMarkerOpacitySliderId = timeMarkerOpacitySliderId;
        this.timeMarkerSelectColorId = timeMarkerSelectColorId;
        this.timeMarkerSelectShapeId = timeMarkerSelectShapeId;
        this.toggleConvolutionId = toggleConvolutionId;

        // get div elements
        this.timeCourseSelectMenu = $(`#${timeCourseSelectMenuId}`);
        this.timeCourseOpacitySlider = $(`#${timeCourseOpacitySliderId}`);
        this.timeCourseLineWidthSlider = $(`#${timeCourseLineWidthSliderId}`);
        this.timeCourseConstantIncrease = $(`#${timeCourseConstantIncreaseId}`);
        this.timeCourseConstantDecrease = $(`#${timeCourseConstantDecreaseId}`);
        this.timeCourseConstantReset = $(`#${timeCourseConstantResetId}`);
        this.timeCourseScaleIncrease = $(`#${timeCourseScaleIncreaseId}`);
        this.timeCourseScaleDecrease = $(`#${timeCourseScaleDecreaseId}`);
        this.timeCourseScaleReset = $(`#${timeCourseScaleResetId}`);
        this.timeCourseSelectColor = $(`#${timeCourseSelectColorId}`);
        this.timeCourseSelectMode = $(`#${timeCourseSelectModeId}`);
        this.timeMarkerWidthSlider = $(`#${timeMarkerWidthSliderId}`);
        this.timeMarkerOpacitySlider = $(`#${timeMarkerOpacitySliderId}`);
        this.timeMarkerSelectColor = $(`#${timeMarkerSelectColorId}`);
        this.timeMarkerSelectShape = $(`#${timeMarkerSelectShapeId}`);
        this.toggleConvolution = $(`#${toggleConvolutionId}`);

        // set state variables
        this.timeMarkerPlotState = true;
        this.selectedTimeCourse = null;
        this.timeCourseType = {}
        

        // get time course and task labels and initialize components
        this.getPlotLabels((labels) => {
            // if no labels, initialize sliders with default values
            if (labels.length === 0) {
                this.initializePlotSliders(1, 2);
                return;
            }
            // initialize time course select menu
            this.initializeTimeCourseSelectMenu(labels, true);
            // initialize plot components for the first time course
            this.initializeLinePlotComponents(this.selectedTimeCourse);
            // modify the shift reset buttons for the time course
            this.modifyShiftResetButtons();
        });
         // initialize time marker plot components
         this.initializeTimeMarkerPlotComponents();

        
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
        this.timeCourseScaleIncrease.on(
            'click', this.handleTimeCourseShiftListener.bind(this, 'scale', 'increase')
        );
        this.timeCourseScaleDecrease.on(
            'click', this.handleTimeCourseShiftListener.bind(this, 'scale', 'decrease')
        );
        this.timeCourseConstantIncrease.on(
            'click', this.handleTimeCourseShiftListener.bind(this, 'constant', 'increase')
        );
        this.timeCourseConstantDecrease.on(
            'click', this.handleTimeCourseShiftListener.bind(this, 'constant', 'decrease')
        );
        this.timeCourseConstantReset.on(
            'click', this.handleTimeCourseShiftResetListener.bind(this, 'constant', true)
        );
        this.timeCourseScaleReset.on(
            'click', this.handleTimeCourseShiftResetListener.bind(this, 'scale', true)
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
        // attach listener for fmri time course added or removed from plot
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE
            ],
            this.handleFmriTimecourseChangeListener.bind(this)
        );
        // attach listener for preprocess and reset of timecourse
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_SUCCESS,
                EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_RESET,
            ],
            // modify shift reset buttons
            this.modifyShiftResetButtons.bind(this)
        );
        // attach listener for global convolution toggle
        eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION_GLOBAL,
            this.changeLinePlotComponents.bind(this)
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
        await getTimeCourseLabels((ts_labels) => {
            for (const label of ts_labels) {
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
     * Changes the line plot components for the selected time course
     */
    changeLinePlotComponents() {
        if (this.timeCourseType[this.selectedTimeCourse] === 'task') {
            getTaskDesignPlotOptions(this.selectedTimeCourse, (plotOptions) => {
                this.timeCourseOpacitySlider.slider('setValue', plotOptions.opacity);
                this.timeCourseLineWidthSlider.slider('setValue', plotOptions.width);
                this.timeCourseSelectColor.val(plotOptions.color);
                this.timeCourseSelectMode.val(plotOptions.mode);
                this.toggleConvolution.prop('disabled', false);
                if (plotOptions.convolution === 'hrf') {
                    this.toggleConvolution.prop('checked', true);
                } else {
                    this.toggleConvolution.prop('checked', false);
                }
            });
        } else {
            getTimeCoursePlotOptions(this.selectedTimeCourse, (plotOptions) => {
                this.timeCourseOpacitySlider.slider('setValue', plotOptions.opacity);
                this.timeCourseLineWidthSlider.slider('setValue', plotOptions.width);
                this.timeCourseSelectColor.val(plotOptions.color);
                this.timeCourseSelectMode.val(plotOptions.mode);
                this.toggleConvolution.prop('disabled', true);
            });
        }
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
                // initialize convolution checkbox
                this.toggleConvolution.prop('disabled', false);
                if (plotOptions.convolution === 'hrf') {
                    this.toggleConvolution.prop('checked', true);
                } else {
                    this.toggleConvolution.prop('checked', false);
                }
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
                // initialize convolution checkbox
                this.toggleConvolution.prop('disabled', true);
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
        // initialize opacity slider
        initializeSingleSlider(
            this.timeCourseOpacitySliderId, 
            timeCourseOpacityValue,
            [0, 1],
            0.01
        );
        // initialize line width slider
        initializeSingleSlider(
            this.timeCourseLineWidthSliderId, 
            timeCourseLineWidthValue,
            [0.5, 10],
            0.1
        );
    }

    /**
     * Initializes the time course select menu
     * @param {Array} labels - The labels for the time course
     */
    initializeTimeCourseSelectMenu(labels) {
        this.timeCourseSelectMenu.empty();
        for (const label of labels) {
            this.timeCourseSelectMenu.append(
                `<option value="${label}">${label}</option>`
            );
        }
        // select the last label as the selected time course
        this.timeCourseSelectMenu.val(labels[labels.length - 1]);
        this.selectedTimeCourse = labels[labels.length - 1];
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
            this.timeMarkerWidthSliderId, 
            timeMarkerWidthValue, 
            [0.5, 10], 
            0.1
        );
        initializeSingleSlider(
            this.timeMarkerOpacitySliderId, 
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
            // set selected time course to the last label - this is 
            // the most recent fmri time course
            this.selectedTimeCourse = labels[labels.length - 1];
            this.initializeTimeCourseSelectMenu(labels, false);
            this.changeLinePlotComponents();
            // modify the shift reset buttons for the time course
            this.modifyShiftResetButtons();
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
                { label: this.selectedTimeCourse, color: this.timeCourseSelectColor.val() },
                callback
            );
        } else {
            updateTimeCoursePlotOptions(
                this.selectedTimeCourse,
                { label: this.selectedTimeCourse, color: this.timeCourseSelectColor.val() },
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
     * @param {string} changeType - The type of change (constant or scale)
     * @param {string} changeDirection - The direction of the change (increase or decrease)
     */
    handleTimeCourseShiftListener(changeType, changeDirection) {
        console.log(`${changeDirection} of ${changeType} for ${this.selectedTimeCourse}`);
        updateTimeCourseShift(
            this.selectedTimeCourse,
            this.timeCourseType[this.selectedTimeCourse],
            changeType,
            changeDirection,
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_SHIFT_CHANGE,
                    { 
                        label: this.selectedTimeCourse, 
                        changeType: changeType, 
                        changeDirection: changeDirection 
                    }
                );
                // modify the shift reset buttons for the time course
                this.modifyShiftResetButtons();
            }
        );
    }

    /**
     * Handles the time course shift reset listener
     * @param {string} timeCourse - The time course to reset the shift for
     * @param {string} changeType - The type of shift to reset (constant or scale)
     * @param {boolean} emitEvent - Whether to emit the shift reset event
     */
    handleTimeCourseShiftResetListener(changeType, emitEvent=true) {
        console.log(`Resetting ${changeType} shift for ${this.selectedTimeCourse}`);
        resetTimeCourseShift(
            this.selectedTimeCourse, 
            this.timeCourseType[this.selectedTimeCourse], 
            changeType,
            () => {
                if (emitEvent) {
                    eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_SHIFT_RESET,
                        { label: this.selectedTimeCourse, changeType: changeType }
                    );
                }
                // modify the shift reset buttons for the time course
                this.modifyShiftResetButtons();
            }
        )
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
        this.changeLinePlotComponents();
        this.modifyShiftResetButtons();
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
                        { label: this.selectedTimeCourse, mode: this.timeCourseSelectMode.val() }
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
                        { label: this.selectedTimeCourse, mode: this.timeCourseSelectMode.val() }
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
        console.log('toggleConvolution change - only for task design input');
        const convChecked = this.toggleConvolution.prop('checked');
        let convolution = null;
        if (convChecked) {
            convolution = 'hrf';
        } else {
            convolution = 'block';
        }
        updateTaskDesignPlotOptions(
            this.selectedTimeCourse,
            { convolution: convolution },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION,
                    { label: this.selectedTimeCourse, convolution: convolution }
                );
            }
        );
    }

    /**
     * Modifies the shift reset buttons for the time course(s)
     */
    modifyShiftResetButtons() {
        // get the shift history for the time course and enable/disable the reset buttons
        getTimeCourseShiftHistory(
            this.selectedTimeCourse, 
            this.timeCourseType[this.selectedTimeCourse], 
            (shiftHistory) => {
                if (shiftHistory.constant.length > 0) {
                    this.timeCourseConstantReset.prop('disabled', false);
                } else {
                    this.timeCourseConstantReset.prop('disabled', true);
                }
                if (shiftHistory.scale.length > 0) {
                    this.timeCourseScaleReset.prop('disabled', false);
                } else {
                    this.timeCourseScaleReset.prop('disabled', true);
                }
            }
        );
    }
}

export default LinePlotOptions;
