import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { initializeSingleSlider } from '../sliders.js';
import ContextManager from '../../api/ContextManager.js';

class TimeSlider {
    /**
     * Constructor for TimeSlider
     * @param {string} displayText - The display text
     * @param {string} timeSliderId - The ID of the time slider
     * @param {string} timeSliderTitle - The title of the time slider
     * @param {string} timeSliderTitleId - The ID of the time slider title
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        displayText,
        timeSliderId,
        timeSliderTitle,
        timeSliderTitleId,
        eventBus,
        contextManager
    ) {

        this.displayText = displayText;
        this.timeSliderId = timeSliderId;
        this.timeSlider = $(`#${this.timeSliderId}`);
        this.timeSliderTitle = $(`#${timeSliderTitleId}`);
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // display time slider title
        this.timeSliderTitle.text(timeSliderTitle);

        // Initialize time slider
        this.initializeTimeSlider();
    }

    /**
     * Initialize time slider
     */
    async initializeTimeSlider() {
        const metadata = await this.contextManager.data.getViewerMetadata();
        this.timePoints = metadata.timepoints;
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
            [0, this.timePoints.length - 1],
            1,
            formatter
        );
         // Attach the `slide` event listener (for when the slider value changes)
         this.timeSlider.on('change', this.handleSlide.bind(this));
    }

    /**
     * Handle slider change
     */
    async handleSlide() {
        const timeIndex = this.timeSlider.slider('getValue');
        console.log(`time slider changed to ${timeIndex}`);
        // update time point
        await this.contextManager.data.updateTimepoint(timeIndex);

        // Trigger a time slider change event
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.FMRI.TIME_SLIDER_CHANGE, 
            timeIndex
        );
    }
}

export default TimeSlider;
