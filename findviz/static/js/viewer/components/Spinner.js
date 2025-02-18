/**
 * Class for handling spinner visualization and visibility
 */
class Spinner {
    /**
     * Create spinner instance
     * @param {string} spinnerOverlayId - ID of spinner overlay div
     * @param {string} spinnerDivId - ID of spinner div
     */
    constructor(
        spinnerOverlayId = 'spinner-overlay',
        spinnerDivId = 'spinner'
    ) {
        this.spinnerOverlay = document.getElementById(spinnerOverlayId);
        this.spinnerDiv = document.getElementById(spinnerDivId);
    }

    /**
     * Show spinner
     */
    show() {
        console.log('showing spinner');
        this.spinnerOverlay.style.display = 'block';
        this.spinnerDiv.style.display = 'block';
    }

    /**
     * Hide spinner
     */
    hide() {
        console.log('hiding spinner');
        this.spinnerOverlay.style.display = 'none';
        this.spinnerDiv.style.display = 'none';
    }
}

export default Spinner;