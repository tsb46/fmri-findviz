// preprocess.js
// API calls for preprocessing data

import { makeRequest, createFormData } from './utils.js';
import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';

/**
 * Preprocesses FMRI data with given parameters
 * @param {Object} preprocessParams - Parameters for FMRI preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getPreprocessedFMRI = async (
    preprocessParams, 
    errorInlineId,
    context_id
) => {
    return makeRequest(
        API_ENDPOINTS.PREPROCESS.GET_PREPROCESSED_FMRI,
        {
            method: 'POST',
            body: createFormData({
                ...preprocessParams,
                context_id
            })
        },
        {
            errorId: errorInlineId,
            isInline: true,
            errorPrefix: 'Error preprocessing FMRI data'
        }
    );
};

/**
 * Preprocesses timecourse data with given parameters
 * @param {Object} preprocessParams - Parameters for timecourse preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getPreprocessedTimeCourse = async (
    preprocessParams, 
    errorInlineId,
    context_id
) => {
    return makeRequest(
        API_ENDPOINTS.PREPROCESS.GET_PREPROCESSED_TIMECOURSE,
        {
            method: 'POST',
            body: createFormData({
                ...preprocessParams,
                context_id
            })
        },
        {
            errorId: errorInlineId,
            isInline: true,
            errorPrefix: 'Error preprocessing timecourse data'
        }
    );
};

/**
 * Resets FMRI preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const resetFMRIPreprocess = async (errorInlineId, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PREPROCESS.RESET_FMRI_PREPROCESS,
        {
            method: 'POST',
            body: createFormData({ context_id })
        },
        {
            errorId: errorInlineId,
            isInline: true,
            errorPrefix: 'Error resetting FMRI preprocessing'
        }
    );
};

/**
 * Resets timecourse preprocessing
 * @param {string} errorInlineId - ID of inline error element
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const resetTimeCoursePreprocess = async (
    selectedTimeCourses,
    errorInlineId,
    context_id
) => {
    return makeRequest(
        API_ENDPOINTS.PREPROCESS.RESET_TIMECOURSE_PREPROCESS,
        {
            method: 'POST',
            body: createFormData({
                ts_labels: selectedTimeCourses,
                context_id
            })
        },
        {
            errorId: errorInlineId,
            isInline: true,
            errorPrefix: 'Error resetting timecourse preprocessing'
        }
    );
};