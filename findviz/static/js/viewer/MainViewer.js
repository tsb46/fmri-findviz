// viewer.js
// Main viewer class for fmri and time course data visualization

// Constants
import { DOM_IDS } from '../constants/DomIds.js';
import { API_ENDPOINTS } from '../constants/APIEndpoints.js';
// Event Bus
import ViewerEvents from './events/ViewerEvents.js';
// Event Types
import { EVENT_TYPES } from '../constants/EventTypes.js';
// Context Manager
import ViewerContextManager from './api/ContextManager.js';
// Components
// io components
import SaveScene from './SaveScene.js';
// general components
import ColorMap from './components/ColorMap.js';
// distance plot components
import DistanceModal from './components/distance/DistanceModal.js';
import DistancePopover from './components/distance/DistancePopover.js';
// FMRI plot components
import ColorSliders from './components/fmri/ColorSliders.js';
import Montage from './components/fmri/Montage.js';
import Movie from './components/fmri/movie/Movie.js';
import MoviePopover from './components/fmri/movie/moviePopover.js';
import PreprocessFmri from './components/fmri/PreprocessFmri.js';
import TimeConvert from './components/fmri/TimeConvert.js';
import TimeSlider from './components/fmri/TimeSlider.js';
import ViewOptionsFmri from './components/fmri/ViewOptionsFmri.js';
// fmri coordinate components
import VertexCoordinate from './components/fmri/coordinate/VertexCoordinate.js';
import VoxelCoordinate from './components/fmri/coordinate/VoxelCoordinate.js';
import WorldCoordinate from './components/fmri/coordinate/WorldCoordinate.js';
// timecourse plot components
import Annotate from './components/timecourse/annotate/Annotate.js';
import AnnotatePopover from './components/timecourse/annotate/AnnotatePopover.js';
import Average from './components/timecourse/Average.js';
import Correlate from './components/timecourse/Correlate.js';
import LinePlotOptions from './components/timecourse/LinePlotOptions.js';
import PeakFinder from './components/timecourse/PeakFinder.js';
import PreprocessTimecourse from './components/timecourse/PreprocessTimeCourse.js';
import TimeCourseFmri from './components/timecourse/TimeCourseFmri.js';
import ViewOptionsTimeCourse from './components/timecourse/viewOptionsTimeCourse.js';
// plot components
import ColorBar from './plots/ColorBar.js';
import Distance from './plots/Distance.js';
import GiftiViewer from './plots/GiftiViewer.js';
import NiftiViewer from './plots/NiftiViewer.js';
import TimeCourse from './plots/TimeCourse.js';
// click handler
import { NiftiClickHandler, GiftiClickHandler } from './plots/clickHandlers.js';

/**
 * MainViewer class handles the primary visualization logic for neuroimaging data
 * @class
 */
class MainViewer{
    /**
     * Creates a new MainViewer instance
     * @param {('nifti'|'gifti')} plotType - The type of plot to display
     */
    constructor(
        plotType
     ) {
        this.plotType = plotType;
        // Initialize event bus
        this.eventBus = new ViewerEvents();
        // Get singleton instance of context manager (main viewer uses default 'main' context)
        this.contextManager = ViewerContextManager.getInstance();
    }

    /**
     * Initializes all viewer components and initial plot and sets up event listeners
     * @public
     * @returns {Promise<void>}
     */
    async init() {
        // Initialize viewer
        await this.initializeViewer();
        // Initialize viewer components
        this.initializeComponents();
        // change DOM elements of upload after successful upload
        this.afterUpload();
        // plot fmri data
        this.viewer.initPlot();
        // plot time course data
        this.timecourse.initPlot();
    }

    /**
     * Initializes all viewer components (TimeSlider, VisualizationOptions, etc.)
     * @private
     */
    initializeComponents() {
        // initialize fmri components
        this.initializeFmriComponents();

        // initialize time course components
        this.initializeTimecourseComponents();

        // initialize save scene component
        this.saveScene = new SaveScene(
            DOM_IDS.SAVE_SCENE.MODAL,
            DOM_IDS.SAVE_SCENE.SUBMIT_BUTTON,
            DOM_IDS.SAVE_SCENE.FILE_NAME,
            DOM_IDS.SAVE_SCENE.ERROR_MESSAGE,
            this.eventBus,
        );
    }

