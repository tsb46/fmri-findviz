// ViewOptionsFmri component
import { captureScreenshot, playMovie } from './capture.js';
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import eventBus from '../../events/ViewerEvents.js';
import { 
    getFmriPlotOptions, 
    updateFmriPlotOptions, 
    getNiftiViewState,
    updateNiftiViewState,
 } from '../../api/plot.js';
import ColorMap from '../ColorMap.js';

class ViewOptionsFmri {
    /**
     * Constructor for ViewOptionsFmri
     * @param {string} fmriFileType - The type of FMRI file
     * @param {string[]} plotlyDivIds - The IDs of the plotly divs for screenshot
     * @param {string} captureDivId - The ID of the capture div for screenshot
     * @param {number} timeSliderId - The ID of the time slider for play movie
     * @param {string} colormapContainerId - The ID of the colormap container
     * @param {string} colormapDropdownMenuId - The ID of the colormap dropdown menu
     * @param {string} colormapDropdownToggleId - The ID of the colormap dropdown toggle
     * @param {string} [viewToggleId = null] - The ID of the view toggle
     * @param {string} [crosshairToggleId = null] - The ID of the crosshair toggle
     * @param {string} [hoverToggleId = null] - The ID of the hover toggle
     * @param {string} [directionMarkerToggleId = null] - The ID of the direction marker toggle
     * @param {string} [screenshotButtonId = null] - The ID of the screenshot button
     * @param {string} [playMovieButtonId = null] - The ID of the play movie button
     * @param {number} [playMovieRate = 500] - The rate of the play movie button
     */
    constructor(
        fmriFileType,
        plotlyDivIds,
        captureDivId,
        timeSliderId,
        colormapContainerId,
        colormapDropdownMenuId,
        colormapDropdownToggleId,
        viewToggleId = null,
        crosshairToggleId = null,
        hoverToggleId = null,
        directionMarkerToggleId = null,
        screenshotButtonId = null,
        playMovieButtonId = null,
        playMovieRate = 500
    ) {
        this.fmriFileType = fmriFileType;
        this.plotlyDivIds = plotlyDivIds;
        this.captureDivId = captureDivId;
        this.viewToggleId = viewToggleId;
        this.colormapContainerId = colormapContainerId;
        this.colormapDropdownMenuId = colormapDropdownMenuId;
        this.colormapDropdownToggleId = colormapDropdownToggleId;
        this.crosshairToggleId = crosshairToggleId;
        this.hoverToggleId = hoverToggleId;
        this.directionMarkerToggleId = directionMarkerToggleId;
        this.screenshotButtonId = screenshotButtonId;
        this.playMovieButtonId = playMovieButtonId;
        this.playMovieRate = playMovieRate;

        // get time slider div
        this.timeSlider = $(`#${timeSliderId}`);

        // get plot options and initialize state variables
        this.toggleState = {};
        getFmriPlotOptions((plotOptions) => {
            this.toggleState['crosshairToggle'] = plotOptions.crosshair_on;
            this.toggleState['hoverToggle'] = plotOptions.hover_text_on;
            this.toggleState['directionMarkerToggle'] = plotOptions.direction_marker_on;
        });

        // get nifti view state
        getNiftiViewState((viewState) => {
            this.toggleState['viewToggle'] = viewState.view_state;
        });

        // initialize color map
        this.colorMap = new ColorMap(
            this.colormapContainerId,
            this.colormapDropdownMenuId,
            this.colormapDropdownToggleId,
            getFmriPlotOptions,
            updateFmriPlotOptions,
            EVENT_TYPES.VISUALIZATION.FMRI.COLOR_MAP_CHANGE
        );

        // initialize view listeners
        this.initializeViewListeners();
    }

    initializeViewListeners() {
        // Nifti specific listeners
        if (this.fmriFileType == 'nifti') {
            // Ortho to Montage view listener (only for nifti)
            if (this.viewToggleId) {
                this.viewToggle = $(`#${this.viewToggleId}`);
                this.viewToggle.on('click', () => {
                    this.toggleState['viewToggle'] = this.toggleState['viewToggle'] == 'ortho' ? 'montage' : 'ortho';
                    updateNiftiViewState(
                        this.toggleState['viewToggle'],
                        () => {
                            eventBus.publish(
                                EVENT_TYPES.VISUALIZATION.FMRI.VIEW_TOGGLE,
                                { view_state: this.toggleState['viewToggle'] }
                            );
                        }
                    );
                });
            }

            // Montage direction marker listener
            if (this.directionMarkerToggleId) {
                this.directionMarkerToggle = $(`#${this.directionMarkerToggleId}`);
                this.directionMarkerToggle.on('click', () => {
                    this.toggleState['directionMarkerToggle'] = !this.toggleState['directionMarkerToggle'];
                    updateFmriPlotOptions(
                        { direction_marker_on: this.toggleState['directionMarkerToggle'] },
                        () => {
                            eventBus.publish(
                                EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_DIRECTION_MARKER,
                                { directionMarkerState: this.toggleState['directionMarkerToggle'] }
                            );
                        }
                    );
                });
            }

            // Crosshair listener
            if (this.crosshairToggleId) {
                this.crosshairToggle = $(`#${this.crosshairToggleId}`);
                this.crosshairToggle.on('click', () => {
                    this.toggleState['crosshairToggle'] = !this.toggleState['crosshairToggle'];
                    updateFmriPlotOptions(
                        { crosshair_on: this.toggleState['crosshairToggle'] },
                        () => {
                            eventBus.publish(
                                EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_CROSSHAIR,
                                { crosshairState: this.toggleState['crosshairToggle'] }
                            );
                        }
                    );
                });
            }
        }

        // Hover label listener
        if (this.hoverToggleId) {
            this.hoverToggle = $(`#${this.hoverToggleId}`);
            this.hoverToggle.on('click', () => {
                this.toggleState['hoverToggle'] = !this.toggleState['hoverToggle'];
                updateFmriPlotOptions(
                    { hover_text_on: this.toggleState['hoverToggle'] },
                    () => {
                        eventBus.publish(
                            EVENT_TYPES.VISUALIZATION.FMRI.HOVER_TEXT_TOGGLE,
                            { hoverState: this.toggleState['hoverToggle'] }
                        );
                    }
                );
            });
        }

        // Screenshot listener
        if (this.screenshotButtonId) {
            this.screenshotButton = $(`#${this.screenshotButtonId}`);
            this.screenshotButton.on('click', () => {
                captureScreenshot(this.plotlyDivIds, this.captureDivId);
            });
        }

        // Play movie listener
        if (this.playMovieButtonId) {
            this.playMovieButton = $(`#${this.playMovieButtonId}`);
            // attach play movie button click listener
            playMovie(this.timeSlider, this.playMovieButton, this.playMovieRate);
        }
    }
}

export default ViewOptionsFmri;