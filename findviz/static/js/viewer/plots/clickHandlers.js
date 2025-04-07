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

        //  Drag state tracking
        this.isDragging = false;
        this.activeSlice = null;
        this.lastUpdateTime = 0;
        this.updateThrottleMs = 30;  // Throttle updates to avoid excessive rendering
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

        // Mouse down events to start dragging
        this.slice1Container.addEventListener('mousedown', (event) => this.mouseDownHandler(event, 'slice_1'));
        this.slice2Container.addEventListener('mousedown', (event) => this.mouseDownHandler(event, 'slice_2'));
        this.slice3Container.addEventListener('mousedown', (event) => this.mouseDownHandler(event, 'slice_3'));
        
        // Mouse move and up events attached to document to capture movements outside the container
        document.addEventListener('mousemove', this.mouseMoveHandler.bind(this));
        document.addEventListener('mouseup', this.mouseUpHandler.bind(this));
        
        // Handle edge case of leaving the window during drag
        window.addEventListener('blur', this.mouseUpHandler.bind(this));
    }

    /**
     * Handle click events for the slice containers (used during drag operations)
     * @param {object} eventData - The event data
     * @param {string} sliceName - The name of the slice
     */
    async clickHandler(eventData, sliceName) {
        // This is triggered during drag operations by Plotly
        // We only update location, not time course
        console.log('plotly_click event on nifti viewer');
        const x = Math.round(eventData.points[0].x);
        const y = Math.round(eventData.points[0].y);
        // Update location
        await this.contextManager.data.updateLocation({ x, y }, sliceName);
        // Publish the location update event
        this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, { x, y, sliceName });
    }

    /**
     * Handle mouse down events to start dragging
     * @param {MouseEvent} event - The mouse event
     * @param {string} sliceName - The name of the slice
     */
    async mouseDownHandler(event, sliceName) {
        // Start dragging
        this.isDragging = true;
        this.activeSlice = sliceName;
        console.log(`starting drag on ${sliceName}`);
        
        // Prevent text selection during drag
        event.preventDefault();
        
        // Get initial position from the plot
        const coords = await this.getPlotCoordinates(event);
        if (!coords) return;
        
        const { x, y } = coords;

        // Publish the time course update event on initial click
        this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_TIMECOURSE_UPDATE, { x, y, sliceName });
    }

    /**
     * Handle mouse move events during dragging
     * @param {MouseEvent} event - The mouse event
     */
    mouseMoveHandler(event) {
        if (!this.isDragging || !this.activeSlice) {
            return;
        }
        
        // Throttle updates for performance
        const currentTime = Date.now();
        if (currentTime - this.lastUpdateTime < this.updateThrottleMs) {
            return;
        }
        
        this.lastUpdateTime = currentTime;
        
        // Get coordinates and update
        this.getPlotCoordinates(event);
    }

    /**
     * Handle mouse up events to end dragging
     * @param {MouseEvent} event - The mouse event
     */
    mouseUpHandler(event) {
        if (this.isDragging) {
            console.log(`ending drag on ${this.activeSlice}`);
            this.isDragging = false;
            this.activeSlice = null;
        }
    }

    /**
     * Get plot coordinates from mouse event and update view
     * @param {MouseEvent} event - The mouse event
     */
    async getPlotCoordinates(event) {
        // Get the plotly div element
        let plotDiv = null;
        if (this.activeSlice === 'slice_1') {
            plotDiv = this.slice1Container;
        } else if (this.activeSlice === 'slice_2') {
            plotDiv = this.slice2Container;
        } else if (this.activeSlice === 'slice_3') {
            plotDiv = this.slice3Container;
        }
        
        if (!plotDiv) {
            return;
        }
        
        // Get plot bounding rect
        const rect = plotDiv.getBoundingClientRect();
        
        // Check if mouse is within the plot bounds
        const isWithinBounds = (
            event.clientX >= rect.left &&
            event.clientX <= rect.right &&
            event.clientY >= rect.top &&
            event.clientY <= rect.bottom
        );
        
        // If outside bounds, don't update (optional: you could also clamp to edge)
        if (!isWithinBounds) {
            return;
        }
        
        // Convert mouse position to relative position in the plot
        const xRatio = (event.clientX - rect.left) / rect.width;
        const yRatio = (event.clientY - rect.top) / rect.height;
        
        // Get the plot data range
        const layout = plotDiv._fullLayout;
        if (!layout || !layout.xaxis || !layout.yaxis) {
            return;
        }
        
        const xaxis = layout.xaxis;
        const yaxis = layout.yaxis;
        
        // Calculate plot coordinates
        let x = Math.round(xaxis.range[0] + xRatio * (xaxis.range[1] - xaxis.range[0]));
        let y = Math.round(yaxis.range[0] + (1 - yRatio) * (yaxis.range[1] - yaxis.range[0]));
        
        // Ensure coordinates are within data bounds
        // Get the data dimensions from the first trace
        let xMax, yMax;
        
        if (plotDiv.data && plotDiv.data[0] && plotDiv.data[0].z) {
            // For 2D data, dimensions come from the z array
            yMax = plotDiv.data[0].z.length - 1;
            xMax = plotDiv.data[0].z[0]?.length - 1 || 0;
        } else {
            // Fallback to the axis range
            xMax = Math.floor(xaxis.range[1]);
            yMax = Math.floor(yaxis.range[1]);
        }
        
        // Clamp coordinates to valid range
        x = Math.max(0, Math.min(x, xMax));
        y = Math.max(0, Math.min(y, yMax));
        
        // Check if coordinates are integers and within reasonable bounds
        if (!Number.isFinite(x) || !Number.isFinite(y) || 
            x < 0 || y < 0 || x > 1000 || y > 1000) {
            console.warn(`Invalid coordinates: x=${x}, y=${y}`);
            return;
        }
        
        // Update location and trigger a view update
        try {
            await this.contextManager.data.updateLocation({ x, y }, this.activeSlice);
            this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.NIFTIVIEWER_CLICK, { x, y, sliceName: this.activeSlice });
            return { x, y };
        } catch (error) {
            console.error('Error updating location:', error);
            // End the drag if there's an error
            this.isDragging = false;
            this.activeSlice = null;
        }
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