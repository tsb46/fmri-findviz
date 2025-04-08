// Coordinate.js
// Handles display of world coordinates on the nifti plot
// World coordinates: the image voxel coordinates, transformed via the
// image qform/ sform transformation matrix
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import ContextManager from '../../../api/ContextManager.js';


class WorldCoordinate {
    /**
     * @param {string} containerId - The id of the world coordinate container
     * @param {string} xCoordinateId - The id of the x coordinate display box
     * @param {string} yCoordinateId - The id of the y coordinate display box
     * @param {string} zCoordinateId - The id of the z coordinate display box
     * @param {EventBus} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        containerId,
        xCoordinateId,
        yCoordinateId,
        zCoordinateId,
        eventBus,
        contextManager
    ) {
        this.xCoordinate = $(`#${xCoordinateId}`);
        this.yCoordinate = $(`#${yCoordinateId}`);
        this.zCoordinate = $(`#${zCoordinateId}`);
        this.container = $(`#${containerId}`);
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // display container
        this.container.show();
        // enable coordinate display boxes
        this.xCoordinate.prop('disabled', false);
        this.yCoordinate.prop('disabled', false);
        this.zCoordinate.prop('disabled', false);
        // update coordinates
        this.updateCoordinates();
        // attach event listeners
        this.attachEventListeners();
    }

    /**
     * Attach event listeners to the coordinate display boxes
     */
    attachEventListeners() {
        this.eventBus.subscribeMultiple([
            EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, 
            EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_DIRECTION_CHANGE,
            EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_CHANGE,
            EVENT_TYPES.VISUALIZATION.FMRI.VIEW_TOGGLE,
        ], this.updateCoordinates.bind(this));
    }

    /**
     * Update the coordinates in the coordinate display boxes
     */
    async updateCoordinates() {
        const worldCoords = await this.contextManager.data.getWorldCoords();
        this.xCoordinate.text(worldCoords.x);
        this.yCoordinate.text(worldCoords.y);
        this.zCoordinate.text(worldCoords.z);
    }
}

export default WorldCoordinate;