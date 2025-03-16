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
     * @param {string} timePointDisplayId - The ID of the time point display
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        displayText,
        timeSliderId,
        timeSliderTitle,
        timeSliderTitleId,
        timePointDisplayId,
        eventBus,
        contextManager
    ) {

        this.displayText = displayText;
        this.timeSliderId = timeSliderId;
        this.timeSlider = $(`#${this.timeSliderId}`);
        this.timeSliderTitle = $(`#${timeSliderTitleId}`);
        this.timePointDisplay = $(`#${timePointDisplayId}`);
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // display time slider title
        this.timeSliderTitle.text(timeSliderTitle);

        // Initialize time slider
        this.initializeTimeSlider();

        // Attach event listeners
        this.attachEventListeners();
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // attach change event listener to time slider
        this.timeSlider.on('change', this.handleSlide.bind(this));

        // listen for time point conversion event
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.TR_CONVERT_BUTTON_CLICK,
            (conversionState) => {
                this.handleTimePointConversion(conversionState);
            }
        );
    }

    /**
     * Initialize time slider
     */
    async initializeTimeSlider() {
        // get time points
        const timePointsResponse = await this.contextManager.data.getTimePoints();
        this.timePoints = timePointsResponse.timepoints;
        // get selected time point
        const selectedTimePointResponse = await this.contextManager.data.getTimePoint();
        const selectedTimePoint = selectedTimePointResponse.timepoint;
        // Get display text for formatter
        const displayText = this.displayText;
        const timePoints = this.timePoints;
        // formatter function
        const formatter = function(value) {
            return displayText + timePoints[value];
        }
        // initialize time slider
        initializeSingleSlider(
            this.timeSliderId,
            selectedTimePoint,
            [0, timePoints.length - 1],
            1,
            formatter
        );
        // update time point display
        this.timePointDisplay.text(timePoints[selectedTimePoint]);
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
        // update time point display
        this.timePointDisplay.text(this.timePoints[timeIndex]);
    }

    /**
     * Handle time point conversion
     * @param {Object} conversionState - The conversion state
     */
    async handleTimePointConversion(conversionState) {
        // get viewer metadata
        const timePointsResponse = await this.contextManager.data.getTimePoints();
        this.timePoints = timePointsResponse.timepoints;
        
        // update formatter function in time slider
        const displayText = this.displayText;
        const timePoints = this.timePoints;
        const formatter = function(value) {
            return displayText + timePoints[value];
        }
        // update time slider
        this.timeSlider.slider('setAttribute', 'formatter', formatter);
        // refresh time slider
        this.timeSlider.slider('refresh', { useCurrentValue: true });
        // update time point display
        const timeIndex = this.timeSlider.slider('getValue');
        this.timePointDisplay.text(timePoints[timeIndex]);
    }
}

export default TimeSlider;
