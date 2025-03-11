// distance.js
// Class for handling distance plot options popover
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { initializeRangeSlider, initializeSingleSlider } from '../sliders.js';
import ContextManager from '../../api/ContextManager.js';
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
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        distancePopOverId,
        distanceColorMapContainerId,
        distanceColorMapDropdownMenuId,
        distanceColorMapDropdownToggleId,
        distanceColorRangeSliderId,
        distanceTimeMarkerWidthSliderId,
        distanceTimeMarkerOpacitySliderId,
        eventBus,
        contextManager
    ) {
        // get elements
        this.distancePopOverId = distancePopOverId;
        this.distanceColorRangeSliderId = distanceColorRangeSliderId;
        this.distanceColorMapContainerId = distanceColorMapContainerId;
        this.distanceColorMapDropdownMenuId = distanceColorMapDropdownMenuId;
        this.distanceColorMapDropdownToggleId = distanceColorMapDropdownToggleId;
        this.distanceTimeMarkerWidthSliderId = distanceTimeMarkerWidthSliderId;
        this.distanceTimeMarkerOpacitySliderId = distanceTimeMarkerOpacitySliderId;
        // get event bus and context manager
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // get elements
        this.distancePopOver = $(`#${distancePopOverId}`);

        // initialize distance plot options popover
        this.initializeDistancePlotPopover();

        // attach event listeners
        this.attachEventListeners();

    }

    /**
     * Attaches event listeners to the distance plot
     */
    attachEventListeners() {
        // listen for distance submit event and enable popover
        this.eventBus.subscribe(EVENT_TYPES.ANALYSIS.DISTANCE, 
            () => {
                this.distancePopOver.prop('disabled', false);
            }
        );

        // listen for distance remove event and disable popover
        this.eventBus.subscribe(EVENT_TYPES.ANALYSIS.DISTANCE_REMOVE, 
            () => {
                this.distancePopOver.prop('disabled', true);
            }
        );
    }

    /**
     * Attaches event listeners to the distance plot options popover
     */
    attachPopoverListeners() {
        // Color Range Slider listener
        $(`#${this.distanceColorRangeSliderId}`).on('change', async (event) => {
            await this.contextManager.plot.updateDistancePlotOptions({
                color_min: event.value.newValue[0],
                color_max: event.value.newValue[1],
            });
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.DISTANCE.COLOR_RANGE_CHANGE);
        });

        // Time Marker Width Slider listener
        $(`#${this.distanceTimeMarkerWidthSliderId}`).on('change', async (event) => {
            await this.contextManager.plot.updateDistancePlotOptions({
                time_marker_width: event.value.newValue,
            });
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_WIDTH_CHANGE);
        });

        // Time Marker Opacity Slider listener
        $(`#${this.distanceTimeMarkerOpacitySliderId}`).on('change', async (event) => {
            await this.contextManager.plot.updateDistancePlotOptions({
                time_marker_opacity: event.value.newValue,
            });
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.DISTANCE.TIME_MARKER_OPACITY_CHANGE);
        });
    }

    async initializeDistancePlotPopover() {
        // initialize tooltips on popup show
        this.distancePopOver.on('shown.bs.popover', async () => {
            // Hide popover when clicking outside
            // Store reference to this
            const self = this;
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest(`.popover, #${self.distancePopOverId}`).length) {
                    $(`#${self.distancePopOverId}`).popover('hide');
                }
            });

            // initialize color map and generate colormap dropdown
            this.colorMap = new ColorMap(
                this.distanceColorMapContainerId,
                this.distanceColorMapDropdownMenuId,
                this.distanceColorMapDropdownToggleId,
                this.contextManager.plot.getDistancePlotOptions,
                this.contextManager.plot.updateDistancePlotOptions,
                EVENT_TYPES.VISUALIZATION.DISTANCE.COLOR_MAP_CHANGE,
                this.eventBus,
                this.contextManager
            );
            // set slider parameters
            const plotOptions = await this.contextManager.plot.getDistancePlotOptions();
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

            // attach event listeners
            this.attachPopoverListeners();
        });
    }


}

export default DistancePopover;
