// user.js - VisualizationOptions and PreprocessingOptions classes

// Import filter parameter validation
import { validateFilterInputs, preprocessingInputError } from './utils.js';

// Class to handle visualization options to modify brain plots
export class VisualizationOptions {
    constructor(
        colorMin,
        colorMax,
        plotType,
        sliceLen,
        onReadyListeners,
        colorMap='viridis',
        sliderSteps=100,
        allowedPrecision=6,
    ) {
        // Keep original color min and max variables for reset
        this.colorMinOrig = colorMin;
        this.colorMaxOrig = colorMax;
        // Set plot type - gifti or nifti
        this.plotType = plotType;
        // state variables for color min and max selections
        this.colorMin = colorMin;
        this.colorMax = colorMax;
        // set slice lengths for montage
        this.sliceLen = sliceLen;
        // Set number of steps in color and threshold sliders
        this.colorSliderSteps = sliderSteps;
        // Calculate the range and precision of the data
        this.dataRange = this.colorMax - this.colorMin;
        // Set allowed precision - precision above this number is ignored
        this.allowedPrecision = allowedPrecision
        // Initialize thresholds (set to [0,0] for no threshold by default)
        this.thresholdMin = 0;
        this.thresholdMax = 0;
        // Initialize montage slice selection as sagittal (x) direction
        this.montageSliceSelection = 'z'
        // Montage slice indices
        this.montageSliceIndices = {}
        if (this.plotType == 'nifti') {
            const sliceDirections = ['x', 'y', 'z']
            const sliceSliders = ['slice1Slider', 'slice2Slider', 'slice3Slider'];
            const sliceIndexInit = [0.33, 0.5, 0.66];
            sliceDirections.forEach((direction, index) => {
                this.montageSliceIndices[direction] = {}
                sliceSliders.forEach((sliceDiv, index) => {
                    const sliceNum = Math.floor(
                        this.sliceLen[direction] * sliceIndexInit[index]
                    );
                    this.montageSliceIndices[direction][sliceDiv] = sliceNum
                })
            });
        };

        // Fetch precision from the Python backend and intialize sliders
        this.fetchPrecision(this.dataRange).then(precision => {
            // Don't allow precision above allowedPrecision
            if (precision > allowedPrecision) {
                this.precision = allowedPrecision;
            }
            else {
                this.precision = precision;
            }
            this.initializeColorSliders();    // Initialize sliders after precision is set
        });
        // Callback function supplied from visualization to attach listeners
        // First check callback function is function
        if (typeof onReadyListeners === 'function') {
            this.onReadyListeners = onReadyListeners; // Store the callback function
        }
        else {
            console.error('a function must be supplied to VisualizationOptions callback')
        }

        // get color range slider
        this.colorSlider = $('#colorRangeSlider');
        // get threshold slider
        this.thresholdSlider = $('#thresholdSlider');
        // get reset slider button
        this.resetSliderButton = $('#reset-slider-button');
        // get ortho to montage viewer
        this.viewToggle = $('#toggle-view');
        // get crosshair toggle
        this.crosshairToggle = $('#toggle-crosshair');
        // get hover toggle
        this.hoverToggle = $("#toggle-hover");
        // get direction marker toggle
        this.directionMarkerToggle = $("#toggle-direction");
        // get screenshot button
        this.screenshotButton = $("#select-screenshot");
        // get play-movie button
        this.playMovieButton = $("#play-movie");
        // Fetch colormap data from the server
        this.initOptions();
    }

    // initialize components in visualization options card
    initOptions() {
        // fetch color map data
        fetch('/get_colormaps')
            .then(response => response.json())
            .then(data => {
                this.colormapData = data;
                // Create the options card after fetching the colormap data
                this.createVizOptions();
            })
            .catch(error => console.error('Error fetching initializing visualization options:', error));
    }

