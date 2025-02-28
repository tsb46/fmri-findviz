// distance_modal.js
// Class for handling distance analysis modal
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { DOM_IDS } from '../../../constants/DomIds.js';
import eventBus from '../../events/ViewerEvents.js';
import { distance } from '../../api/analysis.js';
import Spinner from '../../components/Spinner.js';

class DistanceModal {
    /**
     * @param {string} distanceModalId - The id of the distance modal
     * @param {string} distanceFormId - The id of the distance form
     * @param {string} distanceMetricSelectId - The id of the distance metric select
     * @param {string} timePointMessageId - The id of the time point message
     * @param {string} distanceRemoveButtonId - The id of the distance remove button
     * @param {string} errorMessageId - The id of the error message
     * @param {string} preprocessAlertId - The id of the preprocess alert
     */
    constructor(
        distanceModalId,
        distanceFormId,
        distanceMetricSelectId,
        timePointMessageId,
        distanceRemoveButtonId,
        errorMessageId,
        preprocessAlertId
    ) {
        this.distanceModal = $(`#${distanceModalId}`);
        this.distanceForm = $(`#${distanceFormId}`);
        this.distanceMetricSelect = $(`#${distanceMetricSelectId}`);
        this.timePointMessage = $(`#${timePointMessageId}`);
        this.distanceRemoveButton = $(`#${distanceRemoveButtonId}`);
        this.preprocessAlert = $(`#${preprocessAlertId}`);
        this.errorMessageId = errorMessageId;
        // initialize time point display in modal as 0
        this.timePointMessage.text(0);

        // disable distance remove button by default
        this.distanceRemoveButton.prop('disabled', true);

        // initialize spinner
        this.spinner = new Spinner(
            DOM_IDS.DISTANCE.SPINNER_OVERLAY,
            DOM_IDS.DISTANCE.SPINNER_WHEEL
        );

        // initialize event listeners
        this.attachEventListeners();
    }

    // initialize event listeners
    attachEventListeners() {
        // listen for time slider change
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, (timeIndex) => {
            this.timePointMessage.text(timeIndex);
        });

        // display preprocess alert
        eventBus.subscribe(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS, () => {
            this.preprocessAlert.show();
        });

        // hide preprocess alert on completion of reset
        eventBus.subscribe(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_RESET, () => {
            this.preprocessAlert.hide();
        });

        // listen for distance form submission
        this.distanceForm.on('submit', this.handleDistanceFormSubmit.bind(this));

        // listen for remove distance plot button click
        this.distanceRemoveButton.on('click', this.handleDistanceRemoveButtonClick.bind(this));
    }

    // handle distance form submission
    async handleDistanceFormSubmit(event) {
        event.preventDefault();
        // show spinner
        this.spinner.show();
        const distanceMetric = this.distanceMetricSelect.val();
        distance({ distance_metric: distanceMetric }, this.errorMessageId, 
            // success callback
            () => {
                // publish distance event
                eventBus.publish(EVENT_TYPES.ANALYSIS.DISTANCE);
                // clear error message
                const errorMessage = $(`#${this.errorMessageId}`);
                errorMessage.text('');
                // close modal
                this.distanceModal.modal('hide');
                // hide spinner
                this.spinner.hide();
                // enable distance remove button
                this.distanceRemoveButton.prop('disabled', false);
            },
            // error callback
            () => {
                // hide spinner
                this.spinner.hide();
            }
        );
    }

    // handle remove distance plot button click
    handleDistanceRemoveButtonClick() {
        // publish distance remove event
        eventBus.publish(EVENT_TYPES.ANALYSIS.DISTANCE_REMOVE);
        // disable distance remove button
        this.distanceRemoveButton.prop('disabled', true);
    }
}

export default DistanceModal;
