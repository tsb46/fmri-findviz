// timeConvert.js
// This component is used to toggle between displaying the time courses 
// in time points or seconds

import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import ContextManager from '../../api/ContextManager.js';


class TimeConvert {
    /**
     * @param {string} trConvertFormId - The ID of the form element
     * @param {string} trConvertButtonId - The ID of the button element
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        trConvertFormId,
        trConvertButtonId,
        eventBus,
        contextManager
    ) {
        this.trConvertForm = $(`#${trConvertFormId}`);
        this.trConvertButton = $(`#${trConvertButtonId}`);
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // initialize TR convert state
        this.trConvertOn = false;
        // initialize TR convert form
        this.initializeTrConvertForm();

        // attach event listeners
        this.attachEventListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // attach click event listener to TR convert button
        this.trConvertButton.on('click', async () => {
            // toggle TR convert state
            this.trConvertOn = !this.trConvertOn;
            // update TR
            const tr = this.trConvertForm.val();
            if (tr !== '') {
                // update fmri plot options
                await this.contextManager.plot.updateFmriPlotOptions({
                    tr_convert_on: this.trConvertOn
                });
                // update TR
                await this.contextManager.data.updateTr(tr);
                // convert timepoints
                await this.contextManager.data.convertTimepoints();
                // publish TR event
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.FMRI.TR_CONVERT_BUTTON_CLICK,
                    {
                        tr_convert_on: this.trConvertOn
                    }
                );
            }
        });

        // enable/disable TR convert button if form is not empty
        this.trConvertForm.on('change', () => {
            if (this.trConvertForm.val() !== '') {
                this.trConvertButton.prop('disabled', false);
            } else {
                this.trConvertButton.prop('disabled', true);
            }
        });
    }

    /**
     * Initialize TR convert form
     */
    async initializeTrConvertForm() {
        // get TR convert state from context manager
        const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
        // set TR convert form value
        this.trConvertState = plotOptions.tr_convert_on;
        // if form is empty, disable button
        if (this.trConvertForm.val() === '') {
            this.trConvertButton.prop('disabled', true);
        }
    }
}

export default TimeConvert;