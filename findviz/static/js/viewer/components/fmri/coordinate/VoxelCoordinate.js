// VoxelCoordinate.js
// Handles display of voxel coordinates on the nifti plot
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import ContextManager from '../../../api/ContextManager.js';


class VoxelCoordinate {
    /**
     * @param {string} containerId - The id of the voxel coordinate container
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
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        this.xCoordinate = $(`#${xCoordinateId}`);
        this.yCoordinate = $(`#${yCoordinateId}`);
        this.zCoordinate = $(`#${zCoordinateId}`);
        this.container = $(`#${containerId}`);

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
        const voxelCoords = await this.contextManager.data.getVoxelCoords();
        this.xCoordinate.text(voxelCoords.x);
        this.yCoordinate.text(voxelCoords.y);
        this.zCoordinate.text(voxelCoords.z);
    }
}

export default VoxelCoordinate;
