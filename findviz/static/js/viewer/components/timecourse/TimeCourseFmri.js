// TimeCourseFmri.js
// Handles addition and removal events of fmri time courses to plot
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { popFmriTimeCourse, removeFmriTimeCourses } from '../../api/data.js';

class TimeCourseFmri {
    /**
     * Constructor for TimeCourseFmri
     * @param {string} enableFmriTimeCourseButtonId - The ID of the enable fmri time course button
     * @param {string} timeCourseRemoveButtonId - The ID of the remove fmri time course button
     * @param {string} timeCourseUndoButtonId - The ID of the undo fmri time course button
     * @param {string} timeCourseFreezeButtonId - The ID of the freeze fmri time course button
     */
    constructor(
        enableFmriTimeCourseButtonId,
        timeCourseRemoveButtonId,
        timeCourseUndoButtonId,
        timeCourseFreezeButtonId,
        freezeIconId
    ) {
        this.enableFmriTimeCourseButton = $(`#${enableFmriTimeCourseButtonId}`);
        this.timeCourseRemoveButton = $(`#${timeCourseRemoveButtonId}`);
        this.timeCourseUndoButton = $(`#${timeCourseUndoButtonId}`);
        this.timeCourseFreezeButton = $(`#${timeCourseFreezeButtonId}`);
        this.freezeIcon = $(`#${freezeIconId}`);

        // initialize fmri time course plot states
        this.timeCourseEnabled = false;
        this.timeCourseFreeze = false;

        // attach event listeners
        this.attachEventListeners();
    }

    /**
     * Attach event listeners for fmri time course plotting functionality
     */
    attachEventListeners() {
        // enable fmri time course plotting
        this.enableFmriTimeCourseButton.on('click', () => {
            console.log('fmri time course enable button clicked');
            this.timeCourseEnabled = !this.timeCourseEnabled;
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.ENABLE_FMRI_TIMECOURSE, 
                this.timeCourseEnabled
            );
            // enable/disable freeze, undo and remove buttons
            if (this.timeCourseEnabled) {
                this.timeCourseFreezeButton.prop('disabled', false);
                this.timeCourseUndoButton.prop('disabled', false);
                this.timeCourseRemoveButton.prop('disabled', false);
            } else {
                this.timeCourseFreezeButton.prop('disabled', true);
                this.timeCourseUndoButton.prop('disabled', true);
                this.timeCourseRemoveButton.prop('disabled', true);
            }
        });

        // undo most recent fmri time course
        this.timeCourseUndoButton.on('click', async () => {
            console.log('fmri time course undo button clicked');
            const lastFmriLabel = await popFmriTimeCourse();
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE,
                lastFmriLabel.label
            );
        });

        // remove all fmri time courses
        this.timeCourseRemoveButton.on('click', async () => {
            console.log('fmri time course remove button clicked');
            const fmriLabels = await removeFmriTimeCourses();
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE,
                fmriLabels.labels
            );
        });

        // freeze currently plotted fmri time course
        this.timeCourseFreezeButton.on('click', () => {
            console.log('fmri time course freeze button clicked');
            this.timeCourseFreeze = !this.timeCourseFreeze;
            if (this.timeCourseFreeze) {
                console.log('freezing fmri time course selections');
                // toggle icon to lock
                this.freezeIcon.removeClass('fa-unlock');
                this.freezeIcon.addClass('fa-lock');
            } else {
                console.log('unfreezing fmri time course selections');
                // toggle icon to unlock
                this.freezeIcon.removeClass('fa-lock');
                this.freezeIcon.addClass('fa-unlock');
            }

            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.FREEZE_FMRI_TIMECOURSE,
                this.timeCourseFreeze
            );
        });
    }
}

export default TimeCourseFmri;
