// viewOptionsTimeCourse.js
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import ContextManager from '../../api/ContextManager.js';


class ViewOptionsTimeCourse {
    /**
     * Constructor for the ViewOptionsTimeCourse class
     * @param {string} gridToggleId - ID of the grid toggle button
     * @param {string} hoverTextToggleId - ID of the hover text toggle button
     * @param {string} timeMarkerVisibilityToggleId - ID of the time marker visibility toggle button
     * @param {string} globalConvolutionToggleId - ID of the global convolution toggle button
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        gridToggleId,
        hoverTextToggleId,
        timeMarkerVisibilityToggleId,
        globalConvolutionToggleId,
        eventBus,
        contextManager
    ) {
        // get event bus and context manager
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // get elements
        this.gridToggle = $(`#${gridToggleId}`);
        this.hoverTextToggle = $(`#${hoverTextToggleId}`);
        this.timeMarkerVisibilityToggle = $(`#${timeMarkerVisibilityToggleId}`);
        this.globalConvolutionToggle = $(`#${globalConvolutionToggleId}`);

        // set toggle states
        this.setStateVariables();

        // attach listeners to the toggle buttons
        this.gridToggle.on(
            'click', this.handleGridToggleChangeListener.bind(this)
        );
        this.hoverTextToggle.on(
            'click', this.handleHoverTextToggleChangeListener.bind(this)
        );
        this.timeMarkerVisibilityToggle.on(
            'click', this.handleTimeMarkerVisibilityToggleChangeListener.bind(this)
        );
        this.globalConvolutionToggle.on(
            'click', this.handleGlobalConvolutionToggleChangeListener.bind(this)
        );
    }

    /**
     * Handles the global convolution toggle change listener
     */
    async handleGlobalConvolutionToggleChangeListener() {
        console.log('global convolution toggle change');
        this.toggleState['globalConvolutionToggle'] = !this.toggleState['globalConvolutionToggle'];
        await this.contextManager.plot.changeTaskConvolution(
            this.toggleState['globalConvolutionToggle']
        );
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION_GLOBAL, 
            { global_convolution: this.toggleState['globalConvolutionToggle'] }
        );
    }

    /**
     * Handles the grid toggle change listener
     */
    async handleGridToggleChangeListener() {
        console.log('grid toggle change');
        this.toggleState['gridToggle'] = !this.toggleState['gridToggle'];
        await this.contextManager.plot.updateTimeCourseGlobalPlotOptions(
            { grid_on: this.toggleState['gridToggle'] }
        );
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.GRID_TOGGLE, 
            this.toggleState['gridToggle']
        );
    }

    /**
     * Handles the hover text toggle change listener
     */
    async handleHoverTextToggleChangeListener() {
        console.log('hover text toggle change');
        this.toggleState['hoverTextToggle'] = !this.toggleState['hoverTextToggle'];
        await this.contextManager.plot.updateTimeCourseGlobalPlotOptions(
            { hover_text_on: this.toggleState['hoverTextToggle'] }
        );
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.HOVER_TEXT_TOGGLE, 
            this.toggleState['hoverTextToggle']
        );
    }

    /**
     * Handles the time marker visibility toggle change listener
     */
    async handleTimeMarkerVisibilityToggleChangeListener() {
        console.log('time marker visibility toggle change');
        this.toggleState['timeMarkerVisibilityToggle'] = !this.toggleState['timeMarkerVisibilityToggle'];
        await this.contextManager.plot.updateTimeCourseGlobalPlotOptions(
            { time_marker_on: this.toggleState['timeMarkerVisibilityToggle'] }
        );
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_VISIBILITY_TOGGLE, 
            this.toggleState['timeMarkerVisibilityToggle']
        );
    }

    /**
     * Get plot options and set state variables
     */
    async setStateVariables() {
        this.toggleState = {};
        const plotOptions = await this.contextManager.plot.getTimeCourseGlobalPlotOptions();
        const metadata = await this.contextManager.data.getViewerMetadata();
        this.toggleState['gridToggle'] = plotOptions.grid_on;
        this.toggleState['hoverTextToggle'] = plotOptions.hover_text_on;
        this.toggleState['timeMarkerVisibilityToggle'] = plotOptions.time_marker_on;
        this.toggleState['globalConvolutionToggle'] = plotOptions.global_convolution;
        if (!metadata.task_enabled) {
            this.globalConvolutionToggle.prop('disabled', true);
        }
    }
}

export default ViewOptionsTimeCourse;