    createVizOptions() {
        // Remove an existing visualization options, if they exist
        let colorMapContainer = document.getElementById('form-colormap');

        // Dynamically generate the colormap options
        let colormapOptions = Object.keys(this.colormapData).map(cmap => `
            <li data-value="${cmap}" style="display: flex; justify-content: space-between; align-items: center;">
                <span style="flex: 1; min-width: 70px;">${this.colormapData[cmap].label}</span>
                <span class="colormap-swatch" style="background: ${this.colormapData[cmap].gradient};"></span>
            </li>
        `).join('');

        // Clear any existing content
        colorMapContainer.innerHTML = '';

        // Generate Bootstrap dropdown
        colorMapContainer.innerHTML = `
            <label for="colormapSelect"> <strong>Choose Colormap:</strong></label>
            <div class="custom-dropdown" id="colormapSelect">
                <div class="dropdown-toggle" style="color:black;">Viridis</div> <!-- Default value set to 'Viridis' -->
                <ul class="dropdown-menu">
                    ${colormapOptions}
                </ul>
            </div>
        `;

        // Attach event listeners
        this.attachEventListeners();

        // Initialize montage popover, if nifti
        if (this.plotType == 'nifti') {
            this.initializeMontageOptions();
        } else {
            // remove popover for gifti
            $("#montage-popover").popover('disable');
            // disable button
            $("#montage-popover").prop('disabled', true);
        }

        // execute event listeners callback function
        this.onReadyListeners()
    }

    initializeColorSliders() {
        // extend out color slider to a quarter of range on both of sides
        const extendRange = (this.colorMax - this.colorMin)/4
        // Initialize color range slider dynamically
        this.colorSlider.slider({
            min: +this.colorMin.toFixed(this.precision) - extendRange,
            max: +this.colorMax.toFixed(this.precision) + extendRange,
            step: this.getStepSize(),  // Dynamic step size based on precision
            range: true,
            value: [this.colorMin, this.colorMax],  // Set initial value to min and max
            tooltip: 'show',
            // formatter: formatter_slider
        });
        // Initialize color threshold slider similarly
        this.thresholdSlider.slider({
            min: +this.colorMin.toFixed(this.precision),
            max: +this.colorMax.toFixed(this.precision),
            step: this.getStepSize(),  // Dynamic step size
            range: true,
            value: [0, 0],
            tooltip: 'show',
            // formatter: formatter_slider
        });
    }

    // set montage box popup options
    initializeMontageOptions(popoverShown=false) {
        // if montage is not shown, attach listener for popover show
        if (!popoverShown) {
            // Event listener for when the popover is shown
            $('#montage-popover').on('shown.bs.popover', () => {
                // set selection in drop down menu
                $('#montage-slice-select').val(this.montageSliceSelection);
                // loop through slider divs and set sliders
                for (const sliceDiv in this.montageSliceIndices[this.montageSliceSelection]) {
                    $(`#${sliceDiv}`).slider({
                        min: 0,
                        max: this.sliceLen[this.montageSliceSelection] - 1,
                        step: 1,
                        value: this.montageSliceIndices[this.montageSliceSelection][sliceDiv],
                        tooltip: 'show',
                    });
                };
                // attach montage listeners
                this.attachMontageListeners();
            });
        // if already shown, revise sliders
        } else {
            for (const sliceDiv in this.montageSliceIndices[this.montageSliceSelection]) {
                // re-initialize slider
                $(`#${sliceDiv}`).slider({
                    min: 0,
                    max: this.sliceLen[this.montageSliceSelection]-1,
                    step: 1,
                    value: this.montageSliceIndices[this.montageSliceSelection][sliceDiv],
                    tooltip: 'show',
                });
                // refresh slider
                $(`#${sliceDiv}`).slider('refresh');

            };
        }
    }

    // attach montage dropdown and slider listeners
    attachMontageListeners() {
        // attach dropdown slice selection listener
        $('#montage-slice-select').change((event) => {
            this.montageSliceSelection = event.target.value;
            this.initializeMontageOptions(true);
            // trigger a custom event
            const customEventMontageDirection = $.Event(
                'montageSliceDirectionChange', {
                    detail: {
                        sliceDirection: this.montageSliceSelection,
                        sliceIndices: this.montageSliceIndices[this.montageSliceSelection]
                    }
                }
            );
            // Dispatch the custom event
            $(document).trigger(customEventMontageDirection);
        });

        // Listen for slider changes and update slice index
        for (const sliceDiv in this.montageSliceIndices[this.montageSliceSelection]) {
            $(`#${sliceDiv}`).on('change', (event) => {
                this.montageSliceIndices[this.montageSliceSelection][sliceDiv] = event.value.newValue;
                // Trigger a custom event
                const customEventSlider = $.Event(
                    `${sliceDiv}Change`, {
                        detail: {
                            sliceDirection: this.montageSliceSelection,
                            sliceIndices: this.montageSliceIndices[this.montageSliceSelection]
                        }
                    }
                );
                // Dispatch the custom event
                $(document).trigger(customEventSlider);
            });
        }
    }

