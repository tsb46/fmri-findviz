// PeakFinder.js
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { getTimeCourseLabels, getTaskConditions } from '../../api/data.js';
import { checkTsPreprocessed } from '../../api/plot.js';
import { findPeaks } from '../../api/analysis.js';


class PeakFinder {
    /**
     * Constructor for PeakFinder class
     * @param {string} peakFinderPopOverId - The ID of the peak finder popover
     * @param {string} peakFinderTimeCourseSelectId - The ID of the time course select for the peak finder
     * @param {string} submitPeakFinderId - The ID of the submit button for the peak finder
     * @param {string} peakFinderFormId - The ID of the form for the peak finder
     * @param {string} peakFinderPrepAlertId - The ID of the preprocess alert for the peak finder
     * @param {ViewerEvents} eventBus - The event bus
     */
    constructor(
        peakFinderPopOverId,
        peakFinderTimeCourseSelectId,
        submitPeakFinderId,
        peakFinderFormId,
        peakFinderPrepAlertId,
        eventBus
    ) {
        // set ids
        this.peakFinderPopOverId = peakFinderPopOverId;
        this.peakFinderTimeCourseSelectId = peakFinderTimeCourseSelectId;
        this.submitPeakFinderId = submitPeakFinderId;
        this.peakFinderFormId = peakFinderFormId;
        this.peakFinderPrepAlertId = peakFinderPrepAlertId;
        this.eventBus = eventBus;

        // set elements
        this.peakFinderPopOver = $(`#${peakFinderPopOverId}`);

        // time course types
        this.timeCourseTypes = {};
        // initialize selected time course
        this.selectedTimeCourse = null;
        // initilize peak finder params
        this.peakFinderParams = {
            'peak_height': '',
            'peak_threshold': '',
            'peak_distance': '1.0',
            'peak_prominence': '',
            'peak_width': '',
            'zscore': false
        };
        // initialize peak finder popover
        this.initializePeakFinderPopOver();
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
        await getTimeCourseLabels((ts_labels) => {
            for (const label of ts_labels) {
                labels.push(label);
                this.timeCourseTypes[label] = 'timecourse';
            }
        });
        if (callback) {
            callback(labels);
        }
        return labels;
    }

    /**
     * Initialize the peak finder popover
     */
    initializePeakFinderPopOver() {
        this.peakFinderPopOver.on('shown.bs.popover', () => {
            console.log('peak finder popover shown');
            const popoverContent = $('.popover');
            popoverContent.find('.toggle-immediate').tooltip({
                html: true, // Enable HTML content in the tooltip
                trigger : 'hover'
            });

            const peakFinderTimeCourseSelect = $(`#${this.peakFinderTimeCourseSelectId}`);
            const peakFinderSubmit = $(`#${this.submitPeakFinderId}`);
            const peakFinderForm = $(`#${this.peakFinderFormId}`);

            // fill time course select with labels
            this.fillPeakFinderTimeCourseSelect(peakFinderTimeCourseSelect);

            // fill peak finder form with current params
            this.fillPeakFinderForm();

            // Hide popover when clicking outside
            // Store reference to this
            const self = this;
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest(`.popover, #${self.peakFinderPopOverId}`).length) {
                    $(`#${self.peakFinderPopOverId}`).popover('hide');
                }
            });

            // handle time course select change
            peakFinderTimeCourseSelect.on('change', () => {
                this.handleTimeCourseSelectChange(peakFinderTimeCourseSelect);
            });

            // initialize peak finder click compute button
            peakFinderSubmit.on(
                'click', 
                this.handlePeakFinderSubmit.bind(
                    this,
                    peakFinderForm, 
                    peakFinderTimeCourseSelect
                )
            );
        });
    }

    /**
     * Fill the peak finder form with the current peak finder params
     */
    fillPeakFinderForm() {
        const peakFinderForm = $(`#${this.peakFinderFormId}`);
        peakFinderForm.find('#peak-height').val(this.peakFinderParams['peak_height']);
        peakFinderForm.find('#peak-threshold').val(this.peakFinderParams['peak_threshold']);
        peakFinderForm.find('#peak-distance').val(this.peakFinderParams['peak_distance']);
        peakFinderForm.find('#peak-prominence').val(this.peakFinderParams['peak_prominence']);
        peakFinderForm.find('#peak-width').val(this.peakFinderParams['peak_width']);
        peakFinderForm.find('#peak-z-score').prop('checked', this.peakFinderParams['zscore']);
    }

    /**
     * Fill the peak finder time course select with labels
     * @param {jQuery} peakFinderTimeCourseSelect - The peak finder time course select
     */
    fillPeakFinderTimeCourseSelect(peakFinderTimeCourseSelect) {
        this.getPlotLabels((ts_labels) => {
            peakFinderTimeCourseSelect.empty();
            for (const label of ts_labels) {
                peakFinderTimeCourseSelect.append(`<option value='${label}'>${label}</option>`);
            }
            // select the last label as the selected time course
            peakFinderTimeCourseSelect.val(ts_labels[ts_labels.length - 1]);
            this.selectedTimeCourse = ts_labels[ts_labels.length - 1];
            // check if time course is preprocessed
            checkTsPreprocessed(
                this.selectedTimeCourse, 
                this.timeCourseTypes[this.selectedTimeCourse], 
                (isPreprocessed) => {
                    if (isPreprocessed.is_preprocessed) {
                        $(`#${this.peakFinderPrepAlertId}`).show();
                    }
                }
            );
        });
    }

    /**
     * Handle time course select change
     * @param {Event} event - The event object
     * @param {jQuery} peakFinderTimeCourseSelect - The peak finder time course select
     */
    handleTimeCourseSelectChange(peakFinderTimeCourseSelect) {
        console.log('time course select changed for peak finder');
        // get selected time course
        const timeCourse = peakFinderTimeCourseSelect.val();
        this.selectedTimeCourse = timeCourse;
        // check if time course is preprocessed
        checkTsPreprocessed(timeCourse, this.timeCourseTypes[timeCourse], (isPreprocessed) => {
            if (isPreprocessed.is_preprocessed) {
                $(`#${this.peakFinderPrepAlertId}`).show();
            } else {
                $(`#${this.peakFinderPrepAlertId}`).hide();
            }
        });
    }
    /**
     * Handle the peak finder submit
     * @param {Event} event - The event object
     * @param {jQuery} peakFinderTimeCourseSelect - The peak finder time course select
     */
    handlePeakFinderSubmit(peakFinderForm, peakFinderTimeCourseSelect) {
        console.log('peak finder submit button clicked');
        // get selected time course
        const timeCourse = peakFinderTimeCourseSelect.val();
        const timeCourseType = this.timeCourseTypes[timeCourse];
        const peakFinderParams = {
            'peak_height': peakFinderForm.find('#peak-height').val(),
            'peak_threshold': peakFinderForm.find('#peak-threshold').val(),
            'peak_distance': peakFinderForm.find('#peak-distance').val(),
            'peak_prominence': peakFinderForm.find('#peak-prominence').val(),
            'peak_width': peakFinderForm.find('#peak-width').val(),
            'zscore': peakFinderForm.find('#peak-z-score').is(':checked')
        }
        // update peak finder params
        this.peakFinderParams = peakFinderParams;
        // find peaks
        findPeaks(timeCourse, timeCourseType, peakFinderParams, () => {
            console.log('peak finder success');
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_ADDED);
        });

        // hide popover
        this.peakFinderPopOver.popover('hide');
    }
}

export default PeakFinder;
