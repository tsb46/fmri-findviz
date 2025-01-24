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

    // Enable HTML content in the time point distance button
    $("#distance-popover").popover({
        html: true,
        sanitize: false,
    });

    // Enable HTML content in the find peaks button
    $("#peak-finder-popover").popover({
        html: true,
        sanitize: false,
    });

}


// circular index of array
function circularIndex(arr, index) {
  const length = arr.length;
  return (index % length + length) % length;
}



export {
    initBootstrapComponents,
    circularIndex
};


