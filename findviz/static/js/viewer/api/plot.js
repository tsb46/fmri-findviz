
// API calls for modifying plot display
// Fetch functions:
// - checkFmriPreprocessed
// - checkTsPreprocessed
// - getAnnotationMarkers
// - getAnnotationMarkerPlotOptions
// - getColormapData
// - getDistancePlotOptions
// - getFmriPlotOptions
// - getNiftiViewState
// - getSelectedTimePoint
// - getTaskDesignPlotOptions
// - getTimeCoursePlotOptions
// - getTimeCourseGlobalPlotOptions
// - getTimeMarkerPlotOptions
// - getTimeCourseShiftHistory
// - getTSFmriPlotted

// Update functions:
// - addAnnotationMarker
// - changeTaskConvolution
// - clearAnnotationMarkers
// - moveAnnotationSelection
// - resetFmriColorOptions
// - resetTimeCourseShift
// - removeDistancePlot
// - undoAnnotationMarker
// - updateAnnotationMarkerPlotOptions
// - updateDistancePlotOptions
// - updateFmriPlotOptions
// - updateNiftiViewState
// - updateTaskDesignPlotOptions
// - updateTimeCoursePlotOptions
// - updateTimeCourseGlobalPlotOptions
// - updateTimeCourseShift
// - updateTimeMarkerPlotOptions


import { makeRequest, createFormData } from './utils.js';
import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';

/**
 * Add annotation marker
 * @param {number} marker - marker to add
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const addAnnotationMarker = async (marker, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.ADD_ANNOTATION_MARKER,
        {
            method: 'POST',
            body: createFormData({ marker, context_id })
        },
        {
            errorPrefix: 'Error adding annotation marker'
        }
    );
};

/**
 * Clear annotation markers
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const clearAnnotationMarkers = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.CLEAR_ANNOTATION_MARKERS,
        {
            method: 'POST',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error clearing annotation markers'
        }
    );
};

/**
 * Change task convolution
 * @param {boolean} convolution - Whether to convolve task design with hrf
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const changeTaskConvolution = async (convolution, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.CHANGE_TASK_CONVOLUTION,
        {
            method: 'POST',
            body: createFormData({ convolution, context_id })
        },
        { errorPrefix: 'Error changing task convolution' }
    );
};


/**
 * Check if fmri data is preprocessed
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const checkFmriPreprocessed = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.CHECK_FMRI_PREPROCESSED, 
        { 
            method: 'POST', 
            body: createFormData({ context_id }) 
        }, 
        { errorPrefix: 'Error checking fmri preprocessed' }
    );
};


/**
 * Check if time course is preprocessed
 * @param {string} label - Label of the time course to check
 * @param {string} ts_type - Type of the time course to check (timecourse or task)
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const checkTsPreprocessed = async (label, ts_type, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.CHECK_TS_PREPROCESSED,
        {
            method: 'POST',
            body: createFormData({ label, ts_type, context_id })
        },
        { errorPrefix: 'Error checking time course preprocessed' }
    );
};

/**
 * Get annotation markers
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getAnnotationMarkers = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_ANNOTATION_MARKERS,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error getting annotation markers'
        }
    );
};

/**
 * Fetches marker plot options from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getAnnotationMarkerPlotOptions = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_ANNOTATION_MARKER_PLOT_OPTIONS,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        { errorPrefix: 'Error fetching annotation marker plot options' }
    );
};

/**
 * Fetches colormap data from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getColormapData = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_COLORMAPS,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching colormap data'
        }
    );
};

/**
 * Fetches distance plot options from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getDistancePlotOptions = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_DISTANCE_PLOT_OPTIONS,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        { errorPrefix: 'Error fetching distance plot options' }
    );
};

/**
 * Fetches plot options from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getFmriPlotOptions = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_FMRI_PLOT_OPTIONS,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching plot options'
        }
    );
};


/**
 * Get current nifti view state (ortho or montage)
 * @returns {Promise} Promise object representing the API call
 */
