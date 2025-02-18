// distance.js
// Class for handling distance plot options popover
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { initializeRangeSlider, initializeSingleSlider } from '../sliders.js';
import { getDistancePlotOptions, updateDistancePlotOptions } from '../../api/plot.js';
import ColorMap from '../ColorMap.js';

class DistancePopover {
    /**
     * Constructor for DistancePopover class
     * 
     * @param {string} distancePopOverId - The ID of the distance popover
     * @param {string} distanceColorMapContainerId - The ID of the distance color map container
     * @param {string} distanceColorMapDropdownMenuId - The ID of the distance color map dropdown menu
     * @param {string} distanceColorMapDropdownToggleId - The ID of the distance color map dropdown toggle
     * @param {string} distanceColorRangeSliderId - The ID of the distance color range slider
     * @param {string} distanceTimeMarkerWidthSliderId - The ID of the distance time marker width slider
     * @param {string} distanceTimeMarkerOpacitySliderId - The ID of the distance time marker opacity slider
     */
    constructor(
        distancePopOverId,
        distanceColorMapContainerId,
        distanceColorMapDropdownMenuId,
        distanceColorMapDropdownToggleId,
        distanceColorRangeSliderId,
        distanceTimeMarkerWidthSliderId,
        distanceTimeMarkerOpacitySliderId,
        distancePrepAlertId
    ) {
        this.distancePopOverId = distancePopOverId;
        this.distanceColorRangeSliderId = distanceColorRangeSliderId;
        this.distanceColorMapContainerId = distanceColorMapContainerId;
        this.distanceColorMapDropdownMenuId = distanceColorMapDropdownMenuId;
        this.distanceColorMapDropdownToggleId = distanceColorMapDropdownToggleId;
        this.distanceTimeMarkerWidthSliderId = distanceTimeMarkerWidthSliderId;
        this.distanceTimeMarkerOpacitySliderId = distanceTimeMarkerOpacitySliderId;
        this.distancePrepAlertId = distancePrepAlertId;

        // get elements
        this.distancePopOver = $(`#${distancePopOverId}`);
        this.distanceColorRangeSlider = $(`#${distanceColorRangeSliderId}`);
        this.distanceTimeMarkerWidthSlider = $(`#${distanceTimeMarkerWidthSliderId}`);
        this.distanceTimeMarkerOpacitySlider = $(`#${distanceTimeMarkerOpacitySliderId}`);
        this.distancePrepAlert = $(`#${distancePrepAlertId}`);

        // initialize distance plot options popover
        this.initializeDistancePlotPopover();

        // disable popover by default
        this.distancePopOver.popover('disable');

    }

    /**
     * Attaches event listeners to the distance plot options popover
     */
    attachEventListeners() {
        // Color Range Slider listener
        this.distanceColorRangeSlider.on('change', (event) => {
            updateDistancePlotOptions({
                color_range: event.value.newValue,
            });
            eventBus.publish(EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_COLOR_MAP_CHANGE);
        });

        // Time Marker Width Slider listener
        this.distanceTimeMarkerWidthSlider.on('change', (event) => {
            updateDistancePlotOptions({
                time_marker_width: event.value.newValue,
            });
            eventBus.publish(EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_WIDTH_CHANGE);
        });

        // Time Marker Opacity Slider listener
        this.distanceTimeMarkerOpacitySlider.on('change', (event) => {
            updateDistancePlotOptions({
                time_marker_opacity: event.value.newValue,
            });
            eventBus.publish(EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_OPACITY_CHANGE);
        });

        // listen for distance submit event and enable popover
        eventBus.subscribe(EVENT_TYPES.ANALYSIS.DISTANCE_SUBMIT, 
            () => {
                this.distancePopOver.prop('disabled', false);
            }
        );

        // listen for distance remove event and disable popover
        eventBus.subscribe(EVENT_TYPES.ANALYSIS.DISTANCE_REMOVE, 
            () => {
                this.distancePopOver.prop('disabled', true);
            }
        );
    }

    initializeDistancePlotPopover() {
        // initialize tooltips on popup show
        this.distancePopOver.on('shown.bs.popover', () => {
            // Hide popover when clicking outside
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest(`.popover, #${this.distancePopOverId}`).length) {
                  this.distancePopOver.popover('hide');
                }
            });

            // initialize color map and generate colormap dropdown
            this.colorMap = new ColorMap(
                this.distanceColorMapContainerId,
                this.distanceColorMapDropdownMenuId,
                this.distanceColorMapDropdownToggleId,
                getDistancePlotOptions,
                updateDistancePlotOptions,
                EVENT_TYPES.VISUALIZATION.DISTANCE.COLOR_MAP_CHANGE
            );
            // set slider parameters
            getDistancePlotOptions((plotOptions) => {
                // set color range slider
                initializeRangeSlider(
                    this.distanceColorRangeSliderId, 
                    plotOptions.color_range, 
                    plotOptions.color_min,
                    plotOptions.color_max,
                    plotOptions.slider_step_size,
                );

                // set time marker width slider
                initializeSingleSlider(
                    this.distanceTimeMarkerWidthSliderId,
                    plotOptions.time_marker_width,
                    [1, 20], // hardcoded for now
                    1, // hardcoded for now
                );

                // set time marker opacity slider
                initializeSingleSlider(
                    this.distanceTimeMarkerOpacitySliderId,
                    plotOptions.time_marker_opacity,
                    [0, 1], // hardcoded for now
                    0.01, // hardcoded for now
                );
            });

            // attach event listeners
            this.attachEventListeners();
        })
    }


}

export default DistancePopover;
