// main.js

import MainViewer from './viewer/MainViewer.js';
import FileUploader from './upload/FileUploader.js';
import { initBootstrapComponents } from './utils.js';
import { DOM_IDS } from './constants/DomIds.js';

async function main() {
    // Check if data was pre-loaded via CLI
    try {
        const response = await fetch('/check_cache');
        const data = await response.json();

        if (data.has_cache) {
            // Use pre-loaded data
            const visualizationContainer = document.getElementById(DOM_IDS.PARENT_CONTAINER);
            visualizationContainer.style.display = 'block';
            
            let mainViewer = new MainViewer(data.plot_type);
            mainViewer.init();
        } else {
            // Initialize file uploader for browser inputs
            new FileUploader((fileType) => {
                const visualizationContainer = document.getElementById(DOM_IDS.PARENT_CONTAINER);
                visualizationContainer.style.display = 'block';
                
                let mainViewer = new MainViewer(fileType);
                mainViewer.init();
            });
        }
    } catch (error) {
        console.error('Error checking cache:', error);
    }
}

// Start the application
document.addEventListener("DOMContentLoaded", () => {
    // initialize bootstrap components
    initBootstrapComponents()
    // Run Main
    main();
});


