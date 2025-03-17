// PreprocessFmri.js - Preprocessing for FMRI data
import { DOM_IDS } from '../../../constants/DomIds.js';
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import Spinner from '../../../Spinner.js';
import ContextManager from '../../api/ContextManager.js';


class PreprocessFmri {
    /**
     * Constructor for PreprocessFmri class
     * @param {string} fmriFileType - type of FMRI file
     * @param {string} normSwitchId - ID of normalization switch
     * @param {string} filterSwitchId - ID of filtering switch
     * @param {string} smoothSwitchId - ID of smoothing switch
     * @param {string} prepSubmitId - ID of preprocessing submit button
     * @param {string} prepResetId - ID of preprocessing reset button
     * @param {string} meanCenterId - ID of mean center checkbox
     * @param {string} zScoreId - ID of z-score checkbox
     * @param {string} detrendId - ID of detrend checkbox
     * @param {string} TRId - ID of TR input
     * @param {string} lowCutId - ID of low cut input
     * @param {string} highCutId - ID of high cut input
     * @param {string} smoothFwhmId - ID of smooth FWHM input
     * @param {string} errorInlineId - ID of error message inline
     * @param {string} preprocessAlertId - ID of preprocess alert div
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        fmriFileType,
        normSwitchId,
        filterSwitchId,
        smoothSwitchId,
        prepSubmitId,
        prepResetId,
        meanCenterId,
        zScoreId,
        detrendId,
        TRId,
        lowCutId,
        highCutId,
        smoothFwhmId,
        errorInlineId,
        preprocessAlertId,
        eventBus,
        contextManager
    ) {
        this.fmriFileType = fmriFileType;
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // get preprocessing switches
        this.normSwitch = $(`#${normSwitchId}`);
        this.filterSwitch = $(`#${filterSwitchId}`);
        this.smoothSwitch = $(`#${smoothSwitchId}`);
        // get preprocessing submit button
        this.prepSubmit = $(`#${prepSubmitId}`);
        // get preprocessing reset button
        this.prepReset = $(`#${prepResetId}`);
        // get parameters for preprocessing
        this.meanCenter = $(`#${meanCenterId}`);
        this.zScore = $(`#${zScoreId}`);
        this.detrend = $(`#${detrendId}`);
        this.TR = $(`#${TRId}`);
        this.lowCut = $(`#${lowCutId}`);
        this.highCut = $(`#${highCutId}`);
        this.smoothFwhm = $(`#${smoothFwhmId}`);
        // get error message div
        this.errorInlineId = errorInlineId;
        // get preprocess alert div
        this.preprocessAlert = $(`#${preprocessAlertId}`);
        // Set states of preprocessing switches
        this.normSwitchEnabled = false;
        this.filterSwitchEnabled = false;
        this.smoothSwitchEnabled = false;
        // enable all buttons by default
        this.enableAllButtons();

        // initialize spinner
        this.spinner = new Spinner(
            DOM_IDS.SPINNERS.OVERLAY, 
            DOM_IDS.SPINNERS.WHEEL
        );
        // check if fmri data is preprocessed
        this.checkPreprocess();
        // initialize preprocessing switches
        this.initializeSwitches();
        // initialize preprocess submit
        this.prepSubmit.on('click', (event) => this.handlePreprocessSubmit(event));
        // initialize preprocess reset
        this.prepReset.on('click', (event) => this.handlePreprocessReset(event));
    }

    /**
     * Check if fmri data is preprocessed
     */
    async checkPreprocess() {
        const preprocessed = await this.contextManager.plot.checkFmriPreprocessed();
        if (preprocessed.is_preprocessed) {
            // show preprocess alert
            this.preprocessAlert.css("display", "block");
        }
    }

    /**
     * Enable all buttons
     */
    enableAllButtons() {
        this.normSwitch.prop('disabled', false);
        this.filterSwitch.prop('disabled', false);
        this.smoothSwitch.prop('disabled', false);
        this.detrend.prop('disabled', false);
        this.prepSubmit.prop('disabled', false);
        this.prepReset.prop('disabled', false);
    }

    /**
     * Disable all buttons
     */
    disableAllButtons() {
        this.normSwitch.prop('disabled', true);
        this.filterSwitch.prop('disabled', true);
        this.smoothSwitch.prop('disabled', true);
        this.detrend.prop('disabled', true);
        this.prepSubmit.prop('disabled', true);
        this.prepReset.prop('disabled', true);
    }

