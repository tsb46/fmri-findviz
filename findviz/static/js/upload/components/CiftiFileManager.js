// CiftiFileManager.js
// Manages the cifti file DOM elements

class CiftiFileManager {
    /**
     * Constructor for CiftiFileManager
     * @param {string} dtseriesId - The ID of the dtseries.nii file input
     * @param {string} surfLeftId - The ID of the left hemisphere surface mesh file input
     * @param {string} surfRightId - The ID of the right hemisphere surface mesh file input
     */
    constructor(
        dtseriesId,
        surfLeftId,
        surfRightId
    ) {
        this.dtseriesId = dtseriesId;
        this.surfLeftId = surfLeftId;
        this.surfRightId = surfRightId;
    }

    /**
     * Clear the cifti files
     */
    clearFiles() {
        document.getElementById(this.dtseriesId).value = '';
        document.getElementById(this.surfLeftId).value = '';
        document.getElementById(this.surfRightId).value = '';
    }

    /**
     * Get the cifti files
     * @returns {object} - The cifti files
     */
    getFiles() {
        return {
            cifti_dtseries: document.getElementById(this.dtseriesId).files[0],
            left_gii_mesh: document.getElementById(this.surfLeftId).files[0],
            right_gii_mesh: document.getElementById(this.surfRightId).files[0]
        };
    }
}

export default CiftiFileManager;