/**
 * Class for handling spinner visualization and visibility
 */
class Spinner {
    /**
     * Create spinner instance
     * @param {string} spinnerOverlayId - ID of spinner overlay div
     * @param {string} spinnerWheelId - ID of spinner wheel div
     */
    constructor(
        spinnerOverlayId,
        spinnerWheelId
    ) {
        this.spinnerOverlay = document.getElementById(spinnerOverlayId);
        this.spinnerWheel = document.getElementById(spinnerWheelId);
    }

    /**
     * Show spinner
     */
    show() {
        console.log('showing spinner');
        this.spinnerOverlay.style.display = 'block';
        this.spinnerWheel.style.display = 'block';
    }

    /**
     * Hide spinner
     */
    hide() {
        console.log('hiding spinner');
        this.spinnerOverlay.style.display = 'none';
        this.spinnerWheel.style.display = 'none';
    }
}

export default Spinner;