export const getNiftiViewState = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_NIFTI_VIEW_STATE,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        { errorPrefix: 'Error fetching nifti view state' }
    );
};

/**
 * Get current selected time point
 * @returns {Promise} Promise object representing the API call
 */
export const getSelectedTimePoint = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_SELECTED_TIME_POINT,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        { errorPrefix: 'Error fetching selected time point' }
    );
};

/**
 * Get task design plot options
 * @param {string} label - Label of the task design to get plot options for.
 *      All plot options are returned if label is null
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTaskDesignPlotOptions = async (label, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TASK_DESIGN_PLOT_OPTIONS,
        {
            method: 'GET',
            body: createFormData({ label, context_id })
        },
        { errorPrefix: 'Error fetching task design plot options' }
    );
};

/**
 * Get time course plot options
 * @param {string} label - Label of the time course to get plot options for 
 *  - if null, all plot options are returned
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCoursePlotOptions = async (label, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TIMECOURSE_PLOT_OPTIONS,
        {
            method: 'GET',
            body: createFormData({ label, context_id })
        },
        { errorPrefix: 'Error fetching time course plot options' }
    );
};

/**
 * Get global time course plot options
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseGlobalPlotOptions = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TIMECOURSE_GLOBAL_PLOT_OPTIONS,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        { errorPrefix: 'Error fetching global time course plot options' }
    );
};

/**
 * Get time course shift history
 * @param {string} label - Label of the time course to get shift history for
 * @param {string} source - Source of the time course to get shift history for (timecourse or task)
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseShiftHistory = async (label, source, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TIMECOURSE_SHIFT_HISTORY,
        { method: 'GET', 
            body: createFormData({ label, source, context_id }) 
        },
        { errorPrefix: 'Error fetching time course shift history' }
    );
};


/**
 * Get time marker plot options
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeMarkerPlotOptions = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TIMEMARKER_PLOT_OPTIONS,
        { method: 'GET', 
            body: createFormData({ context_id }) 
        },
        { errorPrefix: 'Error fetching time marker plot options' }
    );
};


/**
 * Get whether an fmri timecourse is plotted
 * @returns {Promise} Promise object representing the API call
 */
export const getTSFmriPlotted = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.GET_TS_FMRI_PLOTTED, 
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        }, 
        { errorPrefix: 'Error fetching ts fmri plotted' }
    );
};


/**
 * Move annotation selection
 * @param {string} direction - Direction to move annotation selection
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const moveAnnotationSelection = async (direction, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.MOVE_ANNOTATION_SELECTION,
        {
            method: 'POST',
            body: createFormData({ direction, context_id })
        },
        {
            errorPrefix: 'Error moving annotation selection'
        }
    );
};

/**
 * Resets color options to default values
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const resetFmriColorOptions = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.RESET_FMRI_COLOR_OPTIONS,
        {
            method: 'POST',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error resetting color options'
        }
    );
};

/**
 * Reset time course shift
 * @param {string} label - Label of the time course to reset shift for
 * @param {string} source - Source of the time course to reset shift for (timecourse or task)
 * @param {string} change_type - Type of the shift to reset (constant or scale)
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const resetTimeCourseShift = async (label, source, change_type, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.RESET_TIMECOURSE_SHIFT,
        {
            method: 'POST',
            body: createFormData({ label, source, change_type, context_id })
        },
        { errorPrefix: 'Error resetting time course shift' }
    );
};
/**
 * Remove distance plot
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const removeDistancePlot = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.REMOVE_DISTANCE_PLOT,
        { method: 'POST',
            body: createFormData({ context_id })
        },
        { errorPrefix: 'Error removing distance plot' }
    );
};

/**
 * Undo most recent annotation marker
 * @returns {Promise} Promise object representing the API call
 */
export const undoAnnotationMarker = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UNDO_ANNOTATION_MARKER,
        { method: 'POST',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error undoing annotation marker'
        }
    );
};

