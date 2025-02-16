// preprocess.js
// API calls for preprocessing data

import { makeRequest, createFormData } from './utils.js';
import { API_ENDPOINTS } from '../constants/APIEndpoints.js';


/**
 * Preprocesses FMRI data with given parameters
 * @param {Object} preprocessParams - Parameters for FMRI preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getPreprocessedFMRI = async (preprocessParams, errorInlineId, callback) => {
    return makeRequest(
        API_ENDPOINTS.PREPROCESS.GET_PREPROCESSED_FMRI,
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
export const getPreprocessedTimeCourse = async (preprocessParams, errorInlineId, callback) => {
    return makeRequest(
        API_ENDPOINTS.PREPROCESS.GET_PREPROCESSED_TIMECOURSE,
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
        API_ENDPOINTS.PREPROCESS.RESET_FMRI_PREPROCESS,
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
export const resetTimeCoursePreprocess = async (errorInlineId, callback) => {
    return makeRequest(
        API_ENDPOINTS.PREPROCESS.RESET_TIMECOURSE_PREPROCESS,
        { method: 'POST' },
        {
            errorPrefix: 'Error resetting timecourse preprocessing'
        },
        callback
    );
};