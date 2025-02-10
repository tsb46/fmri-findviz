// preprocess.js
// API calls for preprocessing data

import { makeRequest, createFormData } from './utils';
import { API_ENDPOINTS } from '../constants/APIEndpoints';


/**
 * Preprocesses FMRI data with given parameters
 * @param {Object} preprocessParams - Parameters for FMRI preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getPreprocessedFMRI = async (preprocessParams, errorInlineId, callback) => {
    return makeRequest(
        API_ENDPOINTS.GET_PREPROCESSED_FMRI,
        {
            method: 'POST',
            body: createFormData(preprocessParams)
        },
        {
            errorId: errorInlineId,
            isInline: true,
            errorPrefix: 'Error preprocessing FMRI data'
        },
        callback
    );
};

/**
 * Preprocesses timecourse data with given parameters
 * @param {Object} preprocessParams - Parameters for timecourse preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getPreprocessedTimecourse = async (preprocessParams, errorInlineId, callback) => {
    return makeRequest(
        API_ENDPOINTS.GET_PREPROCESSED_TIMECOURSE,
        {
            method: 'POST',
            body: createFormData(preprocessParams)
        },
        {
            errorId: errorInlineId,
            isInline: true,
            errorPrefix: 'Error preprocessing timecourse data'
        },
        callback
    );
};

/**
 * Resets FMRI preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const resetFMRIPreprocess = async (errorInlineId, callback) => {
    return makeRequest(
        API_ENDPOINTS.RESET_FMRI_PREPROCESS,
        { method: 'POST' },
        {
            errorPrefix: 'Error resetting FMRI preprocessing'
        },
        callback
    );
};

/**
 * Resets timecourse preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const resetTimecoursePreprocess = async (errorInlineId, callback) => {
    return makeRequest(
        API_ENDPOINTS.RESET_TIMECOURSE_PREPROCESS,
        { method: 'POST' },
        {
            errorPrefix: 'Error resetting timecourse preprocessing'
        },
        callback
    );
};