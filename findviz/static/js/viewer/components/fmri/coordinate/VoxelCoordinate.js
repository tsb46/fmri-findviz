// VoxelCoordinate.js
// Handles display of voxel coordinates on the nifti plot
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import ContextManager from '../../../api/ContextManager.js';


class VoxelCoordinate {
    /**
     * @param {("nifti" | "gifti")} plotType - The type of plot
     * @param {string} xCoordinateId - The id of the x coordinate display box
     * @param {string} yCoordinateId - The id of the y coordinate display box
     * @param {string} zCoordinateId - The id of the z coordinate display box
     * @param {EventBus} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        plotType,
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

        // only enable event listeners for nifti plot
        if (plotType === 'nifti') {
            // enable coordinate display boxes
            this.xCoordinate.prop('disabled', false);
            this.yCoordinate.prop('disabled', false);
            this.zCoordinate.prop('disabled', false);
            // update coordinates
            this.updateCoordinates();
            // attach event listeners
            this.attachEventListeners();
        }
    }

    /**
     * Attach event listeners to the coordinate display boxes
     */
    attachEventListeners() {
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK,
            this.updateCoordinates.bind(this)
        );
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
