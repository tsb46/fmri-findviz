// File Types
export const FILE_TYPES = {
    NIFTI: 'nifti',
    GIFTI: 'gifti'
};

// DOM Element IDs
export const DOM_IDS = {
    TIME_SLIDER_TITLE: 'time-slider-title',
    UPLOAD_BUTTON: 'upload-file',
    SAVE_SCENE: 'save-scene-display',
    COLORMAP_SELECT: 'colormapSelect',
    PARENT_CONTAINER: 'parent-container',
    TIME_COURSE_CONTAINER: 'time-course-container',
    ENABLE_TIME_COURSE: 'enable-time-course',
    FREEZE_TIME_COURSE: 'freeze-time-course',
    UNDO_TIME_COURSE: 'undo-time-course',
    REMOVE_TIME_COURSE: 'remove-time-course',
    FREEZE_ICON: 'freeze-icon',
    TIME_COURSE_FREEZE_ICON: 'time-course-freeze-icon',
    TIME_COURSE_UNDO_ICON: 'time-course-undo-icon',
    ERROR_MESSAGES: {
        AVERAGE: 'error-message-average',
        CORRELATION: 'error-message-correlation',
        DISTANCE: 'error-message-distance'
    },
    SPINNERS: {
        AVERAGE_OVERLAY: 'average-spinner-overlay',
        AVERAGE: 'average-spinner',
        CORRELATE_OVERLAY: 'correlate-spinner-overlay',
        CORRELATE: 'correlate-spinner',
        DISTANCE_OVERLAY: 'distance-spinner-overlay',
        DISTANCE: 'distance-spinner'
    },
    MODALS: {
        AVERAGE: 'averageModal',
        CORRELATION: 'correlationModal',
        DISTANCE: 'distanceModal'
    },
    DISTANCE_EDGES: {
        LEFT: 'averageLeftEdge',
        RIGHT: 'averageRightEdge'
    },
    CORRELATION_LAGS: {
        NEGATIVE: 'correlateNegativeLag',
        POSITIVE: 'correlatePositiveLag'
    },
    NIFTI_CONTAINERS: {
        SLICE_CONTAINER: 'slices_container',
        X_SLICE: 'x_slice_container',
        Y_SLICE: 'y_slice_container',
        Z_SLICE: 'z_slice_container',
        COLORBAR: 'colorbar_container_nii'
    }
};

// Container IDs
export const CONTAINER_IDS = {
    COLORBAR: {
        NIFTI: 'colorbar_container_nii',
        GIFTI: 'colorbar_container_gii'
    }
};

// Default Values
export const DEFAULTS = {
    COLORMAP: 'Viridis',
    OPACITY: 1,
    THRESHOLD: {
        MIN: 0,
        MAX: 0
    },
    SLIDER_STEPS: 100,
    ALLOWED_PRECISION: 6,
    TIME_POINT: 0
};

// API Endpoints
export const API_ENDPOINTS = {
    CHECK_CACHE: '/check_cache',
    CLEAR_CACHE: '/clear_cache',
    COMPUTE: {
        AVERAGE_NIFTI: '/compute_avg_nii',
        AVERAGE_GIFTI: '/compute_avg_gii',
        CORRELATION_NIFTI: '/compute_corr_nii',
        CORRELATION_GIFTI: '/compute_corr_gii',
        DISTANCE_NIFTI: '/compute_distance_nii',
        DISTANCE_GIFTI: '/compute_distance_gii'
    },
    NIFTI: {
        GET_SLICES: '/get_slices',
        GET_TIME_COURSE: '/get_time_course_nii'
    }
};

// Event Names
export const EVENTS = {
    DISTANCE_SUBMIT: 'distanceSubmit',
    CORRELATION_SUBMIT: 'correlationSubmit',
    AVERAGE_SUBMIT: 'averageSubmit'
};