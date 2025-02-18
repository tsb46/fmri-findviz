// distance_modal.js
// Class for handling distance analysis modal
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { distance } from '../../api/analysis.js';

class DistanceModal {
    /**
     * @param {string} distanceModalId - The id of the distance modal
     * @param {string} distanceFormId - The id of the distance form
     * @param {string} distanceMetricSelectId - The id of the distance metric select
     * @param {string} timePointMessageId - The id of the time point message
     * @param {string} distanceRemoveButtonId - The id of the distance remove button
     * @param {string} preprocessAlertId - The id of the preprocess alert
     */
    constructor(
        distanceModalId,
        distanceFormId,
        distanceMetricSelectId,
        timePointMessageId,
        distanceRemoveButtonId,
        preprocessAlertId
    ) {
        this.distanceModal = $(`#${distanceModalId}`);
        this.distanceForm = $(`#${distanceFormId}`);
        this.distanceMetricSelect = $(`#${distanceMetricSelectId}`);
        this.timePointMessage = $(`#${timePointMessageId}`);
        this.distanceRemoveButton = $(`#${distanceRemoveButtonId}`);
        this.preprocessAlert = $(`#${preprocessAlertId}`);
        // initialize time point display in modal as 0
        this.timePointMessage.text(0);

        // disable distance remove button by default
        this.distanceRemoveButton.prop('disabled', true);

        // initialize event listeners
        this.attachEventListeners();
    }

    // initialize event listeners
    attachEventListeners() {
        // listen for time slider change
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, (timeIndex) => {
            this.timePointMessage.text(timeIndex);
        });

        // display preprocess alert and enable plot removal on completion of preprocess
        eventBus.subscribe(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS, () => {
            this.preprocessAlert.show();
            this.distanceRemoveButton.prop('disabled', false);
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
        const distanceMetric = this.distanceMetricSelect.val();
        distance({ distance_metric: distanceMetric }, () => {
            eventBus.publish(EVENT_TYPES.ANALYSIS.DISTANCE);
        });
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
