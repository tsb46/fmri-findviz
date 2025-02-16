// PreprocessFmri.js - Preprocessing for FMRI data
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { getPreprocessedFMRI, resetFMRIPreprocess } from '../../api/preprocess.js';

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
     * @param {string} TRId - ID of TR input
     * @param {string} lowCutId - ID of low cut input
     * @param {string} highCutId - ID of high cut input
     * @param {string} smoothFwhmId - ID of smooth FWHM input
     * @param {string} errorInlineId - ID of error message inline
     * @param {string} preprocessAlertId - ID of preprocess alert div
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
        TRId,
        lowCutId,
        highCutId,
        smoothFwhmId,
        errorInlineId,
        preprocessAlertId
    ) {
        this.fmriFileType = fmriFileType;
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
        // initialize preprocessing switches
        this.initializeSwitches();
    }

    /**
     * Initialize preprocessing switches
     */
    initializeSwitches() {
        // Enable normalization switch
        this.normSwitch.on('click', () => {
            this.normSwitchEnabled = !this.normSwitchEnabled
            const inputsNorm = [this.meanCenter, this.zScore];
            inputsNorm.forEach(
                input => this.normSwitchEnabled ? input.disabled = false : input.disabled = true
            );
        });

        // Enable filtering switch
        this.filterSwitch.on('click', () => {
            this.filterSwitchEnabled = !this.filterSwitchEnabled
            const inputsFilter = [this.lowCut, this.highCut, this.TR];
            inputsFilter.forEach(
                input => this.filterSwitchEnabled ? input.disabled = false : input.disabled = true
            );
        });

        // Enable smoothing switch, smoothing only available for volumes (nifti)
        if (this.fmriFileType == 'nifti') {
            this.smoothSwitch.on('click', () => {
                this.smoothSwitchEnabled = !this.smoothSwitchEnabled;
                const inputSmooth = this.smoothFwhm;
                if (this.smoothSwitchEnabled) {
                    inputSmooth.disabled = false
                } else {
                    inputSmooth.disabled = true
                }
            });
        }
        else {
            // Disable smoothing switch
            this.smoothSwitch.attr('disabled', true)
        }
    }

    /**
     * Handle preprocessing submit button event
     * @param {Event} event - event object
     */
    handlePreprocessSubmit(event) {
        event.preventDefault();
        console.log('preprocess submit button clicked');
        // get preprocess params
        const preprocessParams = {
            normalize: this.normSwitchEnabled,
            filter: this.filterSwitchEnabled,
            smooth: this.smoothSwitchEnabled,
            detrend: false,
            mean_center: this.meanCenter.val(),
            zscore: this.zScore.val(),
            tr: this.TR.val(),
            low_cut: this.lowCut.val(),
            high_cut: this.highCut.val(),
            fwhm: this.smoothFwhm.val()
        }
        // preprocess FMRI
        getPreprocessedFMRI(preprocessParams, this.errorInlineId, (response) => {
            eventBus.publish(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS);
        });
        // show preprocess alert
        this.preprocessAlert.css("display", "block");
    }

    /**
     * Handle preprocessing reset button event
     * @param {Event} event - event object
     */
    handlePreprocessReset(event) {
        event.preventDefault();
        console.log('preprocess reset button clicked');
        // Set switches to disabled
        this.normSwitch.prop('checked', false);
        this.filterSwitch.prop('checked', false);
        this.smoothSwitch.prop('checked', false);
        this.normSwitchEnabled = false;
        this.filterSwitchEnabled = false;
        this.smoothSwitchEnabled = false;
        // clear parameters
        this.meanCenter.val('');
        this.zScore.val('');
        this.TR.val('');
        this.lowCut.val('');
        this.highCut.val('');
        this.smoothFwhm.val('');
        // reset preprocess
        resetFMRIPreprocess(this.errorInlineId, () => {
            eventBus.publish(EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_RESET);
            // hide preprocess alert
            this.preprocessAlert.css("display", "none");
        });
    }

}

export default PreprocessFmri;