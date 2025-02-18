// TimeCourseFmri.js
// Handles addition and removal events of fmri time courses to plot
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { popFmriTimecourse, removeFmriTimecourses } from '../../api/data.js';

class TimeCourseFmri {
    constructor(
        enableFmriTimeCourseButtonId,
        timeCourseRemoveButtonId,
        timeCourseUndoButtonId,
        timeCourseFreezeButtonId,
    ) {
        this.enableFmriTimeCourseButton = $(`#${enableFmriTimeCourseButtonId}`);
        this.timeCourseRemoveButton = $(`#${timeCourseRemoveButtonId}`);
        this.timeCourseUndoButton = $(`#${timeCourseUndoButtonId}`);
        this.timeCourseFreezeButton = $(`#${timeCourseFreezeButtonId}`);

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
        });

        // undo most recent fmri time course
        this.timeCourseUndoButton.on('click', () => {
            console.log('fmri time course undo button clicked');
            popFmriTimecourse(() => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.UNDO_FMRI_TIMECOURSE
                );
            });
        });

        // remove all fmri time courses
        this.timeCourseRemoveButton.on('click', () => {
            console.log('fmri time course remove button clicked');
            removeFmriTimecourses(() => {
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TIMECOURSE.REMOVE_FMRI_TIMECOURSE
                );
            });
        });

        // freeze currently plotted fmri time course
        this.timeCourseFreezeButton.on('click', () => {
            console.log('fmri time course freeze button clicked');
            this.timeCourseFreeze = !this.timeCourseFreeze;
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.TIMECOURSE.FREEZE_FMRI_TIMECOURSE,
                this.timeCourseFreeze
            );
        });
    }
}

export default TimeCourseFmri;