/**
 * Update annotation marker plot options
 * @param {Object} annotationMarkerPlotOptions - Annotation marker plot options to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateAnnotationMarkerPlotOptions = async (annotationMarkerPlotOptions, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_ANNOTATION_MARKER_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                annotation_marker_plot_options: annotationMarkerPlotOptions,
                context_id
            })
        },
        { errorPrefix: 'Error updating annotation marker plot options' }
    );
};

/**
 * Updates distance plot options on the server
 * @param {Object} plotOptions - Plot options to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateDistancePlotOptions = async (plotOptions, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_DISTANCE_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                distance_plot_options: plotOptions,
                context_id
            })
        },
        { errorPrefix: 'Error updating distance plot options' }
    );
};

/**
 * Updates plot options on the server
 * @param {Object} plotOptions - Plot options to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateFmriPlotOptions = async (plotOptions, context_id) => {
    console.log(`Updating fMRI plot options: ${JSON.stringify(plotOptions)}`);
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_FMRI_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                fmri_plot_options: plotOptions,
                context_id
            })
        },
        {
            errorPrefix: 'Error updating fMRI plot options'
        }
    );
};

/**
 * Update nifti view state
 * @param {string} viewState - View state to update (ortho or montage)
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateNiftiViewState = async (viewState, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_NIFTI_VIEW_STATE,
        { method: 'POST',
            body: createFormData({ view_state: viewState, context_id })
        },
        { errorPrefix: 'Error updating nifti view state' }
    );
};

/**
 * Update task design plot options
 * @param {string} label - Label of the task design to update plot options for
 * @param {Object} taskDesignPlotOptions - Task design plot options to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateTaskDesignPlotOptions = async (label, taskDesignPlotOptions, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TASK_DESIGN_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                label,
                task_design_plot_options: taskDesignPlotOptions,
                context_id
            })
        },
        { errorPrefix: 'Error updating task design plot options' }
    );
};

/**
 * Update time course plot options
 * @param {string} label - Label of the time course to update plot options for
 * @param {Object} timeCoursePlotOptions - Time course plot options to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeCoursePlotOptions = async (label, timeCoursePlotOptions, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMECOURSE_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                label,
                timecourse_plot_options: timeCoursePlotOptions,
                context_id
            })
        },
        { errorPrefix: 'Error updating time course plot options' }
    );
};

/**
 * Update global time course plot options
 * @param {Object} timeCourseGlobalPlotOptions - Global time course plot options to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeCourseGlobalPlotOptions = async (timeCourseGlobalPlotOptions, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMECOURSE_GLOBAL_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                timecourse_global_plot_options: timeCourseGlobalPlotOptions,
                context_id
            })
        },
        { errorPrefix: 'Error updating global time course plot options' }
    );
};

/**
 * Update time course shift
 * @param {string} label - Label of the time course to update shift for
 * @param {string} source - Source of the time course to update shift for (task or timecourse)
 * @param {string} change_type - Type of the shift to update (constant or scale)
 * @param {string} change_direction - Direction of the shift change (increase or decrease)
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeCourseShift = async (
    label, 
    source, 
    change_type, 
    change_direction,
    context_id
) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMECOURSE_SHIFT,
        {
            method: 'POST',
            body: createFormData({
                label,
                source,
                change_type,
                change_direction,
                context_id
            })
        },
        { errorPrefix: 'Error updating time course shift' }
    );
};

/**
 * Update time marker plot options
 * @param {Object} timeMarkerPlotOptions - Time marker plot options to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimeMarkerPlotOptions = async (timeMarkerPlotOptions, context_id) => {
    return makeRequest(
        API_ENDPOINTS.PLOT_OPTIONS.UPDATE_TIMEMARKER_PLOT_OPTIONS,
        {
            method: 'POST',
            body: createFormData({
                timemarker_plot_options: timeMarkerPlotOptions,
                context_id
            })
        },
        { errorPrefix: 'Error updating time marker plot options' }
    );
};

