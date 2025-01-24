// preprocess_refactor.js - Preprocessing functions

import { validateFilterInputs, preprocessingInputError } from '../utils.js';

// Initialize preprocessing switches
export function initializePreprocessSwitches() {
    const normSwitch = document.getElementById('enable-normalization');
    const filterSwitch = document.getElementById('enable-filtering');
    const smoothSwitch = document.getElementById('enable-smoothing');
    
    return {
        normSwitch,
        filterSwitch,
        smoothSwitch
    };
}

// Handle normalization switch
export function handleNormalizationSwitch(event) {
    const normalizationParams = document.getElementById('normalization-parameters');
    normalizationParams.style.display = event.target.checked ? 'block' : 'none';
    return event.target.checked;
}

// Handle filtering switch
export function handleFilteringSwitch(event) {
    const filteringParams = document.getElementById('filtering-parameters');
    filteringParams.style.display = event.target.checked ? 'block' : 'none';
    return event.target.checked;
}

// Handle smoothing switch
export function handleSmoothingSwitch(event) {
    const smoothingParams = document.getElementById('smoothing-parameters');
    smoothingParams.style.display = event.target.checked ? 'block' : 'none';
    return event.target.checked;
}

// Validate preprocessing parameters
export function validatePreprocessingParams(
    normEnabled,
    filterEnabled,
    smoothEnabled,
    errorDiv
) {
    // Check if any preprocessing is enabled
    if (!normEnabled && !filterEnabled && !smoothEnabled) {
        preprocessingInputError(errorDiv, 'At least one preprocessing step must be enabled');
        return false;
    }

    // Validate normalization parameters
    if (normEnabled) {
        const meanCenter = document.getElementById('select-mean-center').checked;
        const zScore = document.getElementById('select-z-score').checked;
        
        if (!meanCenter && !zScore) {
            preprocessingInputError(errorDiv, 'At least one normalization method must be selected');
            return false;
        }
    }

    // Validate filtering parameters
    if (filterEnabled) {
        const TR = document.getElementById('filter-tr').value;
        const lowCut = document.getElementById('filter-low-cut').value;
        const highCut = document.getElementById('filter-high-cut').value;
        
        if (!validateFilterInputs(TR, lowCut, highCut, errorDiv)) {
            return false;
        }
    }

    // Validate smoothing parameters
    if (smoothEnabled) {
        const fwhm = document.getElementById('smoothing-fwhm').value;
        if (!fwhm) {
            preprocessingInputError(errorDiv, 'FWHM must be provided for smoothing');
            return false;
        }
        if (fwhm <= 0) {
            preprocessingInputError(errorDiv, 'FWHM must be positive');
            return false;
        }
    }

    return true;
}

// Reset preprocessing options
export function resetPreprocessing() {
    // Reset switches
    document.getElementById('enable-normalization').checked = false;
    document.getElementById('enable-filtering').checked = false;
    document.getElementById('enable-smoothing').checked = false;

    // Reset parameters
    document.getElementById('select-mean-center').checked = false;
    document.getElementById('select-z-score').checked = false;
    document.getElementById('filter-tr').value = '';
    document.getElementById('filter-low-cut').value = '';
    document.getElementById('filter-high-cut').value = '';
    document.getElementById('smoothing-fwhm').value = '';

    // Hide error message
    document.getElementById('error-message-preprocess').style.display = 'none';
    
    // Hide alert
    document.getElementById('preprocess-alert').style.display = 'none';

    // Trigger reset event
    $(document).trigger($.Event('preprocessReset'));
}

// Get preprocessing parameters
export function getPreprocessingParams() {
    return {
        normalization: {
            enabled: document.getElementById('enable-normalization').checked,
            mean_center: document.getElementById('select-mean-center').checked,
            z_score: document.getElementById('select-z-score').checked
        },
        filtering: {
            enabled: document.getElementById('enable-filtering').checked,
            tr: document.getElementById('filter-tr').value,
            low_cut: document.getElementById('filter-low-cut').value,
            high_cut: document.getElementById('filter-high-cut').value
        },
        smoothing: {
            enabled: document.getElementById('enable-smoothing').checked,
            fwhm: document.getElementById('smoothing-fwhm').value
        }
    };
}
