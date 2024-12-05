// utilities module


// enable bootstrap components (tooltips and alerts)
function initBootstrapComponents() {
    // Enable bootstrap tooltips
    // toggles for immediate display
    $('.toggle-immediate').tooltip({
        html: true, // Enable HTML content in the tooltip
        trigger : 'hover'
    });
    // toggles for display after small wait time
    $('.toggle-wait').tooltip({
        trigger : 'hover',
        delay: { show: 1000},
        html: true
    });

    // Enable dismissal of alerts
    $('.alert').alert()

    // Enable HTML content in the montage button
    $("#montage-popover").popover({
        html: true,
        sanitize: false,
    });

    // Enable HTML content in the find peaks button
    $("#peak-finder-popover").popover({
        html: true,
        sanitize: false,
    });

}


// Ensure filer inputs are correct
function validateFilterInputs(TR, lowCut, highCut, errorDiv) {
    // Initialize error message
    let errorMessage
    // Ensure TR has been provided
    if (TR == '') {
        errorMessage = 'TR (repetition time) of functional time courses must be provided';
        preprocessingInputError(errorDiv, errorMessage)
        return false
    }
    // Ensure TR is positive
    if (TR < 0) {
        errorMessage = 'TR (repetition time) must be a positive number';
        preprocessingInputError(errorDiv, errorMessage)
        return false
    }
    // Ensure lowCut or highCut has been provided
    if (lowCut == '' && highCut == '') {
        errorMessage = 'at least lowCut or highCut (in Hz) must be provided';
        preprocessingInputError(errorDiv, errorMessage)
        return false
    }
    // calcualte nyquist frequency
    let nyquistFreq = (1/TR)/2
    // Check low cut is lower than nyquist frequency
    if (lowCut != '') {
        let lowCutNum = Number(lowCut)
        if (lowCutNum > nyquistFreq){
            errorMessage = `lowCut must be less than than Nyquist frequency: ${nyquistFreq}`;
            preprocessingInputError(errorDiv, errorMessage)
            return false
        }
    }
    // Check high cut is lower than nyquist frequency
    if (highCut != ''){
        let highCutNum = Number(highCut)
        if (highCutNum > nyquistFreq){
            errorMessage = `highCut must be less than than Nyquist frequency: ${nyquistFreq}`;
            preprocessingInputError(errorDiv, errorMessage)
            return false
        }
    }
    // Check lowCut is lower than highCut
    if (lowCut != '' && highCut != '') {
        if (lowCut >= highCut) {
            errorMessage = 'lowCut must be less than than highCut';
            preprocessingInputError(errorDiv, errorMessage)
            return false
        }
    }
    return true
}

// Display error for preprocessing input validation
function preprocessingInputError(errorDiv, errorMessage) {
    errorDiv.textContent = errorMessage;
    errorDiv.style.display = 'block';
    // Clear error message after 5 seconds
    setTimeout(function() {
        errorDiv.style.display = 'none';
    }, 5000);
}

// circular index of array
function circularIndex(arr, index) {
  const length = arr.length;
  return (index % length + length) % length;
}



export {
    initBootstrapComponents,
    validateFilterInputs,
    preprocessingInputError,
    circularIndex
};


