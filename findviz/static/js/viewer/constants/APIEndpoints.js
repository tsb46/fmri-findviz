// API Endpoints - used to interact with the backend
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
    UPDATE_LOCATION: '/update_location',
    UPDATE_PLOT_OPTIONS: '/update_plot_options',
    UPDATE_TIMEPOINT: '/update_timepoint',
    RESET_COLOR_OPTIONS: '/reset_color_options',
    GET_FMRI_DATA: '/get_fmri_data',
    GET_FUNCTIONAL_TIMECOURSE: '/get_functional_timecourse',
    GET_PLOT_OPTIONS: '/get_plot_options',
};