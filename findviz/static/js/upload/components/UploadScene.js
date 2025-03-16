// Upload scene file (.pkl file)
import { API_ENDPOINTS } from '../../constants/APIEndpoints.js';
import Spinner from '../../Spinner.js';
import UploadErrorHandler from '../UploadErrorHandler.js';


class UploadScene {
    /**
     * @param {string} uploadSceneButtonId - ID of the upload scene button
     * @param {string} sceneFileDivId - ID of the scene file div
     * @param {Spinner} spinner - Spinner instance
     * @param {UploadErrorHandler} errorHandler - Error handler instance
     */
	constructor(
        uploadSceneButtonId,
        sceneFileDivId,
        spinner,
        errorHandler
    ) {
        this.uploadSceneButton = $(`#${uploadSceneButtonId}`);
        this.sceneFileDiv = $(`#${sceneFileDivId}`);
        this.spinner = spinner;
        this.errorHandler = errorHandler;

        // attach event listeners
        this.attachEventListeners();
	}

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Open file dialog when user clicks upload scene
		this.uploadSceneButton.on('click', () => {
			// simulate file input click
			this.sceneFileDiv.click();
		});
    }

    /**
	 * Upload scene file and process cached data
	 * @param event - Scene file data
	 * @returns {Promise<void>}
	 */
	async uploadFile(event) {
        // show spinner
		this.spinner.show();
		try {
            // get scene file
            const sceneFile = event.target.files[0];
            // create form data
            const formData = new FormData();
            formData.append('scene_file', sceneFile);
            // send form data to server
            const response = await fetch(API_ENDPOINTS.UPLOAD.SCENE, {
                method: 'POST',
                body: formData
            });
            // check if server processed scene file successfully
            if (!response.ok) {
                if (response.status === 400) {
                    const data = await response.json();
                    this.errorHandler.displayError(
                        data.error
                    );
                } else {
                    this.errorHandler.showSceneErrorModal();
                }
                return;
            }
            // get data from server
            const data = await response.json();
            // return data
            return data;
		} catch (error) {
				console.error('Error during scene file upload:', error);
				this.errorHandler.showSceneErrorModal();
		} finally {
				this.spinner.hide();
		}
	}
}

export default UploadScene;