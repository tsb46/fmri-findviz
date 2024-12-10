// similarity.js

class Distance {
    constructor(
        active,
        distancePlotId=null,
        timesliderDiv=null
    ) {
        this.active = active;
        this.plotId = distancePlotId;

        // if not active, disable button
        if (!this.active) {
            $('#distanceModalButton').prop('disabled', true);
        }
        this.sliderElement = timesliderDiv;

        // get modal
        this.distanceModal = $('#distanceModal');

        // change displayed time point on time slider change
        $(document).on('timeSliderChange', this.timePointDisplay.bind(this));

        // handle distance analysis submit
        $('#distanceForm').on('submit', this.handleDistanceSubmit.bind(this));
    }

    // display current timepoint on modal show
    timePointDisplay() {
        // get timepoint from timeslider
        const timeIndex = this.sliderElement.slider('getValue');
        // display timepoint in modal alert box
        $('#timepoint-distance-label').text(timeIndex)
    }

    // package up input to pass to viewer and execute distance computation
    handleDistanceSubmit(event) {
        // prevent page reload
        event.preventDefault();
        // get chosen distance matrix
        const distMetric = document.getElementById('distance-metric-select').value;
        // get time point value
        const timeIndex = this.sliderElement.slider('getValue');
        // Trigger a custom event using jQuery
        const customEvent = $.Event('distanceSubmit', { detail: { distMetric, timeIndex } });
        // Dispatch the custom event
        $(document).trigger(customEvent);
    }
}

export default Distance;