    /**
     * Initialize preprocessing switches
     */
    initializeSwitches() {
        // Enable normalization switch
        this.normSwitch.on('click', () => {
            this.normSwitchEnabled = !this.normSwitchEnabled
            const inputsNorm = [this.meanCenter, this.zScore];
            // Enable/disable bootstrap radio buttons
            inputsNorm.forEach(input => {
                if (this.normSwitchEnabled) {
                    input.prop('disabled', false);
                    input.closest('.custom-control').removeClass('disabled');
                } else {
                    input.prop('checked', false);
                    input.prop('disabled', true); 
                    input.closest('.custom-control').addClass('disabled');
                }
            });
        });

        // Enable filtering switch
        this.filterSwitch.on('click', () => {
            this.filterSwitchEnabled = !this.filterSwitchEnabled
            const inputsFilter = [this.lowCut, this.highCut, this.TR];
            inputsFilter.forEach(input => {
                if (this.filterSwitchEnabled) {
                    input.prop('disabled', false);
                    input.closest('.custom-control').removeClass('disabled');
                } else {
                    input.prop('disabled', true); 
                    input.closest('.custom-control').addClass('disabled');
                }
            });
        });

        // Enable smoothing switch, smoothing only available for volumes (nifti)
        if (this.fmriFileType == 'nifti') {
            this.smoothSwitch.on('click', () => {
                this.smoothSwitchEnabled = !this.smoothSwitchEnabled;
                const inputSmooth = this.smoothFwhm;
                if (this.smoothSwitchEnabled) {
                    inputSmooth.prop('disabled', false);
                    inputSmooth.closest('.custom-control').removeClass('disabled');
                } else {
                    inputSmooth.prop('disabled', true);
                    inputSmooth.closest('.custom-control').addClass('disabled');
                }
            });
        }
        else {
            // Disable smoothing switch
            this.smoothSwitch.prop('disabled', true);
            this.smoothSwitch.closest('.custom-control').addClass('disabled');
        }
    }

    /**
     * Handle preprocessing submit button event
     * @param {Event} event - event object
     */
    async handlePreprocessSubmit(event) {
        event.preventDefault();
        console.log('preprocess submit button clicked');
        // get preprocess params
        const preprocessParams = {
            normalize: this.normSwitchEnabled,
            filter: this.filterSwitchEnabled,
            smooth: this.smoothSwitchEnabled,
            detrend: this.detrend.prop('checked'),
            mean_center: this.meanCenter.prop('checked'),
            zscore: this.zScore.prop('checked'),
            tr: this.TR.val(),
            low_cut: this.lowCut.val(),
            high_cut: this.highCut.val(),
            fwhm: this.smoothFwhm.val()
        }
        // show spinner
        this.spinner.show();
        // preprocess FMRI
        try {
            const result = await this.contextManager.preprocess.getPreprocessedFMRI(
                preprocessParams, 
                this.errorInlineId
            );
            if (result) {
                console.log('preprocessed FMRI successfully');
                // publish event
                this.eventBus.publish(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS);
            }
        } finally {
            this.spinner.hide();
            // show preprocess alert
            this.preprocessAlert.css("display", "block");
        }
    }

    /**
     * Handle preprocessing reset button event
     * @param {Event} event - event object
     */
    async handlePreprocessReset(event) {
        event.preventDefault();
        console.log('preprocess reset button clicked');
        // clear error message
        const errorInline = $(`#${this.errorInlineId}`);
        errorInline.css("display", "none");
        // Set switches to disabled
        this.normSwitch.prop('checked', false);
        this.filterSwitch.prop('checked', false);
        this.smoothSwitch.prop('checked', false);
        this.normSwitchEnabled = false;
        this.filterSwitchEnabled = false;
        this.smoothSwitchEnabled = false;
        // clear parameters
        this.detrend.prop('checked', false);
        this.meanCenter.prop('checked', false);
        this.zScore.prop('checked', false);
        this.TR.val('');
        this.lowCut.val('');
        this.highCut.val('');
        this.smoothFwhm.val('');
        // disable preprocessing parameters
        this.meanCenter.prop('disabled', true);
        this.zScore.prop('disabled', true);
        this.TR.prop('disabled', true);
        this.lowCut.prop('disabled', true);
        this.highCut.prop('disabled', true);
        this.smoothFwhm.prop('disabled', true);
        this.detrend.prop('disabled', true);
        // reset preprocess
        try {
            const result = await this.contextManager.preprocess.resetFMRIPreprocess(this.errorInlineId);
            if (result) {
                console.log('FMRI preprocessing reset successfully');
                // publish event
                this.eventBus.publish(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_RESET);
            }
        } finally {
            // hide preprocess alert
            this.preprocessAlert.css("display", "none");
        }
    }

}

export default PreprocessFmri;