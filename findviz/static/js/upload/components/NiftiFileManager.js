// NiftiFileManager.js
// Manages the nifti file DOM elements

class NiftiFileManager {
    /**
     * @param {string} niftiFuncId - The ID of the nifti functional file input
     * @param {string} niftiAnatId - The ID of the nifti anatomical file input
     * @param {string} niftiMaskId - The ID of the nifti mask file input
     */
    constructor(
        niftiFuncId,
        niftiAnatId,
        niftiMaskId,
    ) {
        this.niftiFuncId = niftiFuncId;
        this.niftiAnatId = niftiAnatId;
        this.niftiMaskId = niftiMaskId;
    }

    /**
     * Clear nifti files
     */
    clearFiles() {
        document.getElementById(this.niftiFuncId).value = '';
        document.getElementById(this.niftiAnatId).value = '';
        document.getElementById(this.niftiMaskId).value = '';
    }

    /**
     * Get nifti files
     * @returns {object} - The nifti files
     */
    getFiles() {
        return {
            nii_func: document.getElementById(this.niftiFuncId).files[0],
            nii_anat: document.getElementById(this.niftiAnatId).files[0],
            nii_mask: document.getElementById(this.niftiMaskId).files[0],
        };
    }
}

export default NiftiFileManager;