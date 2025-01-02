// main.js

import MainViewer from './viewer.js';
import FileUploader from './upload/file.js';
import { initBootstrapComponents } from './utils.js';


async function main() {
    // Check if data was pre-loaded via CLI
    try {
        const response = await fetch('/check_cache');
        const data = await response.json();
        
        if (data.has_cache) {
            // Use pre-loaded data
            const visualizationContainer = document.getElementById('parent-container');
            visualizationContainer.style.display = 'block';
            
            let mainViewer = new MainViewer(data.cache_data, data.plot_type);
            mainViewer.init();
        } else {
            // Initialize file uploader for browser inputs
            new FileUploader((data, plotType) => {
                const visualizationContainer = document.getElementById('parent-container');
                visualizationContainer.style.display = 'block';
                
                let mainViewer = new MainViewer(data, plotType);
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


