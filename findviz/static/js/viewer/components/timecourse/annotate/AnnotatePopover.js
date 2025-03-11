// AnnotatePopover.js - handles the plot options for the annotation markers
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import { initializeSingleSlider } from '../../sliders.js';
import ContextManager from '../../../api/ContextManager.js';


class AnnotatePopover {
    /**
     * Constructor
     * @param {string} annotatePopoverId - The id of the annotate popover
     * @param {string} annotateColorDropdownId - The id of the annotate color dropdown
     * @param {string} annotateMarkerSelectId - The id of the annotate marker select
     * @param {string} annotateMarkerWidthSliderId - The id of the annotate marker width slider
     * @param {string} annotateMarkerOpacitySliderId - The id of the annotate marker opacity slider
     * @param {string} highlightAnnotateId - The id of the highlight annotate
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        annotatePopoverId,
        annotateColorDropdownId,
        annotateMarkerSelectId,
        annotateMarkerWidthSliderId,
        annotateMarkerOpacitySliderId,
        highlightAnnotateId,
        eventBus,
        contextManager
    ) {
        // get elements
        this.annotatePopoverId = annotatePopoverId;
        this.annotateColorDropdownId = annotateColorDropdownId;
        this.annotateMarkerSelectId = annotateMarkerSelectId;
        this.annotateMarkerWidthSliderId = annotateMarkerWidthSliderId;
        this.annotateMarkerOpacitySliderId = annotateMarkerOpacitySliderId;
        this.highlightAnnotateId = highlightAnnotateId;
        // get event bus and context manager
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // initialize the annotate popover
        this.initializeAnnotatePopover();
    }

    /**
     * Initializes the annotate popover
     */
    initializeAnnotatePopover() {
        // initialize the annotate popover
        $(`#${this.annotatePopoverId}`).on('shown.bs.popover', async () => {
            console.log('annotate popover shown');
            // get annotate marker width and opacity    
            const plotOptions = await this.contextManager.plot.getAnnotationMarkerPlotOptions();
            // initialize the annotate sliders
            this.initializeAnnotateSliders(plotOptions.width, plotOptions.opacity);
            // set selection for color dropdown
            $(`#${this.annotateColorDropdownId}`).val(plotOptions.color);
            // set selection for marker select
            $(`#${this.annotateMarkerSelectId}`).val(plotOptions.shape);
            // set selection for highlight annotate
            $(`#${this.highlightAnnotateId}`).prop('checked', plotOptions.highlight);

            // Hide popover when clicking outside
            // Store reference to this
            const self = this;
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest(`.popover, #${self.annotatePopoverId}`).length) {
                    $(`#${self.annotatePopoverId}`).popover('hide');
                }
            });

            // attach listeners
            $(`#${this.annotateColorDropdownId}`).on(
                'change', this.handleColorDropdownChange.bind(this)
            );
            $(`#${this.annotateMarkerSelectId}`).on(
                'change', this.handleMarkerSelectChange.bind(this)
            );
            $(`#${this.annotateMarkerWidthSliderId}`).on(
                'change', this.handleMarkerWidthSliderChange.bind(this)
            );
            $(`#${this.annotateMarkerOpacitySliderId}`).on(
                'change', this.handleMarkerOpacitySliderChange.bind(this)
            );
            $(`#${this.highlightAnnotateId}`).on(
                'change', this.handleHighlightAnnotateChange.bind(this)
            );
        });
    }

    /**
     * Initializes the annotate sliders
     * @param {number} markerWidthValue - The width of the annotate marker
     * @param {number} markerOpacityValue - The opacity of the annotate marker
     */
    initializeAnnotateSliders(markerWidthValue, markerOpacityValue) {
        // initialize the annotate marker width slider
        initializeSingleSlider(
            this.annotateMarkerWidthSliderId,
            markerWidthValue,
            [0.5, 10],
            0.01
        );
        // initialize the annotate marker opacity slider
        initializeSingleSlider(
            this.annotateMarkerOpacitySliderId,
            markerOpacityValue,
            [0, 1],
            0.01
        );
    }

    /**
     * Handles the color dropdown change
     */
    async handleColorDropdownChange() {
        // get the selected color
        const selectedColor = $(`#${this.annotateColorDropdownId}`).val();
        // update the annotation marker plot options
        await this.contextManager.plot.updateAnnotationMarkerPlotOptions(
            {color: selectedColor}
        );
        console.log('annotation marker color changed');
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_COLOR_CHANGE,
            selectedColor
        );
    }

    /**
     * Handles the highlight annotate change
     */
    async handleHighlightAnnotateChange() {
        // get the checkbox value
        const selectedHighlight = $(`#${this.highlightAnnotateId}`).prop('checked');
        // update the annotation marker plot options
        await this.contextManager.plot.updateAnnotationMarkerPlotOptions(
            {highlight: selectedHighlight}
        );
        console.log('annotation marker highlight changed');
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_HIGHLIGHT_TOGGLE,
            selectedHighlight
        );
    }

    /**
     * Handles the marker select change
     */
    async handleMarkerSelectChange() {
        // get the selected marker
        const selectedMarker = $(`#${this.annotateMarkerSelectId}`).val();
        // update the annotation marker plot options
        await this.contextManager.plot.updateAnnotationMarkerPlotOptions(
            {shape: selectedMarker}
        );
        console.log(`annotation marker shape changed to ${selectedMarker}`);
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_SHAPE_CHANGE,
            selectedMarker
        );
    }

    /**
     * Handles the marker width slider change
     */
    async handleMarkerWidthSliderChange(event) {
        // get the selected width
        const selectedWidth = event.value.newValue;
        // update the annotation marker plot options
        await this.contextManager.plot.updateAnnotationMarkerPlotOptions(
            {width: selectedWidth}
        );
        console.log(`annotation marker width changed to ${selectedWidth}`);
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_WIDTH_CHANGE, 
            selectedWidth
        );
    }

    /**
     * Handles the marker opacity slider change
     */
    async handleMarkerOpacitySliderChange(event) {
        // get the selected opacity
        const selectedOpacity = event.value.newValue;
        // update the annotation marker plot options
        await this.contextManager.plot.updateAnnotationMarkerPlotOptions(
            {opacity: selectedOpacity}
        );
        console.log(`annotation marker opacity changed to ${selectedOpacity}`);
        this.eventBus.publish(
            EVENT_TYPES.VISUALIZATION.ANNOTATE.ANNOTATE_MARKER_OPACITY_CHANGE,
            selectedOpacity
        );
    }
}

export default AnnotatePopover;