// Correlate.js
// Correlate fmri time courses with another time course
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { DOM_IDS } from '../../../constants/DomIds.js';
import ContextManager from '../../api/ContextManager.js';
import Spinner from '../../components/Spinner.js';

class Correlate {
    /**
     * Constructor for Correlate class
     * @param {string} correlateModalId - The ID of the correlation modal
     * @param {string} modalButtonId - The ID of the modal button
     * @param {string} negativeLagId - The ID of the negative lag input
     * @param {string} positiveLagId - The ID of the positive lag input
     * @param {string} correlateTimeCourseSelectId - The ID of the correlation time course select
     * @param {string} submitCorrelateId - The ID of the submit correlation button
     * @param {string} correlateFormId - The ID of the correlation form
     * @param {string} prepAlertId - The ID of the preprocess alert
     * @param {string} errorMessageId - The ID of the error message
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        correlateModalId,
        modalButtonId,
        negativeLagId,
        positiveLagId,
        correlateTimeCourseSelectId,
        submitCorrelateId,
        correlateFormId,
        prepAlertId,
        errorMessageId,
        eventBus,
        contextManager
    ) {
        // get elements
        this.correlateModal = $(`#${correlateModalId}`);
        this.modalButton = $(`#${modalButtonId}`);
        this.negativeLag = $(`#${negativeLagId}`);
        this.positiveLag = $(`#${positiveLagId}`);
        this.correlateTimeCourseSelect = $(`#${correlateTimeCourseSelectId}`);
        this.submitCorrelate = $(`#${submitCorrelateId}`);
        this.correlateForm = $(`#${correlateFormId}`);
        this.prepAlert = $(`#${prepAlertId}`);
        // error message id
        this.errorMessageId = errorMessageId;
        // get event bus and context manager
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // initialize time course types
        this.timeCourseTypes = {};
        // initialize selected time course
        this.selectedTimeCourse = null;

        // enable modal button by default
        this.modalButton.prop('disabled', false);

        // fill correlation time course select
        this.fillCorrelateTimeCourseSelect();

        // initialize spinner
        this.spinner = new Spinner(
            DOM_IDS.CORRELATE.SPINNER_OVERLAY,
            DOM_IDS.CORRELATE.SPINNER_WHEEL
        );

        // attach event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        // initialize correlation form
        this.correlateForm.on('submit', this.handleCorrelateSubmit.bind(this));

        // refill time course select on addition/removal of fmri time course,
        // preprocessed time course, or reset time course preprocess
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE,
                EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_SUCCESS,
                EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_RESET
            ], 
            this.fillCorrelateTimeCourseSelect.bind(this)
        );

        // handle time course select change
        this.correlateTimeCourseSelect.on(
            'change', this.handleTimeCourseSelectChange.bind(this)
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
        const conditions = await this.contextManager.data.getTaskConditions();
        for (const condition of conditions) {
            labels.push(condition);
            this.timeCourseTypes[condition] = 'task';
        }
        const ts_labels = await this.contextManager.data.getTimeCourseLabels();
        for (const label of ts_labels) {
            labels.push(label);
            this.timeCourseTypes[label] = 'timecourse';
        }
        if (callback) {
            callback(labels);
        }
        return labels;
    }

     /**
     * Fill the correlation time course select with labels
     */
     fillCorrelateTimeCourseSelect() {
        this.getPlotLabels(async (labels) => {
            // clear the select
            this.correlateTimeCourseSelect.empty();
            // if no labels, do nothing
            if (labels.length === 0) {
                return;
            }
            // add labels to select
            for (const label of labels) {
                this.correlateTimeCourseSelect.append(`<option value='${label}'>${label}</option>`);
            }
            // select the last label as the selected time course
            this.correlateTimeCourseSelect.val(labels[labels.length - 1]);
            this.selectedTimeCourse = labels[labels.length - 1];
            // check if time course is preprocessed
            const isPreprocessed = await this.contextManager.plot.checkTsPreprocessed(
                this.selectedTimeCourse, 
                this.timeCourseTypes[this.selectedTimeCourse]
            );
            if (isPreprocessed.is_preprocessed) {
                this.prepAlert.show();
            } else {
                this.prepAlert.hide();
            }
        });
    }

    /**
     * Handle the correlation form submission
     */
    async handleCorrelateSubmit(event) {
        event.preventDefault();
        console.log('correlation submit button clicked');
        // show spinner
        this.spinner.show();
        const label = this.selectedTimeCourse;
        const timeCourseType = this.timeCourseTypes[label];
        const correlateParams = {
            negative_lag: this.negativeLag.val(),
            positive_lag: this.positiveLag.val(),
        };
        try {
            await this.contextManager.analysis.correlate(
                label, timeCourseType, correlateParams, this.errorMessageId
            );
            this.eventBus.publish(EVENT_TYPES.ANALYSIS.CORRELATION);
            // open correlation analysis window
            window.open('/analysis_view/correlate', '_blank');
        } finally {
            // hide spinner
            this.spinner.hide();
        }
        // hide modal
        this.correlateModal.modal('hide');
    }

    /**
     * Handle time course select change
     * 
     */
    async handleTimeCourseSelectChange() {
        console.log('time course select changed for correlate');
        // get selected time course
        const timeCourse = this.correlateTimeCourseSelect.val();
        this.selectedTimeCourse = timeCourse;
        // check if time course is preprocessed
        const isPreprocessed = await this.contextManager.plot.checkTsPreprocessed(
            timeCourse, 
            this.timeCourseTypes[timeCourse]
        );
        if (isPreprocessed.is_preprocessed) {
            this.prepAlert.show();
        } else {
            this.prepAlert.hide();
        }
    }

}

export default Correlate;
