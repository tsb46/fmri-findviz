// main.js

import MainViewer from './viewer.js';
import FileUploader from './file.js';
import { loadComponent, initBootstrapComponents } from './utils.js';


// Load all main page components
async function loadPageComponents() {
    const components = [
        loadComponent("uploadFileComponent", "uploadModal.html"),
        loadComponent("visualizationOptions", "visualizationOptions.html"),
        loadComponent("preprocessingOptions", "preprocessingOptions.html"),
        loadComponent("fmriVisualizationCard", "fmriVisualizationCard.html"),
        loadComponent("timeCourse", "timeCourse.html")
    ];
    // wait for all component promises to resolve
    await Promise.all(components);
}

function main() {
    // initialize file uploader w/ callback function to initiate viz classes
    new FileUploader((data, files) => {
         // Toggle parent visualization container to display
        const visualizationContainer = document.getElementById('parent-container');
        visualizationContainer.style.display = 'block'
        // determine plot type
        let plotType;
        if (files.niftiFile) {
            plotType = 'nifti'
        } else if (files.leftFile || files.rightFile) {
            plotType = 'gifti'
        } else {
            throw new Error('No fMRI files provided in file input');
        }

        let mainViewer = new MainViewer(data, plotType);
        // initialize plots
        mainViewer.init();
    });
}

// Start the application
document.addEventListener("DOMContentLoaded", async () => {
    // Load HTML components
    await loadPageComponents();
    // initialize bootstrap components
    initBootstrapComponents()
    // Run Main
    main();

});


