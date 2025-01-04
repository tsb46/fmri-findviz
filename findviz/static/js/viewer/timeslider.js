class TimeSlider {
    constructor(timePoints, displayText) {
        this.timePoints = timePoints;
        this.displayText = displayText;
        this.sliderElement = $('#time_slider');

        // Initialize time slider
        this.initializeTimeSlider(this.timePoints)

        // Attach the `slide` event listener (for when the slider value changes)
        this.sliderElement.on('change', this.handleSlide.bind(this));
    }

    // Initialize bootstrap-slider with options
    initializeTimeSlider(timePoints) {
        // Get display text for formatter
        const displayText = this.displayText;
        // get time point to display text converter
        const timeToDisplay = {}
        this.timePoints.forEach((item, index) => {
          timeToDisplay[index] = item
        });
        this.sliderElement.slider({
            min: 0,
            max: timePoints.length - 1,
            step: 1,
            value: 0,
            tooltip: 'show',  // Show tooltip with the current value
            focus: true,
            formatter: function(value) {
                return displayText + timeToDisplay[value];
            }
        });
    }

    handleSlide() {
        const timeIndex = this.sliderElement.slider('getValue');

        // Trigger a custom event using jQuery
        const customEvent = $.Event('timeSliderChange', { detail: { timeIndex } });

        // Dispatch the custom event
        $(document).trigger(customEvent);
    }
}

export default TimeSlider;
