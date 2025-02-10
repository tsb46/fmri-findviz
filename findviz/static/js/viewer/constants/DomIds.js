// DOM IDs - used to identify DOM elements

export const DOM_IDS = {
    AVERAGE: {
        LEFT_EDGE: 'average-left-edge',
        RIGHT_EDGE: 'average-right-edge',
        SUBMIT_AVERAGE: 'submit-average',
        AVERAGE_FORM: 'average-form',
        ANNOTATION_WARNING: 'no-annotation-message-average'
    },
    CORRELATE: {
        NEGATIVE_LAG: 'correlate-negative-lag',
        POSITIVE_LAG: 'correlate-positive-lag',
        CORRELATE_FORM: 'correlation-form',
        SUBMIT_CORRELATE: 'submit-correlation',
        TIMECOURSE_SELECT: 'ts-correlate-select'
    },
    DISTANCE: {
        CONTAINER: 'distance-container',
        COLORMAP_DROPDOWN: 'distance-plot-colormap',
        COLORMAP_DROPDOWN_MENU: 'distance-plot-colormap-dropdown-menu',
        COLORMAP_DROPDOWN_TOGGLE: 'distance-plot-colormap-dropdown-toggle',
        COLOR_RANGE_SLIDER: 'distance-plot-color-range',
        DISTANCE_FORM: 'distance-form',
        METRIC_SELECT: 'distance-metric-select',
        TIME_POINT_MESSAGE: 'timepoint-distance-label',
        TIME_MARKER_WIDTH_SLIDER: 'distance-plot-time-marker-width',
        TIME_MARKER_OPACITY_SLIDER: 'distance-plot-time-marker-opacity',
        PLOT: 'distance-plot',
        POPOVER: 'distance-popover',
        REMOVE_DISTANCE_BUTTON: 'remove-distance-plot',
        PREPROCESS_ALERT: 'distance-prep-alert'
    },
    ERROR_MESSAGES: {
        VIEWER: 'error-message-viewer',
        AVERAGE: 'error-message-average',
        CORRELATION: 'error-message-correlation',
        DISTANCE: 'error-message-distance',
        PREPROCESS: 'error-message-preprocess',
        TIMECOURSE: 'error-message-timecourse'
    },
    FMRI: {
        GIFTI_CONTAINERS: {
            COLORBAR: 'colorbar-container-gii',
            SURFACE_CONTAINER: 'surface-container',
            LEFT_SURFACE_CONTAINER: 'left-surface-container',
            RIGHT_SURFACE_CONTAINER: 'right-surface-container'
        },
        NIFTI_CONTAINERS: {
            COLORBAR: 'colorbar-container-nii',
            SLICE_CONTAINER: 'slice-container',
            SLICE_1_CONTAINER: 'slice-1-container',
            SLICE_2_CONTAINER: 'slice-2-container',
            SLICE_3_CONTAINER: 'slice-3-container'
        },
        VISUALIZATION_OPTIONS: {
            COLOR_RANGE_SLIDER: 'color-range-slider',
            COLORMAP_DROPDOWN: 'colormap-dropdown',
            COLORMAP_DROPDOWN_MENU: 'colormap-dropdown-menu',
            COLORMAP_DROPDOWN_TOGGLE: 'colormap-dropdown-toggle',
            CROSSHAIR_TOGGLE: 'crosshair-toggle',
            HOVER_TOGGLE: 'hover-toggle',
            DIRECTION_LABELS_TOGGLE: 'direction-labels-toggle',
            MONTAGE_POPOVER: 'montage-popover',
            MONTAGE_SLICE_SELECT: 'montage-slice-select',
            MONTAGE_SLICE_1_SLIDER: 'slice-1-slider',
            MONTAGE_SLICE_2_SLIDER: 'slice-2-slider',
            MONTAGE_SLICE_3_SLIDER: 'slice-3-slider',
            OPACITY_SLIDER: 'opacity-slider',
            PLAY_MOVIE_BUTTON: 'play-movie',
            RESET_SLIDER_BUTTON: 'reset-slider-button',
            THRESHOLD_SLIDER: 'threshold-slider',
            TOGGLE_VIEW_BUTTON: 'toggle-view',
            SCREENSHOT_BUTTON: 'select-screenshot',

        },
        PREPROCESSING_OPTIONS: {
            ENABLE_NORMALIZATION: 'enable-normalization',
            ENABLE_FILTERING: 'enable-filtering',
            ENABLE_SMOOTHING: 'enable-smoothing',
            FILTER_LOW_CUT: 'filter-low-cut',
            FILTER_HIGH_CUT: 'filter-high-cut',
            FILTER_TR: 'filter-tr',
            SELECT_MEAN_CENTER: 'select-mean-center',
            SELECT_Z_SCORE: 'select-z-score',
            SMOOTHING_FWHM: 'smoothing-fwhm',
            SUBMIT_PREPROCESS_BUTTON: 'submit-preprocess-button',
            RESET_PREPROCESS_BUTTON: 'reset-preprocess-button',
            ERROR_MESSAGE_PREPROCESS: 'error-message-preprocess',
            PREPROCESS_ALERT: 'preprocess-alert'
        }
    },
    MODALS: {
        AVERAGE: 'average-modal',
        CORRELATION: 'correlation-modal',
        DISTANCE: 'distance-modal',
        ERROR: 'error-modal'
    },
    PARENT_CONTAINER: 'parent-container',
    TIME_SLIDER: {
        TIME_SLIDER: 'time-slider',
        TIME_SLIDER_TITLE: 'time-slider-title',
    },
    TIMECOURSE : {
        ANNOTATE: {
            ENABLE_ANNOTATE: 'enable-annotate',
            LEFT_MOVE_ANNOTATE: 'left-move-annotate',
            RIGHT_MOVE_ANNOTATE: 'right-move-annotate',
            HIGHLIGHT_ANNOTATE: 'highlight-annotate',
            UNDO_ANNOTATE: 'undo-annotate',
            REMOVE_ANNOTATE: 'remove-annotate',
        },
        LINE_PLOT_OPTIONS: {
            SELECT_TIMECOURSE: 'ts-select',
            COLOR_SELECT: 'ts-color-select',
            MARKER_SELECT: 'ts-marker-select',
            WIDTH_SLIDER: 'ts-width-slider',
            OPACITY_SLIDER: 'ts-opacity-slider'
        },
        MARKER_PLOT_OPTIONS: {
            COLOR_SELECT: 'timepoint-color-select',
            OPACITY_SLIDER: 'timepoint-opacity-slider',
            MARKER_SELECT: 'timepoint-marker-select',
            WIDTH_SLIDER: 'timepoint-width-slider'
        },
        PEAK_FINDER: {
            POPOVER: 'peak-finder-popover',
            PEAK_FORM: 'peak-finder-form',
            SELECT_TIMECOURSE: 'ts-select-peak-finder',
            SUBMIT_PEAK_FINDER: 'submit-peak-finder'
        },
        PREPROCESSING_OPTIONS: {
            ENABLE_NORMALIZATION: 'ts-enable-normalization',
            ENABLE_FILTERING: 'ts-enable-filtering',
            ERROR_MESSAGE_PREPROCESS: 'ts-error-message-preprocess',
            FILTER_LOW_CUT: 'ts-filter-low-cut',
            FILTER_HIGH_CUT: 'ts-filter-high-cut',
            FILTER_TR: 'ts-filter-tr',
            RESET_PREPROCESS_BUTTON: 'ts-reset-preprocess',
            SELECT_MEAN_CENTER: 'ts-select-mean-center',
            SELECT_Z_SCORE: 'ts-select-z-score',
            SELECT_TIMECOURSE: 'ts-prep-select',
            SUBMIT_PREPROCESS_BUTTON: 'ts-submit-preprocess',
        },
        PREPROCESS_ALERT: 'ts-preprocess-alert',
        TIME_COURSE_CONTAINER: 'time-course-container',
        TIME_COURSE_PLOT: 'time-course-plot',
        FREEZE_TIME_COURSE: 'freeze-time-course',
        UNDO_TIME_COURSE: 'undo-time-course',
        REMOVE_TIME_COURSE: 'remove-time-course',
        VISUALIZATION_OPTIONS: {
            TOGGLE_CONVOLUTION: 'toggle-convolution',
            TOGGLE_GRID: 'toggle-grid',
            TOGGLE_TIME_MARKER: 'toggle-time-marker',
            TOGGLE_TS_HOVER: 'toggle-ts-hover'
        }
    },
    SAVE_SCENE: 'save-scene-display',
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
    UPLOAD_BUTTON: 'upload-file'
    
};