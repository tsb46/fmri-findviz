// PeakFinder.js
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { getTimeCourseLabels, getTaskConditions } from '../../api/data.js';
import { findPeaks } from '../../api/analysis.js';


class PeakFinder {
    /**
     * Constructor for PeakFinder class
     * @param {string} peakFinderPopOverId - The ID of the peak finder popover
     * @param {string} peakFinderTimeCourseSelectId - The ID of the time course select for the peak finder
     * @param {string} submitPeakFinderId - The ID of the submit button for the peak finder
     * @param {string} peakFinderFormId - The ID of the form for the peak finder
     */
    constructor(
        peakFinderPopOverId,
        peakFinderTimeCourseSelectId,
        submitPeakFinderId,
        peakFinderFormId
    ) {
        this.peakFinderPopOver = $(`#${peakFinderPopOverId}`);
        this.peakFinderTimeCourseSelect = $(`#${peakFinderTimeCourseSelectId}`);
        this.submitPeakFinder = $(`#${submitPeakFinderId}`);
        this.peakFinderForm = $(`#${peakFinderFormId}`);

        // time course types
        this.timeCourseTypes = {};
        // initialize peak finder popover
        this.initializePeakFinderPopOver();

        // listen for addition of fmri time courses and update time course select
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.TIMECOURSE.ADD_FMRI_TIMECOURSE, () => {
            this.fillPeakFinderTimeCourseSelect();
        });
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
            // fill time course select with labels
            this.fillPeakFinderTimeCourseSelect();

            // Hide popover when clicking outside
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest(`.popover, #${this.peakFinderPopOverId}`).length) {
                  this.peakFinderPopOver.popover('hide');
                }
            });

            // initialize peak finder submit
            this.peakFinderForm.on(
                'submit', this.handlePeakFinderSubmit.bind(this)
            );
        });
    }

    /**
     * Fill the peak finder time course select with labels
     */
    fillPeakFinderTimeCourseSelect() {
        this.getPlotLabels((labels) => {
            this.peakFinderTimeCourseSelect.empty();
            for (const label of labels) {
                this.peakFinderTimeCourseSelect.append(`<option value='${label}'>${label}</option>`);
            }
        });
    }

    /**
     * Handle the peak finder submit
     * @param {Event} event - The event object
     */
    handlePeakFinderSubmit(event) {
        event.preventDefault();
        console.log('peak finder submit button clicked');
        // get selected time course
        const timeCourse = this.peakFinderTimeCourseSelect.val();
        const timeCourseType = this.timeCourseTypes[timeCourse];
        const peakFinderParams = {
            'peak_height': this.peakFinderForm.find('#peak-height').val(),
            'peak_threshold': this.peakFinderForm.find('#peak-threshold').val(),
            'peak_distance': this.peakFinderForm.find('#peak-distance').val(),
            'peak_prominence': this.peakFinderForm.find('#peak-prominence').val(),
            'peak_width': this.peakFinderForm.find('#peak-width').val(),
        }
        findPeaks(timeCourse, timeCourseType, peakFinderParams, () => {
            console.log('peak finder success');
            eventBus.publish(EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_ADDED);
        });

        // hide popover
        this.peakFinderPopOver.popover('hide');
    }
}

export default PeakFinder;
