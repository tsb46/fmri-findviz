// Annotate.js - handles annotation of time courses
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import { 
    addAnnotationMarker, 
    clearAnnotationMarkers, 
    moveAnnotationSelection,
    undoAnnotationMarker
} from '../../../api/plot.js';

class Annotate {
    /**
     * @param {string} plotlyPlotId - The id of the plotly plot
     * @param {string} timeSliderId - The id of the time slider
     * @param {string} annotateSwitchId - The id of the annotate switch
     * @param {string} rightMoveAnnotateId - The id of the right move annotate
     * @param {string} leftMoveAnnotateId - The id of the left move annotate
     * @param {string} undoAnnotateId - The id of the undo annotate
     * @param {string} removeAnnotateId - The id of the remove annotate
     * @param {ViewerEvents} eventBus - The event bus
     */
    constructor(
        plotlyPlotId,
        timeSliderId,
        annotateSwitchId,
        rightMoveAnnotateId,
        leftMoveAnnotateId,
        undoAnnotateId,
        removeAnnotateId,
        eventBus
    ) {
        this.eventBus = eventBus;
        // check that plotlyPlotId is plotted
        this.plotlyPlot = document.getElementById(plotlyPlotId);
        if (!this.plotlyPlot) {
            throw new Error(`Plotly plot with id ${plotlyPlotId} not found`);
        }
        this.timeSlider = $(`#${timeSliderId}`);
        this.annotateSwitch = $(`#${annotateSwitchId}`);
        this.rightMoveAnnotate = $(`#${rightMoveAnnotateId}`);
        this.leftMoveAnnotate = $(`#${leftMoveAnnotateId}`);
        this.undoAnnotate = $(`#${undoAnnotateId}`);
        this.removeAnnotate = $(`#${removeAnnotateId}`);
        // set annotate state as false
        this.annotateState = false;

        // listen for initialization of time course plot and attach listeners
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.INIT_TIMECOURSE_PLOT,
            () => {
                this.attachListeners();
            }
        );
    }

    /**
     * Attaches event listeners to the annotate switch, right move annotate,
     * left move annotate, undo annotate, and remove annotate
     */
    attachListeners() {
        // initialize annotation switch listener
        this.initializeAnnotateSwitchListener();
        // initialize plotly click listener
        this.initializePlotlyClickListener();
        // initialize right move highlight listener
        this.initializeRightMoveAnnotateListener();
        // initialize left move highlight listener
        this.initializeLeftMoveAnnotateListener();
        // initialize undo most recent annotate listener
        this.initializeUndoAnnotateListener();
        // initialize remove all annotations listener
        this.initializeRemoveAnnotateListener();
    }

    /**
     * Initializes the annotate switch listener
     */
    initializeAnnotateSwitchListener() {
        this.annotateSwitch.on('click', () => {
            this.annotateState = !this.annotateState;
            // enable annotate/disable buttons
            if (this.annotateState) {
                this.rightMoveAnnotate.prop('disabled', false);
                this.leftMoveAnnotate.prop('disabled', false);
                this.undoAnnotate.prop('disabled', false);
                this.removeAnnotate.prop('disabled', false);
            } else {
                this.rightMoveAnnotate.prop('disabled', true);
                this.leftMoveAnnotate.prop('disabled', true);
                this.undoAnnotate.prop('disabled', true);
                this.removeAnnotate.prop('disabled', true);
            }
            this.eventBus.publish(
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_STATE_CHANGED, 
                this.annotateState
            );
        });
    }

    /**
     * Initializes the plotly click listener
     */
    initializePlotlyClickListener() {
        this.plotlyPlot.on('plotly_click', (eventData) => {
            if (this.annotateState) {
                const x = Math.round(eventData.points[0].x);
                addAnnotationMarker(x, (marker) => {
                    console.log('annotation marker added at x = ', marker.marker);
                    // update time slider to the x value
                    this.timeSlider.slider('setValue', marker.marker);
                    this.timeSlider.trigger('change');
                    this.eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_ADDED, 
                        marker
                    );
                });
            }
        });
    }

    /**
     * Initializes the right move annotate listener
     */
    initializeRightMoveAnnotateListener() {
        this.rightMoveAnnotate.on('click', () => {
            console.log('right move annotate clicked');
            moveAnnotationSelection('right', (selectedMarker) => {
                console.log(
                    'selected marker moved to right: ', 
                    selectedMarker.selected_marker
                );
                // update time slider to the x value
                this.timeSlider.slider('setValue', selectedMarker.selected_marker);
                this.timeSlider.trigger('change');
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_MOVED, 
                    'right'
                );
            });
        });
    }

    /**
     * Initializes the left move annotate listener
     */
    initializeLeftMoveAnnotateListener() {
        this.leftMoveAnnotate.on('click', () => {
            console.log('left move annotate clicked');
            moveAnnotationSelection('left', (selectedMarker) => {
                console.log(
                    'selected marker moved to left: ', 
                    selectedMarker.selected_marker
                );
                // update time slider to the x value
                this.timeSlider.slider('setValue', selectedMarker.selected_marker);
                this.timeSlider.trigger('change');
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_MOVED, 
                    selectedMarker
                );
            });
        });
    }

    /**
     * Initializes the undo annotate listener
     */
    initializeUndoAnnotateListener() {
        this.undoAnnotate.on('click', () => {
            console.log('undo annotate clicked');
            undoAnnotationMarker((marker) => {
                if (marker.marker) {
                    // update time slider to the marker value
                    this.timeSlider.slider('setValue', marker.marker);
                    this.timeSlider.trigger('change');
                }
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_UNDONE, 
                    marker
                );
            });
        });
    }

    /**
     * Initializes the remove annotate listener
     */
    initializeRemoveAnnotateListener() {
        this.removeAnnotate.on('click', () => {
            console.log('remove annotate clicked');
            clearAnnotationMarkers(() => {
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_REMOVED, 
                    true
                );
            });
        });
    }

}

export default Annotate;