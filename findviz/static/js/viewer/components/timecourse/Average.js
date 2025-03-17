// average.js
// Class for handling windowed average analysis
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { DOM_IDS } from '../../../constants/DomIds.js';
import Spinner from '../../components/Spinner.js';
import ContextManager from '../../api/ContextManager.js';

class Average {
    /**
     * @param {string} averageModalId - The id of the average modal
     * @param {string} modalButtonId - The id of the modal button
     * @param {string} leftEdgeId - The id of the left edge input
     * @param {string} rightEdgeId - The id of the right edge input
     * @param {string} submitAverageId - The id of the submit average button
     * @param {string} averageFormId - The id of the average form
     * @param {string} annotationWarningId - The id of the annotation warning
     * @param {string} errorMessageId - The id of the error message
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        averageModalId,
        modalButtonId,
        leftEdgeId,
        rightEdgeId,
        submitAverageId,
        averageFormId,
        annotationWarningId,
        errorMessageId,
        eventBus,
        contextManager
    ) {
        // get elements
        this.averageModal = $(`#${averageModalId}`);
        this.modalButton = $(`#${modalButtonId}`);
        this.leftEdge = $(`#${leftEdgeId}`);
        this.rightEdge = $(`#${rightEdgeId}`);
        this.submitAverage = $(`#${submitAverageId}`);
        this.averageForm = $(`#${averageFormId}`);
        this.annotationWarning = $(`#${annotationWarningId}`);
        // error message
        this.errorMessageId = errorMessageId;
        // get event bus and context manager
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // enable modal button by default
        this.modalButton.prop('disabled', false);
        
        // initialize average form
        this.averageForm.on('submit', this.handleAverageSubmit.bind(this));

        // on modal show, check if any annotation markers are selected
        this.averageModal.on('show.bs.modal', this.checkAnnotationMarkers.bind(this));

        // initialize spinner
        this.spinner = new Spinner(
            DOM_IDS.AVERAGE.SPINNER_OVERLAY,
            DOM_IDS.AVERAGE.SPINNER_WHEEL
        );
    }

    /**
     * Check if any annotation markers are selected
     */
    async checkAnnotationMarkers() {
        // clear error message
        $(`#${this.errorMessageId}`).css('display', 'none');
        const annotationMarkers = await this.contextManager.plot.getAnnotationMarkers();
        if (annotationMarkers.markers.length === 0) {
            this.annotationWarning.show();
            this.submitAverage.prop('disabled', true);
        } else {
            this.annotationWarning.hide();
            this.submitAverage.prop('disabled', false);
        }
    }

    /**
     * Handle average form submission
     * @param {Event} event - Form submission event
     */
    async handleAverageSubmit(event) {
        event.preventDefault();
        // show spinner
        this.spinner.show();
        console.log('average submit button clicked');
        const windowedAverageParams = {
            left_edge: this.leftEdge.val(),
            right_edge: this.rightEdge.val(),
        };
        try {
            await this.contextManager.analysis.windowedAverage(windowedAverageParams, this.errorMessageId);
            this.eventBus.publish(EVENT_TYPES.ANALYSIS.WINDOWED_AVERAGE);
            // open average analysis window
            window.open('/analysis_view/average', '_blank');
        } finally {
            // hide spinner
            this.spinner.hide();
        }
        // hide modal
        this.averageModal.modal('hide');
    }
}

export default Average;