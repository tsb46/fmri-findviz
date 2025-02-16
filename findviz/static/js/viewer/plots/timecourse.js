// Timecourse plot
// Handles all plotting and click events for time course visualization
import { EVENT_TYPES } from '../constants/EventTypes.js';
import eventBus from '../events/ViewerEvents.js';
import { 
    getTimeCourseData, 
    getTimePoint,
    popFmriTimeCourse,
    removeFmriTimeCourses,
    updateFmriTimeCourse 
} from '../api/data.js';
import {
    getAnnotationMarkers,
    getTaskDesignPlotOptions,
    getTimeCourseGlobalPlotOptions, 
    getTimeCoursePlotOptions,
    getTimeMarkerPlotOptions
} from '../api/plot.js';

class TimeCourse {
    /**
     * Constructor for TimeCourse
     * @param {string} timeCoursePlotContainerId - The ID of the time course plot container
     * @param {boolean} timeCourseInput - Whether the time course input is provided
     * @param {boolean} taskDesignInput - Whether the task design input is provided
     */
    constructor(
        timeCoursePlotContainerId,
        timeCourseInput,
        taskDesignInput
    ) {
        this.timeCoursePlotContainerId = timeCoursePlotContainerId;
        this.timeCoursePlotContainer = $(`#${timeCoursePlotContainerId}`);
        this.timeCourseInput = timeCourseInput;
        this.taskDesignInput = taskDesignInput;
        // Show time course container if time course or task design input is provided
        if (this.timeCourseInput || this.taskDesignInput) {
            this.timeCoursePlotContainer.css("visibility", "visible");
            // create flag for whether user input time courses are present
            this.userInput = true;
        } else {
            this.userInput = false;
        }

        // initialize fmri time course plot states
        this.timeCourseEnabled = false;
        this.timeCourseFreeze = false;

        // attach event listeners
        this.attachEventListeners();

        // initialize plot state - i.e. whether time course is plotted
        this.plotState = false;
    }

    attachEventListeners() {
        // listen for enable/disable fmri time course events
        eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.ENABLE_FMRI_TIMECOURSE, (state) => {
                this.timeCourseEnabled = state;
                // state is true and no user input, make time course container visible
                if (state && !this.userInput) {
                    this.timeCoursePlotContainer.css("visibility", "visible");
                // state is false and no user input, make time course container hidden
                } else if (!state && !this.userInput) {
                    this.timeCoursePlotContainer.css("visibility", "hidden");
                }
            }
        );

