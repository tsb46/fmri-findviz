// preprocess.js
// API calls for preprocessing data

import { displayModalError, displayInlineError, clearInlineError } from '../error';


/**
 * Preprocesses FMRI data with given parameters
 * @param {Object} preprocessParams - Parameters for FMRI preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getPreprocessedFMRI = async (preprocessParams, errorInlineId, callback) => {
    try {
        console.log('preprocessFMRI called');
        const formData = new FormData();
        // Add preprocessing parameters to form data
        Object.keys(preprocessParams).forEach(key => {
            formData.append(key, preprocessParams[key]);
        });

        console.log('preprocessParams:', preprocessParams);

        const response = await fetch(API_ENDPOINTS.GET_PREPROCESSED_FMRI, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayInlineError(errorText, errorInlineId);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error preprocessing FMRI data:', error);
        displayModalError(error.message);
        return;
    }
};

/**
 * Preprocesses timecourse data with given parameters
 * @param {Object} preprocessParams - Parameters for timecourse preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getPreprocessedTimecourse = async (preprocessParams, errorInlineId, callback) => {
    try {
        const formData = new FormData();
        // Add preprocessing parameters to form data
        Object.keys(preprocessParams).forEach(key => {
            formData.append(key, preprocessParams[key]);
        });

        const response = await fetch(API_ENDPOINTS.GET_PREPROCESSED_TIMECOURSE, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayInlineError(errorText, errorInlineId);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error preprocessing timecourse data:', error);
        displayModalError(error.message);
        return;
    }
};

/**
 * Resets FMRI preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const resetFMRIPreprocess = async (errorInlineId, callback) => {
    try {
        const response = await fetch(API_ENDPOINTS.RESET_FMRI_PREPROCESS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        // clear inline error
        clearInlineError(errorInlineId);

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error resetting FMRI preprocessing:', error);
        displayInlineError(error.message, errorInlineId);
        return;
    }
};

/**
 * Resets timecourse preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const resetTimecoursePreprocess = async (errorInlineId, callback) => {
    try {
        const response = await fetch(API_ENDPOINTS.RESET_TIMECOURSE_PREPROCESS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        // clear inline error
        clearInlineError(errorInlineId);

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error resetting timecourse preprocessing:', error);
        displayModalError(error.message);
        return;
    }
};