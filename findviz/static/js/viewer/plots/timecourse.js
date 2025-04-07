// Timecourse plot
// Handles all plotting and click events for time course visualization
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import TraceManager from './TraceManager.js';
import ContextManager from '../api/ContextManager.js';


class TimeCourse {
    /**
     * Constructor for TimeCourse
     * @param {string} timeCourseContainerId - The ID of the parent time course container
     * @param {string} timeCoursePlotContainerId - The ID of the time course plot container
     * @param {boolean} timeCourseInput - Whether the time course input is provided
     * @param {boolean} taskDesignInput - Whether the task design input is provided
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        timeCourseContainerId,
        timeCoursePlotContainerId,
        timeCourseInput,
        taskDesignInput,
        eventBus,
        contextManager,
        yAxisPadding=0.05
    ) {
        this.timeCourseContainerId = timeCourseContainerId;
        this.timeCourseContainer = $(`#${timeCourseContainerId}`);
        this.timeCoursePlotContainerId = timeCoursePlotContainerId;
        this.timeCoursePlotContainer = $(`#${timeCoursePlotContainerId}`);
        this.timeCourseInput = timeCourseInput;
        this.taskDesignInput = taskDesignInput;
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        this.yAxisPadding = yAxisPadding;
        // initialize empty plot with default layout
        this.initEmptyPlot();

        // display time course container
        this.displayContainer();

        // set state variables
        this.setStateVariables();

        // attach event listeners
        this.attachEventListeners();

        // Initialize TraceManager with startIndex of 1 to account for dummy data
        this.traceManager = new TraceManager({ startIndex: 1 });

        // initialize shapes
        this.annotationShapes = [];
        this.timeMarkerShape = null;

    }

    attachEventListeners() {
        // listen for enable/disable fmri time course events
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.ENABLE_FMRI_TIMECOURSE, (state) => {
                console.log('enabling fmri time course plotting');
                this.timeCourseEnabled = state;
                // state is true and no user input, make time course container visible
                if (state && !this.userInput) {
                    console.log('making time course container visible');
                    this.timeCourseContainer.css("visibility", "visible");
                // state is false and no user input, make time course container hidden
                } else if (!state && !this.userInput) {
                    console.log('making time course container hidden');
                    this.timeCourseContainer.css("visibility", "hidden");
                }
            }
        );

        // listen for freeze/unfreeze fmri time course events
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.FREEZE_FMRI_TIMECOURSE, (state) => {
                this.timeCourseFreeze = state;
                console.log('freezing fmri time course');
            }
        );

        // listen for time slider change event - replot time marker
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, (timePoint) => {
                console.log('replotting time marker');
                const timeLabel = this.timePoints[timePoint];
                this.plotTimeMarker(timeLabel);
            }
        );

        // listen for time point conversion event
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.TR_CONVERT_BUTTON_CLICK, 
            async (conversionState) => {
                console.log('replotting time course due to time point conversion');
                // get timepoints
                const timePointsResponse = await this.contextManager.data.getTimePoints();
                this.timePoints = timePointsResponse.timepoints;
                // replot all time courses with new x-axis (pass null to get all time courses)
                const timeCourseData = await this.contextManager.data.getTimeCourseData(null);
                for (const ts_label of Object.keys(timeCourseData)) {
                    this.updateTimeCourseData(ts_label, timeCourseData);
                }
                // update x-axis range
                this.updateXAxisRange(this.timePoints[this.timePoints.length - 1]);
                // replot time marker
                const timePoint = await this.contextManager.data.getTimePoint();
                const timeLabel = this.timePoints[timePoint.timepoint];
                this.plotTimeMarker(timeLabel);
            }
        );

        // listen for plotly click events on Nifti or GiftiViewer
        // if fmri time course enabled, add functional timecourse and plot
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_TIMECOURSE_UPDATE, 
                EVENT_TYPES.VISUALIZATION.FMRI.GIFTIVIEWER_CLICK
            ], async () => {  
                // if fmri time course enabled, update functional timecourse
                if (this.timeCourseEnabled) {
                    console.log('updating functional timecourse on plotly click');
                    // if previous selection was frozen, update functional timecourse
                    if (this.timeCourseFreeze) {
                        console.log('adding functional timecourse due to freeze');
                        await this.contextManager.data.updateFmriTimeCourse();
                        // get time course data and plot
                        const timeCourseData = await this.contextManager.data.getLastTimecourse();
                        const plotOptions = await this.getPlotOptions();
                        this.plotTimeCourseData(timeCourseData, plotOptions);
                        // publish event that fmri time course has been added
                        this.eventBus.publish(
                            EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE
                        );
                    } else {
                        // if previous selection was not frozen, remove most recent 
                        // fmri timecourse and replace with current selection
                        console.log('removing most recent fmri timecourse and replacing with current selection');
                        const lastFmriLabel = await this.contextManager.data.popFmriTimeCourse();
                        // remove most recent fmri timecourse from plot
                        if (lastFmriLabel.label !== null) {
                            this.removeTimeCourse(lastFmriLabel.label);
                        }
                        // add currently selected voxel fmri timecourse to plot
                        await this.contextManager.data.updateFmriTimeCourse();
                        // get time course data and plot
                        const timeCourseData = await this.contextManager.data.getLastTimecourse();
                        const plotOptions = await this.getPlotOptions();
                        this.plotTimeCourseData(timeCourseData, plotOptions);
                        // publish event that fmri time course has been added
                        this.eventBus.publish(
                            EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE
                        );
                    }
                    // update axis range
                    const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                    this.updateYAxisRange(timeCourseGlobalPlotOptions);
                }
            }
        );

        // listen for undo fmri time course event
        // remove most recent fmri timecourse and replot
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE,
            async (label) => {
                console.log('removing most recently added fmri timecourse');
                // remove most recent fmri timecourse from plot
                if (label !== null) {
                    this.removeTimeCourse(label);
                }
                // update axis range
                const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                this.updateYAxisRange(timeCourseGlobalPlotOptions);
            }
        );

        // listen for remove all fmri time course event
        // remove all fmri timecourses and replot
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE,
            async (labels) => {
                console.log('removing all fmri timecourses');
                // reverse labels to remove in reverse order
                labels.reverse();
                // remove fmri timecourses from plot
                if (labels.length > 0) {
                    for (const label of labels) {
                        this.removeTimeCourse(label);
                    }
                }
                // update axis range
                const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                this.updateYAxisRange(timeCourseGlobalPlotOptions);
            }
        );

        // listen for time course visualization change events
        // update time course plot properties (color, mode, width, visibility, opacity)
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_COLOR_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_MODE_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_OPACITY_SLIDER_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_LINE_WIDTH_SLIDER_CHANGE,
            ], async (label) => {
                console.log('updating time course property for label', label);
                const ts_label = label.label;
                const plotOptions = await this.getPlotOptions();
                this.updateTimeCourseProperty(
                    ts_label, 
                    plotOptions[ts_label].mode, 
                    plotOptions[ts_label].color, 
                    plotOptions[ts_label].width, 
                    plotOptions[ts_label].visibility, 
                    plotOptions[ts_label].opacity
                );
            }
        );

        // listen for time course scale or constant shift slider change event
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_SHIFT_CHANGE, 
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_SHIFT_RESET
            ], 
            async (shiftParams) => {
                console.log(
                    're-plotting time course due to scale or constant shift for', shiftParams.label
                );
                // get time course data and plot
                const timeCourseData = await this.contextManager.data.getTimeCourseData([shiftParams.label]);
                this.updateTimeCourseData(shiftParams.label, timeCourseData);
                // update axis range
                const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                this.updateYAxisRange(timeCourseGlobalPlotOptions);
            }
        );

        // listen for local convolution toggle event
        // update time course data and plot
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION,
            async (label) => {
                console.log('replotting task design plot due to convolution toggle for label', label);
                // get time course data and plot
                const timeCourseData = await this.contextManager.data.getTimeCourseData([label.label]);
                this.updateTimeCourseData(label.label, timeCourseData);
                // update axis range
                const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                this.updateYAxisRange(timeCourseGlobalPlotOptions);
            }
        );

        // Listen for global convolution toggle event
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION_GLOBAL,
            async () => {
                console.log('replotting time course due to global convolution toggle');
                // get time course data and plot
                const taskConditions = await this.contextManager.data.getTaskConditions();
                const timeCourseData = await this.contextManager.data.getTimeCourseData(taskConditions);
                for (const ts_label of taskConditions) {
                    this.updateTimeCourseData(ts_label, timeCourseData);
                }
                // update axis range
                const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                this.updateYAxisRange(timeCourseGlobalPlotOptions);
            }
        );

        // listen for time course global plot options change events
        // update time marker plot properties (color, width, shape, opacity)
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_COLOR_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_WIDTH_SLIDER_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_SHAPE_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_OPACITY_SLIDER_CHANGE
            ], async () => {
                console.log('updating time marker property');
                const timeMarkerPlotOptions = await this.contextManager.plot.getTimeMarkerPlotOptions();
                const timePoint = await this.contextManager.data.getTimePoint();
                const timeLabel = this.timePoints[timePoint.timepoint];
                this.plotTimeMarker(timeLabel, timeMarkerPlotOptions);
            }
        );

        // listen for time marker visibility toggle event
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_VISIBILITY_TOGGLE, 
            async (state) => {
                if (state) {
                    console.log('plotting time marker');
                    const timeMarkerPlotOptions = await this.contextManager.plot.getTimeMarkerPlotOptions();
                    const timePoint = await this.contextManager.data.getTimePoint();
                    const timeLabel = this.timePoints[timePoint.timepoint];
                    this.plotTimeMarker(timeLabel, timeMarkerPlotOptions);
                } else {
                    console.log('hiding time marker');
                    this.timeMarkerShape = null;
                    this.updateShapes();
                }
            }
        );

        // listen for hover text toggle event
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.HOVER_TEXT_TOGGLE, (state) => {
                if (state) {
                    console.log('plotting hover text');
                    this.plotHoverText();
                } else {
                    console.log('removing hover text');
                    this.removeHoverText();
                }
            }
        );

        // listen for grid lines toggle event
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.GRID_TOGGLE, async (state) => {
                const globalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                if (state) {
                    console.log('plotting grid lines');
                    this.plotGridLines(
                        globalPlotOptions.global_min,
                        globalPlotOptions.global_max
                    );
                } else {
                    console.log('removing grid lines');
                    this.removeGridLines(
                        globalPlotOptions.global_min,
                        globalPlotOptions.global_max
                    );
                }
            }
        );

        // listen for annotation marker change events
        // update time course data and plot
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_ADDED,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_MOVED,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_REMOVED,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_UNDONE,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_HIGHLIGHT_TOGGLE,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_COLOR_CHANGE,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_WIDTH_CHANGE,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_OPACITY_CHANGE,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_SHAPE_CHANGE
            ], async () => {
                console.log('replotting time course due to annotation marker change');
                // get annnotation markers and plot
                const annotationData = await this.contextManager.plot.getAnnotationMarkers();
                // if no annotation markers, change highlight to false
                if (annotationData.markers.length === 0) {
                    annotationData.plot_options.highlight = false;
                }
                this.plotAnnotationMarkers(
                    annotationData.markers, 
                    annotationData.selection,
                    annotationData.plot_options
                );
            }
        );

        // listen for preprocess time course event
        this.eventBus.subscribe(
            EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_SUCCESS, 
            async (selectedTimeCourses) => {
                console.log('replotting time course due to preprocess time course');
                // replace raw time courses with preprocessed time courses
                for (const ts_label of selectedTimeCourses) {
                    this.removeTimeCourse(ts_label);
                }
                // get time course data and plot
                const timeCourseData = await this.contextManager.data.getTimeCourseData(selectedTimeCourses);
                const plotOptions = await this.getPlotOptions();
                this.plotTimeCourseData(timeCourseData, plotOptions);
                // update axis range
                const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                this.updateYAxisRange(timeCourseGlobalPlotOptions);
            }
        );

        // listen for reset fmri preprocessing event
        this.eventBus.subscribe(
            EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_RESET, 
            async (preprocessedLabels) => {
                console.log('replotting time course due to reset fmri preprocessing');
                // replace preprocessed time courses with raw time courses
                for (const ts_label of preprocessedLabels) {
                    this.removeTimeCourse(ts_label);
                }
                // get time course data and plot
                const timeCourseData = await this.contextManager.data.getTimeCourseData(preprocessedLabels);
                const plotOptions = await this.getPlotOptions();
                this.plotTimeCourseData(timeCourseData, plotOptions);
                // update axis range
                const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
                this.updateYAxisRange(timeCourseGlobalPlotOptions);
            }
        );
    }

    /**
     * Create layout for time course plot
     */
    createLayout(globalPlotOptions) {
        // create layout
        const layout = {
            height: 500,
            xaxis: {
                title: 'Time Point',
                range: [0, this.timePoints.length - 1],
                autorange: true
            },
            yaxis: {
                title: 'Signal Intensity',
                range: [
                    globalPlotOptions.global_min - this.yAxisPadding, 
                    globalPlotOptions.global_max + this.yAxisPadding
                ],
                autorange: true
            },
            uirevision: true,
            autosize: true,  // Enable autosizing
            responsive: true, // Make the plot responsive
            margin: {
                l: 50,  // left margin
                r: 30,  // right margin
                t: 40,  // top margin
                b: 40   // bottom margin
            },
            // always show legend, even with one trace
            showlegend: true,
            // Place legend at bottom of the plot
            legend: {
                xanchor: 'center',     // Centers the legend horizontally
                x: 0.5,                // Centers it in the middle (x: 50%)
                yanchor: 'top',        // Anchors the legend to the top of its container
                y: -0.25                // Places the legend below the plot (-0.1 moves it just below the plot)
            }
        };
        return layout;
    }

