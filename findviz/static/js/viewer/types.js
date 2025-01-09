// Type definitions for viewer module

/**
 * @typedef {Object} ViewerData
 * @property {string} file_type - Type of neuroimaging file ('nifti' or 'gifti')
 * @property {number[]} timepoints - Array of timepoint indices
 * @property {number} global_min - Global minimum value
 * @property {number} global_max - Global maximum value
 * @property {boolean} ts_enabled - Whether timeseries is enabled
 * @property {boolean} task_enabled - Whether task design is enabled
 * @property {Object} [slice_len] - NIFTI-specific slice lengths
 * @property {boolean} [anat_input] - Whether anatomical input exists (NIFTI)
 * @property {boolean} [mask_input] - Whether mask input exists (NIFTI)
 * @property {boolean} [left_input] - Whether left hemisphere exists (GIFTI)
 * @property {boolean} [right_input] - Whether right hemisphere exists (GIFTI)
 * @property {number[][]} [vertices_left] - Left hemisphere vertices (GIFTI)
 * @property {number[][]} [vertices_right] - Right hemisphere vertices (GIFTI)
 * @property {number[][]} [faces_left] - Left hemisphere faces (GIFTI)
 * @property {number[][]} [faces_right] - Right hemisphere faces (GIFTI)
 */

/**
 * @typedef {Object} VisualizationParams
 * @property {string} colormap - Colormap name
 * @property {number} timePoint - Current timepoint
 * @property {number} colorMin - Minimum color value
 * @property {number} colorMax - Maximum color value
 * @property {number} thresholdMin - Minimum threshold
 * @property {number} thresholdMax - Maximum threshold
 * @property {number} opacity - Opacity value
 * @property {boolean} hoverTextOn - Whether hover text is enabled
 */

/**
 * @typedef {Object} TaskDesign
 * @property {number[]} onset - Task onset times
 * @property {number[]} duration - Task durations
 * @property {string[]} trial_type - Task trial types
 */

/**
 * @typedef {Object} TimeCourseData
 * @property {Object.<string, number[]>} timeseries - Timeseries data by ROI
 * @property {string[]} labels - ROI labels
 * @property {TaskDesign} [task] - Optional task design data
 */

export const Types = {
    // Type checking functions
    isViewerData: (data) => {
        return data &&
            typeof data.file_type === 'string' &&
            Array.isArray(data.timepoints) &&
            typeof data.global_min === 'number' &&
            typeof data.global_max === 'number' &&
            typeof data.ts_enabled === 'boolean' &&
            typeof data.task_enabled === 'boolean';
    },
    
    isTaskDesign: (data) => {
        return data &&
            Array.isArray(data.onset) &&
            Array.isArray(data.duration) &&
            Array.isArray(data.trial_type);
    }
};