// contextManager.js

// Data API functions
import {
    convertTimepoints,
    getCrosshairCoords,
    getDirectionLabelCoords,
    getDistanceData,
    getFMRIData,
    getClickCoords,
    getCoordLabels,
    getLastTimecourse,
    getMontageData,
    getTaskConditions,
    getTimeCourseData,
    getTimeCourseLabels,
    getTimeCourseLabelsPreprocessed,
    getTimeCourseSource,
    getTimePoint,
    getTimePoints,
    getVertexCoords,
    getViewerMetadata,
    getWorldCoords,
    getVoxelCoords,
    popFmriTimeCourse,
    removeFmriTimeCourses,
    updateFmriTimeCourse,
    updateLocation,
    updateMontageSliceDir,
    updateMontageSliceIdx,
    updateTimepoint,
    updateTr,
} from './data.js';

// Plot API functions
import {
    checkFmriPreprocessed,
    checkTsPreprocessed,
    getAnnotationMarkers,
    getAnnotationMarkerPlotOptions,
    getColormapData,
    getDistancePlotOptions,
    getFmriPlotOptions,
    getNiftiViewState,
    getSelectedTimePoint,
    getTaskDesignPlotOptions,
    getTimeCoursePlotOptions,
    getTimeCourseGlobalPlotOptions,
    getTimeMarkerPlotOptions,
    getTimeCourseShiftHistory,
    getTSFmriPlotted,
    addAnnotationMarker,
    changeTaskConvolution,
    clearAnnotationMarkers,
    moveAnnotationSelection,
    resetFmriColorOptions,
    resetTimeCourseShift,
    removeDistancePlot,
    undoAnnotationMarker,
    updateAnnotationMarkerPlotOptions,
    updateDistancePlotOptions,
    updateFmriPlotOptions,
    updateNiftiViewState,
    updateTaskDesignPlotOptions,
    updateTimeCoursePlotOptions,
    updateTimeCourseGlobalPlotOptions,
    updateTimeCourseShift,
    updateTimeMarkerPlotOptions,
} from './plot.js';

// Analysis API functions
import {
    correlate,
    distance,
    findPeaks,
    windowedAverage,
} from './analysis.js';

// Preprocess API functions
import {
    getPreprocessedFMRI,
    getPreprocessedTimeCourse,
    resetFMRIPreprocess,
    resetTimeCoursePreprocess,
} from './preprocess.js';

/**
 * ViewerContextManager is a class that manages the context of the viewer.
 * It is implemented as a singleton to ensure consistent context management across the application.
 */
class ViewerContextManager {
    static _instance = null;