    /**
     * Initializes fmri components
     * @private
     */
    initializeFmriComponents() {
        // Initialize time slider component
        this.timeSlider = new TimeSlider(
            'Time Point: ',
            DOM_IDS.TIME_SLIDER.TIME_SLIDER,
            'Time Point: ',
            DOM_IDS.TIME_SLIDER.TIME_SLIDER_TITLE,
            DOM_IDS.TIME_SLIDER.TIME_POINT_DISPLAY,
            this.eventBus,
            this.contextManager
        );

        // initialize time conversion component
        this.timeConvert = new TimeConvert(
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TR_CONVERT_FORM,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TR_CONVERT_BUTTON,
            this.eventBus,
            this.contextManager
        );

        // initialize color map component for fmri
        this.colorMap = new ColorMap(
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_MENU,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_TOGGLE,
            this.contextManager.plot.getFmriPlotOptions,
            this.contextManager.plot.updateFmriPlotOptions,
            EVENT_TYPES.VISUALIZATION.FMRI.COLOR_MAP_CHANGE,
            this.eventBus,
            this.contextManager
        );

        // initialize color sliders component
        this.colorSliders = new ColorSliders(
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLOR_RANGE_SLIDER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.THRESHOLD_SLIDER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.OPACITY_SLIDER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.RESET_SLIDER_BUTTON,
            this.eventBus,
            this.contextManager
        );

        // initialize montage component
        this.montage = new Montage(
            this.plotType,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_POPOVER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_SLICE_SELECT,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_SLICE_1_SLIDER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_SLICE_2_SLIDER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_SLICE_3_SLIDER,
            this.eventBus,
            this.contextManager
        );

        // initialize preprocessing fmri component
        this.preprocessFmri = new PreprocessFmri(
            this.plotType,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_NORMALIZATION,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_FILTERING,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_SMOOTHING,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SUBMIT_PREPROCESS_BUTTON,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.RESET_PREPROCESS_BUTTON,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SELECT_MEAN_CENTER,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SELECT_Z_SCORE,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_DETRENDING,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.FILTER_TR,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.FILTER_LOW_CUT,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.FILTER_HIGH_CUT,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SMOOTHING_FWHM,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ERROR_MESSAGE_PREPROCESS,
            DOM_IDS.FMRI.PREPROCESSING_OPTIONS.PREPROCESS_ALERT,
            this.eventBus,
            this.contextManager
        );

        // initialize fmri viewer options component
        let plotlyDivIds;
        let captureDivId;
        if (this.plotType === 'nifti') {
            plotlyDivIds = [
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_1_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_2_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_3_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.COLORBAR
            ];
            captureDivId = DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_CONTAINER;
        }
        else if (this.plotType === 'gifti') {
            plotlyDivIds = [
                DOM_IDS.FMRI.GIFTI_CONTAINERS.LEFT_SURFACE_CONTAINER,
                DOM_IDS.FMRI.GIFTI_CONTAINERS.RIGHT_SURFACE_CONTAINER,
                DOM_IDS.FMRI.GIFTI_CONTAINERS.COLORBAR
            ];
            captureDivId = DOM_IDS.FMRI.GIFTI_CONTAINERS.SURFACE_CONTAINER;
        }
        this.fmriViewerOptions = new ViewOptionsFmri(
            this.plotType,
            plotlyDivIds,
            captureDivId,
            DOM_IDS.TIME_SLIDER.TIME_SLIDER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_MENU,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_TOGGLE,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TOGGLE_VIEW_BUTTON,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.CROSSHAIR_TOGGLE,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.HOVER_TOGGLE,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.DIRECTION_LABELS_TOGGLE,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORBAR_TOGGLE,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.REVERSE_COLORBAR_TOGGLE,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.FREEZE_VIEW_TOGGLE,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.SCREENSHOT_BUTTON,
            this.eventBus,
            this.contextManager
        );

        // initialize movie component
        this.movie = new Movie(
            DOM_IDS.TIME_SLIDER.TIME_SLIDER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.PLAY_MOVIE_BUTTON,
            this.eventBus,
            this.contextManager
        );

        // initialize movie popover component
        this.moviePopover = new MoviePopover(
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.PLAY_MOVIE_POPOVER,
            DOM_IDS.FMRI.VISUALIZATION_OPTIONS.PLAY_MOVIE_SPEED,
            this.eventBus,
            this.contextManager
        );

        // initialize distance modal component
        this.distanceModal = new DistanceModal(
            DOM_IDS.MODALS.DISTANCE,
            DOM_IDS.DISTANCE.MODAL_BUTTON,
            DOM_IDS.DISTANCE.DISTANCE_FORM,
            DOM_IDS.DISTANCE.METRIC_SELECT,
            DOM_IDS.DISTANCE.TIME_POINT_MESSAGE,
            DOM_IDS.DISTANCE.REMOVE_DISTANCE_BUTTON,
            DOM_IDS.DISTANCE.ERROR_MESSAGE,
            DOM_IDS.DISTANCE.PREPROCESS_ALERT,
            this.eventBus,
            this.contextManager
        );

        // initialize distance popover component
        this.distancePopover = new DistancePopover(
            DOM_IDS.DISTANCE.POPOVER,
            DOM_IDS.DISTANCE.COLORMAP_DROPDOWN,
            DOM_IDS.DISTANCE.COLORMAP_DROPDOWN_MENU,
            DOM_IDS.DISTANCE.COLORMAP_DROPDOWN_TOGGLE,
            DOM_IDS.DISTANCE.COLOR_RANGE_SLIDER,
            DOM_IDS.DISTANCE.TIME_MARKER_WIDTH_SLIDER,
            DOM_IDS.DISTANCE.TIME_MARKER_OPACITY_SLIDER,
            this.eventBus,
            this.contextManager
        );

        // initialize distance plot component
        this.distancePlot = new Distance(
            DOM_IDS.DISTANCE.PLOT,
            DOM_IDS.DISTANCE.CONTAINER,
            this.eventBus,
            this.contextManager
        );

        
        // coordinate display for nifti plot
        if (this.plotType === 'nifti') {
            // initialize voxel coordinate display
            this.voxelCoordinate = new VoxelCoordinate(
                DOM_IDS.FMRI.COORDINATE.VOXEL_COORD_CONTAINER,
                DOM_IDS.FMRI.COORDINATE.VOXEL_X,
                DOM_IDS.FMRI.COORDINATE.VOXEL_Y,
                DOM_IDS.FMRI.COORDINATE.VOXEL_Z,
                this.eventBus,
                this.contextManager
            );
            // initialize world coordinate display
            this.worldCoordinate = new WorldCoordinate(
                DOM_IDS.FMRI.COORDINATE.WORLD_COORD_CONTAINER,
                DOM_IDS.FMRI.COORDINATE.WORLD_X,
                DOM_IDS.FMRI.COORDINATE.WORLD_Y,
                DOM_IDS.FMRI.COORDINATE.WORLD_Z,
                this.eventBus,
                this.contextManager
            );
        } else {
            // initialize vertex coordinate display
            this.vertexCoordinate = new VertexCoordinate(
                DOM_IDS.FMRI.COORDINATE.VERTEX_COORD_CONTAINER,
                DOM_IDS.FMRI.COORDINATE.VERTEX_NUMBER,
                DOM_IDS.FMRI.COORDINATE.SELECTED_HEMISPHERE,
                this.eventBus,
                this.contextManager
            )
        }
    }


