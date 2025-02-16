// data.js 
// API calls for pulling fmri and time course data
// Fetch functions:
// - getCrosshairCoords
// - getDirectionLabelCoords
// - getDistanceData
// - getFMRIData
// - getClickCoords
// - getMontageData
// - getSliceLengths
// - getTaskConditions
// - getTimeCourseLabels
// - getTimeCourseData
// - getTimeCourseSource
// - getTimePoint
// - getViewerMetadata

// Update functions:
// - popFmriTimeCourse
// - removeFmriTimeCourses
// - updateFmriTimeCourse
// - updateLocation
// - updateMontageSliceDir
// - updateMontageSliceIdx
// - updateTimepoint

import { API_ENDPOINTS } from '../constants/APIEndpoints.js';
import { makeRequest, createFormData } from './utils.js';


/**
 * Change timecourse scale
 * @param {string} label - Label of the timecourse to change
 * @param {string} scale_change - Direction of the scale change
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const changeTimecourseScale = async (label, scale_change, callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.CHANGE_TIMECOURSE_SCALE,
        {
            method: 'POST',
            body: createFormData({ label, scale_change })
        },
        {
            errorPrefix: 'Error changing timecourse scale'
        },
        callback
    );
};

/**
 * Fetches click coords from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getClickCoords = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_CLICK_COORDS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching click coords'
        },
        callback
    );
};

/**
 * Fetches crosshair coordinates from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getCrosshairCoords = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_CROSSHAIR_COORDS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching crosshair coordinates'
        },
        callback
    );
};

/**
 * Fetches direction label coordinates from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getDirectionLabelCoords = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_DIRECTION_LABEL_COORDS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching direction label coordinates'
        },
        callback
    );
};

/**
 * Fetches distance vector from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getDistanceData = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_DISTANCE_DATA,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching distance data'
        },
        callback
    );
};

/**
 * Fetches FMRI data from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getFMRIData = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_FMRI_DATA,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching FMRI data'
        },
        callback
    );
};

/**
 * Fetches montage slice direction and montage slice indices from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getMontageData = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_MONTAGE_DATA,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching montage data'
        },
        callback
    );
};

/**
 * Fetches slice lengths from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getSliceLengths = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_SLICE_LENGTHS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching slice lengths'
        },
        callback
    );
};

/**
 * Fetches task conditions from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTaskConditions = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TASK_CONDITIONS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching task conditions'
        },
        callback
    );
};

/**
 * Fetches timecourse labels from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseLabels = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMECOURSE_LABELS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching timecourse labels'
        },
        callback
    );
};

/**
 * Fetches timecourse data from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseData = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMECOURSE_DATA,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching timecourse data'
        },
        callback
    );
};

/**
 * Fetches timecourse source from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseSource = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMECOURSE_SOURCE,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching timecourse source'
        },
        callback
    );
};

/**
 * Fetch timepoint from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTimePoint = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMEPOINT,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching timepoint'
        },
        callback
    );
};

/**
 * Fetches viewer metadata from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getViewerMetadata = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_VIEWER_METADATA,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching viewer metadata'
        },
        callback
    );
};

/**
 * Remove most recent fmri time course
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const popFmriTimeCourse = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.POP_FMRI_TIMECOURSE,
        { method: 'POST' },
        {
            errorPrefix: 'Error popping fmri timecourse'
        },
        callback
    );
};

/**
 * Remove all fmri time courses
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const removeFmriTimeCourses = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.REMOVE_FMRI_TIMECOURSES,
        { method: 'POST' },
        {
            errorPrefix: 'Error removing fmri timecourses'
        },
        callback
    );
};

/**
 * Updates functional timecourse data on the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateFmriTimeCourse = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_FMRI_TIMECOURSE,
        {
            method: 'POST',
        },
        {
            errorPrefix: 'Error updating fmri timecourse'
        },
        callback
    );
};

/**
 * Updates location data on the server
 * @param {Object} clickCoords - Click coordinates to update
 * @param {string} sliceName - Slice name to update - only for nifti data
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateLocation = async (clickCoords, sliceName, callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_LOCATION,
        {
            method: 'POST',
            body: createFormData({ click_coords: clickCoords, slice_name: sliceName })
        },
        {
            errorPrefix: 'Error updating location'
        },
        callback
    );
};

/**
 * Updates montage slice direction on the server
 * @param {string} montageSliceDir - Montage slice direction to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateMontageSliceDir = async (montageSliceDir, callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_MONTAGE_SLICE_DIR,
        {
            method: 'POST',
            body: createFormData({ montage_slice_dir: montageSliceDir })
        },
        {
            errorPrefix: 'Error updating montage slice direction'
        },
        callback
    );
};

/**
 * Updates montage slice indices on the server
 * @param {Object} montageSliceParams - Montage slice parameters to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateMontageSliceIdx = async (montageSliceParams, callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_MONTAGE_SLICE_IDX,
        {
            method: 'POST',
            body: createFormData(
                {
                    slice_name: montageSliceParams.slice_name,
                    slice_idx: montageSliceParams.slice_idx
                }
            )
        },
        {
            errorPrefix: 'Error updating montage slice indices'
        },
        callback
    );
};

/**
 * Updates timepoint on the server
 * @param {number} timePoint - Time point to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimepoint = async (timePoint, callback) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_TIMEPOINT,
        {
            method: 'POST',
            body: createFormData({ time_point: timePoint })
        },
        {
            errorPrefix: 'Error updating timepoint'
        },
        callback
    );
};

