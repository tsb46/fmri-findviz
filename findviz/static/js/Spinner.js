// Spinner.js - visualization of loading spinner for 
// upload, preprocessing, and analysis

/**
 * Spinner class for showing and hiding loading spinners
 */
class Spinner {
    /**
     * Constructor for Spinner class
     * @param {string} overlayId - ID of the spinner overlay
     * @param {string} wheelId - ID of the spinner wheel
     */
    constructor(
        overlayId,
        wheelId
    ) {
        this.overlay = document.getElementById(overlayId);
        this.wheel = document.getElementById(wheelId);
        this.container = document.querySelector('.spinner-container');
    }

    /**
     * Hide spinner overlay and wheel
     */
    hide() {
        this.overlay.style.display = 'none';
        this.wheel.style.display = 'none';
        this.container.style.display = 'none';
    }
    
    /**
     * Show spinner overlay and wheel
     */
    show() {
        this.overlay.style.display = 'block';
        this.wheel.style.display = 'block';
        this.container.style.display = 'block';
    }

}

export default Spinner;