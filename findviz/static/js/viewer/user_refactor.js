// user_refactor.js - Visualization options functions

import { DOM_IDS, API_ENDPOINTS, FILE_TYPES } from '../constants/constants.js';
import { EVENT_TYPES } from '../constants/EventTypes.js';
import { 
    createColormapDropdown, 
    closeColormapDropdown, 
    colorMapToggle
} from './components/colormap.js';
import { 
    initializeRangeSlider,
    initializeSingleSlider
} from './components/sliders.js';
import { captureScreenshot, playMovie } from './components/capture.js';

/**
 * Initialize viewer option listeners
 * 
 * @param {string} plotType - Plot type - 'nifti' or 'gifti'
 */
export async function initializeUserOptions(plotType) {
    // fetch plot options
    const plotOptions = await fetchPlotOptions();
    // fetch colormap data
    const colormapData = await fetchColormapData();
    // initialize color sliders
    initializeColorSliders(
        plotOptions.color_min,
        plotOptions.color_max,
        plotOptions.color_range,
        plotOptions.threshold_min,
        plotOptions.threshold_max,
        plotOptions.threshold_range,
        plotOptions.slider_step_size,
        plotOptions.opacity_value
    );
    // initialize montage options
    initializeMontageOptions(plotType);
}

/**
 * Fetch plot options from backend
 * @returns {Promise<Object>} Plot options
 * @throws {Error} If the fetch fails
 */
export async function fetchPlotOptions() {
    const response = await fetch(API_ENDPOINTS.GET_PLOT_OPTIONS);
    if (response.ok) {
        return await response.json();
    } else {
        // throw error to be caught by the caller
        const error = await response.text();
        throw new Error(error);
    }
}

/**
 * Fetch colormap data and create colormap dropdown
 * 
 * @param {string} defaultColormap - Default colormap to select
 */
export async function fetchColormapData(defaultColormap) {
    const response = await fetch(API_ENDPOINTS.GET_COLORMAP_DATA);
    if (response.ok) {
        const colormapData = await response.json();
        // create colormap dropdown
        createColormapDropdown(
            colormapData,
            defaultColormap,
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN,
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_MENU,
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_TOGGLE
        );
        // attach event listeners
        // toggle colormap dropdown
        colorMapToggle(
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_TOGGLE,
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_MENU
        );
        // close colormap dropdown
        closeColormapDropdown(
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_TOGGLE,
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_MENU
        );
        // create event listener to trigger colormap change
        colormapChangeListener(
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_TOGGLE,
            DOM_IDS.USER_OPTIONS.COLORMAP_DROPDOWN_MENU
        );

    } else {
        // throw error to be caught by the caller
        const error = await response.text();
        throw new Error(error);
    }
}

/**
 * Update plot options
 * 
 * @param {Object} plotOptions - Plot options
 * @param {Function} plotCallback - Callback function to execute after plot options are updated
 */
export async function updatePlotOptions(plotOptions, plotCallback) {
    // update plot options
    const response = await fetch(API_ENDPOINTS.UPDATE_PLOT_OPTIONS, {
        method: 'POST',
        body: JSON.stringify(plotOptions)
    });
    if (response.ok) {
        // execute callback function
        plotCallback();
    } else {
        // throw error to be caught by the caller
        const error = await response.text();
        throw new Error(error);
    }
}



/**
 * Color slider change listener
 * 
 * @param {Event} event - Event object
 */
export function colorSliderChangeListener(event) {
    $(document).trigger(
        $.Event(
            EVENT_TYPES.VISUALIZATION.COLOR_SLIDER_CHANGE, 
            { detail: event.value }
        )
    );
}

/**
 * Threshold slider change listener
 * 
 * @param {Event} event - Event object
 */
export function thresholdSliderChangeListener(event) {
    $(document).trigger(
        $.Event(
            EVENT_TYPES.VISUALIZATION.THRESHOLD_SLIDER_CHANGE, 
            { detail: event.value }
        )
    );
}

