// plot.js
// API calls for modifying plot display
// Fetch functions:
// - getAnnotationMarkers
// - getDistancePlotOptions
// - getColormapData
// - getFmriPlotOptions
// - getNiftiViewState
// - getSelectedTimePoint
// - getTaskDesignPlotOptions
// - getTimeCoursePlotOptions
// - getTimeCourseGlobalPlotOptions
// - getTimeMarkerPlotOptions

// Update functions:
// - addAnnotationMarker
// - changeTaskConvolution
// - clearAnnotationMarkers
// - moveAnnotationSelection
// - resetFmriColorOptions
// - removeDistancePlot
// - undoAnnotationMarker
// - updateDistancePlotOptions
// - updateFmriPlotOptions
// - updateNiftiViewState
// - updateTaskDesignPlotOptions
// - updateTimeCoursePlotOptions
// - updateTimeCourseGlobalPlotOptions
// - updateTimeCourseScale
// - updateTimeMarkerPlotOptions


import { makeRequest, createFormData } from './utils.js';
import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';

/**
 * Add annotation marker
 * @param {number} marker - marker to add
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const addAnnotationMarker = async (marker, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.ADD_ANNOTATION_MARKER,
        {
            method: 'POST',
            body: createFormData({ marker })
        },
        {
            errorPrefix: 'Error adding annotation marker'
        },
        callback
    );
};

/**
 * Clear annotation markers
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const clearAnnotationMarkers = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.CLEAR_ANNOTATION_MARKERS,
        {
            method: 'POST',
            body: createFormData({})
        },
        {
            errorPrefix: 'Error clearing annotation markers'
        },
        callback
    );
};

/**
 * Change task convolution
 * @param {boolean} convolution - Whether to convolve task design with hrf
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const changeTaskConvolution = async (convolution, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.CHANGE_TASK_CONVOLUTION,
        {
            method: 'POST',
            body: createFormData({ convolution })
        },
        { errorPrefix: 'Error changing task convolution' },
        callback
    );
};

/**
 * Get annotation markers
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getAnnotationMarkers = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_ANNOTATION_MARKERS,
        { method: 'GET' },
        {
            errorPrefix: 'Error getting annotation markers'
        },
        callback
    );
};

/**
 * Fetches distance plot options from the server
 * @param {Function} callback - Callback function to handle successful response 
 * @returns {Promise} Promise object representing the API call
 */
export const getDistancePlotOptions = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_DISTANCE_PLOT_OPTIONS,
        { method: 'GET' },
        { errorPrefix: 'Error fetching distance plot options' },
        callback
    );
};

/**
 * Fetches colormap data from the server
 * @param {Function} callback - Callback function to handle successful response 
 * @returns {Promise} Promise object representing the API call
 */
export const getColormapData = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_COLORMAPS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching colormap data'
        },
        callback
    );
};