    async initPlot() {
        // get whether fmri timecourse is plotted
        const tsFmriPlotted = await this.contextManager.plot.getTSFmriPlotted();
        // if time course or task design input, plot time course
        if (this.timeCourseInput || this.taskDesignInput || tsFmriPlotted.ts_fmri_plotted) {
            console.log('plotting time course with user-provided input');
            // get plot options
            const plotOptions = await this.getPlotOptions();
            // get timecourse data - pass null to get all timecourse data
            const timeCourseData = await this.contextManager.data.getTimeCourseData(null);
            this.plotTimeCourseData(timeCourseData, plotOptions);
        }
    }

    async displayContainer() {
        // Show time course container if time course or task design input is provided
        if (this.timeCourseInput || this.taskDesignInput) {
            this.timeCourseContainer.css("visibility", "visible");
            // create flag for whether user input time courses are present
            this.userInput = true;
        } else {
            const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
            if (plotOptions.fmri_timecourse_enabled) {
                this.timeCourseContainer.css("visibility", "visible");
                this.userInput = true;
            } else {
                this.timeCourseContainer.css("visibility", "hidden");
                this.userInput = false;
            }
        }
    }

    /**
     * Initialize empty time course plot
     */
    async initEmptyPlot() {
        try {
            console.log('initializing empty time course plot');
            // get timepoints
            const timePointsResponse = await this.contextManager.data.getTimePoints();
            this.timePoints = timePointsResponse.timepoints;
            // get time marker and global plot options
            const timeMarkerPlotOptions = await this.contextManager.plot.getTimeMarkerPlotOptions();
            const timeCourseGlobalPlotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
            // combine all plot options into one object
            const globalPlotOptions = {
            ...timeMarkerPlotOptions,
            ...timeCourseGlobalPlotOptions
            };
            // create layout
            const layout = this.createLayout(globalPlotOptions);

            // Create dummy data to force axis range and plot time marker
            const dummyData = [{
                x: this.timePoints,
                y: [timeCourseGlobalPlotOptions.global_min, timeCourseGlobalPlotOptions.global_max],
                type: 'scatter',
                mode: 'lines',
                line: { width: 0 },  // Make line invisible
                opacity: 0,          // Make fully transparent
                showlegend: false,   // Hide from legend
                hoverinfo: 'none'    // Disable hover effects
            }];
            // create plot
            Plotly.react(this.timeCoursePlotContainerId, dummyData, layout);

            // emit event to indicate initialization of plot is complete
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.TIMECOURSE.INIT_TIMECOURSE_PLOT);

            // if grid lines on, plot grid lines
            if (globalPlotOptions.grid_on) {
                this.plotGridLines(
                    timeCourseGlobalPlotOptions.global_min,
                    timeCourseGlobalPlotOptions.global_max
                );
            }

            // get time point marker and plot
            if (globalPlotOptions.time_marker_on) {
                const timePoint = await this.contextManager.data.getTimePoint();
                const timeLabel = this.timePoints[timePoint.timepoint];
                this.plotTimeMarker(timeLabel, timeMarkerPlotOptions);
            }

            // get annnotation markers and plot
            const annotationData = await this.contextManager.plot.getAnnotationMarkers();
            // if no annotation markers, don't plot
            if (annotationData.markers.length > 0) {
                this.plotAnnotationMarkers(
                    annotationData.markers, 
                    annotationData.selection,
                    annotationData.highlight
                );
            }

        } catch (error) {
            console.error('Error initializing empty time course plot', error);
        }
    }

    // get plot options from task and timecourse plot options
    async getPlotOptions() {
        // get time course plot options - pass null to get plot options for all time courses
        const timeCoursePlotOptions = await this.contextManager.plot.getTimeCoursePlotOptions(null);
        // get task design plot options - pass null to get plot options for all tasks
        const taskDesignPlotOptions = await this.contextManager.plot.getTaskDesignPlotOptions(null);
        // combine task and time course plot options into one object
        const plotOptions = {
            ...timeCoursePlotOptions,
            ...taskDesignPlotOptions
        };
        return plotOptions;
    }

    /**
     * Hide time marker
     */
    hideTimeMarker() {
        this.timeMarkerShape = null;
        this.updateShapes();
    }

    /**
     * Plot annotation markers
     * @param {Array} markers - The annotation markers
     * @param {Array} selection - The annotation selection
     * @param {Object} plotOptions - The annotation plot options
     */
    plotAnnotationMarkers(markers, selection, plotOptions) {
        // create a vertical line at each annotation marker
        this.annotationShapes = markers.map(marker => ({
            type: 'line',
            x0: marker,
            y0: 0,
            x1: marker,
            y1: 1,
            yref: 'paper',
            opacity: plotOptions.opacity,
            line: {
                color: plotOptions.color,
                width: plotOptions.width,
                dash: plotOptions.shape 
            },
        }));

        // if highlight, highlight currently selected annotation marker
        if (plotOptions.highlight) {
            this.annotationShapes.push(
                {
                    type: 'line',
                    x0: selection,
                    y0: 0,
                    x1: selection,
                    y1: 1,
                    yref: 'paper',
                    opacity: 0.2,
                    line: {
                        color: 'gray',
                        width: 7
                    },
                }
            )
        }
        // combined shapes and update plot
        this.updateShapes();
    }

    /**
     * Plot grid lines on X- and Y-axis
     * @param {number} globalMin - The minimum value of the global range
     * @param {number} globalMax - The maximum value of the global range
     */
    plotGridLines(globalMin, globalMax) {
        let gridLinesUpdate = {
            xaxis: { 
                showgrid: true,
                range: [0, this.timePoints.length - 1]
            },
            yaxis: { 
                showgrid: true,
                range: [
                    globalMin - this.yAxisPadding, 
                    globalMax + this.yAxisPadding
                ]
            }
        }
        Plotly.relayout(this.timeCoursePlotContainerId, gridLinesUpdate);
    }

    /**
     * Adds hover text to time course plot
     */
    plotHoverText() {
        let hoverTextUpdate = {
            hoverinfo: 'all'
        }
        Plotly.restyle(this.timeCoursePlotContainerId, hoverTextUpdate);
    }

    /**
     * Plot time course data
     * @param {Object} timeCourseData - The time course data
     * @param {Object} timeCoursePlotOptions - Plot options for each time course
     */
    plotTimeCourseData(timeCourseData, timeCoursePlotOptions) {
        // loop through each time course and add to plot
        for (const ts in timeCourseData){
            // Add new trace and get its index
            const traceIndex = this.traceManager.addTrace(ts);
            // create a line plot trace
            const tsTrace = {
                x: this.timePoints,
                y: timeCourseData[ts],
                type: 'scatter',
                mode: timeCoursePlotOptions[ts]['mode'],
                name: timeCoursePlotOptions[ts]['label'],
                marker: { color: timeCoursePlotOptions[ts]['color'] },
                line: {
                    shape: 'linear',
                    width: timeCoursePlotOptions[ts]['width']
                },
                visible: timeCoursePlotOptions[ts]['visibility'],
                opacity: timeCoursePlotOptions[ts]['opacity'],
            }
            console.log(`adding trace ${ts} to plot`);
            // add data to plot
            Plotly.addTraces(this.timeCoursePlotContainerId, [tsTrace], traceIndex);
        }
    }

    /**
     * Plot time point marker
     * @param {number} timePoint - The time point
     * @param {Object} timeMarkerPlotOptions [null] - Plot options for the time marker
     */
    plotTimeMarker(timePoint, timeMarkerPlotOptions = null) {
        // store time marker plot options for future reference
        if (timeMarkerPlotOptions) {
            this.timeMarkerPlotOptions = timeMarkerPlotOptions;
        }
        this.timeMarkerShape = {
            type: 'line',
            x0: timePoint,
            y0: 0,
            x1: timePoint,
            y1: 1,
            yref: 'paper',
            opacity: this.timeMarkerPlotOptions['opacity'],
            line: {
                color: this.timeMarkerPlotOptions['color'],
                width: this.timeMarkerPlotOptions['width'],
                dash: this.timeMarkerPlotOptions['shape']
            },
        }
        
        // Combined shapes and update plot
        this.updateShapes();
    }

    /**
     * Remove grid lines from X- and Y-axis
     * @param {number} globalMin - The minimum value of the global range
     * @param {number} globalMax - The maximum value of the global range
     */
    removeGridLines(globalMin, globalMax) {
        let gridLinesUpdate = {
            xaxis: { 
                showgrid: false,
                range: [0, this.timePoints.length - 1]
            },
            yaxis: { 
                showgrid: false,
                range: [
                    globalMin - this.yAxisPadding, 
                    globalMax + this.yAxisPadding
                ]
            }
        }
        Plotly.relayout(this.timeCoursePlotContainerId, gridLinesUpdate);
    }

    /**
     * Removes hover text from time course plot
     */
    removeHoverText() {
        let hoverTextUpdate = {
            hoverinfo: 'none'
        }
        Plotly.restyle(this.timeCoursePlotContainerId, hoverTextUpdate);
    }

    /**
     * Remove time course from plot
     */
    removeTimeCourse(tsLabel) {
        try {
            let traceIndex = this.traceManager.getTraceIndex(tsLabel);
            // remove trace from plot
            console.log(`removing trace ${tsLabel} from plot`);
            Plotly.deleteTraces(this.timeCoursePlotContainerId, traceIndex);
            // remove trace index from trace index
            this.traceManager.removeTrace(tsLabel);
        } catch (error) {
            console.error(`Error removing time course ${tsLabel} from plot: ${error.message}`);
        }
    }

    // set state variables
    async setStateVariables() {
        // initialize fmri time course plot states
        const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
        this.timeCourseEnabled = plotOptions.fmri_timecourse_enabled;
        this.timeCourseFreeze = plotOptions.fmri_timecourse_freeze;
    }

    /**
     * Helper method to combine and update all shapes
     */
    updateShapes() {
        const allShapes = [...this.annotationShapes];
        if (this.timeMarkerShape) {
            allShapes.push(this.timeMarkerShape);
        }
        Plotly.relayout(this.timeCoursePlotContainerId, {
            shapes: allShapes
        });
    }

    /**
     * Update time course data
     * @param {string} tsLabel - The label of the time course
     * @param {Object} timeCourseData - The time course data
     */
    updateTimeCourseData(tsLabel, timeCourseData) {
        // get trace index
        const traceIndex = this.traceManager.getTraceIndex(tsLabel);
        const dataUpdate = {
            x: [this.timePoints],
            y: [timeCourseData[tsLabel]],
        }
        console.log('updating time course data for traceIndex', traceIndex);
        // update time course data
        Plotly.restyle(
            this.timeCoursePlotContainerId, 
            dataUpdate, 
            traceIndex
        );
    }

    /**
     * Update time course plot options
     */
    updateTimeCourseProperty(
        tsLabel, 
        mode=null, 
        color=null, 
        width=null, 
        visibility=null, 
        opacity=null
    ) {
        let traceIndex = this.traceManager.getTraceIndex(tsLabel);
        let timeCourseUpdate = {};
        if (mode) {
            timeCourseUpdate.mode = mode;
        }
        if (color) {
            timeCourseUpdate.marker = {color: color};
        }
        if (width) {
            timeCourseUpdate.line = {width: width};
        }
        if (visibility) {
            timeCourseUpdate.visible = visibility;
        }
        if (opacity) {
            timeCourseUpdate.opacity = opacity;
        }
        // update time course plot
        Plotly.restyle(this.timeCoursePlotContainerId, timeCourseUpdate, traceIndex);
    }

    /**
     * Update x-axis range
     * @param {number} xEnd - The end of the x-axis
     */
    updateXAxisRange(xEnd) {
        let xAxisUpdate = {
            xaxis: {
                range: [0, xEnd]
            }
        }
        Plotly.relayout(this.timeCoursePlotContainerId, xAxisUpdate);
    }

    /**
     * Update y-axis range
     * @param {Object} timeCourseGlobalPlotOptions - The global plot options
     */
    updateYAxisRange(timeCourseGlobalPlotOptions) {
        let axisRangeUpdate = {
            yaxis: { 
                range: [
                    timeCourseGlobalPlotOptions.global_min - this.yAxisPadding, 
                    timeCourseGlobalPlotOptions.global_max + this.yAxisPadding
                ]
            }
        }
        Plotly.relayout(this.timeCoursePlotContainerId, axisRangeUpdate);
    }


}

export default TimeCourse;
