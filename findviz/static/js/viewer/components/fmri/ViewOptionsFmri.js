// ViewOptionsFmri component
import { captureScreenshot } from './capture.js';
import { EVENT_TYPES } from '../../../constants/EventTypes.js';
import ContextManager from '../../api/ContextManager.js';
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
     * @param {string} viewToggleId - The ID of the view toggle
     * @param {string} crosshairToggleId - The ID of the crosshair toggle
     * @param {string} hoverToggleId - The ID of the hover toggle
     * @param {string} directionMarkerToggleId - The ID of the direction marker toggle
     * @param {string} colorbarToggleId - The ID of the colorbar toggle
     * @param {string} reverseColorbarToggleId - The ID of the reverse colorbar toggle
     * @param {string} freezeViewToggleId - The ID of the freeze view toggle
     * @param {string} screenshotButtonId - The ID of the screenshot button
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        fmriFileType,
        plotlyDivIds,
        captureDivId,
        timeSliderId,
        colormapContainerId,
        colormapDropdownMenuId,
        colormapDropdownToggleId,
        viewToggleId,
        crosshairToggleId,
        hoverToggleId,
        directionMarkerToggleId,
        colorbarToggleId,
        reverseColorbarToggleId,
        freezeViewToggleId,
        screenshotButtonId,
        eventBus,
        contextManager
    ) {
        // get elements
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
        this.freezeViewToggleId = freezeViewToggleId;
        this.screenshotButtonId = screenshotButtonId;
        // get event bus and context manager
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // get time slider div
        this.timeSlider = $(`#${timeSliderId}`);

        // initialize color map
        this.colorMap = new ColorMap(
            this.colormapContainerId,
            this.colormapDropdownMenuId,
            this.colormapDropdownToggleId,
            this.contextManager.plot.getFmriPlotOptions,
            this.contextManager.plot.updateFmriPlotOptions,
            EVENT_TYPES.VISUALIZATION.FMRI.COLOR_MAP_CHANGE,
            this.eventBus,
            this.contextManager
        );

        // initialize view listeners
        this.initializeViewListeners();
        // enable buttons based on the file type (nifti or gifti)
        this.enableButtons();
    }

    async initializeViewListeners() {
        // initialize state variables
        await this.setStateVariables();
        // Nifti specific listeners
        if (this.fmriFileType == 'nifti') {
            // Ortho to Montage view listener (only for nifti)
            if (this.viewToggleId) {
                this.viewToggle = $(`#${this.viewToggleId}`);
                this.viewToggle.on('click', async () => {
                    console.log('view toggle clicked');
                    this.toggleState['viewToggle'] = this.toggleState['viewToggle'] == 'ortho' ? 'montage' : 'ortho';
                    await this.contextManager.plot.updateNiftiViewState(
                        this.toggleState['viewToggle']
                    );
                    // if view state is montage, set text to ortho
                    if (this.toggleState['viewToggle'] == 'montage') {
                        this.viewToggle.text('Ortho');
                    } else {
                        this.viewToggle.text('Montage');
                    }
                    this.eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.FMRI.VIEW_TOGGLE,
                        { view_state: this.toggleState['viewToggle'] }
                    );
                });
            }

            // Montage direction marker listener
            if (this.directionMarkerToggleId) {
                this.directionMarkerToggle = $(`#${this.directionMarkerToggleId}`);
                this.directionMarkerToggle.on('click', async () => {
                    console.log('direction marker toggle clicked');
                    this.toggleState['directionMarkerToggle'] = !this.toggleState['directionMarkerToggle'];
                    await this.contextManager.plot.updateFmriPlotOptions(
                        { direction_marker_on: this.toggleState['directionMarkerToggle'] }
                    );
                    this.eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_DIRECTION_MARKER,
                        { directionMarkerState: this.toggleState['directionMarkerToggle'] }
                    );
                });
            }

            // Crosshair listener
            if (this.crosshairToggleId) {
                this.crosshairToggle = $(`#${this.crosshairToggleId}`);
                this.crosshairToggle.on('click', async () => {
                    console.log('crosshair toggle clicked');
                    this.toggleState['crosshairToggle'] = !this.toggleState['crosshairToggle'];
                    await this.contextManager.plot.updateFmriPlotOptions(
                        { crosshair_on: this.toggleState['crosshairToggle'] },
                    );
                    this.eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_CROSSHAIR,
                        { crosshairState: this.toggleState['crosshairToggle'] }
                    );
                });
            }
        } else {
            // Freeze view listener
            if (this.freezeViewToggleId) {
                this.freezeViewToggle = $(`#${this.freezeViewToggleId}`);
                this.freezeViewToggle.on('click', async () => {
                    console.log('freeze view toggle clicked');
                    this.toggleState['freezeViewToggle'] = !this.toggleState['freezeViewToggle'];
                    await this.contextManager.plot.updateFmriPlotOptions(
                        { freeze_view_on: this.toggleState['freezeViewToggle'] }
                    );
                    if (this.toggleState['freezeViewToggle']) {
                        // set icon to unlock
                        this.freezeViewToggle.find('i').addClass('fa-unlock');
                        this.freezeViewToggle.find('i').removeClass('fa-lock');
                    } else {
                        // set icon to lock
                        this.freezeViewToggle.find('i').addClass('fa-lock');
                        this.freezeViewToggle.find('i').removeClass('fa-unlock');
                    }
                    this.eventBus.publish(
                        EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_FREEZE_VIEW,
                        { freezeViewState: this.toggleState['freezeViewToggle'] }
                    );
                });
            }
        }

        // Hover label listener
        if (this.hoverToggleId) {
            this.hoverToggle = $(`#${this.hoverToggleId}`);
            this.hoverToggle.on('click', async () => {
                console.log('hover toggle clicked');
                this.toggleState['hoverToggle'] = !this.toggleState['hoverToggle'];
                await this.contextManager.plot.updateFmriPlotOptions(
                    { hover_text_on: this.toggleState['hoverToggle'] },
                );
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.FMRI.HOVER_TEXT_TOGGLE,
                    { hoverState: this.toggleState['hoverToggle'] }
                );
            });
        }

        // Colorbar listener
        if (this.colorbarToggleId) {
            this.colorbarToggle = $(`#${this.colorbarToggleId}`);
            this.colorbarToggle.on('click', async () => {
                console.log('colorbar toggle clicked');
                this.toggleState['colorbarToggle'] = !this.toggleState['colorbarToggle'];
                await this.contextManager.plot.updateFmriPlotOptions(
                    { colorbar_on: this.toggleState['colorbarToggle'] }
                );
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_COLORBAR,
                    { colorbarState: this.toggleState['colorbarToggle'] }
                );
            });
        }

        // Reverse colorbar listener
        if (this.reverseColorbarToggleId) {
            this.reverseColorbarToggle = $(`#${this.reverseColorbarToggleId}`);
            this.reverseColorbarToggle.on('click', async () => {
                console.log('reverse colorbar toggle clicked');
                this.toggleState['reverseColorbarToggle'] = !this.toggleState['reverseColorbarToggle'];
                await this.contextManager.plot.updateFmriPlotOptions(
                    { reverse_colormap: this.toggleState['reverseColorbarToggle'] }
                );
                this.eventBus.publish(
                    EVENT_TYPES.VISUALIZATION.FMRI.TOGGLE_REVERSE_COLORBAR,
                    { reverseColormapState: this.toggleState['reverseColorbarToggle'] }
                );
            });
        }

        // Screenshot listener
        if (this.screenshotButtonId) {
            this.screenshotButton = $(`#${this.screenshotButtonId}`);
            this.screenshotButton.on('click', () => {
                console.log('screenshot button clicked');
                captureScreenshot(this.plotlyDivIds, this.captureDivId);
            });
        }
    }

    /**
     * Enable buttons based on the file type (nifti or gifti)
     */
    enableButtons() {
        if (this.fmriFileType == 'nifti') {
            $(`#${this.viewToggleId}`).prop('disabled', false);
            $(`#${this.crosshairToggleId}`).prop('disabled', false);
            $(`#${this.directionMarkerToggleId}`).prop('disabled', false);
        } else {
            $(`#${this.freezeViewToggleId}`).prop('disabled', false);
        }
        $(`#${this.hoverToggleId}`).prop('disabled', false);
        $(`#${this.colorbarToggleId}`).prop('disabled', false);
        $(`#${this.reverseColorbarToggleId}`).prop('disabled', false);
        $(`#${this.screenshotButtonId}`).prop('disabled', false);
    }

    async setStateVariables() {
        this.toggleState = {};
        const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
        const viewState = await this.contextManager.plot.getNiftiViewState();
        this.toggleState['crosshairToggle'] = plotOptions.crosshair_on;
        this.toggleState['hoverToggle'] = plotOptions.hover_text_on;
        this.toggleState['directionMarkerToggle'] = plotOptions.direction_marker_on;
        this.toggleState['colorbarToggle'] = plotOptions.colorbar_on;
        this.toggleState['reverseColorbarToggle'] = plotOptions.reverse_colormap;
        this.toggleState['viewToggle'] = viewState.view_state;
        this.toggleState['freezeViewToggle'] = plotOptions.freeze_view_on;
    }
}

export default ViewOptionsFmri;