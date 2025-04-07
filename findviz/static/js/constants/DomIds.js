// DOM IDs - used to identify DOM elements

export const DOM_IDS = {
    AVERAGE: {
        ANNOTATION_WARNING: 'no-annotation-message-average',
        AVERAGE_FORM: 'average-form',
        ERROR_MESSAGE: 'error-message-average',
        LEFT_EDGE: 'average-left-edge',
        MODAL_BUTTON: 'run-average-button',
        RIGHT_EDGE: 'average-right-edge',
        SPINNER_OVERLAY: 'average-spinner-overlay',
        SPINNER_WHEEL: 'average-spinner-wheel',
        SUBMIT_AVERAGE: 'submit-average',
    },
    CORRELATE: {
        CORRELATE_FORM: 'correlation-form',
        ERROR_MESSAGE: 'error-message-correlation',
        MODAL_BUTTON: 'run-correlation-button',
        NEGATIVE_LAG: 'correlate-negative-lag',
        POSITIVE_LAG: 'correlate-positive-lag',
        PREPROCESS_ALERT: 'correlate-prep-alert',
        SPINNER_OVERLAY: 'correlate-spinner-overlay',
        SPINNER_WHEEL: 'correlate-spinner-wheel',
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
        ERROR_MESSAGE: 'error-message-distance',
        METRIC_SELECT: 'distance-metric-select',
        MODAL_BUTTON: 'distance-modal-button',
        TIME_POINT_MESSAGE: 'timepoint-distance-label',
        TIME_MARKER_WIDTH_SLIDER: 'distance-plot-time-marker-width',
        TIME_MARKER_OPACITY_SLIDER: 'distance-plot-time-marker-opacity',
        PLOT: 'distance-plot',
        POPOVER: 'distance-popover',
        REMOVE_DISTANCE_BUTTON: 'remove-distance-plot',
        PREPROCESS_ALERT: 'distance-prep-alert',
        SPINNER_OVERLAY: 'distance-spinner-overlay',
        SPINNER_WHEEL: 'distance-spinner-wheel'
    },
    FILE_UPLOAD: {
        ERROR_MESSAGE: 'error-message-upload',
        ERROR_MODAL_SERVER: 'error-upload-modal',
        ERROR_MODAL_SCENE: 'error-scene-modal',
        FMRI: {
            GIFTI: {
                LEFT_FUNC: 'left-hemisphere-gifti-func',
                RIGHT_FUNC: 'right-hemisphere-gifti-func',
                LEFT_MESH: 'left-hemisphere-gifti-mesh',
                RIGHT_MESH: 'right-hemisphere-gifti-mesh'
            },
            NIFTI: {
                FUNC: 'nifti-func',
                ANAT: 'nifti-anat',
                MASK: 'nifti-mask',
            },
            CIFTI: {
                DTSERIES: 'cifti-dtseries',
                LEFT_MESH: 'cifti-surf-left',
                RIGHT_MESH: 'cifti-surf-right'
            }
        },
        FORM: 'upload-form',
        MODAL: 'upload-modal',
        MODAL_BUTTON: 'upload-file',
        SPINNERS: {
            OVERLAY: 'file-load-spinner-overlay',
            WHEEL: 'file-load-spinner-wheel'
        },
        TS: {
            ADD_TS: 'add-time-series',
            CONTAINER: 'time-series-file-container',
            FILE: 'time-series-file',
            LABEL: 'time-series-label',
            HEADER: 'has-header',
            REMOVE_BUTTON: 'remove-time-series',
            FILE_PAIR: 'times-series-file-pair'
        },
        TASK: {
          FILE: 'task-design-file',
          TR: 'task-design-tr',
          SLICETIME: 'task-design-slicetime'
        },
        SCENE: {
            BUTTON: 'upload-scene',
            FILE: 'file-scene'
        },
        SUBMIT_BUTTON: 'submit-file'
    },
    FMRI: {
        COORDINATE: {
            WORLD_X: 'x-world',
            WORLD_Y: 'y-world',
            WORLD_Z: 'z-world',
            VOXEL_X: 'x-voxel',
            VOXEL_Y: 'y-voxel',
            VOXEL_Z: 'z-voxel',
            WORLD_COORD_CONTAINER: 'world-coord-container',
            VOXEL_COORD_CONTAINER: 'voxel-coord-container',
            VERTEX_COORD_CONTAINER: 'vertex-coord-container',
            VERTEX_NUMBER: 'vertex-number',
            SELECTED_HEMISPHERE: 'selected-hemisphere'
        },
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
        PREPROCESSING_OPTIONS: {
            ENABLE_DETRENDING: 'enable-detrending',
            ENABLE_FILTERING: 'enable-filtering',
            ENABLE_NORMALIZATION: 'enable-normalization',
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
        },
        VISUALIZATION_CONTAINER: 'fmri-visualization-container',
        VISUALIZATION_OPTIONS: {
            COLORBAR_TOGGLE: 'toggle-colorbar',
            COLOR_RANGE_SLIDER: 'color-range-slider',
            COLORMAP_DROPDOWN: 'colormap-dropdown',
            COLORMAP_DROPDOWN_MENU: 'colormap-dropdown-menu',
            COLORMAP_DROPDOWN_TOGGLE: 'colormap-dropdown-toggle',
            CROSSHAIR_TOGGLE: 'toggle-crosshair',
            FREEZE_VIEW_TOGGLE: 'toggle-freeze-view',
            HOVER_TOGGLE: 'toggle-hover',
            DIRECTION_LABELS_TOGGLE: 'toggle-direction-labels',
            MONTAGE_POPOVER: 'montage-popover',
            MONTAGE_SLICE_SELECT: 'montage-slice-select',
            MONTAGE_SLICE_1_SLIDER: 'slice-1-slider',
            MONTAGE_SLICE_2_SLIDER: 'slice-2-slider',
            MONTAGE_SLICE_3_SLIDER: 'slice-3-slider',
            OPACITY_SLIDER: 'opacity-slider',
            PLAY_MOVIE_BUTTON: 'play-movie',
            PLAY_MOVIE_POPOVER: 'play-movie-popover',
            PLAY_MOVIE_SPEED: 'play-movie-speed',
            RESET_SLIDER_BUTTON: 'reset-slider-button',
            REVERSE_COLORBAR_TOGGLE: 'reverse-colorbar',
            THRESHOLD_SLIDER: 'threshold-slider',
            TR_CONVERT_FORM: 'tr-convert-form',
            TR_CONVERT_BUTTON: 'toggle-tr-convert',
            TOGGLE_VIEW_BUTTON: 'toggle-view',
            SCREENSHOT_BUTTON: 'select-screenshot',
        }
    },
    MODALS: {
        AVERAGE: 'average-modal',
        CORRELATION: 'correlation-modal',
        DISTANCE: 'distance-modal',
        ERROR: 'error-modal'
    },
    PARENT_CONTAINER: 'parent-container',
    SAVE_SCENE: {
        MODAL: 'save-scene-modal',
        SUBMIT_BUTTON: 'save-scene-button',
        FILE_NAME: 'scene-name',
        ERROR_MESSAGE: 'error-message-save-scene',
        SPINNER_OVERLAY: 'save-scene-spinner-overlay',
        SPINNER_WHEEL: 'save-scene-spinner-wheel'
    },
    TIME_SLIDER: {
        TIME_SLIDER: 'time-slider',
        TIME_SLIDER_TITLE: 'time-slider-title',
        TIME_POINT_DISPLAY: 'time-point-display'
    },
    TIMECOURSE: {
        ANNOTATE: {
            ENABLE_ANNOTATE: 'enable-annotate',
            LEFT_MOVE_ANNOTATE: 'left-move-annotate',
            RIGHT_MOVE_ANNOTATE: 'right-move-annotate',
            HIGHLIGHT_ANNOTATE: 'highlight-annotate',
            UNDO_ANNOTATE: 'undo-annotate',
            REMOVE_ANNOTATE: 'remove-annotate',
            POPOVER: 'annotate-plot-popover',
            COLOR_DROPDOWN: 'annotate-color-select',
            MARKER_SELECT: 'annotate-marker-select',
            MARKER_WIDTH_SLIDER: 'annotate-marker-width',
            MARKER_OPACITY_SLIDER: 'annotate-marker-opacity'
        },
        FMRI: {
            ENABLE_FMRI_TIMECOURSE: 'enable-fmri-time-course',
            FREEZE_FMRI_TIMECOURSE: 'freeze-fmri-time-course',
            FREEZE_ICON: 'freeze-icon',
            REMOVE_FMRI_TIMECOURSE: 'remove-fmri-time-course',
            UNDO_FMRI_TIMECOURSE: 'undo-fmri-time-course'
        },
        LINE_PLOT_OPTIONS: {
            COLOR_SELECT: 'ts-color-select',
            CONVOLUTION_CHECKBOX: 'ts-convolution-checkbox',
            CONSTANT_SHIFT_INCREASE: 'ts-increase-constant',
            CONSTANT_SHIFT_DECREASE: 'ts-decrease-constant',
            CONSTANT_SHIFT_RESET: 'ts-reset-constant',
            MARKER_SELECT: 'ts-marker-select',
            OPACITY_SLIDER: 'ts-opacity-slider',
            SCALE_SHIFT_INCREASE: 'ts-increase-scale',
            SCALE_SHIFT_DECREASE: 'ts-decrease-scale',
            SCALE_SHIFT_RESET: 'ts-reset-scale',
            SELECT_TIMECOURSE: 'ts-select',
            WIDTH_SLIDER: 'ts-width-slider',
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
            PEAK_PREP_ALERT: 'peak-finder-prep-alert',
            SELECT_TIMECOURSE: 'ts-select-peak-finder',
            SUBMIT_PEAK_FINDER: 'submit-peak-finder'
        },
        PREPROCESSING_OPTIONS: {
            ENABLE_DETRENDING: 'ts-enable-detrending',
            ENABLE_FILTERING: 'ts-enable-filtering',
            ENABLE_NORMALIZATION: 'ts-enable-normalization',
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
        VISUALIZATION_OPTIONS: {
            TOGGLE_CONVOLUTION: 'toggle-convolution',
            TOGGLE_GRID: 'toggle-grid',
            TOGGLE_TIME_MARKER: 'toggle-time-marker',
            TOGGLE_TS_HOVER: 'toggle-ts-hover'
        }
    },
    SPINNERS: {
        OVERLAY: 'spinner-overlay',
        WHEEL: 'spinner-wheel',
    }
    
};