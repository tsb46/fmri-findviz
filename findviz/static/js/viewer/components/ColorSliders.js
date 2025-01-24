// Colorsliders.js - used to initialize color sliders

import { initializeRangeSlider, initializeSingleSlider } from '../utils/sliders';
import { EVENT_TYPES } from '../constants/EventTypes';
import eventBus from '../events/ViewerEvents';
import { getPlotOptions, resetColorOptions } from '../api/plot';

class ColorSliders {
    /**
     * Constructor for ColorSliders
     * @param {string} colorSliderId - ID of the color slider
     * @param {string} thresholdSliderId - ID of the threshold slider
     * @param {string} opacitySliderId - ID of the opacity slider
     * @param {string} resetColorSliderId - ID of the reset color slider
     */
    constructor(
        colorSliderId,
        thresholdSliderId,
        opacitySliderId,
        resetColorSliderId
    ) {
        // get slider ids 
        this.colorSliderId = colorSliderId;
        this.thresholdSliderId = thresholdSliderId;
        this.opacitySliderId = opacitySliderId;
        this.resetColorSliderId = resetColorSliderId;

        // get plot options
        getPlotOptions((plotOptions) => {
            this.initializeColorSliders(
                plotOptions.colorMin,
                plotOptions.colorMax,
                plotOptions.colorRange,
                plotOptions.thresholdMin,
                plotOptions.thresholdMax,
                plotOptions.thresholdRange,
                plotOptions.sliderStepSize,
                plotOptions.opacityValue,
                this.colorSliderId,
                this.thresholdSliderId,
                this.opacitySliderId,
            );
        });
        // attach listeners
        this.colorRangeSliderListener();
        this.thresholdSliderListener();
        this.opacitySliderListener();
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
            sliderStepSize
        );
    }

    // color range slider listener
    colorRangeSliderListener() {
        const colorSlider = $(`#${this.colorSliderId}`);
        colorSlider.on('change', (event) => {
            const colorValues = event.value;
            eventBus.publish(EVENT_TYPES.COLOR_SLIDER_CHANGE, colorValues);
        });
    }

    // threshold slider listener
    thresholdSliderListener() {
        const thresholdSlider = $(`#${this.thresholdSliderId}`);
        thresholdSlider.on('change', (event) => {
            const thresholdValues = event.value;
            eventBus.publish(EVENT_TYPES.THRESHOLD_SLIDER_CHANGE, thresholdValues);
        });
    }

    /**
     * Opacity slider listener
     */
    opacitySliderListener() {
        const opacitySlider = $(`#${this.opacitySliderId}`);
        opacitySlider.on('change', (event) => {
            const opacityValues = event.value;
            eventBus.publish(EVENT_TYPES.OPACITY_SLIDER_CHANGE, opacityValues);
        });
    }

    /**
     * Reset color slider listener
     */
    resetColorSliderListener() {
        const resetColorSlider = $(`#${this.resetColorSliderId}`);
        resetColorSlider.on('click', () => {
            this.resetColorSliders();
        });
    }

    /**
     * Reset color sliders
     */
    async resetColorSliders() {
        await resetColorOptions();
        getPlotOptions((plotOptions) => {
            this.initializeColorSliders(
                plotOptions.colorMin,
                plotOptions.colorMax,
                plotOptions.colorRange,
                plotOptions.thresholdMin,
                plotOptions.thresholdMax,
                plotOptions.thresholdRange,
                plotOptions.sliderStepSize,
                plotOptions.opacityValue,
                this.colorSliderId,
                this.thresholdSliderId,
                this.opacitySliderId,
            );
        });
    }
}

export default ColorSliders;