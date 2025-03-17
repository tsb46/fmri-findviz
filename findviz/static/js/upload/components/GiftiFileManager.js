// GiftiFileManager.js
// Manages the gifti file DOM elements

class GiftiFileManager {
    /**
     * @param {string} leftGiftiFuncId - The ID of the left gifti functional file input
     * @param {string} rightGiftiFuncId - The ID of the right gifti functional file input
     * @param {string} leftGiftiMeshId - The ID of the left gifti mesh file input
     * @param {string} rightGiftiMeshId - The ID of the right gifti mesh file input
     */
    constructor(
        leftGiftiFuncId,
        rightGiftiFuncId,
        leftGiftiMeshId,
        rightGiftiMeshId,
    ) {
        this.leftGiftiFuncId = leftGiftiFuncId;
        this.rightGiftiFuncId = rightGiftiFuncId;
        this.leftGiftiMeshId = leftGiftiMeshId;
        this.rightGiftiMeshId = rightGiftiMeshId;
    }

    /**
     * Clear gifti files
     */
    clearFiles() {
        document.getElementById(this.leftGiftiFuncId).value = '';
        document.getElementById(this.rightGiftiFuncId).value = '';
        document.getElementById(this.leftGiftiMeshId).value = '';
        document.getElementById(this.rightGiftiMeshId).value = '';
    }

    /**
     * Get gifti files
     * @returns {object} - The gifti files
     */
    getFiles() {
        return {
            left_gii_func: document.getElementById(this.leftGiftiFuncId).files[0],
            right_gii_func: document.getElementById(this.rightGiftiFuncId).files[0],
            left_gii_mesh: document.getElementById(this.leftGiftiMeshId).files[0],
            right_gii_mesh: document.getElementById(this.rightGiftiMeshId).files[0],
        };
    }
}

export default GiftiFileManager;