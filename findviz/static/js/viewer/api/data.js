// data.js 
// API calls for pulling fmri and time course data
// Fetch functions:
// - getClickCoords
// - getCoordLabels
// - getCrosshairCoords
// - getDirectionLabelCoords
// - getDistanceData
// - getFMRIData
// - getMontageData
// - getTaskConditions
// - getTimeCourseData
// - getTimeCourseLabels
// - getTimeCourseLabelsPreprocessed
// - getTimeCourseSource
// - getTimePoint
// - getTimePoints
// - getVertexCoords
// - getViewerMetadata
// - getVoxelCoords
// - getWorldCoords

// Update functions:
// - convertTimepoints
// - popFmriTimeCourse
// - removeFmriTimeCourses
// - updateFmriTimeCourse
// - updateLocation
// - updateMontageSliceDir
// - updateMontageSliceIdx
// - updateTimepoint
// - updateTr

import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';
import { makeRequest, createFormData } from './utils.js';

/**
 * Convert timepoints to seconds
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const convertTimepoints = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.CONVERT_TIMEPOINTS,
        {
            method: 'POST',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error converting timepoints to seconds'
        }
    );
};


/**
 * Fetches click coords from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getClickCoords = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_CLICK_COORDS,
        {
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching click coords'
        }
    );
};


/**
 * Fetches coordinate labels from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getCoordLabels = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_COORD_LABELS,
        {
            method: 'GET',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error fetching coordinate labels'
        }
    );
};

/**
 * Fetches crosshair coordinates from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getCrosshairCoords = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_CROSSHAIR_COORDS,
        {
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching crosshair coordinates'
        }
    );
};

/**
 * Fetches direction label coordinates from the server
 * @returns {Promise} Promise object representing the API call
 */
export const getDirectionLabelCoords = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_DIRECTION_LABEL_COORDS,
        {
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching direction label coordinates'
        }
    );
};

/**
 * Fetches distance vector from the server
 * @returns {Promise} Promise object representing the API call
 */
export const getDistanceData = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_DISTANCE_DATA,
        {
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching distance data'
        }
    );
};

/**
 * Fetches FMRI data from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getFMRIData = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_FMRI_DATA,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching FMRI data'
        }
    );
};

/**
 * Fetches last added fmri timecourse from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getLastTimecourse = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_LAST_TIMECOURSE,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching last fmri timecourse'
        }
    );
};

/**
 * Fetches montage slice direction and montage slice indices from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getMontageData = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_MONTAGE_DATA,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching montage data'
        }
    );
};

/**
 * Fetches task conditions from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTaskConditions = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TASK_CONDITIONS,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching task conditions'
        }
    );
};

/**
 * Fetches timecourse data from the server
 * @param {Array} ts_labels - Array of timecourse labels to fetch - if null,
 * all timecourse data will be fetched
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseData = async (ts_labels = null, context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMECOURSE_DATA,
        {
            method: 'GET',
            body: createFormData({ ts_labels, context_id })
        },
        {
            errorPrefix: 'Error fetching timecourse data'
        }
    );
};

/**
 * Fetches timecourse labels from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseLabels = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMECOURSE_LABELS,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching timecourse labels'
        }
    );
};

/**
 * Fetches preprocessed timecourse labels from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseLabelsPreprocessed = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMECOURSE_LABELS_PREPROCESSED,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching preprocessed timecourse labels'
        }
    );
};

/**
 * Fetches timecourse source from the server
 * @returns {Promise} Promise object representing the API call
 */
export const getTimeCourseSource = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMECOURSE_SOURCE,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching timecourse source'
        }
    );
};

/**
 * Fetch selected timepoint from the server
 * @returns {Promise} Promise object representing the API call
 */
export const getTimePoint = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMEPOINT,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching timepoint'
        }
    );
};

