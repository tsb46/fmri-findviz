// AnalysisViewer.js
// AnalysisViewer class for displaying fmri and time course data from analysis results

// Constants
import { DOM_IDS } from '../constants/DomIds.js';
// Event Bus
import ViewerEvents from './events/ViewerEvents.js';
// Event Types
import { EVENT_TYPES } from '../constants/EventTypes.js';
// Context Manager
import ViewerContextManager from './api/ContextManager.js';
// Components
// general components
import ColorMap from './components/ColorMap.js';
// FMRI plot components
import ColorSliders from './components/fmri/ColorSliders.js';
import Montage from './components/fmri/Montage.js';
import Movie from './components/fmri/movie/Movie.js';
import MoviePopover from './components/fmri/movie/moviePopover.js';
import TimeSlider from './components/fmri/TimeSlider.js';
import TimeConvert from './components/fmri/TimeConvert.js';
import ViewOptionsFmri from './components/fmri/ViewOptionsFmri.js';
// fmri coordinate components
import VertexCoordinate from './components/fmri/coordinate/VertexCoordinate.js';
import VoxelCoordinate from './components/fmri/coordinate/VoxelCoordinate.js';
import WorldCoordinate from './components/fmri/coordinate/WorldCoordinate.js';
// timecourse plot components
import Annotate from './components/timecourse/annotate/Annotate.js';
import AnnotatePopover from './components/timecourse/annotate/AnnotatePopover.js';
import LinePlotOptions from './components/timecourse/LinePlotOptions.js';
import PeakFinder from './components/timecourse/PeakFinder.js';
import TimeCourseFmri from './components/timecourse/TimeCourseFmri.js';
import ViewOptionsTimeCourse from './components/timecourse/viewOptionsTimeCourse.js';
// plot components
import ColorBar from './plots/ColorBar.js';
import GiftiViewer from './plots/GiftiViewer.js';
import NiftiViewer from './plots/NiftiViewer.js';
import TimeCourse from './plots/TimeCourse.js';
// click handler
import { NiftiClickHandler, GiftiClickHandler } from './plots/clickHandlers.js';


class AnalysisViewer {
    /**
     * Creates a new AnalysisViewer instance
     * @param {string} plotType - The type of plot to display
     * @param {('average'|'correlate')} analysisContext - The context of the analysis
     */
    constructor(
        plotType,
        analysisContext
    ) {
        this.plotType = plotType;
        // Initialize new event bus for analysis viewer
        this.eventBus = new ViewerEvents();
       // Get singleton instance of context manager
        this.contextManager = ViewerContextManager.getInstance();
        // check if analysis context is valid
        if (analysisContext !== 'average' && analysisContext !== 'correlate') {
            throw new Error('Invalid analysis context');
        }
        // switch context to analysis context
        this.contextManager.setContext(analysisContext);

        // set text labels for components
        this.textLabels = {}
        if (analysisContext === 'average') {
            this.textLabels = {
                timeSlider: 'Time Point: ',
                timeSliderTitle: 'Time Point: ',
                colorbarTitle: 'Average<br>Intensity'
            }
        }
        else if (analysisContext === 'correlate') {
            this.textLabels = {
                timeSlider: 'Lag: ',
                timeSliderTitle: 'Time Lag: ',
                colorbarTitle: 'Correlation<br>Coefficient'
            }
        }
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
    }

    /**
     * Initializes fmri components
     * @private
     */
    initializeFmriComponents() {
        // Initialize time slider component
        this.timeSlider = new TimeSlider(
            this.textLabels.timeSlider,
            DOM_IDS.TIME_SLIDER.TIME_SLIDER,
            this.textLabels.timeSliderTitle,
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

        // initialize fmri viewer options component
        let plotlyDivIds;
        let captureDivId;
        if (this.plotType === 'nifti') {
            plotlyDivIds = [
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_1_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_2_CONTAINER,
                DOM_IDS.FMRI.NIFTI_CONTAINERS.SLICE_3_CONTAINER
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
            this.textLabels.colorbarTitle,
            this.eventBus,
            this.contextManager
        );

        // initialize time course viewer
        this.timecourse = new TimeCourse(
            DOM_IDS.TIMECOURSE.TIME_COURSE_CONTAINER,
            DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT,
            false, // no time course input
            false, // no task design input
            this.eventBus,
            this.contextManager
        );
    }
}

export default AnalysisViewer;
    
    