    /**
     * Initializes time course components
     * @private
     */
    initializeTimecourseComponents() {
        // initialize annotate component
        this.annotate = new Annotate(
            DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT,
            DOM_IDS.TIME_SLIDER.TIME_SLIDER,
            DOM_IDS.TIMECOURSE.ANNOTATE.ENABLE_ANNOTATE,
            DOM_IDS.TIMECOURSE.ANNOTATE.RIGHT_MOVE_ANNOTATE,
            DOM_IDS.TIMECOURSE.ANNOTATE.LEFT_MOVE_ANNOTATE,
            DOM_IDS.TIMECOURSE.ANNOTATE.UNDO_ANNOTATE,
            DOM_IDS.TIMECOURSE.ANNOTATE.REMOVE_ANNOTATE,
            this.eventBus,
            this.contextManager
        );

        // initialize annotate popover component
        this.annotatePopover = new AnnotatePopover(
            DOM_IDS.TIMECOURSE.ANNOTATE.POPOVER,
            DOM_IDS.TIMECOURSE.ANNOTATE.COLOR_DROPDOWN,
            DOM_IDS.TIMECOURSE.ANNOTATE.MARKER_SELECT,
            DOM_IDS.TIMECOURSE.ANNOTATE.MARKER_WIDTH_SLIDER,
            DOM_IDS.TIMECOURSE.ANNOTATE.MARKER_OPACITY_SLIDER,
            DOM_IDS.TIMECOURSE.ANNOTATE.HIGHLIGHT_ANNOTATE,
            this.eventBus,
            this.contextManager
        );

        // initialize window average component
        this.average = new Average(
            DOM_IDS.MODALS.AVERAGE,
            DOM_IDS.AVERAGE.MODAL_BUTTON,
            DOM_IDS.AVERAGE.LEFT_EDGE,
            DOM_IDS.AVERAGE.RIGHT_EDGE,
            DOM_IDS.AVERAGE.SUBMIT_AVERAGE,
            DOM_IDS.AVERAGE.AVERAGE_FORM,
            DOM_IDS.AVERAGE.ANNOTATION_WARNING,
            DOM_IDS.AVERAGE.ERROR_MESSAGE,
            this.eventBus,
            this.contextManager
        );

        // initialize correlation component
        this.correlate = new Correlate(
            DOM_IDS.MODALS.CORRELATION,
            DOM_IDS.CORRELATE.MODAL_BUTTON,
            DOM_IDS.CORRELATE.NEGATIVE_LAG,
            DOM_IDS.CORRELATE.POSITIVE_LAG,
            DOM_IDS.CORRELATE.TIMECOURSE_SELECT,
            DOM_IDS.CORRELATE.SUBMIT_CORRELATE,
            DOM_IDS.CORRELATE.CORRELATE_FORM,
            DOM_IDS.CORRELATE.PREPROCESS_ALERT,
            DOM_IDS.CORRELATE.ERROR_MESSAGE,
            this.eventBus,
            this.contextManager
        );

        // initialize line plot components
        this.linePlotOptions = new LinePlotOptions(
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SELECT_TIMECOURSE,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.OPACITY_SLIDER,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.WIDTH_SLIDER,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SCALE_SHIFT_INCREASE,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SCALE_SHIFT_DECREASE,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SCALE_SHIFT_RESET,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONSTANT_SHIFT_INCREASE,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONSTANT_SHIFT_DECREASE,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONSTANT_SHIFT_RESET,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.COLOR_SELECT,
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.MARKER_SELECT,
            DOM_IDS.TIMECOURSE.MARKER_PLOT_OPTIONS.WIDTH_SLIDER,
            DOM_IDS.TIMECOURSE.MARKER_PLOT_OPTIONS.OPACITY_SLIDER,
            DOM_IDS.TIMECOURSE.MARKER_PLOT_OPTIONS.MARKER_SELECT,
            DOM_IDS.TIMECOURSE.MARKER_PLOT_OPTIONS.COLOR_SELECT, 
            DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONVOLUTION_CHECKBOX,
            this.eventBus,
            this.contextManager
        );

        // initialize peak finder component
        this.peakFinder = new PeakFinder(
            DOM_IDS.TIMECOURSE.PEAK_FINDER.POPOVER,
            DOM_IDS.TIMECOURSE.PEAK_FINDER.SELECT_TIMECOURSE,
            DOM_IDS.TIMECOURSE.PEAK_FINDER.SUBMIT_PEAK_FINDER,
            DOM_IDS.TIMECOURSE.PEAK_FINDER.PEAK_FORM,
            DOM_IDS.TIMECOURSE.PEAK_FINDER.PEAK_PREP_ALERT,
            this.eventBus,
            this.contextManager
        );

        // initialize preprocessing timecourse component
        this.preprocessTimecourse = new PreprocessTimecourse(
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.SELECT_TIMECOURSE,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.ENABLE_NORMALIZATION,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.ENABLE_FILTERING,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.SUBMIT_PREPROCESS_BUTTON,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.RESET_PREPROCESS_BUTTON,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.SELECT_MEAN_CENTER,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.SELECT_Z_SCORE,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.ENABLE_DETRENDING,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.FILTER_TR,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.FILTER_LOW_CUT,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.FILTER_HIGH_CUT,
            DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.ERROR_MESSAGE_PREPROCESS,
            DOM_IDS.TIMECOURSE.PREPROCESS_ALERT,
            this.eventBus,
            this.contextManager
        );

        // initialize timecourse viewer options component
        this.timecourseViewerOptions = new ViewOptionsTimeCourse(
            DOM_IDS.TIMECOURSE.VISUALIZATION_OPTIONS.TOGGLE_GRID,
            DOM_IDS.TIMECOURSE.VISUALIZATION_OPTIONS.TOGGLE_TS_HOVER,
            DOM_IDS.TIMECOURSE.VISUALIZATION_OPTIONS.TOGGLE_TIME_MARKER,
            DOM_IDS.TIMECOURSE.VISUALIZATION_OPTIONS.TOGGLE_CONVOLUTION,
            this.eventBus,
            this.contextManager
        );

        // initialize timecourse fmri component
        this.timecourseFmri = new TimeCourseFmri(
            DOM_IDS.TIMECOURSE.FMRI.ENABLE_FMRI_TIMECOURSE,
            DOM_IDS.TIMECOURSE.FMRI.REMOVE_FMRI_TIMECOURSE,
            DOM_IDS.TIMECOURSE.FMRI.UNDO_FMRI_TIMECOURSE,
            DOM_IDS.TIMECOURSE.FMRI.FREEZE_FMRI_TIMECOURSE,
            DOM_IDS.TIMECOURSE.FMRI.FREEZE_ICON,
            this.eventBus,
            this.contextManager
        );
    }

