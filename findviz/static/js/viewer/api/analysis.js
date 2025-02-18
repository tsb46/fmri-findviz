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
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const correlate = async (label, time_course_type, correlateParams, callback) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.CORRELATE,
        { method: 'POST', body: createFormData({ label, time_course_type, ...correlateParams }) },
        callback
    );
};


/**
 * Calculate distance between fmri time points
 * 
 * @param {Object} distanceParams - Parameters for distance calculation
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const distance = async (distanceParams, callback) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.DISTANCE,
        { method: 'POST', body: createFormData(distanceParams) },
        callback
    );
};

/**
 * Find peaks on selected time course
 * 
 * @param {string} label - Label of time course to find peaks on
 * @param {Object} peakFinderParams - Parameters for peak finder
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const findPeaks = async (label, time_course_type, peakFinderParams, callback) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.FIND_PEAKS,
        { method: 'POST', body: createFormData(
            { label, time_course_type, ...peakFinderParams }
            ) 
        },
        {
            errorPrefix: 'Error finding peaks'
        },
        callback
    );
};


/**
 * Windowed average of fmri time courses
 * 
 * @param {Object} windowedAverageParams - Parameters for windowed average
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const windowedAverage = async (windowedAverageParams, callback) => {
    return makeRequest(
        API_ENDPOINTS.ANALYSIS.WINDOWED_AVERAGE, 
        { method: 'POST', body: createFormData(windowedAverageParams) }, 
        {
            errorPrefix: 'Error windowing average'
        },
        callback
    );
};