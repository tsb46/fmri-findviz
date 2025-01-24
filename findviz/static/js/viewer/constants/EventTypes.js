export const EVENT_TYPES = {
    ANALYSIS: {
        AVERAGE: 'averageSubmit',
        CORRELATION: 'correlationSubmit',
        DISTANCE: 'distanceSubmit',
    },
    VISUALIZATION: {
        COLOR_MAP_CHANGE: 'colormapChange',
        COLOR_SLIDER_CHANGE: 'colorSliderChange',
        OPACITY_SLIDER_CHANGE: 'opacitySliderChange',
        THRESHOLD_SLIDER_CHANGE: 'thresholdSliderChange',
        HOVER_TEXT_TOGGLE: 'toggleHoverChange',
        VIEW_TOGGLE: 'toggleViewChange',
        MONTAGE_POPOVER_SHOW: 'montagePopoverShow',
        MONTAGE_SLICE_DIRECTION_CHANGE: 'montageSliceDirectionChange',
        SLICE_SLIDER: {
            slice1Slider: 'slice1SliderChange',
            slice2Slider: 'slice2SliderChange',
            slice3Slider: 'slice3SliderChange',
        },
        TOGGLE_CROSSHAIR: 'toggleCrosshairChange',
        TOGGLE_DIRECTION_MARKER: 'toggleDirectionMarkerChange',
        TIME_SLIDER_CHANGE: 'timeSliderChange',
    },
    PREPROCESSING: {
        PREPROCESS_FMRI_RESET: 'preprocessFmriReset',
        PREPROCESS_FMRI_SUCCESS: 'preprocessFmriSuccess',
        PREPROCESS_TIMECOURSE_RESET: 'preprocessTimecourseReset',
        PREPROCESS_TIMECOURSE_SUCCESS: 'preprocessTimecourseSuccess',
    }
};
