// Correlate.js
// Correlate fmri time courses with another time course

import { EVENT_TYPES } from '../../constants/EventTypes';
import eventBus from '../../events/ViewerEvents';
import { getTimeCourseLabels, getTaskConditions } from '../../api/data';
import { correlate } from '../../api/analysis';

class Correlate {
    /**
     * Constructor for Correlate class
     * @param {string} correlateModalId - The ID of the correlation modal
     * @param {string} negativeLagId - The ID of the negative lag input
     * @param {string} positiveLagId - The ID of the positive lag input
     * @param {string} correlateTimeCourseSelectId - The ID of the correlation time course select
     * @param {string} submitCorrelateId - The ID of the submit correlation button
     * @param {string} correlateFormId - The ID of the correlation form
     */
    constructor(
        correlateModalId,
        negativeLagId,
        positiveLagId,
        correlateTimeCourseSelectId,
        submitCorrelateId,
        correlateFormId
    ) {
        // get elements
        this.correlateModal = $(`#${correlateModalId}`);
        this.negativeLag = $(`#${negativeLagId}`);
        this.positiveLag = $(`#${positiveLagId}`);
        this.correlateTimeCourseSelect = $(`#${correlateTimeCourseSelectId}`);
        this.submitCorrelate = $(`#${submitCorrelateId}`);
        this.correlateForm = $(`#${correlateFormId}`);

        // initialize time course types
        this.timeCourseTypes = {};

        // initialize correlation form
        this.correlateForm.on('submit', this.handleCorrelateSubmit.bind(this));

        // fill correlation time course select
        this.fillCorrelateTimeCourseSelect();

        // refill time course select on addition of fmri time course
        eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE, 
            this.fillCorrelateTimeCourseSelect.bind(this)
        );
    }

    /**
     * Get plot labels from all time courses and/or tasks
     * @param {Function} callback - Callback function to handle successful response
     * @returns {Array} labels - The labels for the time courses and/or tasks
     */
    async getPlotLabels(callback=null) {
        // clear time course types object
        this.timeCourseTypes = {};
        const labels = [];
        await getTaskConditions((conditions) => {
            for (const condition of conditions) {
                labels.push(condition);
                this.timeCourseTypes[condition] = 'task';
            }
        });
        await getTimeCourseLabels((labels) => {
            for (const label of labels) {
                labels.push(label);
                this.timeCourseTypes[label] = 'timecourse';
            }
        });
        if (callback) {
            callback();
        }
        return labels;
    }

     /**
     * Fill the correlation time course select with labels
     */
     fillCorrelateTimeCourseSelect() {
        this.getPlotLabels((labels) => {
            this.correlateTimeCourseSelect.empty();
            for (const label of labels) {
                this.correlateTimeCourseSelect.append(`<option value='${label}'>${label}</option>`);
            }
        });
    }

    /**
     * Handle the correlation form submission
     */
    handleCorrelateSubmit(event) {
        event.preventDefault();
        const label = this.correlateTimeCourseSelect.val();
        const timeCourseType = this.timeCourseTypes[label];
        const correlateParams = {
            negative_lag: this.negativeLag.val(),
            positive_lag: this.positiveLag.val(),
        };
        correlate(label, timeCourseType, correlateParams, () => {
            eventBus.publish(EVENT_TYPES.ANALYSIS.CORRELATION);
        });
        // hide popover
        this.correlateModal.modal('hide');
    }

}

export default Correlate;
