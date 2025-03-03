// PreprocessTimeCourse.js - Preprocessing for timecourse data
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { getPreprocessedTimeCourse, resetTimeCoursePreprocess } from '../../api/preprocess.js';
import { getTimeCourseLabels, getTimeCourseLabelsPreprocessed } from '../../api/data.js';

class PreprocessTimeCourse {
    /**
     * Constructor for PreprocessTimeCourse class
     * @param {string} timeCoursePrepMenuId - ID of time course prep menu
     * @param {string} normSwitchId - ID of normalization switch
     * @param {string} filterSwitchId - ID of filtering switch
     * @param {string} prepSubmitId - ID of preprocessing submit button
     * @param {string} prepResetId - ID of preprocessing reset button
     * @param {string} meanCenterId - ID of mean center checkbox
     * @param {string} zScoreId - ID of z-score checkbox
     * @param {string} TRId - ID of TR input
     * @param {string} lowCutId - ID of low cut input
     * @param {string} highCutId - ID of high cut input
     * @param {string} errorInlineId - ID of error message inline
     * @param {string} preprocessAlertId - ID of preprocess alert div
     * @param {ViewerEvents} eventBus - The event bus
     */
    constructor(
        timeCoursePrepMenuId,
        normSwitchId,
        filterSwitchId,
        prepSubmitId,
        prepResetId,
        meanCenterId,
        zScoreId,
        TRId,
        lowCutId,
        highCutId,
        errorInlineId,
        preprocessAlertId,
        eventBus
    ) {
        // get time course prep menu
        this.timeCoursePrepMenu = $(`#${timeCoursePrepMenuId}`);
        // get preprocessing switches
        this.normSwitch = $(`#${normSwitchId}`);
        this.filterSwitch = $(`#${filterSwitchId}`);
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
        // get error message div
        this.errorInlineId = errorInlineId;
        // get preprocess alert div
        this.preprocessAlert = $(`#${preprocessAlertId}`);
        // get event bus
        this.eventBus = eventBus;
        // Set states of preprocessing switches
        this.normSwitchEnabled = false;
        this.filterSwitchEnabled = false;
        // initialize preprocessing switches
        this.initializeSwitches();
        // initialize preprocessing submit button event
        this.prepSubmit.on('click', (event) => this.handlePreprocessSubmit(event));
        // initialize preprocessing reset button event
        this.prepReset.on('click', (event) => this.handlePreprocessReset(event));
        // initialize time course preprocessing selection menu
        this.initializeTimeCoursePrepSelect();
        // attach event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Listen for addition and removal of fmri time courses
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE, 
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE,
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE
            ],
            () => {
                // clear all options from the select menu
                this.timeCoursePrepMenu.empty();
                // destroy and reinitialize bootstrap-select
                this.timeCoursePrepMenu.selectpicker('destroy');
                // initialize time course prep menu with fresh options
                this.initializeTimeCoursePrepSelect();
            }
        );
    }

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
    }

    /**
     * Initialize time course preprocessing selection menu
     */
    initializeTimeCoursePrepSelect() {
        // get time course labels
        getTimeCourseLabels((labels) => {
            // Loop through time courses and append label to select dropdown menu
            for (let ts of labels) {
                const label = ts;
                let newOption = $('<option>', { value: label, text: label });
                this.timeCoursePrepMenu.append(newOption);
            };
            // hack to remove duplicates due to bug
            //https://github.com/snapappointments/bootstrap-select/issues/2738
            this.timeCoursePrepMenu.selectpicker('destroy');
            this.timeCoursePrepMenu.selectpicker();
        });
    }

    /**
     * Handle preprocessing submit button event
     * @param {Event} event - event object
     */
    handlePreprocessSubmit(event) {
        event.preventDefault();
        console.log('preprocess submit button clicked');
        // get selected time courses
        const selectedTimeCourses = this.timeCoursePrepMenu.val();
        // get preprocess params
        const preprocessParams = {
            normalize: this.normSwitchEnabled,
            filter: this.filterSwitchEnabled,
            detrend: false,
            mean_center: this.meanCenter.prop('checked'),
            zscore: this.zScore.prop('checked'),
            tr: this.TR.val(),
            low_cut: this.lowCut.val(),
            high_cut: this.highCut.val(),
            ts_labels: selectedTimeCourses
        }
        // preprocess timecourse
        getPreprocessedTimeCourse(preprocessParams, this.errorInlineId, () => {
            this.eventBus.publish(
                EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_SUCCESS, 
                selectedTimeCourses
            );
            // show preprocess alert
            this.preprocessAlert.css("display", "block");
        });
        
    }

    /**
     * Handle preprocessing reset button event
     * @param {Event} event - event object
     */
    async handlePreprocessReset(event) {
        event.preventDefault();
        console.log('preprocess reset button clicked');
        // Set switches to disabled
        this.normSwitch.prop('checked', false);
        this.filterSwitch.prop('checked', false);
        this.normSwitchEnabled = false;
        this.filterSwitchEnabled = false;
        // clear parameters
        this.meanCenter.prop('checked', false);
        this.meanCenter.prop('disabled', true);
        this.zScore.prop('checked', false);
        this.zScore.prop('disabled', true);
        this.TR.val('');
        this.TR.prop('disabled', true);
        this.lowCut.val('');
        this.lowCut.prop('disabled', true);
        this.highCut.val('');
        this.highCut.prop('disabled', true);
        
        // clear error message (if any)
        const errorInline = $(`#${this.errorInlineId}`);
        errorInline.text('');
        errorInline.hide();
        // get selected time courses
        const selectedTimeCourses = this.timeCoursePrepMenu.val();
        // reset preprocess
        resetTimeCoursePreprocess(selectedTimeCourses, this.errorInlineId, () => {
            this.eventBus.publish(
                EVENT_TYPES.PREPROCESSING.PREPROCESS_TIMECOURSE_RESET,
                selectedTimeCourses
            );
            // hide preprocess alert
            this.preprocessAlert.css("display", "none");
        });
    }
}

export default PreprocessTimeCourse;