// VertexCoordinate.js
// Handles display of vertex coordinates on the gifti plot
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import ContextManager from '../../../api/ContextManager.js';


class VertexCoordinate {
    /**
     * @param {string} containerId - The id of the vertex coordinate container
     * @param {string} vertexNumberId - The id of the vertex number display box
     * @param {string} selectedHemisphereId - The id of the selected hemisphere display box
     * @param {EventBus} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        containerId,
        vertexNumberId,
        selectedHemisphereId,
        eventBus, 
        contextManager
    ) {
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        this.vertexNumber = $(`#${vertexNumberId}`);
        this.selectedHemisphere = $(`#${selectedHemisphereId}`);
        this.container = $(`#${containerId}`);

        // display container
        this.container.show();
        // enable coordinate display boxes
        this.vertexNumber.prop('disabled', false);
        this.selectedHemisphere.prop('disabled', false);
        // attach event listeners
        this.attachEventListeners();
    }

    /**
     * Attach event listeners to the coordinate display boxes
     */
    attachEventListeners() {
        this.eventBus.subscribe(
            EVENT_TYPES.VISUALIZATION.FMRI.GIFTIVIEWER_CLICK,
            this.updateCoordinates.bind(this)
        );
    }

    /**
     * Update the coordinates in the coordinate display boxes
     */
    async updateCoordinates() {
        const vertexCoords = await this.contextManager.data.getVertexCoords();
        this.vertexNumber.text(vertexCoords.vertex_number);
        this.selectedHemisphere.text(vertexCoords.selected_hemisphere);
    }
}

export default VertexCoordinate;
