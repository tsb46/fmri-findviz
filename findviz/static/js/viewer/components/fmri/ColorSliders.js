// Colorsliders.js - used to initialize color sliders

import { initializeRangeSlider, initializeSingleSlider } from '../sliders.js';
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import { 
    getFmriPlotOptions, 
    updateFmriPlotOptions, 
    resetFmriColorOptions 
} from '../../api/plot.js';

class ColorSliders {
    /**
     * Constructor for ColorSliders
     * @param {string} colorSliderId - ID of the color slider
     * @param {string} thresholdSliderId - ID of the threshold slider
     * @param {string} opacitySliderId - ID of the opacity slider
     * @param {string} resetColorSliderId - ID of the reset color slider
     * @param {ViewerEvents} eventBus - The event bus
     */
    constructor(
        colorSliderId,
        thresholdSliderId,
        opacitySliderId,
        resetColorSliderId,
        eventBus
    ) {
        // get slider ids 
        this.colorSliderId = colorSliderId;
        this.thresholdSliderId = thresholdSliderId;
        this.opacitySliderId = opacitySliderId;
        this.resetColorSliderId = resetColorSliderId;
        this.eventBus = eventBus;
        // get plot options
        getFmriPlotOptions((plotOptions) => {
            this.initializeColorSliders(
                plotOptions.color_min,
                plotOptions.color_max,
                plotOptions.color_range,
                plotOptions.threshold_min,
                plotOptions.threshold_max,
                plotOptions.threshold_range,
                plotOptions.slider_step_size,
                plotOptions.opacity,
                this.colorSliderId,
                this.thresholdSliderId,
                this.opacitySliderId,
            );
        });
        // attach listeners
        this.colorRangeSliderListener();
        this.thresholdSliderListener();
        this.opacitySliderListener();
        // listen for reset color slider values
        this.resetColorSliderValuesListener();

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
 * 
 * @param {number} colorMin - Minimum color value of the sliders
 * @param {number} colorMax - Maximum color value of the sliders
 * @param {number[]} colorRange - Color min and max range of the sliders
 * @param {number} thresholdMin - Minimum threshold of the sliders
 * @param {number} thresholdMax - Maximum threshold of the sliders
 * @param {number[]} thresholdRange - Threshold min and max range of the sliders
 * @param {number} sliderStepSize - Step size of the sliders
 * @param {number} opacityValue - Opacity value of the sliders
 * @param {string} colorSliderId - ID of the color slider
 * @param {string} thresholdSliderId - ID of the threshold slider
 * @param {string} opacitySliderId - ID of the opacity slider
 */
initializeColorSliders( 
    colorMin,
    colorMax,
    colorRange,
    thresholdMin,
    thresholdMax,
    thresholdRange,
    sliderStepSize,
    opacityValue,
    colorSliderId,
    thresholdSliderId,
    opacitySliderId,
) {
    // Initialize color range slider
    initializeRangeSlider(
        colorSliderId,
        colorRange,
        colorMin,
        colorMax,
        sliderStepSize
    );

    // Initialize threshold slider
    initializeRangeSlider(
        thresholdSliderId,
        thresholdRange, 
        thresholdMin, 
        thresholdMax, 
        sliderStepSize
    );

    // Initialize opacity slider
    initializeSingleSlider(
        opacitySliderId,
        opacityValue,
        [0,1],
        0.01
    );
    }

    /**
     * Color range slider listener
     */
    colorRangeSliderListener() {
        const colorSlider = $(`#${this.colorSliderId}`);
        colorSlider.on('change', (event) => {
            console.log('color range slider changed');
            const colorValues = event.value.newValue;
            updateFmriPlotOptions({
                color_min: colorValues[0],
                color_max: colorValues[1],
            }, () => {
                this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.COLOR_SLIDER_CHANGE, colorValues);
            });
        });
    }

    /**
     * Threshold slider listener
     */
    thresholdSliderListener() {
        const thresholdSlider = $(`#${this.thresholdSliderId}`);
        thresholdSlider.on('change', (event) => {
            console.log('threshold slider changed');
            const thresholdValues = event.value.newValue;
            updateFmriPlotOptions({
                threshold_min: thresholdValues[0],
                threshold_max: thresholdValues[1],
            }, () => {
                this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.THRESHOLD_SLIDER_CHANGE, thresholdValues);
            });
        });
    }

    /**
     * Opacity slider listener
     */
    opacitySliderListener() {
        const opacitySlider = $(`#${this.opacitySliderId}`);
        opacitySlider.on('change', (event) => {
            console.log('opacity slider changed');
            const opacityValues = event.value.newValue;
            updateFmriPlotOptions({
                opacity: opacityValues,
            }, () => {
                this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.OPACITY_SLIDER_CHANGE, opacityValues);
            });
        });
    }

    /**
     * Full reset of color sliders (values and range) for preprocessed data
     */
    resetColorSliders() {
        console.log('resetting color sliders');
        getFmriPlotOptions((plotOptions) => {
            this.resetColorSliderRange(plotOptions);
            this.resetColorSliderValues(plotOptions);
        });
    }

    /**
    * Reset color slider listener
     */
    resetColorSliderValuesListener() {
        const resetColorSlider = $(`#${this.resetColorSliderId}`);
        resetColorSlider.on('click', async () => {
            await resetFmriColorOptions();
            getFmriPlotOptions((plotOptions) => {
                this.resetColorSliderValues(plotOptions);
                // publish reset color sliders event
                this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.RESET_COLOR_SLIDERS);
            });
        });
    }

    /**
     * Reset color slider range
     * 
     * @param {object} plotOptions - Plot options object
     */
    resetColorSliderRange(plotOptions) {
        // reset slider range
        const colorSlider = $(`#${this.colorSliderId}`);
        colorSlider.slider('setAttribute', 'max', plotOptions.color_range[1]);
        colorSlider.slider('setAttribute', 'min', plotOptions.color_range[0]);
        // reset threshold slider range
        const thresholdSlider = $(`#${this.thresholdSliderId}`);
        thresholdSlider.slider('setAttribute', 'max', plotOptions.color_range[1]);
        thresholdSlider.slider('setAttribute', 'min', plotOptions.color_range[0]);
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