// average.js
// Class for handling windowed average analysis

import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { windowedAverage } from '../../api/analysis.js';
import { getAnnotationMarkers } from '../../api/plot.js';

class Average {
    /**
     * @param {string} averageModalId - The id of the average modal
     * @param {string} leftEdgeId - The id of the left edge input
     * @param {string} rightEdgeId - The id of the right edge input
     * @param {string} submitAverageId - The id of the submit average button
     * @param {string} averageFormId - The id of the average form
     * @param {string} annotationWarningId - The id of the annotation warning
     */
    constructor(
        averageModalId,
        leftEdgeId,
        rightEdgeId,
        submitAverageId,
        averageFormId,
        annotationWarningId,
    ) {
        // get elements
        this.averageModal = $(`#${averageModalId}`);
        this.leftEdge = $(`#${leftEdgeId}`);
        this.rightEdge = $(`#${rightEdgeId}`);
        this.submitAverage = $(`#${submitAverageId}`);
        this.averageForm = $(`#${averageFormId}`);
        this.annotationWarning = $(`#${annotationWarningId}`);

        // initialize average form
        this.averageForm.on('submit', this.handleAverageSubmit.bind(this));

        // on modal show, check if any annotation markers are selected
        this.averageModal.on('show.bs.modal', this.checkAnnotationMarkers.bind(this));
    }

    /**
     * Check if any annotation markers are selected
     */
    checkAnnotationMarkers() {
        getAnnotationMarkers((response) => {
            if (response.length === 0) {
                this.annotationWarning.show();
            }
            else {
                this.annotationWarning.hide();
            }
        });
    }

    /**
     * Handle average form submission
     * @param {Event} event - Form submission event
     */
    handleAverageSubmit(event) {
        event.preventDefault();
        console.log('average submit button clicked');
        const windowedAverageParams = {
            leftEdge: this.leftEdge.val(),
            rightEdge: this.rightEdge.val(),
        };
        windowedAverage(windowedAverageParams, () => {
            eventBus.publish(EVENT_TYPES.ANALYSIS.WINDOWED_AVERAGE);
        });
        // hide modal
        this.averageModal.modal('hide');
    }
}

export default Average;