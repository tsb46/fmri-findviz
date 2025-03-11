// Colorsliders.js - used to initialize color sliders

import { initializeRangeSlider, initializeSingleSlider } from '../sliders.js';
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import ContextManager from '../../api/ContextManager.js';

class ColorSliders {
    /**
     * Constructor for ColorSliders
     * @param {string} colorSliderId - ID of the color slider
     * @param {string} thresholdSliderId - ID of the threshold slider
     * @param {string} opacitySliderId - ID of the opacity slider
     * @param {string} resetColorSliderId - ID of the reset color slider
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        colorSliderId,
        thresholdSliderId,
        opacitySliderId,
        resetColorSliderId,
        eventBus,
        contextManager
    ) {
        // get slider ids 
        this.colorSliderId = colorSliderId;
        this.thresholdSliderId = thresholdSliderId;
        this.opacitySliderId = opacitySliderId;
        this.resetColorSliderId = resetColorSliderId;
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // initialize color sliders
        this.initializeColorSliders();

        // listen for preprocess submit and reset - full reset of color sliders (range and values)
        this.eventBus.subscribeMultiple(
            [
                EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_SUCCESS,
                EVENT_TYPES.PREPROCESSING.PREPROCESS_FMRI_RESET
            ],
            () => {
                this.resetColorSliders();
            }
        );
    }

    /**
     * Initialize color sliders based on data range
     */
    async initializeColorSliders() {
        // get plot options
        const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
        // Initialize color range slider
        initializeRangeSlider(
            this.colorSliderId,
            plotOptions.color_range,
            plotOptions.color_min,
            plotOptions.color_max,
            plotOptions.slider_step_size
        );

        // Initialize threshold slider
        initializeRangeSlider(
            this.thresholdSliderId,
            plotOptions.threshold_range, 
            plotOptions.threshold_min, 
            plotOptions.threshold_max, 
            plotOptions.slider_step_size
        );

        // Initialize opacity slider
        initializeSingleSlider(
            this.opacitySliderId,
            plotOptions.opacity,
            [0,1],
            0.01
        );

        // attach listeners
        this.colorRangeSliderListener();
        this.thresholdSliderListener();
        this.opacitySliderListener();
        // listen for reset color slider values
        this.resetColorSliderValuesListener();
    }

    /**
     * Color range slider listener
     */
    colorRangeSliderListener() {
        const colorSlider = $(`#${this.colorSliderId}`);
        colorSlider.on('change', async (event) => {
            console.log('color range slider changed');
            const colorValues = event.value.newValue;
            // update plot options
            await this.contextManager.plot.updateFmriPlotOptions(
                {
                    color_min: colorValues[0],
                    color_max: colorValues[1],
                }
            );
            // publish color slider change event
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.COLOR_SLIDER_CHANGE, colorValues);
        });
    }

    /**
     * Threshold slider listener
     */
    thresholdSliderListener() {
        const thresholdSlider = $(`#${this.thresholdSliderId}`);
        thresholdSlider.on('change', async (event) => {
            console.log('threshold slider changed');
            const thresholdValues = event.value.newValue;
            // update plot options
            await this.contextManager.plot.updateFmriPlotOptions(
                {
                    threshold_min: thresholdValues[0],
                    threshold_max: thresholdValues[1],
                }
            );
            // publish threshold slider change event
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.THRESHOLD_SLIDER_CHANGE, thresholdValues);
        });
    }

    /**
     * Opacity slider listener
     */
    opacitySliderListener() {
        const opacitySlider = $(`#${this.opacitySliderId}`);
        opacitySlider.on('change', async (event) => {
            console.log('opacity slider changed');
            const opacityValues = event.value.newValue;
            // update plot options
            await this.contextManager.plot.updateFmriPlotOptions(
                {
                    opacity: opacityValues,
                }
            );
            // publish opacity slider change event
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.OPACITY_SLIDER_CHANGE, opacityValues);
        });
    }

    /**
     * Full reset of color sliders (values and range) for preprocessed data
     */
    async resetColorSliders() {
        console.log('resetting color sliders');
        // get plot options
        const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
        // reset color slider range and step size
        this.resetColorSliderRange(plotOptions);
        // reset color slider values
        this.resetColorSliderValues(plotOptions);
    }

    /**
    * Reset color slider listener
     */
    resetColorSliderValuesListener() {
        const resetColorSlider = $(`#${this.resetColorSliderId}`);
        resetColorSlider.on('click', async () => {
            await this.contextManager.plot.resetFmriColorOptions();
            const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
            this.resetColorSliderValues(plotOptions);
            // publish reset color sliders event
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.RESET_COLOR_SLIDERS);
        });
    }

    /**
     * Reset color slider range
     * 
     * @param {object} plotOptions - Plot options object
     */
    resetColorSliderRange(plotOptions) {
        // reset slider range and step size
        const colorSlider = $(`#${this.colorSliderId}`);
        colorSlider.slider('setAttribute', 'max', plotOptions.color_range[1]);
        colorSlider.slider('setAttribute', 'min', plotOptions.color_range[0]);
        colorSlider.slider('setAttribute', 'step', plotOptions.slider_step_size);
        // reset threshold slider range
        const thresholdSlider = $(`#${this.thresholdSliderId}`);
        thresholdSlider.slider('setAttribute', 'max', plotOptions.color_range[1]);
        thresholdSlider.slider('setAttribute', 'min', plotOptions.color_range[0]);
        thresholdSlider.slider('setAttribute', 'step', plotOptions.slider_step_size);
    }

    /**
     * Reset color slider values
     * 
     * @param {object} plotOptions - Plot options object
     */
    resetColorSliderValues(plotOptions) {
        // set color slider to original min and max values
        const colorSlider = $(`#${this.colorSliderId}`);
        colorSlider.slider('setValue', [plotOptions.color_min, plotOptions.color_max], false, true);
        // Set threshold slider back to [0,0]
        const thresholdSlider = $(`#${this.thresholdSliderId}`);
        thresholdSlider.slider('setValue', [plotOptions.threshold_min, plotOptions.threshold_max], false, true);
        // set opacity slider back to 1
        const opacitySlider = $(`#${this.opacitySliderId}`);
        opacitySlider.slider('setValue', [plotOptions.opacity], false, true);
    }

}

export default ColorSliders;