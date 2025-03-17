/**
 * Take screenshot of brain image
 * 
 * @param {string[]} plotlyDivs - Plotly divs
 * @param {string} captureDiv - Capture div - the full div to capture
 */
export function captureScreenshot(plotlyDivs, captureDiv) {
    // Initialize image promises array
    const imagePromises = [];

    // Array to store the original Plotly divs to restore after capture
    const originalDivs = [];

    // Iterate over each Plotly divs and convert to image
    plotlyDivs.forEach((plotlyDivLabel) => {
        const plotlyDiv = document.getElementById(plotlyDivLabel)
        // ensure plotlyDiv exists
        if (plotlyDiv) {
            // Save the original div for restoring later
            originalDivs.push(plotlyDiv);

            // Convert each Plotly graph to an image
            const imagePromise = Plotly.toImage(
                plotlyDiv, 
                { format: 'png', width: plotlyDiv.offsetWidth, height: plotlyDiv.offsetHeight }
            ).then((dataUrl) => {
                // Create an image element
                const img = new Image();
                img.src = dataUrl;
                // Set the size of the image to match the original Plotly div
                img.width = plotlyDiv.offsetWidth;
                img.height = plotlyDiv.offsetHeight;
                // Replace the Plotly graph with the image
                plotlyDiv.parentNode.replaceChild(img, plotlyDiv);

                // Return the img element for later restoration
                return img;
            });

            imagePromises.push(imagePromise);
        }
    });

    // Wait until all Plotly graphs are converted to images
    Promise.all(imagePromises).then((images) => {
        // Now use html2canvas to capture the parent div
        html2canvas(document.getElementById(captureDiv)).then((canvas) => {
            // download the image
            const link = document.createElement('a');
            link.href = canvas.toDataURL();
            link.download = 'screenshot.png';
            link.click();
            // Restore the original Plotly graphs
            images.forEach((img, index) => {
                img.parentNode.replaceChild(originalDivs[index], img);
            });
        });
    }).catch((error) => {
        console.error('Error capturing Plotly graphs as images:', error);
    });
}