/**
 * Fetches plot options from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getFmriPlotOptions = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_FMRI_PLOT_OPTIONS,
        { method: 'GET' },
        {
            errorPrefix: 'Error fetching plot options'
        },
        callback
    );
};

/**
 * Get current nifti view state (ortho or montage)
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getNiftiViewState = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_NIFTI_VIEW_STATE,
        { method: 'GET' },
        { errorPrefix: 'Error fetching nifti view state' },
        callback
    );
};

/**
 * Get current selected time point
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getSelectedTimePoint = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_SELECTED_TIME_POINT,
        { method: 'GET' },
        { errorPrefix: 'Error fetching selected time point' },
        callback
    );
};

/**
 * Get task design plot options
 * @param {string} label - Label of the task design to get plot options for
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTaskDesignPlotOptions = async (label, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TASK_DESIGN_PLOT_OPTIONS,
        {
            method: 'GET',
            body: createFormData({ label })
        },
        { errorPrefix: 'Error fetching task design plot options' },
        callback
    );
};

/**
 * Get time course plot options
 * @param {string} label - Label of the time course to get plot options for 
 *  (optional - if not provided, all plot options are returned)
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCoursePlotOptions = async (label = null, callback = null) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TIMECOURSE_PLOT_OPTIONS,
        {
            method: 'GET',
            body: createFormData({ label })
        },
        { errorPrefix: 'Error fetching time course plot options' },
        callback
    );
};

/**
 * Get global time course plot options
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseGlobalPlotOptions = async(callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS,
        { method: 'GET' },
        { errorPrefix: 'Error fetching global time course plot options' },
        callback
    );
}




/**
 * Get time marker plot options
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeMarkerPlotOptions = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TIMEMARKER_PLOT_OPTIONS,
        { method: 'GET' },
        { errorPrefix: 'Error fetching time marker plot options' },
        callback
    );
};


/**
 * Move annotation selection
 * @param {string} direction - Direction to move annotation selection
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const moveAnnotationSelection = async (direction, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.MOVE_ANNOTATION_SELECTION,
        {
            method: 'POST',
            body: createFormData({ direction })
        },
        {
            errorPrefix: 'Error moving annotation selection'
        },
        callback
    );
};

/**
 * Resets color options to default values
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const resetFmriColorOptions = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.RESET_FMRI_COLOR_OPTIONS,
        { method: 'POST' },
        {
            errorPrefix: 'Error resetting color options'
        },
        callback
    );
};

/**
 * Remove distance plot
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const removeDistancePlot = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.REMOVE_DISTANCE_PLOT,
        { method: 'POST' },
        { errorPrefix: 'Error removing distance plot' },
        callback
    );
};

/**
 * Undo most recent annotation marker
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const undoAnnotationMarker = async (callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UNDO_ANNOTATION_MARKER,
        { method: 'POST' },
        {
            errorPrefix: 'Error undoing annotation marker'
        },
        callback
    );
};

/**
 * Updates distance plot options on the server
 * @param {Object} plotOptions - Plot options to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateDistancePlotOptions = async (plotOptions, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_DISTANCE_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({ distance_plot_options: plotOptions })
        },
        { errorPrefix: 'Error updating distance plot options' },
        callback
    );
};

/**
 * Updates plot options on the server
 * @param {Object} plotOptions - Plot options to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateFmriPlotOptions = async (plotOptions, callback) => {
    console.log(`Updating fMRI plot options: ${JSON.stringify(plotOptions)}`);
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_FMRI_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({ fmri_plot_options: plotOptions })
        },
        {
            errorPrefix: 'Error updating fMRI plot options'
        },
        callback
    );
};

/**
 * Update nifti view state
 * @param {string} viewState - View state to update (ortho or montage)
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateNiftiViewState = async (viewState, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_NIFTI_VIEW_STATE,
        { method: 'POST', body: createFormData({ view_state: viewState }) },
        { errorPrefix: 'Error updating nifti view state' },
        callback
    );
};

/**
 * Update task design plot options
 * @param {string} label - Label of the task design to update plot options for
 * @param {Object} taskDesignPlotOptions - Task design plot options to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateTaskDesignPlotOptions = async (label, taskDesignPlotOptions, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TASK_DESIGN_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                label,
                task_design_plot_options: taskDesignPlotOptions
            })
        },
        { errorPrefix: 'Error updating task design plot options' },
        callback
    );
};

/**
 * Update time course plot options
 * @param {string} label - Label of the time course to update plot options for
 * @param {Object} timeCoursePlotOptions - Time course plot options to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeCoursePlotOptions = async (label, timeCoursePlotOptions, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMECOURSE_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                label,
                time_course_plot_options: timeCoursePlotOptions
            })
        },
        { errorPrefix: 'Error updating time course plot options' },
        callback
    );
};

/**
 * Update global time course plot options
 * @param {Object} timeCourseGlobalPlotOptions - Global time course plot options to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeCourseGlobalPlotOptions = async (timeCourseGlobalPlotOptions, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({ time_course_global_plot_options: timeCourseGlobalPlotOptions })
        },
        { errorPrefix: 'Error updating global time course plot options' },
        callback
    );
};

/**
 * Update time course scale
 * @param {string} label - Label of the time course to update scale for
 * @param {string} ts_type - Type of the time course to update scale for
 * @param {string} scale_change - Direction of the scale change
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeCourseScale = async (label, ts_type, scale_change, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMECOURSE_SCALE,
        {
            method: 'POST',
            body: createFormData({ label, ts_type, scale_change })
        },
        { errorPrefix: 'Error updating time course scale' },
        callback
    );
};

/**
 * Update time marker plot options
 * @param {Object} timeMarkerPlotOptions - Time marker plot options to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeMarkerPlotOptions = async (timeMarkerPlotOptions, callback) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMEMARKER_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({ time_marker_plot_options: timeMarkerPlotOptions })
        },
        { errorPrefix: 'Error updating time marker plot options' },
        callback
    );
};

