// viewOptionsTimeCourse.js
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import {
    getViewerMetadata,
} from '../../api/data.js';
import { 
    changeTaskConvolution,
    getTimeCourseGlobalPlotOptions,
    updateTimeCourseGlobalPlotOptions 
} from '../../api/plot.js';

class ViewOptionsTimeCourse {
    /**
     * Constructor for the ViewOptionsTimeCourse class
     * @param {string} gridToggleId - ID of the grid toggle button
     * @param {string} hoverTextToggleId - ID of the hover text toggle button
     * @param {string} timeMarkerVisibilityToggleId - ID of the time marker visibility toggle button
     * @param {string} globalConvolutionToggleId - ID of the global convolution toggle button
     */
    constructor(
        gridToggleId,
        hoverTextToggleId,
        timeMarkerVisibilityToggleId,
        globalConvolutionToggleId,
    ) {
        this.gridToggle = $(`#${gridToggleId}`);
        this.hoverTextToggle = $(`#${hoverTextToggleId}`);
        this.timeMarkerVisibilityToggle = $(`#${timeMarkerVisibilityToggleId}`);
        this.globalConvolutionToggle = $(`#${globalConvolutionToggleId}`);

        // set toggle state
        this.toggleState = {};
        getTimeCourseGlobalPlotOptions(
            (plotOptions) => {
                this.toggleState['gridToggle'] = plotOptions.grid_on;
                this.toggleState['hoverTextToggle'] = plotOptions.hover_text_on;
                this.toggleState['timeMarkerVisibilityToggle'] = plotOptions.time_marker_on;
                this.toggleState['globalConvolutionToggle'] = plotOptions.global_convolution;
            }
        );

        getViewerMetadata(
            (metadata) => {
                // if no task data is passed, disable convolution toggle
                if (!metadata.task_enabled) {
                    this.globalConvolutionToggle.prop('disabled', true);
                }
            }
        );

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
    handleGlobalConvolutionToggleChangeListener() {
        console.log('global convolution toggle change');
        this.toggleState['globalConvolutionToggle'] = !this.toggleState['globalConvolutionToggle'];
        changeTaskConvolution(this.toggleState['globalConvolutionToggle'], () => {
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.TOGGLE_CONVOLUTION_GLOBAL, 
                { global_convolution: this.toggleState['globalConvolutionToggle'] }
            );
        });
    }

    /**
     * Handles the grid toggle change listener
     */
    handleGridToggleChangeListener() {
        console.log('grid toggle change');
        this.toggleState['gridToggle'] = !this.toggleState['gridToggle'];
        updateTimeCourseGlobalPlotOptions(
            { grid_on: this.toggleState['gridToggle'] },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.GRID_TOGGLE, 
                    this.toggleState['gridToggle']
                );
            }
        );
    }

    /**
     * Handles the hover text toggle change listener
     */
    handleHoverTextToggleChangeListener() {
        console.log('hover text toggle change');
        this.toggleState['hoverTextToggle'] = !this.toggleState['hoverTextToggle'];
        updateTimeCourseGlobalPlotOptions(
            { hover_text_on: this.toggleState['hoverTextToggle'] },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.HOVER_TEXT_TOGGLE, 
                    this.toggleState['hoverTextToggle']
                );
            }
        );
    }

    /**
     * Handles the time marker visibility toggle change listener
     */
    handleTimeMarkerVisibilityToggleChangeListener() {
        console.log('time marker visibility toggle change');
        this.toggleState['timeMarkerVisibilityToggle'] = !this.toggleState['timeMarkerVisibilityToggle'];
        updateTimeCourseGlobalPlotOptions(
            { time_marker_on: this.toggleState['timeMarkerVisibilityToggle'] },
            () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.TIME_MARKER_VISIBILITY_TOGGLE, 
                    this.toggleState['timeMarkerVisibilityToggle']
                );
            }
        );
    }
}

export default ViewOptionsTimeCourse;