    attachEventListeners() {
        // Custom-drop down functionality listener
        this.attachCustomDropDown();

        // Color Range Slider listener
        this.colorSlider.on('change', this.handleColorSlider.bind(this));

        // Threshold Slider listener
        this.thresholdSlider.on('change', this.handleThresholdSlider.bind(this));

        // Reset slider button listener
        this.resetSliderButton.on('click', this.handleResetSliders.bind(this));

        // Ortho to Montage view listener
        if (this.plotType == 'nifti') {
            this.viewToggle.on(
                'click', this.handleViewToggle.bind(this)
            );
        } else {
            // disable crosshairs button for gifti
            this.viewToggle.addClass('disabled');
        }

        // Toggle crosshairs listener (only applicable for Nifti)
        if (this.plotType == 'nifti') {
            this.crosshairToggle.on(
                'click', this.handleCrosshairToggle.bind(this)
            );
        } else {
            // disable crosshairs button for gifti
            this.crosshairToggle.addClass('disabled');
        }

        // Toggle hover text listener
        this.hoverToggle.on(
            'click', this.handleHoverToggle.bind(this)
        );

        // Toggle direction marker labels listener (only applicable for Nifti)
        if (this.plotType == 'nifti') {
            this.directionMarkerToggle.on(
                'click', this.handleDirectionMarkerToggle.bind(this)
            );
        } else {
            // disable crosshairs button for gifti
            this.directionMarkerToggle.addClass('disabled');
        }

        // Take screenshot of container listener
        this.screenshotButton.on(
            "click", this.handleScreenshot.bind(this)
        );

        // Initialize play movie listener
        this.handlePlayMovie()

    }

    // Custom-drop down functionality listener
    attachCustomDropDown() {
        const dropdownToggle = document.querySelector('.custom-dropdown .dropdown-toggle');
        const dropdownMenu = document.querySelector('.custom-dropdown .dropdown-menu');

        // Toggle the dropdown menu on click
        dropdownToggle.addEventListener('click', (event) => {
            dropdownMenu.classList.toggle('show');
            event.stopPropagation();  // Stop event propagation to prevent the document click event from closing it immediately
        });

        // Close the dropdown if a click happens outside of it
        document.addEventListener('click', (event) => {
            // Check if the clicked element is outside the dropdown
            if (!dropdownMenu.contains(event.target) && !dropdownToggle.contains(event.target)) {
                dropdownMenu.classList.remove('show');
            }
        });

        // Handle dropdown item selection
        dropdownMenu.addEventListener('click', (event) => {
            if (event.target.tagName === 'LI' || event.target.parentElement.tagName === 'LI') {
                const selectedValue = event.target.closest('li').getAttribute('data-value');
                dropdownToggle.textContent = event.target.closest('li').querySelector('span:first-child').textContent;
                dropdownMenu.classList.remove('show');
                // Create custom event for dropdown menu selection to pass to viewers
                const customEventColormap = new CustomEvent(
                    'colormapChange', { detail: { selectedValue } }
                );
                // Dispatch custom event
                document.dispatchEvent(customEventColormap);
            }
        });
    }

    // Initiate color slider event
    handleColorSlider(event) {
        // event.value gives the current slider value
        const colorValues = event.value;
        // Trigger a custom event using jQuery
        const customEventColor = $.Event(
            'colorSliderChange', { detail: colorValues }
        );
        // Dispatch the custom event
        $(document).trigger(customEventColor);
    }

    // Initiate threshold slider event
    handleThresholdSlider(event) {
        // event.value gives the current slider value
        const thresholdValues = event.value;
        // Trigger a custom event using jQuery
        const customEventThreshold = $.Event(
            'thresholdSliderChange', { detail: thresholdValues }
        );
        // Dispatch the custom event
        $(document).trigger(customEventThreshold);
    }

