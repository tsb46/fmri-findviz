// analysis.js
// API calls for analysis functions
import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';
import { makeRequest, createFormData } from './utils.js';


/**
 * Correlate time course with fMRI data
 * 
 * @param {string} label - Label of time course to correlate
 * @param {string} time_course_type - Type of time course (timecourse or task)
 * @param {Object} correlateParams - Parameters for correlation
 * @param {string} errorInlineId - ID of inline error element
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const correlate = async (
    label, 
    time_course_type, 
    correlateParams, 
    errorInlineId, 
    context_id
) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.CORRELATE,
        { 
            method: 'POST', 
            body: createFormData(
                { 
                    label, 
                    time_course_type, 
                    ...correlateParams,
                    context_id
                }
            ) 
        },
        {
            errorPrefix: 'Error performing correlation',
            errorId: errorInlineId,
            isInline: true,
        }
    );
};


/**
 * Calculate distance between fmri time points
 * 
 * @param {string} distanceMetric - Metric for distance calculation
 * @param {string} errorInlineId - ID of inline error element
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const distance = async (
    distanceMetric,
    errorInlineId,
    context_id
) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.DISTANCE,
        { 
            method: 'POST', 
            body: createFormData(
                { distance_metric: distanceMetric, context_id }
            ) 
        },
        {
            errorPrefix: 'Error calculating distance',
            errorId: errorInlineId,
            isInline: true,
        }
    );
};

/**
 * Find peaks on selected time course
 * 
 * @param {string} label - Label of time course to find peaks on
 * @param {string} time_course_type - Type of time course (timecourse or task)
 * @param {Object} peakFinderParams - Parameters for peak finder
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const findPeaks = async (label, time_course_type, peakFinderParams, context_id) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.FIND_PEAKS,
        { 
            method: 'POST', 
            body: createFormData(
                { 
                    label, 
                    time_course_type, 
                    peak_finder_params: peakFinderParams,
                    context_id
                }
            ) 
        },
        {
            errorPrefix: 'Error finding peaks'
        }
    );
};


/**
 * Windowed average of fmri time courses
 * 
 * @param {Object} windowedAverageParams - Parameters for windowed average
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const windowedAverage = async (
    windowedAverageParams, 
    errorInlineId,
    context_id
) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.WINDOWED_AVERAGE, 
        { 
            method: 'POST', 
            body: createFormData(
                { 
                    window_average_params: JSON.stringify(windowedAverageParams), 
                    context_id 
                }
            ) 
        }, 
        {
            errorPrefix: 'Error during window average',
            errorId: errorInlineId,
            isInline: true,
        }
    );
};