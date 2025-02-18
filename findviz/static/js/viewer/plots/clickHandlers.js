// ClickHandler.js
// Handles click events for NiftiViewer and GiftiViewer
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import eventBus from '../events/ViewerEvents.js';
import { updateLocation } from '../api/data.js';

export class NiftiClickHandler {
    /**
     * @param {string} slice1ContainerId - The ID of the first slice container
     * @param {string} slice2ContainerId - The ID of the second slice container
     * @param {string} slice3ContainerId - The ID of the third slice container
     */
    constructor(
        slice1ContainerId,
        slice2ContainerId,
        slice3ContainerId,
    ) {
        this.slice1Container = document.getElementById(slice1ContainerId);
        this.slice2Container = document.getElementById(slice2ContainerId);
        this.slice3Container = document.getElementById(slice3ContainerId);

        // Attach click listeners after initialization of viewer is complete
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.INIT_NIFTI_VIEWER, () => {
            this.attachClickListeners();
        });
    }

    /**
     * Attach click listeners to the slice containers
     */
    attachClickListeners() {
        this.slice1Container.on('plotly_click', (event) => this.clickHandler(event, 'slice_1'));
        this.slice2Container.on('plotly_click', (event) => this.clickHandler(event, 'slice_2'));
        this.slice3Container.on('plotly_click', (event) => this.clickHandler(event, 'slice_3'));
    }

    /**
     * Handle click events for the slice containers
     * @param {object} eventData - The event data
     * @param {string} sliceName - The name of the slice
     */
    clickHandler(eventData, sliceName) {
        console.log('click event on nifti viewer');
        const x = Math.round(eventData.points[0].x);
        const y = Math.round(eventData.points[0].y);
        updateLocation({ x, y }, sliceName, () => {
            eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, { x, y, sliceName });
        });
    }
}


export class GiftiClickHandler {
    /**
     * @param {string} leftSurfaceId - The ID of the left surface. May be null if not present
     * @param {string} rightSurfaceId - The ID of the right surface. May be null if not present
     */
    constructor(
        leftSurfaceId = null,
        rightSurfaceId = null,
    ) {
        if (leftSurfaceId) {
            this.leftSurface = document.getElementById(leftSurfaceId);
        }
        if (rightSurfaceId) {
            this.rightSurface = document.getElementById(rightSurfaceId);
        }

        // Attach click listeners after initialization of viewer is complete
        eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.INIT_GIFTIVIEWER, () => {
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
    clickHandler(eventData, hemisphere) {
        console.log('click event on gifti viewer');
        const vertexIndex = eventData.points[0].pointNumber;
        updateLocation({ click_coords: { selected_vertex: vertexIndex, selected_hemi: hemisphere }}, null, () => {
            eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.GIFTIVIEWER_CLICK, { vertexIndex, hemisphere });
        });
    }
}