/**
 * Fetches timepoints from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getTimePoints = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_TIMEPOINTS,
        {
            method: 'GET',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error fetching timepoints'
        }
    );
};


/**
 * Fetches vertex coordinates from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getVertexCoords = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_VERTEX_COORDS,
        {
            method: 'GET',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error fetching vertex coordinates'
        }
    );
};

/**
 * Fetches viewer metadata from the server
 * @returns {Promise} Promise object representing the API call
 */
export const getViewerMetadata = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_VIEWER_METADATA,
        { 
            method: 'GET', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error fetching viewer metadata'
        }
    );
};

/** 
 * Fetches voxel coordinates from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getVoxelCoords = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_VOXEL_COORDS,
        {
            method: 'GET',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error fetching voxel coordinates'
        }
    );
};

/**
 * Fetches world coordinates from the server
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const getWorldCoords = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.GET_WORLD_COORDS,
        {
            method: 'GET',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error fetching world coordinates'
        }
    );
};

/**
 * Remove most recent fmri time course
 * @returns {Promise} Promise object representing the API call
 */
export const popFmriTimeCourse = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.POP_FMRI_TIMECOURSE,
        { 
            method: 'POST', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error popping fmri timecourse'
        }
    );
};

/**
 * Remove all fmri time courses
 * @returns {Promise} Promise object representing the API call
 */
export const removeFmriTimeCourses = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.REMOVE_FMRI_TIMECOURSES,
        { 
            method: 'POST', 
            body: createFormData({ context_id }) 
        },
        {
            errorPrefix: 'Error removing fmri timecourses'
        }
    );
};

/**
 * Updates functional timecourse data on the server
 * @returns {Promise} Promise object representing the API call
 */
export const updateFmriTimeCourse = async (context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_FMRI_TIMECOURSE,
        {
            method: 'POST',
            body: createFormData({ context_id })
        },
        {
            errorPrefix: 'Error updating fmri timecourse'
        }
    );
};

/**
 * Updates location data on the server
 * @param {Object} clickCoords - Click coordinates to update
 * @param {string} sliceName - Slice name to update - only for nifti data
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateLocation = async (clickCoords, sliceName, context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_LOCATION,
        {
            method: 'POST',
            body: createFormData(
                { click_coords: clickCoords, slice_name: sliceName, context_id }
            )
        },
        {
            errorPrefix: 'Error updating location'
        }
    );
};

/**
 * Updates montage slice direction on the server
 * @param {string} montageSliceDir - Montage slice direction to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateMontageSliceDir = async (montageSliceDir, context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_MONTAGE_SLICE_DIR,
        {
            method: 'POST',
            body: createFormData(
                { montage_slice_dir: montageSliceDir, context_id }
            )
        },
        {
            errorPrefix: 'Error updating montage slice direction'
        }
    );
};

/**
 * Updates montage slice indices on the server
 * @param {Object} montageSliceParams - Montage slice parameters to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateMontageSliceIdx = async (montageSliceParams, context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_MONTAGE_SLICE_IDX,
        {
            method: 'POST',
            body: createFormData(
                {
                    slice_name: montageSliceParams.slice_name,
                    slice_idx: montageSliceParams.slice_idx,
                    context_id
                }
            )
        },
        {
            errorPrefix: 'Error updating montage slice indices'
        }
    );
};

/**
 * Updates timepoint on the server
 * @param {number} timePoint - Time point to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimepoint = async (timePoint, context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_TIMEPOINT,
        {
            method: 'POST',
            body: createFormData(
                { time_point: timePoint, context_id }
            )
        },
        {
            errorPrefix: 'Error updating timepoint'
        }
    );
};

/**
 * Updates TR on the server
 * @param {number} tr - TR to update
 * @param {string} context_id - ID of context to switch to
 * @returns {Promise} Promise object representing the API call
 */
export const updateTr = async (tr, context_id) => {
    return makeRequest(
        API_ENDPOINTS.DATA.UPDATE_TR,
        {
            method: 'POST',
            body: createFormData({ tr, context_id })
        },
        {
            errorPrefix: 'Error updating TR'
        }
    );
};