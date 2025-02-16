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


/**
 * Play movie by cycling through fMRI time points
 * 
 * @param {jQuery} timeSlider - Time slider element
 * @param {jQuery} playMovieButton - Play movie button
 * @param {number} [intervalTime = 500] - Time interval in milliseconds (0.5 seconds)
 * @returns {Object} Movie control functions
 */
export function playMovie(timeSlider, playMovieButton, intervalTime = 500) {
    let isPlaying = false;  // State to track whether the slider is playing
    let intervalId = null;  // Store the interval ID for controlling the slider progression
    const playMovieButtonIcon = playMovieButton.find('i');  // Get the <i> tag inside the button

    // Add click listener to toggle play/pause
    playMovieButton.on('click', () => {
        if (isPlaying) {
            // Currently playing, so stop the slider and change icon to play
            stopMovie();
        } else {
            // Currently paused, so start the slider and change icon to stop
            startMovie();
        }
    });

    // Function to start the slider progression
    function startMovie() {
        const intervalTime = 500;  // Time interval in milliseconds (0.5 seconds)
        isPlaying = true;
        playMovieButtonIcon.removeClass('fa-play').addClass('fa-stop');  // Change icon to stop

        // Start updating the slider at the defined interval
        intervalId = setInterval(() => {
            let currentValue = timeSlider.slider('getValue');
            let maxValue = timeSlider.slider('getAttribute', 'max');

            if (currentValue < maxValue) {
                timeSlider.slider('setValue', currentValue + 1);
                timeSlider.trigger('change')
            } else {
                stopMovie();  // Stop the movie when the slider reaches the max value
            }
        }, intervalTime);
    }

    // Function to stop the slider progression
    function stopMovie() {
        clearInterval(intervalId);  // Stop the interval
        isPlaying = false;
        playMovieButtonIcon.removeClass('fa-stop').addClass('fa-play');  // Change icon to play
    }

    // Return control functions for external use if needed
    return {
        start: startMovie,
        stop: stopMovie
    };
}