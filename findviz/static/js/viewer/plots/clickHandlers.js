// ClickHandler.js
// Handles click events for NiftiViewer and GiftiViewer
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import ContextManager from '../api/ContextManager.js';

export class NiftiClickHandler {
    /**
     * @param {string} slice1ContainerId - The ID of the first slice container
     * @param {string} slice2ContainerId - The ID of the second slice container
     * @param {string} slice3ContainerId - The ID of the third slice container
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        slice1ContainerId,
        slice2ContainerId,
        slice3ContainerId,
        eventBus,
        contextManager
    ) {
        this.slice1Container = document.getElementById(slice1ContainerId);
        this.slice2Container = document.getElementById(slice2ContainerId);
        this.slice3Container = document.getElementById(slice3ContainerId);
        this.eventBus = eventBus;
        this.contextManager = contextManager;
        // Attach click listeners after initialization of viewer is complete
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.INIT_NIFTI_VIEWER, () => {
            this.attachClickListeners();
        });
    }

    /**
     * Attach click listeners to the slice containers
     */
    attachClickListeners() {
        console.log('attaching click listeners to nifti viewer');
        // handle click events
        this.slice1Container.on('plotly_click', (event) => this.clickHandler(event, 'slice_1'));
        this.slice2Container.on('plotly_click', (event) => this.clickHandler(event, 'slice_2'));
        this.slice3Container.on('plotly_click', (event) => this.clickHandler(event, 'slice_3'));
    }

    /**
     * Handle click events for the slice containers
     * @param {object} eventData - The event data
     * @param {string} sliceName - The name of the slice
     */
    async clickHandler(eventData, sliceName) {
        console.log('click event on nifti viewer');
        const x = Math.round(eventData.points[0].x);
        const y = Math.round(eventData.points[0].y);
        await this.contextManager.data.updateLocation({ x, y }, sliceName);
        this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, { x, y, sliceName });
    }
}


export class GiftiClickHandler {
    /**
     * @param {string} leftSurfaceId - The ID of the left surface. May be null if not present
     * @param {string} rightSurfaceId - The ID of the right surface. May be null if not present
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        leftSurfaceId = null,
        rightSurfaceId = null,
        eventBus,
        contextManager
    ) {
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // Attach click listeners after initialization of viewer is complete
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.INIT_GIFTI_VIEWER, () => {
            console.log('attaching click listeners to gifti viewer');
            if (leftSurfaceId) {
                this.leftSurface = document.getElementById(leftSurfaceId);
            }
            if (rightSurfaceId) {
                this.rightSurface = document.getElementById(rightSurfaceId);
            }
            this.attachClickListeners();
        });
    }

    /**
     * Attach click listeners to the left and right surfaces
     */
    attachClickListeners() {
        if (this.leftSurface) {
            this.leftSurface.on('plotly_click', (event) => this.clickHandler(event, 'left'));
        }
        if (this.rightSurface) {
            this.rightSurface.on('plotly_click', (event) => this.clickHandler(event, 'right'));
        }
    }

    /**
     * Handle click events for the left or right surface
     * @param {object} eventData - The event data
     * @param {string} hemisphere - The hemisphere
     */
    async clickHandler(eventData, hemisphere) {
        console.log('click event on gifti viewer');
        const vertexIndex = eventData.points[0].pointNumber;
        await this.contextManager.data.updateLocation({selected_vertex: vertexIndex, selected_hemi: hemisphere }, null);
        this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.GIFTIVIEWER_CLICK, { vertexIndex, hemisphere });
    }
}