/**
 * Opacity slider change listener
 * 
 * @param {Event} event - Event object
 */
export function opacitySliderChangeListener(event) {
    $(document).trigger(
        $.Event(
            EVENT_TYPES.VISUALIZATION.OPACITY_SLIDER_CHANGE, 
            { detail: event.value }
        )
    );
}

/**
 * Toggle direction marker listener
 */
export function directionMarkerChangeListener() {
    $(document).trigger(
        $.Event(EVENT_TYPES.VISUALIZATION.TOGGLE_DIRECTION_MARKER)
    );
}

/**
 * Listener for ortho to montage viewer event, and vice versa
 * 
 * @param {number[]} montageSliceIndices - Montage slice indices
 * @param {string} montageSliceSelection - Montage slice selection
 */
export function viewChangeListener(
    montageSliceIndices, 
    montageSliceSelection
) {
    // Trigger a custom event using jQuery
    const customEventView = $.Event(
        EVENT_TYPES.VISUALIZATION.VIEW_TOGGLE, {
            detail: {
                sliceIndices: montageSliceIndices[montageSliceSelection],
                sliceDirection: montageSliceSelection
            }
        }
    );
    // Dispatch the custom event
    $(document).trigger(customEventView);
}

/**
 * Listener for crosshair click event
 */
export function crosshairChangeListener() {
    // Trigger a custom event using jQuery
    const customEventCrosshair = $.Event('');
    // Dispatch the custom event
    $(document).trigger(customEventCrosshair);
}


// Reset sliders to default values
export async function resetColorSliders() {
    // get sliders
    const colorSlider = document.getElementById(DOM_IDS.USER_OPTIONS.COLOR_SLIDER);
    const thresholdSlider = document.getElementById(DOM_IDS.USER_OPTIONS.THRESHOLD_SLIDER);
    const opacitySlider = document.getElementById(DOM_IDS.USER_OPTIONS.OPACITY_SLIDER);

    // revert color options back to original values
    const response = await fetch(API_ENDPOINTS.RESET_COLOR_OPTIONS);
    if (response.ok) {
        const colorOptions = await response.json();
        // set sliders to default values
        colorSlider.slider(
            'setValue', [colorOptions.color_min, colorOptions.color_max], false, true
        );
        thresholdSlider.slider(
            'setValue', [colorOptions.threshold_min, colorOptions.threshold_max], false, true
        );
        opacitySlider.slider(
            'setValue', [colorOptions.opacity_value], false, true
        );
    } else {
        // throw error to be caught by the caller
        const error = await response.text();
        throw new Error(error);
    }
}

/**
 * Initialize montage options for NIFTI data
 * 
 * @param {string} plotType - Plot type - 'nifti' or 'gifti'
 */
export function initializeMontageOptions(plotType) {
    if (plotType === FILE_TYPES.NIFTI) {
        $("#montage-popover").popover('enable');
        $("#montage-popover").prop('disabled', false);
    } else {
        $("#montage-popover").popover('disable');
        $("#montage-popover").prop('disabled', true);
    }
}

/**
 * Attach colormap dropdown event listeners
 * 
 * @param {string} dropdownToggleId - ID of the dropdown toggle
 * @param {string} dropdownMenuId - ID of the dropdown menu
 */
function colormapChangeListener(dropdownToggleId, dropdownMenuId) {
    const dropdownToggle = document.getElementById(dropdownToggleId);
    const dropdownMenu = document.getElementById(dropdownMenuId);

    // Handle item selection
    dropdownMenu.addEventListener('click', (event) => {
        if (event.target.tagName === 'LI' || event.target.parentElement.tagName === 'LI') {
            const selectedValue = event.target.closest('li').getAttribute('data-value');
            dropdownToggle.textContent = event.target.closest('li').querySelector('span:first-child').textContent;
            dropdownMenu.classList.remove('show');
            
            $(document).trigger(
                $.Event(EVENT_TYPES.VISUALIZATION.COLOR_MAP_CHANGE, { detail: { selectedValue } })
            );
        }
    });
}

