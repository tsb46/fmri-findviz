import { EVENT_TYPES } from '../constants/EventTypes.js';
import { initializeSingleSlider } from './sliders.js';
import eventBus from '../events/ViewerEvents.js';
import { updateTimePoint } from '../api/plot.js';

class TimeSlider {
    /**
     * Constructor for TimeSlider
     * @param {Array} timePoints - The time points
     * @param {string} displayText - The display text
     * @param {string} timeSliderId - The ID of the time slider
     */
    constructor(
        timePoints, 
        displayText,
        timeSliderId
    ) {
        this.timePoints = timePoints;
        this.displayText = displayText;
        this.timeSliderId = timeSliderId;
        this.timeSlider = $(`#${this.timeSliderId}`);

        // Initialize time slider
        this.initializeTimeSlider(this.timePoints)

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
        const timeIndex = this.timeSlider.slider('getValue');
        // update time point
        await updateTimePoint(timeIndex);

        // Trigger a time slider change event
        eventBus.publish(EVENT_TYPES.VISUALIZATION.TIME_SLIDER_CHANGE, timeIndex);
    }
}

export default TimeSlider;
