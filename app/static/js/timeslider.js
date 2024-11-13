class TimeSlider {
    constructor(timePoints) {
        this.timePoints = timePoints;
        this.sliderElement = $('#time_slider');

        // Initialize time slider
        this.initializeTimeSlider(this.timePoints)

        // Attach the `slide` event listener (for when the slider value changes)
        this.sliderElement.on('change', this.handleSlide.bind(this));
    }

    initializeTimeSlider(timePoints) {
        // Initialize bootstrap-slider with options
        this.sliderElement.slider({
            min: 0,
            max: timePoints.length - 1,
            step: 1,
            value: 0,
            tooltip: 'show',  // Show tooltip with the current value
            focus: true,
            formatter: function(value) {
                return 'Time Point: ' + value;
            }
        });
    }

    handleSlide() {
        const timeIndex = this.sliderElement.slider('getValue');

        // Trigger a custom event using jQuery
        const customEvent = $.Event('timeSliderChange', { detail: { timeIndex } });

        // Dispatch the custom event through the jQuery object
        this.sliderElement.trigger(customEvent);
    }
}

export default TimeSlider;
