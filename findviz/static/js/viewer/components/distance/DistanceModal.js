// distance_modal.js
// Class for handling distance analysis modal
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { DOM_IDS } from '../../../constants/DomIds.js';
import ContextManager from '../../api/ContextManager.js';
import Spinner from '../../components/Spinner.js';

class DistanceModal {
    /**
     * @param {string} distanceModalId - The id of the distance modal
     * @param {string} distanceModalButtonId - The id of the distance modal button
     * @param {string} distanceFormId - The id of the distance form
     * @param {string} distanceMetricSelectId - The id of the distance metric select
     * @param {string} timePointMessageId - The id of the time point message
     * @param {string} distanceRemoveButtonId - The id of the distance remove button
     * @param {string} errorMessageId - The id of the error message
     * @param {string} preprocessAlertId - The id of the preprocess alert
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        distanceModalId,
        distanceModalButtonId,
        distanceFormId,
        distanceMetricSelectId,
        timePointMessageId,
        distanceRemoveButtonId,
        errorMessageId,
        preprocessAlertId,
        eventBus,
        contextManager
    ) {
        // get elements
        this.distanceModal = $(`#${distanceModalId}`);
        this.distanceModalButton = $(`#${distanceModalButtonId}`);
        this.distanceForm = $(`#${distanceFormId}`);
        this.distanceMetricSelect = $(`#${distanceMetricSelectId}`);
        this.timePointMessage = $(`#${timePointMessageId}`);
        this.distanceRemoveButton = $(`#${distanceRemoveButtonId}`);
        this.preprocessAlert = $(`#${preprocessAlertId}`);
        this.errorMessageId = errorMessageId;
        // get event bus and context manager
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // enable distance modal button by default
        this.distanceModalButton.prop('disabled', false);

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
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, (timeIndex) => {
            this.timePointMessage.text(timeIndex);
        });

        // display preprocess alert
        this.eventBus.subscribe(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS, () => {
            this.preprocessAlert.show();
        });

        // hide preprocess alert on completion of reset
        this.eventBus.subscribe(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_RESET, () => {
            this.preprocessAlert.hide();
        });

        // listen for distance form submission
        this.distanceForm.on('submit', this.handleDistanceFormSubmit.bind(this));

        // listen for remove distance plot button click
        this.distanceRemoveButton.on('click', this.handleDistanceRemoveButtonClick.bind(this));

        // add a data attribute so Cypress will automatically wait for that attribute to be present
		this.distanceModal.on('shown.bs.modal', (evt) => {
			evt.target.setAttribute('data-cy', 'modal')
		})

		// Remove the `data-cy` attribute when the modal is finished transitioning closed
		this.distanceModal.on('hidden.bs.modal', (evt) => {
			evt.target.removeAttribute('data-cy')
		})
    }

    // handle distance form submission
    async handleDistanceFormSubmit(event) {
        event.preventDefault();
        // show spinner
        this.spinner.show();
        try {
            const distanceMetric = this.distanceMetricSelect.val();
            const result = await this.contextManager.analysis.distance(
                distanceMetric, this.errorMessageId
            );
    
            if (result) {
                this.eventBus.publish(EVENT_TYPES.ANALYSIS.DISTANCE);
                this.distanceModal.modal('hide');
                this.distanceRemoveButton.prop('disabled', false);
            }
        } finally {
            this.spinner.hide();
        }
    }

    // handle remove distance plot button click
    handleDistanceRemoveButtonClick() {
        // publish distance remove event
        this.eventBus.publish(EVENT_TYPES.ANALYSIS.DISTANCE_REMOVE);
        // disable distance remove button
        this.distanceRemoveButton.prop('disabled', true);
    }
}

export default DistanceModal;