    // Trigger custom toggle ortho to montage viewer event
    handleViewToggle() {
        // Trigger a custom event using jQuery
        const customEventView = $.Event(
            'toggleViewChange', {
                detail: {
                    sliceIndices: this.montageSliceIndices[this.montageSliceSelection],
                    sliceDirection: this.montageSliceSelection
                }
            }
        );
        // Dispatch the custom event
        $(document).trigger(customEventView);
    }

    // Trigger custom crosshair click event
    handleCrosshairToggle() {
        // Trigger a custom event using jQuery
        const customEventCrosshair = $.Event('toggleCrosshairChange');
        // Dispatch the custom event
        $(document).trigger(customEventCrosshair);
    }

    // Trigger custom hover click event
    handleHoverToggle() {
        // Trigger a custom event using jQuery
        const customEventHover = $.Event('toggleHoverChange');
        // Dispatch the custom event
        $(document).trigger(customEventHover);
    }

    // Trigger custom hover click event
    handleDirectionMarkerToggle() {
        // Trigger a custom event using jQuery
        const customDirectionHover = $.Event('toggleDirectionMarkerChange');
        // Dispatch the custom event
        $(document).trigger(customDirectionHover);
    }

    // Take screenshot of brain image
    handleScreenshot() {
        // get divs based on plot type
        let plotlyDivs
        // parent container
        let captureDiv
        if (this.plotType == 'nifti') {
            captureDiv = 'slices_container'
            plotlyDivs = [
                'x_slice_container',
                'y_slice_container',
                'z_slice_container',
                'colorbar_container_nii'
            ]
        } else if (this.plotType == 'gifti') {
            captureDiv = 'surface_container'
            plotlyDivs = [
                'left_brain_visualization',
                'right_brain_visualization',
                'colorbar_container_gii'
            ]
        }
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
                    plotlyDiv, { format: 'png', width: plotlyDiv.offsetWidth, height: plotlyDiv.offsetHeight }
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

    // Play movie by cycling through fMRI time points
    handlePlayMovie() {
        this.sliderElement = $('#time_slider');  // Get the time slider element
        this.isPlaying = false;  // State to track whether the slider is playing
        this.intervalId = null;  // Store the interval ID for controlling the slider progression
        this.playMovieButtonIcon = this.playMovieButton.find('i');  // Get the <i> tag inside the button

        // Add click listener to toggle play/pause
        this.playMovieButton.on('click', () => {
            if (this.isPlaying) {
                // Currently playing, so stop the slider and change icon to play
                this.stopMovie();
            } else {
                // Currently paused, so start the slider and change icon to stop
                this.startMovie();
            }
        });
    }

    // Function to start the slider progression
    startMovie() {
        const intervalTime = 500;  // Time interval in milliseconds (0.5 seconds)
        this.isPlaying = true;
        this.playMovieButtonIcon.removeClass('fa-play').addClass('fa-stop');  // Change icon to stop

        // Start updating the slider at the defined interval
        this.intervalId = setInterval(() => {
            let currentValue = this.sliderElement.slider('getValue');
            let maxValue = this.sliderElement.slider('getAttribute', 'max');

            if (currentValue < maxValue) {
                this.sliderElement.slider('setValue', currentValue + 1);
                let timeIndex = this.sliderElement.slider('getValue');
                // Trigger a custom event to update fmri plots
                const customEvent = $.Event('timeSliderChange',
                    { detail: { timeIndex } }
                );
                // Dispatch the custom event through the jQuery object
                $(document).trigger(customEvent);
            } else {
                this.stopMovie();  // Stop the movie when the slider reaches the max value
            }
        }, intervalTime);
    }

    // Function to stop the slider progression
    stopMovie() {
        clearInterval(this.intervalId);  // Stop the interval
        this.isPlaying = false;
        this.playMovieButtonIcon.removeClass('fa-stop').addClass('fa-play');  // Change icon to play
    }


    // modify visualization options after change to data scale
    modifyVizOptions(colorMin, colorMax) {
        // Keep original color min and max variables for reset
        this.colorMinOrig = colorMin;
        this.colorMaxOrig = colorMax;
        // state variables for color min and max selections
        this.colorMin = colorMin;
        this.colorMax = colorMax;
        // Calculate the range and precision of the data
        this.dataRange = this.colorMax - this.colorMin;
        // Initialize thresholds (set to [0,0] for no threshold by default)
        this.thresholdMin = 0;
        this.thresholdMax = 0;
        // Fetch precision from the Python backend and intialize sliders
        this.fetchPrecision(this.dataRange).then(precision => {
            // Don't allow precision above allowedPrecision
            if (precision > this.allowedPrecision) {
                this.precision = this.allowedPrecision;
            }
            else {
                this.precision = precision
            }
            // Initialize sliders after precision is set
            this.initializeColorSliders();
            // Reset sliders
            this.handleResetSliders()
        });
    }

    handleResetSliders() {
        // Set color range slide back to default values
        this.colorMin = this.colorMinOrig
        this.colorMax = this.colorMaxOrig
        this.colorSlider.slider('setValue', [this.colorMinOrig, this.colorMaxOrig], false, true)
        // Set threshold slider back to [0,0]
        this.thresholdSlider.slider('setValue', [0, 0], false, true)
    }

    fetchPrecision() {
        return fetch(`/get_precision?data_range=${this.dataRange}`)
            .then(response => response.json())
            .then(data => {
                return data
            })
            .catch(error => console.error('Error fetching precision of slider:', error));
    }

    // Helper function to get an appropriate step size
    getStepSize() {
        // Get step size that gives you about N (= slider_steps) steps
        return +(this.dataRange/this.colorSliderSteps).toFixed(this.precision)
    }
}


// Class to handle preprocessing options
export class PreprocessingOptions {
    constructor(
        plotType,
        onReadyListeners,
        maskKey=null,
    ) {
        // Set plot type - gifti or nifti
        this.plotType = plotType;
        // Determine whether mask has been passed (only used for nifti files)
        this.maskKey = maskKey
        // Set states of preprocessing switches
        this.normSwitchEnabled = false;
        this.filterSwitchEnabled = false;
        this.smoothSwitchEnabled = false;
        // Callback function supplied from visualization to attach listeners
        // First check callback function is function
        if (typeof onReadyListeners === 'function') {
            this.onReadyListeners = onReadyListeners; // Store the callback function
        }
        else {
            console.error('a function must be supplied to PreprocessingOptions callback')
        }

        // Get preprocessing button
        this.preprocessSubmit = $('#submit-preprocess');
        // get reset preprocess button
        this.resetPreprocessButton = $('#reset-preprocess-button');
        // Initialize preprocess switches
        this.initializeSwitches();
        // Attach event listeners
        this.attachEventListeners();
        // execute event listeners callback function
        this.onReadyListeners()
    }