        // listen for freeze/unfreeze fmri time course events
        eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.FREEZE_FMRI_TIMECOURSE, (state) => {
                this.timeCourseFreeze = state;
            }
        );

        // listen for time slider change event - replot time marker
        eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, (timePoint) => {
                if (this.plotState) {
                    this.plotTimeMarker(timePoint);
                }
            }
        );

        // listen for plotly click events on Nifti or GiftiViewer
        // if fmri time course enabled, add functional timecourse and plot
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, 
                EVENT_TYPES.VISUALIZATION.FMRI.GIFTIVIEWER_CLICK
            ], async () => {  
                // if fmri time course enabled, update functional timecourse
                if (this.timeCourseEnabled) {
                    // set plot state to true
                    this.plotState = true;
                    // if previous selection was frozen, update functional timecourse
                    if (this.timeCourseFreeze) {
                        await updateFmriTimeCourse();
                        // get time course data and plot
                        const timeCourseData = await getTimeCourseData();
                        const plotOptions = await this.getPlotOptions();
                        this.plotTimeCourseDataUpdate(timeCourseData, plotOptions);
                        // publish event that fmri time course has been added
                        eventBus.publish(
                            EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE
                        );
                    } else {
                        // if previous selection was not frozen, remove most recent 
                        // fmri timecourse and replace with current selection
                        await popFmriTimeCourse();
                        await updateFmriTimeCourse();
                        // get time course data and plot
                        const timeCourseData = await getTimeCourseData();
                        const plotOptions = await this.getPlotOptions();
                        this.plotTimeCourseDataUpdate(timeCourseData, plotOptions);
                        // publish event that fmri time course has been added
                        eventBus.publish(
                            EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE
                        );
                    }
                }
            }
        );

        // listen for undo fmri time course event
        // remove most recent fmri timecourse and replot
        eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE, async () => {
                if (this.plotState) {
                    // set plot state to false
                    this.plotState = false;
                    // remove most recent fmri timecourse
                    await popFmriTimeCourse();
                    // get time course data and plot
                    const timeCourseData = await getTimeCourseData();
                    const plotOptions = await this.getPlotOptions();
                    this.plotTimeCourseDataUpdate(timeCourseData, plotOptions);
                    // publish event that most recentfmri time course has been removed
                    eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE
                    );
                }
            }
        );

        // listen for remove all fmri time course event
        // remove all fmri timecourses and replot
        eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE, async () => {
                if (this.plotState) {
                    // set plot state to false
                    this.plotState = false;
                    // remove all fmri timecourses
                    await removeFmriTimeCourses();
                    // get time course data and plot
                    const timeCourseData = await getTimeCourseData();
                    const plotOptions = await this.getPlotOptions();
                    this.plotTimeCourseDataUpdate(timeCourseData, plotOptions);
                    // publish event that all fmri time courses have been removed
                    eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE
                    );
                }
            }
        );

        // listen for time course visualization change events
        // update time course plot properties (color, mode, width, visibility, opacity)
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_COLOR_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_MODE_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_OPACITY_SLIDER_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_LINE_WIDTH_SLIDER_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIMECOURSE_SCALE_CHANGE
            ], async (label) => {
                const plotOptions = await this.getPlotOptions();
                this.plotTimeCoursePropertyUpdate(
                    label, 
                    plotOptions[label].mode, 
                    plotOptions[label].color, 
                    plotOptions[label].width, 
                    plotOptions[label].visibility, 
                    plotOptions[label].opacity
                );
            }
        );

        // listen for time course global plot options change events
        // update time marker plot properties (color, width, shape, opacity)
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_COLOR_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_WIDTH_SLIDER_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_SHAPE_CHANGE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_OPACITY_SLIDER_CHANGE
            ], async () => {
                const timeMarkerPlotOptions = await getTimeMarkerPlotOptions();
                const timePoint = await getTimePoint();
                this.plotTimeMarker(timePoint, timeMarkerPlotOptions);
            }
        );

        // listen for local and global convolution toggle events
        // update time course data and plot
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION_GLOBAL
            ], async () => {
                // get time course data and plot
                const timeCourseData = await getTimeCourseData();
                const plotOptions = await this.getPlotOptions();
                this.plotTimeCourseDataUpdate(timeCourseData, plotOptions);
            }
        );

        // listen for annotation marker change events
        // update time course data and plot
        eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_ADDED,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_MOVED,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_REMOVED,
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_UNDONE
            ], async () => {
                // get annnotation markers and plot
                getAnnotationMarkers( (annotationData) => {
                    // if no annotation markers, don't plot
                    if (annotationData.markers.length > 0) {
                        this.plotAnnotationMarkers(
                            annotationData.markers, 
                            annotationData.selection,
                            annotationData.highlight
                        );
                    }
                });
            }
        );
    }

    async initPlot() {
        // if time course or task design input, plot time course
        if (this.timeCourseInput || this.taskDesignInput) {
            // set plot state to true
            this.plotState = true;
            // get plot options
            const plotOptions = await this.getPlotOptions();
            // get time marker and global plot options
            const timeMarkerPlotOptions = await getTimeMarkerPlotOptions();
            const timeCourseGlobalPlotOptions = await getTimeCourseGlobalPlotOptions();
            // combine all plot options into one object
            const globalPlotOptions = {
                ...timeMarkerPlotOptions,
                ...timeCourseGlobalPlotOptions
            };
            // get timecourse data
            const timeCourseData = await getTimeCourseData();
            this.plotTimeCourseFullUpdate(timeCourseData, plotOptions, globalPlotOptions);
        }
    }

    // get plot options from task and timecourse plot options
    async getPlotOptions() {
        // get time course plot options
        const timeCoursePlotOptions = await getTimeCoursePlotOptions();
        // get task design plot options
        const taskDesignPlotOptions = await getTaskDesignPlotOptions();
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
     * @param {boolean} highlight - Whether to highlight the annotation selection
     */
    plotAnnotationMarkers(markers, selection, highlight) {
        // create a vertical line at each annotation marker
        this.annotationShapes = markers.map(marker => ({
            type: 'line',
            x0: marker,
            y0: 0,
            x1: marker,
            y1: 1,
            yref: 'paper',
            opacity: 0.5,
            line: {
                color: 'rgb(255, 0, 0)',
                width: 1
            },
        }));

        // if highlight, highlight currently selected annotation marker
        if (highlight) {
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
     */
    plotGridLines() {
        let gridLinesUpdate = {
            xaxis: { showgrid: true },
            yaxis: { showgrid: true }
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
     * Update time course plot options
     */
    plotTimeCoursePropertyUpdate(
        traceIndex, 
        mode=null, 
        color=null, 
        width=null, 
        visibility=null, 
        opacity=null
    ) {
        let timeCourseUpdate
        if (mode) {
            timeCourseUpdate = {
                mode: mode
            }
        }
        if (color) {
            timeCourseUpdate = {
                marker: {color: color}
            }
        }
        if (width) {
            timeCourseUpdate = {
                line: {width: width}
            }
        }
        if (visibility) {
            timeCourseUpdate = {
                visible: visibility
            }
        }
        if (opacity) {
            timeCourseUpdate = {
                opacity: opacity
            }
        }
        // update time course plot
        Plotly.restyle(this.timeCoursePlotContainerId, timeCourseUpdate, traceIndex);
    }

    /**
     * Plot time course data
     * @param {Object} timeCourseData - The time course data
     * @param {Object} timeCoursePlotOptions - Plot options for each time course
     * @param {boolean} layoutUpdate[false] - Whether to update the layout
     */
    plotTimeCourseDataUpdate(timeCourseData, timeCoursePlotOptions, layoutUpdate=false) {
        // initialize plot arrays
        let plotData = []
        this.traceIndex = {}
        // add input time courses to plot, if any
        let index = 0;
        for (ts in timeCourseData){
            // keep up with trace labels
            traceIndex[ts] = index;
            index++;
            // get length of time course data
            const timeCourseLength = timeCourseData[ts].length;
            // create a line plot trace
            const tsTrace = {
                x: Array.from({ length: timeCourseLength }, (_, i) => i),
                y: timeCourseData[ts],
                type: 'scatter',
                mode: timeCoursePlotOptions[ts]['mode'],
                name: timeCoursePlotOptions[ts]['name'],
                marker: { color: timeCoursePlotOptions[ts]['color'] },
                line: {
                    shape: 'linear',
                    width: timeCoursePlotOptions[ts]['width']
                },
                visible: timeCoursePlotOptions[ts]['visibility'],
                opacity: timeCoursePlotOptions[ts]['opacity'],
            }
            plotData.push(tsTrace)
        }

        // create layout
        if (layoutUpdate) {
            const layout = {
                height: 500,
                xaxis: {
                title: 'Time Point',
                range: [0, timeCourseLength],
            },
            yaxis: {
                title: 'Signal Intensity',
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
            // create plot
            Plotly.react(this.timeCoursePlotContainerId, plotData, layout);
        } else {
            // restyle data in plot
            Plotly.restyle(this.timeCoursePlotContainerId, plotData);
        }
    }

    /**
     * Plot all time course data
     * @param {Object} timeCourseData - The time course data
     * @param {Object} timeCoursePlotOptions - Plot options for each time course
     * @param {Object} globalPlotOptions - Global plot options
     */
    plotTimeCourseFullUpdate(
        timeCourseData,
        timeCoursePlotOptions,
        globalPlotOptions
    ) {
        // plot time course data
        this.plotTimeCourseDataUpdate(timeCourseData, timeCoursePlotOptions, true);

        // if hover text on, enable hover text
        if (globalPlotOptions.hover_text_on) {
            this.plotHoverText();
        }

        // if grid lines on, plot grid lines
        if (globalPlotOptions.grid_on) {
            this.plotGridLines();
        }

        // get time point marker and plot
        if (globalPlotOptions.time_marker_on) {
            getTimePoint( (timePoint) => {
                this.plotTimeMarker(timePoint, timeMarkerPlotOptions);
            });
        }

        // get annnotation markers and plot
        getAnnotationMarkers( (annotationData) => {
            // if no annotation markers, don't plot
            if (annotationData.markers.length > 0) {
                this.plotAnnotationMarkers(
                    annotationData.markers, 
                    annotationData.selection,
                    annotationData.highlight
                );
            }
        });
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
     */
    removeGridLines() {
        let gridLinesUpdate = {
            xaxis: { showgrid: false },
            yaxis: { showgrid: false }
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
     * Update shapes and plot
     */
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


}

export default TimeCourse;
