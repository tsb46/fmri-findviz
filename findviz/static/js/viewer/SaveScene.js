// SaveScene.js
// Save scene (current state)functionality
import { DOM_IDS } from '../constants/DomIds.js';
import { EVENT_TYPES } from '../constants/EventTypes.js';
import { saveScene } from './api/io.js';
import Spinner from './components/Spinner.js';

class SaveScene {
    /**
     * @param {string} saveSceneModalId - The ID of the save scene modal
     * @param {string} saveSceneSubmitButtonId - The ID of the save scene submit button
     * @param {string} saveSceneFileNameId - The ID of the save scene file name input
     * @param {string} saveSceneErrorMessageId - The ID of the save scene error message
     * @param {EventBus} eventBus - The event bus
     */
    constructor(
        saveSceneModalId,
        saveSceneSubmitButtonId,
        saveSceneFileNameId,
        saveSceneErrorMessageId,
        eventBus,
    ) {
        this.saveSceneModalId = saveSceneModalId;
        this.saveSceneSubmitButtonId = saveSceneSubmitButtonId;
        this.saveSceneFileNameId = saveSceneFileNameId;
        this.saveSceneErrorMessageId = saveSceneErrorMessageId;
        this.eventBus = eventBus;

        this.attachEventListeners();

        // initialize spinner
        this.spinner = new Spinner(
            DOM_IDS.SAVE_SCENE.SPINNER_OVERLAY,
            DOM_IDS.SAVE_SCENE.SPINNER_WHEEL
        );
    }

    attachEventListeners() {
        // on save scene submit
        const saveSceneSubmitButton = $(`#${this.saveSceneSubmitButtonId}`);
        saveSceneSubmitButton.on('click', this.onSaveSceneSubmit.bind(this));
    }

    downloadScene(blob, fileName) {
        // Create a download link and trigger click
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = fileName.endsWith('.fvstate') ? fileName : `${fileName}.fvstate`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }

    async onSaveSceneSubmit() {
        // Get the file name
        let fileName = $(`#${this.saveSceneFileNameId}`).val();
        // if file name is not provided, use default name
        if (!fileName || fileName === '') {
            fileName = 'scene';
        }
        // show spinner
        this.spinner.show();
        try {
            // Save the scene
            const blob = await saveScene(fileName, this.saveSceneErrorMessageId);
            // Download the scene
            this.downloadScene(blob, fileName);
            // Publish event
            this.eventBus.publish(EVENT_TYPES.SAVE_SCENE.SAVE_SCENE_SUCCESS);
             // close modal
             $(`#${this.saveSceneModalId}`).modal('hide');
        } finally {
            // hide spinner
            this.spinner.hide();
        }
    }
    
    
}
export default SaveScene;