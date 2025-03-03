// average.js
// Class for handling windowed average analysis

import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { DOM_IDS } from '../../../constants/DomIds.js';
import { windowedAverage } from '../../api/analysis.js';
import { getAnnotationMarkers } from '../../api/plot.js';
import Spinner from '../../components/Spinner.js';

class Average {
    /**
     * @param {string} averageModalId - The id of the average modal
     * @param {string} leftEdgeId - The id of the left edge input
     * @param {string} rightEdgeId - The id of the right edge input
     * @param {string} submitAverageId - The id of the submit average button
     * @param {string} averageFormId - The id of the average form
     * @param {string} annotationWarningId - The id of the annotation warning
     * @param {string} errorMessageId - The id of the error message
     * @param {ViewerEvents} eventBus - The event bus
     */
    constructor(
        averageModalId,
        leftEdgeId,
        rightEdgeId,
        submitAverageId,
        averageFormId,
        annotationWarningId,
        errorMessageId,
        eventBus
    ) {
        // get elements
        this.averageModal = $(`#${averageModalId}`);
        this.leftEdge = $(`#${leftEdgeId}`);
        this.rightEdge = $(`#${rightEdgeId}`);
        this.submitAverage = $(`#${submitAverageId}`);
        this.averageForm = $(`#${averageFormId}`);
        this.annotationWarning = $(`#${annotationWarningId}`);
        // error message
        this.errorMessageId = errorMessageId;
        this.eventBus = eventBus;
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
    checkAnnotationMarkers() {
        // clear error message
        $(`#${this.errorMessageId}`).css('display', 'none');
        getAnnotationMarkers((annotationMarkers) => {
            if (annotationMarkers.markers.length === 0) {
                this.annotationWarning.show();
                this.submitAverage.prop('disabled', true);
            }
            else {
                this.annotationWarning.hide();
                this.submitAverage.prop('disabled', false);
            }
        });
    }

    /**
     * Handle average form submission
     * @param {Event} event - Form submission event
     */
    handleAverageSubmit(event) {
        event.preventDefault();
        // show spinner
        this.spinner.show();
        console.log('average submit button clicked');
        const windowedAverageParams = {
            left_edge: this.leftEdge.val(),
            right_edge: this.rightEdge.val(),
        };
        windowedAverage(windowedAverageParams, this.errorMessageId, () => {
            this.eventBus.publish(EVENT_TYPES.ANALYSIS.WINDOWED_AVERAGE);
            // hide spinner
            this.spinner.hide();
            // hide modal
            this.averageModal.modal('hide');
        }, () => {
            // hide spinner
            this.spinner.hide();
        });
    }
}

export default Average;