    /**
     * Initializes the appropriate viewer based on file type
     * @private
     */
    async initializeViewer() {
        let colorBarContainerId;
        if (this.plotType === 'nifti') {
            this.viewer = new NiftiViewer(
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_1_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_2_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_3_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.COLORBAR,
                this.eventBus,
                this.contextManager
            );
            // initialize click handler
            this.clickHandler = new NiftiClickHandler(
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_1_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_2_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_3_CONTAINER,
                this.eventBus,
                this.contextManager
            );
            colorBarContainerId = DOM_IDS.FMRI.NIFTI_CONTAINERS.COLORBAR;
        } else if (this.plotType === 'gifti') {
            this.viewer = new GiftiViewer(
                DOM_IDS.FMRI.GIFTI_CONTAINERS.SURFACE_CONTAINER,
                DOM_IDS.FMRI.GIFTI_CONTAINERS.LEFT_SURFACE_CONTAINER,
                DOM_IDS.FMRI.GIFTI_CONTAINERS.RIGHT_SURFACE_CONTAINER,
                DOM_IDS.FMRI.GIFTI_CONTAINERS.COLORBAR,
                this.eventBus,
                this.contextManager
            );
            // initialize click handler
            this.clickHandler = new GiftiClickHandler(
                DOM_IDS.FMRI.GIFTI_CONTAINERS.LEFT_SURFACE_CONTAINER,
                DOM_IDS.FMRI.GIFTI_CONTAINERS.RIGHT_SURFACE_CONTAINER,
                this.eventBus,
                this.contextManager
            );
            colorBarContainerId = DOM_IDS.FMRI.GIFTI_CONTAINERS.COLORBAR;
        }

        // initialize colorbar 
        this.colorBar = new ColorBar(
            colorBarContainerId,
            'Intensity',
            this.eventBus,
            this.contextManager
        );

        // check for time course or task design input
        const viewerMetadata = await this.contextManager.data.getViewerMetadata();
        if (viewerMetadata.ts_enabled) {
            this.timeCourseInput = true;
        }
        if (viewerMetadata.task_enabled) {
            this.taskDesignInput = true;
        }
        // initialize time course viewer
        this.timecourse = new TimeCourse(
            DOM_IDS.TIMECOURSE.TIME_COURSE_CONTAINER,
            DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT,
            this.timeCourseInput,
            this.taskDesignInput,
            this.eventBus,
            this.contextManager
        );
    }

   /**
     * Handles post-upload initialization tasks
     * @private
     * @returns {void}
     */
    afterUpload(){
        const uploadButton = document.getElementById(DOM_IDS.FILE_UPLOAD.MODAL_BUTTON)
        // Change button color
        uploadButton.classList.add('btn-secondary');
        uploadButton.classList.remove('btn-primary');
        // Change button text to reupload file
        uploadButton.innerHTML = 'Reupload Files'
        // Set listener to refresh page when user clicks reupload files
        uploadButton.addEventListener("click", async() => {
            // clear cache
            await fetch(API_ENDPOINTS.CLEAR_CACHE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            location.reload()
        });
    }

}

export default MainViewer;
