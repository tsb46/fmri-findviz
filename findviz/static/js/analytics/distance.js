// similarity.js

// Import from utils
import { colorMapDropdrown } from '../utils.js';

class Distance {
    constructor(
        active,
        timesliderDiv=null
    ) {
        this.active = active;
        this.plotId = 'distancePlot';
        this.plotContainerId = 'distance_container';

        // set dist vec and timeIndex variables as null
        this.distVec = null;
        this.timeIndex = null;

        // set plot default plot settings
        this.plotSettings = {
            colorMap: 'RdBu',
            dataMin: 0,
            dataMax: 1,
            colorMin: 0,
            colorMax: 1
        }

        // set plot state as false
        this.plotState = false;

        // initialize time point as 0
        this.timePoint = 0;

        // initialize time point marker state
        this.timePointMarker = true;

        // initialize time point marker state vars
        this.timePointMarkerState = {
            width: 1,
            color: 'black',
            opacity: 0.8
        }

        // get time slider div
        this.sliderElement = timesliderDiv;

        // get modal
        this.distanceModal = $('#distanceModal');

        // get time point

        // get trash button
        this.distanceRemoveButton = $('#remove-distance-plot');

        // get time point options button
        this.timePointPopover = $('#distance-popover');

        // set event listeners, if active
        if (this.active) {
            // distance plot 'remove' listener
            this.distanceRemoveButton.on('click', this.removeDistancePlot.bind(this));
            // handle distance analysis submit
            $('#distanceForm').on('submit', this.handleDistanceSubmit.bind(this));
            // set popover info
            this.initializeDistancePlotPopup();
            // change displayed time point on time slider change
            $(document).on('timeSliderChange', this.timePointDisplay.bind(this));
            // re-plot on time-slider change
            $(document).on('timeSliderChange', this.timeSliderUpdate.bind(this));
            // display preprocess alert if preprocess submit
            $(document).on('preprocessSubmit', () => {
                document.getElementById('distancePrepAlert').style.display='block';
            });
            // remove preprocess alert if preprocess submit
            $(document).on('preprocessReset', () => {
                document.getElementById('distancePrepAlert').style.display='none';
            });
            // Add event listener for window resize
            window.addEventListener('resize', () => this.onWindowResize());
        }
        // if not active, disable modal button
        else {
            $('#distanceModalButton').prop('disabled', true);
        }
    }

    // Listen for time slider change
    timeSliderUpdate(event) {
        this.timePoint = event.detail.timeIndex;
        if (this.plotState) {
            this.plotDistance();
        }
    }

    // display current timepoint on modal show
    timePointDisplay() {
        // get timepoint from timeslider
        const timeIndex = this.sliderElement.slider('getValue');
        // display timepoint in modal alert box
        $('#timepoint-distance-label').text(timeIndex)
    }

    // remove distance plot
    removeDistancePlot() {
        // remove display
        document.getElementById(this.plotContainerId).style.display = 'none';
        // disable buttons
        this.distanceRemoveButton.prop('disabled', true);
        this.timePointPopover.prop('disabled', true);
        // set plot state to false
        this.plotState = false;
    }

    // Custom-drop down functionality listener
    attachCustomDropDown() {
        const dropdownToggle = document.querySelector('#distancePlotColorMap .dropdown-toggle');
        const dropdownMenu = document.querySelector('#distancePlotColorMap .dropdown-menu');

        // Toggle the dropdown menu on click
        dropdownToggle.addEventListener('click', (event) => {
            dropdownMenu.classList.toggle('show');
            event.stopPropagation();  // Stop event propagation to prevent the document click event from closing it immediately
        });

        // Close the dropdown if a click happens outside of it
        document.addEventListener('click', (event) => {
            // Check if the clicked element is outside the dropdown
            if (!dropdownMenu.contains(event.target) && !dropdownToggle.contains(event.target)) {
                dropdownMenu.classList.remove('show');
            }
        });

        // Handle dropdown item selection
        dropdownMenu.addEventListener('click', (event) => {
            if (event.target.tagName === 'LI' || event.target.parentElement.tagName === 'LI') {
                const selectedValue = event.target.closest('li').getAttribute('data-value');
                dropdownToggle.textContent = event.target.closest('li').querySelector('span:first-child').textContent;
                dropdownMenu.classList.remove('show');
                // update colormap and plot
                this.plotSettings['colormap'] = selectedValue;
                this.plotDistance();
            }
        });
    }

    initializeDistancePlotPopup() {
        // initialize tooltips on popup show
        $('#distance-popover').on('shown.bs.popover', () => {
            // Hide popover when clicking outside
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest('.popover, #distance-popover').length) {
                  $('#distance-popover').popover('hide');
                }
            });

            // generate colormap dropdown
            let colorMapContainer = document.getElementById('distancePlotColorMap')
            // create colormap dropdown
            colorMapDropdrown(
                colorMapContainer,
                this.attachCustomDropDown.bind(this),
                this.plotSettings['colormap']
            );