    /**
     * Constructor for the ViewerContextManager class.
     * If an instance exists, returns that instance (singleton pattern).
     */
    constructor() {
        if (ViewerContextManager._instance) {
            return ViewerContextManager._instance;
        }
        // set the current context to 'main'
        this.currentContext = 'main';

        // Group API functions by category
        // Data API functions
        this.data = {
            convertTimepoints: (...args) => this.wrapApiCall(convertTimepoints, ...args),
            getCrosshairCoords: (...args) => this.wrapApiCall(getCrosshairCoords, ...args),
            getDirectionLabelCoords: (...args) => this.wrapApiCall(getDirectionLabelCoords, ...args),
            getDistanceData: (...args) => this.wrapApiCall(getDistanceData, ...args),
            getFMRIData: (...args) => this.wrapApiCall(getFMRIData, ...args),
            getClickCoords: (...args) => this.wrapApiCall(getClickCoords, ...args),
            getCoordLabels: (...args) => this.wrapApiCall(getCoordLabels, ...args),
            getLastTimecourse: (...args) => this.wrapApiCall(getLastTimecourse, ...args),
            getMontageData: (...args) => this.wrapApiCall(getMontageData, ...args),
            getTaskConditions: (...args) => this.wrapApiCall(getTaskConditions, ...args),
            getTimeCourseData: (...args) => this.wrapApiCall(getTimeCourseData, ...args),
            getTimeCourseLabels: (...args) => this.wrapApiCall(getTimeCourseLabels, ...args),
            getTimeCourseLabelsPreprocessed: (...args) => this.wrapApiCall(getTimeCourseLabelsPreprocessed, ...args),
            getTimeCourseSource: (...args) => this.wrapApiCall(getTimeCourseSource, ...args),
            getTimePoint: (...args) => this.wrapApiCall(getTimePoint, ...args),
            getTimePoints: (...args) => this.wrapApiCall(getTimePoints, ...args),
            getVertexCoords: (...args) => this.wrapApiCall(getVertexCoords, ...args),
            getViewerMetadata: (...args) => this.wrapApiCall(getViewerMetadata, ...args),
            getVoxelCoords: (...args) => this.wrapApiCall(getVoxelCoords, ...args),
            getWorldCoords: (...args) => this.wrapApiCall(getWorldCoords, ...args),
            popFmriTimeCourse: (...args) => this.wrapApiCall(popFmriTimeCourse, ...args),
            removeFmriTimeCourses: (...args) => this.wrapApiCall(removeFmriTimeCourses, ...args),
            updateFmriTimeCourse: (...args) => this.wrapApiCall(updateFmriTimeCourse, ...args),
            updateLocation: (...args) => this.wrapApiCall(updateLocation, ...args),
            updateMontageSliceDir: (...args) => this.wrapApiCall(updateMontageSliceDir, ...args),
            updateMontageSliceIdx: (...args) => this.wrapApiCall(updateMontageSliceIdx, ...args),
            updateTimepoint: (...args) => this.wrapApiCall(updateTimepoint, ...args),
            updateTr: (...args) => this.wrapApiCall(updateTr, ...args),
        };

        // Plot API functions
        this.plot = {
            checkFmriPreprocessed: (...args) => this.wrapApiCall(checkFmriPreprocessed, ...args),
            checkTsPreprocessed: (...args) => this.wrapApiCall(checkTsPreprocessed, ...args),
            getAnnotationMarkers: (...args) => this.wrapApiCall(getAnnotationMarkers, ...args),
            getAnnotationMarkerPlotOptions: (...args) => this.wrapApiCall(getAnnotationMarkerPlotOptions, ...args),
            getColormapData: (...args) => this.wrapApiCall(getColormapData, ...args),
            getDistancePlotOptions: (...args) => this.wrapApiCall(getDistancePlotOptions, ...args),
            getFmriPlotOptions: (...args) => this.wrapApiCall(getFmriPlotOptions, ...args),
            getNiftiViewState: (...args) => this.wrapApiCall(getNiftiViewState, ...args),
            getSelectedTimePoint: (...args) => this.wrapApiCall(getSelectedTimePoint, ...args),
            getTaskDesignPlotOptions: (...args) => this.wrapApiCall(getTaskDesignPlotOptions, ...args),
            getTimeCoursePlotOptions: (...args) => this.wrapApiCall(getTimeCoursePlotOptions, ...args),
            getTimeCourseGlobalPlotOptions: (...args) => this.wrapApiCall(getTimeCourseGlobalPlotOptions, ...args),
            getTimeMarkerPlotOptions: (...args) => this.wrapApiCall(getTimeMarkerPlotOptions, ...args),
            getTimeCourseShiftHistory: (...args) => this.wrapApiCall(getTimeCourseShiftHistory, ...args),
            getTSFmriPlotted: (...args) => this.wrapApiCall(getTSFmriPlotted, ...args),
            addAnnotationMarker: (...args) => this.wrapApiCall(addAnnotationMarker, ...args),
            changeTaskConvolution: (...args) => this.wrapApiCall(changeTaskConvolution, ...args),
            clearAnnotationMarkers: (...args) => this.wrapApiCall(clearAnnotationMarkers, ...args),
            moveAnnotationSelection: (...args) => this.wrapApiCall(moveAnnotationSelection, ...args),
            resetFmriColorOptions: (...args) => this.wrapApiCall(resetFmriColorOptions, ...args),
            resetTimeCourseShift: (...args) => this.wrapApiCall(resetTimeCourseShift, ...args),
            removeDistancePlot: (...args) => this.wrapApiCall(removeDistancePlot, ...args),
            undoAnnotationMarker: (...args) => this.wrapApiCall(undoAnnotationMarker, ...args),
            updateAnnotationMarkerPlotOptions: (...args) => this.wrapApiCall(updateAnnotationMarkerPlotOptions, ...args),
            updateDistancePlotOptions: (...args) => this.wrapApiCall(updateDistancePlotOptions, ...args),
            updateFmriPlotOptions: (...args) => this.wrapApiCall(updateFmriPlotOptions, ...args),
            updateNiftiViewState: (...args) => this.wrapApiCall(updateNiftiViewState, ...args),
            updateTaskDesignPlotOptions: (...args) => this.wrapApiCall(updateTaskDesignPlotOptions, ...args),
            updateTimeCoursePlotOptions: (...args) => this.wrapApiCall(updateTimeCoursePlotOptions, ...args),
            updateTimeCourseGlobalPlotOptions: (...args) => this.wrapApiCall(updateTimeCourseGlobalPlotOptions, ...args),
            updateTimeCourseShift: (...args) => this.wrapApiCall(updateTimeCourseShift, ...args),
            updateTimeMarkerPlotOptions: (...args) => this.wrapApiCall(updateTimeMarkerPlotOptions, ...args),
        };

        // Analysis API functions
        this.analysis = {
            correlate: (...args) => this.wrapApiCall(correlate, ...args),
            distance: (...args) => this.wrapApiCall(distance, ...args),
            findPeaks: (...args) => this.wrapApiCall(findPeaks, ...args),
            windowedAverage: (...args) => this.wrapApiCall(windowedAverage, ...args)
        };

        // Preprocess API functions
        this.preprocess = {
            getPreprocessedFMRI: (...args) => this.wrapApiCall(getPreprocessedFMRI, ...args),
            getPreprocessedTimeCourse: (...args) => this.wrapApiCall(getPreprocessedTimeCourse, ...args),
            resetFMRIPreprocess: (...args) => this.wrapApiCall(resetFMRIPreprocess, ...args),
            resetTimeCoursePreprocess: (...args) => this.wrapApiCall(resetTimeCoursePreprocess, ...args),
        };

        // set the instance
        ViewerContextManager._instance = this;
    }

    /**
     * Get the singleton instance of ViewerContextManager
     * @returns {ViewerContextManager} The singleton instance
     */
    static getInstance() {
        if (!ViewerContextManager._instance) {
            ViewerContextManager._instance = new ViewerContextManager();
        }
        return ViewerContextManager._instance;
    }

    /**
     * Set the current context.
     * @param {string} contextId - The context to set.
     */
    setContext(contextId) {
        this.currentContext = contextId;
    }

    /**
     * Get the current context.
     * @returns {string} The current context.
     */
    getContext() {
        return this.currentContext;
    }

    /**
     * Wrap an API call with the current context.
     * @param {Function} apiFunction - The API function to wrap.
     * @param {...any} args - The arguments to pass to the API function.
     * @returns {Promise} The result of the API call.
     */
    wrapApiCall(apiFunction, ...args) {
        args.push(this.currentContext);
        return apiFunction(...args);
    }
}

export default ViewerContextManager;