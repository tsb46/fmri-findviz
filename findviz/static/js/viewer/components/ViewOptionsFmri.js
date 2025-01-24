// ViewOptionsFmri component
import { captureScreenshot, playMovie } from './capture.js';
import { EVENT_TYPES } from '../constants/EventTypes.js';
import eventBus from '../events/ViewerEvents.js';
import { getPlotOptions, updatePlotOptions } from '../api/plot.js';

class ViewOptionsFmri {
    /**
     * Constructor for ViewOptionsFmri
     * @param {string} fmriFileType - The type of FMRI file
     * @param {string[]} plotlyDivIds - The IDs of the plotly divs for screenshot
     * @param {string} captureDivId - The ID of the capture div for screenshot
     * @param {number} timeSliderId - The ID of the time slider for play movie
     * @param {string} [viewToggleId = null] - The ID of the view toggle
     * @param {string} [crosshairToggleId = null] - The ID of the crosshair toggle
     * @param {string} [hoverToggleId = null] - The ID of the hover toggle
     * @param {string} [directionMarkerToggleId = null] - The ID of the direction marker toggle
     * @param {string} [screenshotButtonId = null] - The ID of the screenshot button
     * @param {string} [playMovieButtonId = null] - The ID of the play movie button
     * @param {number} [playMovieButtonRate = 500] - The rate of the play movie button
     */
    constructor(
        fmriFileType,
        plotlyDivIds,
        captureDivId,
        timeSliderId,
        viewToggleId = null,
        crosshairToggleId = null,
        hoverToggleId = null,
        directionMarkerToggleId = null,
        screenshotButtonId = null,
        playMovieButtonId = null,
        playMovieButtonRate = 500
    ) {
        this.fmriFileType = fmriFileType;
        this.plotlyDivIds = plotlyDivIds;
        this.captureDivId = captureDivId;
        this.viewToggleId = viewToggleId;
        this.crosshairToggleId = crosshairToggleId;
        this.hoverToggleId = hoverToggleId;
        this.directionMarkerToggleId = directionMarkerToggleId;
        this.screenshotButtonId = screenshotButtonId;
        this.playMovieButtonId = playMovieButtonId;
        this.playMovieButtonRate = playMovieButtonRate;

        // get time slider div
        this.timeSlider = $(`#${this.timeSliderId}`);

        // get plot options and initialize state variables
        this.toggleState = {};
        getPlotOptions(this.fmriFileType, (plotOptions) => {
            this.toggleState['viewToggle'] = plotOptions.viewToggle;
            this.toggleState['crosshairToggle'] = plotOptions.crosshairToggle;
            this.toggleState['hoverToggle'] = plotOptions.hoverToggle;
            this.toggleState['directionMarkerToggle'] = plotOptions.directionMarkerToggle;
        });
    }

    viewListeners() {
        // Nifti specific listeners
        if (this.fmriFileType == 'nifti') {
            // Ortho to Montage view listener (only for nifti)
            if (this.viewToggleId) {
                this.viewToggle = $(`#${this.viewToggleId}`);
                this.viewToggle.on('click', () => {
                    this.toggleState['viewToggle'] = !this.toggleState['viewToggle'];
                    eventBus.publish(EVENT_TYPES.VISUALIZATION.VIEW_TOGGLE);
                });
            }

            // Montage direction marker listener
            if (this.directionMarkerToggleId) {
                this.directionMarkerToggle = $(`#${this.directionMarkerToggleId}`);
                this.directionMarkerToggle.on('click', () => {
                    this.toggleState['directionMarkerToggle'] = !this.toggleState['directionMarkerToggle'];
                    eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.TOGGLE_DIRECTION_MARKER,
                        { plotOptions: this.toggleState['directionMarkerToggle'] }
                    );
                });
            }
        }

        // Crosshair listener
        if (this.crosshairToggleId) {
            this.crosshairToggle = $(`#${this.crosshairToggleId}`);
            this.crosshairToggle.on('click', () => {
                this.toggleState['crosshairToggle'] = !this.toggleState['crosshairToggle'];
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.TOGGLE_CROSSHAIR,
                    { plotOptions: this.toggleState['crosshairToggle'] }
                );
            });
        }

        // Hover label listener
        if (this.hoverToggleId) {
            this.hoverToggle = $(`#${this.hoverToggleId}`);
            this.hoverToggle.on('click', () => {
                this.toggleState['hoverToggle'] = !this.toggleState['hoverToggle'];
                eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.HOVER_TEXT_TOGGLE,
                    { plotOptions: this.toggleState['hoverToggle'] }
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
            this.playMovieButton.on('click', () => {
                playMovie(this.timeSlider, this.playMovieButton, this.playMovieButtonRate);
            });
        }
    }
}

export default ViewOptionsFmri;