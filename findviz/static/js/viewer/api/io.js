// io.js
// apis for saving and loading scenes
// - saveScene
// - loadScene

import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';

/**
 * Save scene
 * @param {string} sceneName - Name of scene to save
 * @param {string} errorMessageId - ID of error message element
 * @returns {Promise} Promise object representing the API call
 */
export const saveScene = async (sceneName, errorMessageId) => {
    const url = API_ENDPOINTS.IO.SAVE_SCENE;
    const formData = new FormData();
    formData.append('sceneName', sceneName);
    // clear error message (if any)
    $(`#${errorMessageId}`).text('');
    $(`#${errorMessageId}`).hide();
    try {
        // Use fetch with blob response type to handle binary data
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            $(`#${errorMessageId}`).text('Error saving scene');
            $(`#${errorMessageId}`).show();
            throw new Error('Error saving scene');
        }
            
        // return the blob from response
        return await response.blob();
        
    } catch (error) {
        console.error('Error during scene download:', error);
        $(`#${errorMessageId}`).text('Error saving scene');
        $(`#${errorMessageId}`).show();
        throw error;
    }
}