    initializeSwitches() {
        // Enable normalization switch
        const enableNormalization = $('#enable-normalization')
        enableNormalization.on('click', () => {
            this.normSwitchEnabled = !this.normSwitchEnabled
            const inputs_norm = document.querySelectorAll('input.norm-option');
            inputs_norm.forEach(
                input => this.normSwitchEnabled ? input.disabled = false : input.disabled = true
            );
        });

        // Enable filtering switch
        const enableFiltering = $('#enable-filtering')
        enableFiltering.on('click', () => {
            this.filterSwitchEnabled = !this.filterSwitchEnabled
            const inputs_filter = document.querySelectorAll('input.filter-option');
            inputs_filter.forEach(
                input => this.filterSwitchEnabled ? input.disabled = false : input.disabled = true
            );
        });

        // Enable smoothing switch, smoothing only available for volumes (nifti)
        if (this.plotType == 'nifti') {
            const enableSmoothing = $('#enable-smoothing')
            enableSmoothing.on('click', () => {
                this.smoothSwitchEnabled = !this.smoothSwitchEnabled;
                const input_smooth = document.getElementById('smoothing-fwhm');
                if (this.smoothSwitchEnabled) {
                    input_smooth.disabled = false
                } else {
                    input_smooth.disabled = true
                }
            });
        }
        else {
            // Disable smoothing switch
            const enableSmoothing = $('#enable-smoothing')
            enableSmoothing.attr('disabled', true)
        }
    }

