// main.js

import MainViewer from './viewer.js';
import FileUploader from './file.js';
import { initBootstrapComponents } from './utils.js';


function main() {
    // initialize file uploader w/ callback function to initiate viz classes
    new FileUploader((data, plotType) => {
         // Toggle parent visualization container to display
        const visualizationContainer = document.getElementById('parent-container');
        visualizationContainer.style.display = 'block'

        let mainViewer = new MainViewer(data, plotType);
        // initialize plots
        mainViewer.init();
    });

}

// Start the application
document.addEventListener("DOMContentLoaded", () => {
    // initialize bootstrap components
    initBootstrapComponents()
    // Run Main
    main();
});


