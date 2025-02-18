import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { initializeSingleSlider } from '../sliders.js';
import eventBus from '../../events/ViewerEvents.js';
import { getViewerMetadata, updateTimepoint } from '../../api/data.js';

class TimeSlider {
    /**
     * Constructor for TimeSlider
     * @param {string} displayText - The display text
     * @param {string} timeSliderId - The ID of the time slider
     * @param {string} timeSliderTitle - The title of the time slider
     * @param {string} timeSliderTitleId - The ID of the time slider title
     */
    constructor(
        displayText,
        timeSliderId,
        timeSliderTitle,
        timeSliderTitleId
    ) {

        this.displayText = displayText;
        this.timeSliderId = timeSliderId;
        this.timeSlider = $(`#${this.timeSliderId}`);
        this.timeSliderTitle = $(`#${timeSliderTitleId}`);

        // display time slider title
        this.timeSliderTitle.text(timeSliderTitle);

        // get timepoint array from viewer metadata
        getViewerMetadata(
            (metadata) => {
                this.timePoints = metadata.timepoints;
                // Initialize time slider
                this.initializeTimeSlider(this.timePoints)
            }
        );
        
        // Attach the `slide` event listener (for when the slider value changes)
        this.timeSlider.on('change', this.handleSlide.bind(this));
    }

    /**
     * Initialize time slider
     * @param {Array} timePoints - The time points
     */
    initializeTimeSlider(timePoints) {
        // Get display text for formatter
        const displayText = this.displayText;
        // get time point to display text converter
        const timeToDisplay = {}
        this.timePoints.forEach((item, index) => {
          timeToDisplay[index] = item
        });
        // formatter function
        const formatter = function(value) {
            return displayText + timeToDisplay[value];
        }
        // initialize time slider
        initializeSingleSlider(
            this.timeSliderId,
            0,
            [0, timePoints.length - 1],
            1,
            formatter
        );
    }

    /**
     * Handle slider change
     */
    async handleSlide() {
        console.log('time slider changed');
        const timeIndex = this.timeSlider.slider('getValue');
        // update time point
        await updateTimepoint(timeIndex);

        // Trigger a time slider change event
        eventBus.publish(
            EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, 
            timeIndex
        );
    }
}

export default TimeSlider;