    attachEventListeners() {
        // Preprocessing submit listener
        this.preprocessSubmit.on(
            'click', this.handlePreprocessingButton.bind(this)
        );

        // Reset preprocess button listener
        this.resetPreprocessButton.on(
            'click', this.handleResetPreprocess.bind(this)
        );

    }

    // Validate inputs and initiate normalization button event
    handlePreprocessingButton(event) {
        // Get error message div
        let errorDiv = document.getElementById('error-message-preprocess');
        // Clear previous error message
        errorDiv.style.display = 'none';
        // Initialize error message
        let errorMessage;

        // Check normalization options
        let meanCenter = false;
        let zScore = false;
        if (this.normSwitchEnabled) {
            meanCenter = document.getElementById('select-mean-center').checked;
            zScore = document.getElementById('select-z-score').checked;
            // make sure an option has been provided
            if (!meanCenter && !zScore) {
                errorMessage = 'If normalization is enabled, mean-center or z-score option must be selected';
                preprocessingInputError(errorDiv, errorMessage);
                return
            }
        }

        // Check filter options
        let TR = null;
        let lowCut = null;
        let highCut = null;
        let filterParamsOK = false;
        if (this.filterSwitchEnabled) {
            TR = document.getElementById('filter-tr').value;
            lowCut = document.getElementById('filter-low-cut').value;
            highCut = document.getElementById('filter-high-cut').value;
            // if mask has not been provided, raise error
            if (!this.maskKey && this.plotType == 'nifti') {
                errorMessage = 'a brain mask must be supplied (in file upload) to perform temporal filtering';
                preprocessingInputError(errorDiv, errorMessage);
                return
            }
            // Validate filter parameters
            filterParamsOK = validateFilterInputs(
                TR, lowCut, highCut, errorDiv
            )
            if (!filterParamsOK) {
                return
            }
        }

        // Check smoothing
        let smoothFWHM = null;
        if (this.smoothSwitchEnabled) {
            smoothFWHM = document.getElementById('smoothing-fwhm').value;
            if (smoothFWHM < 0) {
                errorMessage = 'FWHM values must be positive';
                preprocessingInputError(errorDiv, errorMessage);
                return
            }

        }

        // If no options selected, return error message
        if (!meanCenter && !zScore && TR === null && lowCut === null && highCut === null && smoothFWHM === null) {
            errorMessage = 'No preprocessing options selected';
            preprocessingInputError(errorDiv, errorMessage)
            return
        }

        // Dispatch the custom event through the jQuery object
        // Trigger a custom event using jQuery
        const customPreprocessEvent = $.Event('preprocessSubmit');
        const preprocessData = {
            meanCenter,
            zScore,
            TR,
            lowCut,
            highCut,
            smoothFWHM
        }
        $(document).trigger(
            customPreprocessEvent, {detail: preprocessData}
        );

        // Turn on preprocess alert
        document.getElementById('preprocess-alert').style.display = 'block'
    }

    // initiate reset preprocessing event
    handleResetPreprocess() {
        // Get error message div
        let errorDiv = document.getElementById('error-message-preprocess');
        // Clear previous error message, if any
        errorDiv.style.display = 'none';
        // Set switches to disabled
        document.getElementById('enable-normalization').checked = false;
        document.getElementById('enable-filtering').checked = false;
        document.getElementById('enable-smoothing').checked = false;
        this.filterSwitchEnabled = false;
        this.normSwitchEnabled = false;
        this.smoothSwitchEnabled = false;

        // Clear parameters
        document.getElementById('select-mean-center').checked = false;
        document.getElementById('select-z-score').checked = false;
        document.getElementById('filter-tr').value = '';
        document.getElementById('filter-low-cut').value = '';
        document.getElementById('filter-high-cut').value = '';
        document.getElementById('smoothing-fwhm').value = '';

        // initiate preprocess reset event
        const customPreprocessResetEvent = $.Event('preprocessReset');
        $(document).trigger(customPreprocessResetEvent);

        // Turn off preprocess alert
        document.getElementById('preprocess-alert').style.display = 'none'
    }

}