            // set colorslider parameters
            const range = this.plotSettings['dataMax'] - this.plotSettings['dataMin']
            // extend out color slider to a quarter of range on both of sides
            const extendRange = range / 4
            // set step size as 100 equal units of range
            const stepSize = range/100
            // set color range
            $(`#distancePlotColorRange`).slider({
                min: this.plotSettings['dataMin'] - extendRange,
                max: this.plotSettings['dataMax'] + extendRange,
                step: stepSize,
                value: [this.plotSettings['colorMin'], this.plotSettings['colorMax']],
                tooltip: 'show',
            });
            // set time marker width slider
            this.timeMarkerWidthSlider = $('#distancePlotTimeMarkerWidth');
            this.timeMarkerWidthSlider.slider({
                min: 1,
                max:20,
                step: 1,
                value: this.timePointMarkerState['width'],
                tooltip: 'show',
            });
            // set time marker opacity slider
            this.timeMarkerOpacitySlider = $('#distancePlotTimeMarkerOpacity');
            this.timeMarkerOpacitySlider.slider({
                min: 0,
                max: 1,
                step: 0.01,
                value: this.timePointMarkerState['opacity'],
                tooltip: 'show',
            });

            // set time slider listeners
            // Color Range Slider listener
            $(`#distancePlotColorRange`).on('change', (event) => {
                const colorRange = event.value.newValue;
                this.plotSettings['colorMin'] = colorRange[0];
                this.plotSettings['colorMax'] = colorRange[1];
                // replot with new color range
                this.plotDistance();
            });

            // Threshold Slider listener
            this.timeMarkerWidthSlider.on('change', (event) => {
                const widthValue = event.value.newValue;
                this.timePointMarkerState['width'] = widthValue;
                // replot with new time point marker width
                this.plotDistance();
            });

            // Opacity Slider listener
            this.timeMarkerOpacitySlider.on('change', (event) => {
                const opacityValue = event.value.newValue;
                this.timePointMarkerState['opacity'] = opacityValue;
                // replot with new time point marker width
                this.plotDistance();
            });
        })
    }

    // package up input and trigger an event for viewer
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

    // plot distance vector using plotly
    plotDistance(distVec=null, timeIndex=null) {
        // update state variables if input passed
        if (distVec !== null) {
            this.distVec = distVec;
            // get min and max of distance vector for setting color slider parameters
            this.plotSettings['dataMin'] = Math.min(...distVec);
            this.plotSettings['dataMax'] = Math.max(...distVec);
            this.plotSettings['colorMin'] = this.plotSettings['dataMin'];
            this.plotSettings['colorMax'] = this.plotSettings['dataMax'];
        }
        if (timeIndex !== null) {
            this.timeIndex = timeIndex;
        }

        const distPlot = [{
            z: [this.distVec],  // Small data for colorbar
            type: 'heatmap',
            zmin: this.plotSettings['colorMin'],
            zmax: this.plotSettings['colorMax'],
            colorscale: this.plotSettings['colormap'],
            showscale: true,  // Enable colorbar
            hovertemplate: 'Time Point: %{x}<br>Distance: %{z}<extra></extra>',
            colorbar: {
                tickfont: {
                    size: 8  // Set the desired font size here
                }
            }
        }];

        const layout = {
            title: {
                text: `Time Point Distance: ${this.timeIndex}`
            },
            autosize: true,
            responsive: true, // Make the plot responsive
            height: 80,
            margin: { l: 0, r: 0, b: 0, t: 30 },  // No margin around colorbar
            showlegend: false,  // Hide any legends
            xaxis: {
                visible: false,  // Hide the X-axis
                fixedrange: true,  // Prevent zooming/panning
            },
            yaxis: {
                visible: false,  // Hide the Y-axis
                fixedrange: true,  // Prevent zooming/panning
            }
        }

        if (this.timePointMarker) {
            layout['shapes'] = [
                {
                    type: 'line',
                    x0: this.timePoint,
                    y0: 0,
                    x1: this.timePoint,
                    y1: 1,
                    yref: 'paper',
                    opacity: this.timePointMarkerState['opacity'],
                    line: {
                        color: this.timePointMarkerState['color'],
                        width: this.timePointMarkerState['width'],
                    },
                }
            ]
        }

        Plotly.react(this.plotId, distPlot, layout);

        // set plot state as true
        this.plotState = true;

        // enable buttons
        this.distanceRemoveButton.prop('disabled', false);
        this.timePointPopover.prop('disabled', false);

        // iniital display is off, resize
        this.onWindowResize();

        // set display
        document.getElementById(this.plotContainerId).style.display = 'block';
    }

    // resize plotly plots to window resizing
    onWindowResize() {
        Plotly.Plots.resize(document.getElementById(this.plotId));
    }
}

export default Distance;
