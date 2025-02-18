// Annotate.js - handles annotation of time courses
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { 
    addAnnotationMarker, 
    clearAnnotationMarkers, 
    moveAnnotationSelection,
    undoAnnotationMarker
} from '../../api/plot.js';

class Annotate {
    /**
     * @param {string} plotlyPlotId - The id of the plotly plot
     * @param {string} annotateSwitchId - The id of the annotate switch
     * @param {string} highlightToggleId - The id of the highlight toggle
     * @param {string} rightMoveAnnotateId - The id of the right move annotate
     * @param {string} leftMoveAnnotateId - The id of the left move annotate
     * @param {string} undoAnnotateId - The id of the undo annotate
     * @param {string} removeAnnotateId - The id of the remove annotate
     */
    constructor(
        plotlyPlotId,
        annotateSwitchId,
        highlightToggleId,
        rightMoveAnnotateId,
        leftMoveAnnotateId,
        undoAnnotateId,
        removeAnnotateId,
    ) {
        // check that plotlyPlotId is plotted
        if (!document.getElementById(plotlyPlotId)) {
            throw new Error(`Plotly plot with id ${plotlyPlotId} not found`);
        }
        this.annotateSwitch = $(`#${annotateSwitchId}`);
        this.plotlyPlot = $(`#${plotlyPlotId}`);
        this.highlightToggle = $(`#${highlightToggleId}`);
        this.rightMoveAnnotate = $(`#${rightMoveAnnotateId}`);
        this.leftMoveAnnotate = $(`#${leftMoveAnnotateId}`);
        this.undoAnnotate = $(`#${undoAnnotateId}`);
        this.removeAnnotate = $(`#${removeAnnotateId}`);
        // set annotate state as false
        this.annotateState = false;
        // set highlight state as false
        this.highlightState = false;
    }

    // initialize plotly click listener
    initializePlotlyClickListener() {
        this.plotlyPlot.on('plotly_click', (eventData) => {
            if (this.annotateState) {
                const x = Math.round(eventData.points[0].x);
                addAnnotationMarker(x, () => {
                    console.log('annotation marker added');
                    eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_ADDED, 
                        x
                    );
                });
            }
        });
    }

    // initialize highlight toggle listener
    initializeHighlightToggleListener() {
        this.highlightToggle.on('click', () => {
            this.highlightState = !this.highlightState;
            console.log('highlight toggle clicked');
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_HIGHLIGHT_TOGGLE, 
                this.highlightState
            );
        });
    }

    // initialize right move annotate listener
    initializeRightMoveAnnotateListener() {
        this.rightMoveAnnotate.on('click', () => {
            console.log('right move annotate clicked');
            moveAnnotationSelection('right', () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_MOVED, 
                    'right'
                );
            });
        });
    }

    // initialize left move annotate listener
    initializeLeftMoveAnnotateListener() {
        this.leftMoveAnnotate.on('click', () => {
            console.log('left move annotate clicked');
            moveAnnotationSelection('left', () => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_MOVED, 
                    'left'
                );
            });
        });
    }

    // initialize undo annotate listener
    initializeUndoAnnotateListener() {
        this.undoAnnotate.on('click', () => {
            console.log('undo annotate clicked');
            undoAnnotationMarker(() => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_UNDONE, 
                    true
                );
            });
        });
    }

    // initialize remove annotate listener
    initializeRemoveAnnotateListener() {
        this.removeAnnotate.on('click', () => {
            console.log('remove annotate clicked');
            clearAnnotationMarkers(() => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_REMOVED, 
                    true
                );
            });
        });
    }

}

export default Annotate;