// sliders.js - Slider functions

/**
 * Initializes a single (non-range) slider
 * @param {string} sliderId - ID of the slider
 * @param {number} sliderValue - Value of the slider
 * @param {number[]} sliderRange - min and max range of the slider
 * @param {number} sliderStepSize - step size of the slider
 * @param {function | null} formatter - formatter function (optional)
 */
export function initializeSingleSlider(
    sliderId,
    sliderValue,
    sliderRange,
    sliderStepSize,
    formatter=null
) {
    const slider = $(`#${sliderId}`);
    slider.slider({
        min: sliderRange[0],
        max: sliderRange[1],
        step: sliderStepSize,
        value: sliderValue,
        tooltip: 'show',
        focus: true,
        formatter: formatter,
    });
}

/**
 * Initializes a range slider
 * @param {string} sliderId - ID of the slider
 * @param {number[]} sliderRange - min and max range of the slider
 * @param {number} sliderMin - min value of the slider
 * @param {number} sliderMax - max value of the slider
 * @param {number} sliderStepSize - step size of the slider
 * @param {function} formatter - formatter function
 */
export function initializeRangeSlider(
    sliderId,
    sliderRange,
    sliderMin,
    sliderMax,
    sliderStepSize,
    formatter=null
) {
    const slider = $(`#${sliderId}`);
    slider.slider({
        min: sliderRange[0],
        max: sliderRange[1],
        step: sliderStepSize,
        value: [sliderMin, sliderMax],
        tooltip: 'show',
        focus: true,
        formatter: formatter,
    });
}