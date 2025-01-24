// DOM IDs - used to identify DOM elements

export const DOM_IDS = {
    UPLOAD_BUTTON: 'upload-file',
    SAVE_SCENE: 'save-scene-display',
    COLORMAP_SELECT: 'colormapSelect',
    PARENT_CONTAINER: 'parent-container',
    FMRI: {
        NIFTI_CONTAINERS: {
            SLICE_CONTAINER: 'slices_container',
            X_SLICE: 'x_slice_container',
            Y_SLICE: 'y_slice_container',
            Z_SLICE: 'z_slice_container',
            COLORBAR: 'colorbar_container_nii'
        },
        GIFTI_CONTAINERS: {
            SURFACE_CONTAINER: 'surface_container',
            COLORBAR: 'colorbar_container_gii'
        },
        USER_OPTIONS: {
            MONTAGE_POPOVER: 'montage-popover',
            MONTAGE_SLICE_SELECT: 'montage-slice-select',
            COLOR_RANGE_SLIDER: 'color-range-slider',
            THRESHOLD_SLIDER: 'threshold-slider',
            OPACITY_SLIDER: 'opacity-slider',
            COLORMAP_DROPDOWN: 'colormap-dropdown',
            COLORMAP_DROPDOWN_MENU: 'colormap-dropdown-menu',
            COLORMAP_DROPDOWN_TOGGLE: 'colormap-dropdown-toggle'
        }
    },
    TIME_SLIDER: {
        TIME_SLIDER_TITLE: 'time-slider-title',
    },
    TIMECOURSE : {
        TIME_COURSE_CONTAINER: 'time-course-container',
        ENABLE_TIME_COURSE: 'enable-time-course',
        FREEZE_TIME_COURSE: 'freeze-time-course',
        UNDO_TIME_COURSE: 'undo-time-course',
        REMOVE_TIME_COURSE: 'remove-time-course',
        FREEZE_ICON: 'freeze-icon',
        TIME_COURSE_FREEZE_ICON: 'time-course-freeze-icon',
        TIME_COURSE_UNDO_ICON: 'time-course-undo-icon',
        REMOVE_ICON: 'remove-icon',
    },
    ERROR_MESSAGES: {
        VIEWER: 'error-message-viewer',
        AVERAGE: 'error-message-average',
        CORRELATION: 'error-message-correlation',
        DISTANCE: 'error-message-distance',
        PREPROCESS: 'error-message-preprocess',
        TIMECOURSE: 'error-message-timecourse'
    },
    SPINNERS: {
        AVERAGE_OVERLAY: 'average-spinner-overlay',
        AVERAGE: 'average-spinner',
        CORRELATE_OVERLAY: 'correlate-spinner-overlay',
        CORRELATE: 'correlate-spinner',
        DISTANCE_OVERLAY: 'distance-spinner-overlay',
        DISTANCE: 'distance-spinner',
        PREPROCESS_OVERLAY: 'preprocess-spinner-overlay',
        PREPROCESS: 'preprocess-load-spinner'
    },
    MODALS: {
        AVERAGE: 'averageModal',
        CORRELATION: 'correlationModal',
        DISTANCE: 'distanceModal',
        ERROR: 'errorModal'
    },
    DISTANCE_EDGES: {
        LEFT: 'averageLeftEdge',
        RIGHT: 'averageRightEdge'
    },
    CORRELATION_LAGS: {
        NEGATIVE: 'correlateNegativeLag',
        POSITIVE: 'correlatePositiveLag'
    },
    
};