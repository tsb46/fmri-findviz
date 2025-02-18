// ViewOptionsFmri component
import { captureScreenshot } from './capture.js';
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
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
     * @param {string} [colorbarToggleId = null] - The ID of the colorbar toggle
     * @param {string} [reverseColorbarToggleId = null] - The ID of the reverse colorbar toggle
     * @param {string} [screenshotButtonId = null] - The ID of the screenshot button
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
        colorbarToggleId = null,
        reverseColorbarToggleId = null,
        screenshotButtonId = null
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
        this.colorbarToggleId = colorbarToggleId;
        this.reverseColorbarToggleId = reverseColorbarToggleId;
        this.screenshotButtonId = screenshotButtonId;

        // get time slider div
        this.timeSlider = $(`#${timeSliderId}`);

        // get plot options and initialize state variables
        this.toggleState = {};
        getFmriPlotOptions((plotOptions) => {
            this.toggleState['crosshairToggle'] = plotOptions.crosshair_on;
            this.toggleState['hoverToggle'] = plotOptions.hover_text_on;
            this.toggleState['directionMarkerToggle'] = plotOptions.direction_marker_on;
            this.toggleState['colorbarToggle'] = plotOptions.colorbar_on;
            this.toggleState['reverseColorbarToggle'] = plotOptions.reverse_colormap;
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
                    console.log('view toggle clicked');
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
                    console.log('direction marker toggle clicked');
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
                    console.log('crosshair toggle clicked');
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
                console.log('hover toggle clicked');
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

        // Colorbar listener
        if (this.colorbarToggleId) {
            this.colorbarToggle = $(`#${this.colorbarToggleId}`);
            this.colorbarToggle.on('click', () => {
                console.log('colorbar toggle clicked');
                this.toggleState['colorbarToggle'] = !this.toggleState['colorbarToggle'];
                updateFmriPlotOptions(
                    { colorbar_on: this.toggleState['colorbarToggle'] },
                    () => {
                        eventBus.publish(
                            EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_COLORBAR,
                            { colorbarState: this.toggleState['colorbarToggle'] }
                        );
                    }
                );
            });
        }

        // Reverse colorbar listener
        if (this.reverseColorbarToggleId) {
            this.reverseColorbarToggle = $(`#${this.reverseColorbarToggleId}`);
            this.reverseColorbarToggle.on('click', () => {
                console.log('reverse colorbar toggle clicked');
                this.toggleState['reverseColorbarToggle'] = !this.toggleState['reverseColorbarToggle'];
                updateFmriPlotOptions(
                    { reverse_colormap: this.toggleState['reverseColorbarToggle'] },
                    () => {
                        eventBus.publish(
                            EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_REVERSE_COLORBAR,
                            { reverseColormapState: this.toggleState['reverseColorbarToggle'] }
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
    }
}

export default ViewOptionsFmri;