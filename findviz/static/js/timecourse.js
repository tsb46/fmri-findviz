// timecourse.js

// Import filter parameter validation
import { validateFilterInputs, preprocessingInputError, circularIndex } from './utils.js';

class TimeCourse {
    constructor(
        timeLength,
        timeCourses=null,
        timeCourseLabels=null,
        taskConditions=null,
        timeSliderDiv
    ) {
        this.timeLength = timeLength;
        this.timeSliderElement = timeSliderDiv;
        // get time plot container
        this.timeCourseContainer = document.getElementById(
            'timeCourseContainer'
        );
        // Modify behavior of time course plot, depending on whether a
        // time course or task file was passed for display
        if (timeCourses === null && taskConditions === null) {
            this.userInput = false;
            this.timeCourseInput = false;
            this.taskDesignInput = false;
        } else {
            // If any input passed, set userInput to true
            this.userInput = true;
            // if time course or task file is passed, display time course container
            this.timeCourseContainer.style.visibility = 'visible';
            // Check if time courses were passed
            if (timeCourses === null) {
                this.timeCourseInput = false;
            } else {
                this.timeCourseInput = true;
            }
            // check if task design file was passed
            if (taskConditions === null) {
                this.taskDesignInput = false;
            } else {
                this.taskDesignInput = true;
            }
        }
        // Keep track of number of time courses in time course and task regressor container
        this.timeCoursesN = 0
        // initilialize time course container
        this.timeCourses = []
        // grab color options in dropdown menu and store as attribute
        let colorDropdown = Array.from(
            document.getElementById('ts-color-select').options
        );
        this.colorOptions = colorDropdown.map(
         (options) => options.value
        )
        // set color index
        let colorIndex
        // if time courses passed, store time course and attributes
        if (this.timeCourseInput) {
            // Loop through time courses and assign properties
            for (const [index, timeCourse] of timeCourses.entries()) {
                // start index over if timecourses exceed length of preset color list
                colorIndex = index % this.colorOptions.length
                this.timeCourses.push({
                    // trace name in plot
                    name: timeCourseLabels[index],
                    // time course
                    ts: timeCourse,
                    // Whether the time course is user-input or fmri
                    type: 'user',
                    // initialize preprocessed state as false
                    preprocessed: false,
                    // initialize preprocessed time course as null
                    ts_prep: null,
                    // Set color from color options
                    color: this.colorOptions.shift(),
                    // initialize plot state as true
                    plot: true,
                    // initialize line opacity as 1
                    opacity: 1,
                    // initialize width
                    width: 2,
                    // initialize line mode
                    mode: 'lines+markers'
                });
            }
            this.timeCoursesN += 1;
        }
        // initialize task regressors container
        this.taskRegressors = []
        // if task design file passed, store regressors and attributes
        if (this.taskDesignInput) {
            // Loop through task conditions and assign properties
            for (const [index, cLabel] of taskConditions.labels.entries()) {
                // start index over if loop index exceeds color list length
                colorIndex = index % this.colorOptions.length
                this.taskRegressors.push({
                    // trace name in plot
                    name: cLabel,
                    // non-convolved hrf regressors
                    block: taskConditions.conditions_block[index],
                    // convolved hrf regressor
                    hrf: taskConditions.conditions_hrf[index],
                    // initialize plot state as true
                    plot: true,
                    // Set color from color options
                    color: this.colorOptions.shift(),
                    // initialize line opacity as 1
                    opacity: 1,
                    // initialize width
                    width: 2,
                    // initialize line mode
                    mode: 'lines+markers'
                });
            }
            this.timeCoursesN += 1;
        }
        // get time course plot div
        this.plotId = 'ts-plot';
        // initialize time point state variable
        this.timePoint = 0;
        // Set states of preprocessing switches
        this.normSwitchEnabled = false;
        this.filterSwitchEnabled = false;
        // set plot state - whether a plotly plot is in the container
        this.plotState = false;
        // initialize task design plot state
        this.taskPlotState = true;
        // Initialize annotation state
        this.annotateState = false;
        // Annotation markers
        this.annotationMarkers = [];
        // initialize annotation selection
        this.annotationSelection = 0;
        // initialize annotation selection highlight state
        this.annotationSelectionHighlight = true;
        // initialize task plot type - hrf vs block
        this.taskPlotType = 'hrf';
        // initialize time point marker as true
        this.timePointMarker = true;
        // initialize time point marker state vars
        this.timePointMarkerState = {
            width: 1,
            shape: 'solid',
            color: 'grey',
            opacity: 0.5
        }
        // initialize grid line markers as true
        this.plotGridLine = true;
        // Initialize plot layout as null
        this.plotLayout = null;
        // Initialize hover as true
        this.plotHoverText = true;
        // Initialize user options
        this.initializeOptions();
        // Initialize correlation analysis submission event
        $('#correlationForm').on(
            'submit', this.handleCorrelationSubmit.bind(this)
        );
        // Initialize average analysis submission event
        $('#averageForm').on(
            'submit', this.handleAverageSubmit.bind(this)
        );
        // Add event listener for window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    // Initialize time course user options
    initializeOptions() {
        this.opacitySlider = $('#ts-opacity-slider');
        this.opacitySlider.slider({
            min: 0,
            max: 1,
            step: 0.01,
            value: 1,
            tooltip: 'show',
        });
        // Initialize time series line width slider
        this.lineWidthSlider = $('#ts-width-slider');
        this.lineWidthSlider.slider({
            min: 0.5,
            max: 10,
            step: 0.1,
            value: 2,
            tooltip: 'show',
        });
        // Initialize time series line width slider
        this.timePointLineWidthSlider = $('#timepoint-width-slider');
        this.timePointLineWidthSlider.slider({
            min: 1,
            max: 10,
            step: 1,
            value: this.timePointMarkerState['width'],
            tooltip: 'show',
        });
        // Initialize time point marker opacity slider
        this.timePointOpacitySlider = $('#timepoint-opacity-slider');
        this.timePointOpacitySlider.slider({
            min: 0,
            max: 1,
            step: 0.01,
            value: this.timePointMarkerState['opacity'],
            tooltip: 'show',
        });

        // Initialize time course plot option listeners
        this.initializeTimeCoursePlotOptions();
        // Initialize the color change listener once the card is loaded
        this.initializeColorChangeListener();
        // Initialize time marker plot option listeners
        this.initializeTimeMarkerPlotOptions();
        // Initialize switches
        this.initializeSwitches();
        // Initialize preprocessing time course selection menu
        this.initializeTimeCoursePrepSelect();
        // Initialize selection menu in analysis modals
        this.updateAnalysisMenu();
        // Initialize peak finder popup
        this.initializePeakFinderPopup();
        // Get preprocessing button
        this.preprocessSubmit = $('#ts-submit-preprocess');
        // Initialize preprocessing submit listener
        this.preprocessSubmit.on(
            'click', this.handlePreprocessingButton.bind(this)
        );
        // Get reset button
        this.resetPreprocessButton = $('#ts-reset-preprocess');
        // Initialize reset preprocess button listener
        this.resetPreprocessButton.on(
            'click', this.handleResetPreprocess.bind(this)
        );

        // initialize time marker toggle listener
        $('#toggle-time-marker').on('click', (event) => {
            // if checked
            this.timePointMarker = !this.timePointMarker;
            // plot with or without time point marker
            this.plotTimeCourses(this.timePoint);
        });

        // initialize grid toggle listener
        $('#toggle-grid').on('click', (event) => {
            // if checked
            this.plotGridLine = !this.plotGridLine;
            // plot with or without grid
            this.plotTimeCourses(this.timePoint);
        });

        // Initialize hover toggle listener
        $('#toggle-ts-hover').on('click', (event) => {
            // if checked
            this.plotHoverText = !this.plotHoverText;
            // plot with or without grid
            this.plotTimeCourses(this.timePoint);
        });

        // set max and min of lag input in analysis modal
        const timeLengthMid = Math.floor(this.timeLength / 2);
        document.getElementById('correlateNegativeLag').min = -timeLengthMid;
        document.getElementById('correlatePositiveLag').max = timeLengthMid;
        document.getElementById('averageLeftEdge').min = -timeLengthMid;
        document.getElementById('averageRightEdge').max = timeLengthMid;

        // set up listener on average modal show to ensure annotations are present
        $( "#averageModal" ).on('show.bs.modal', () => {
            // raise alert if no annotation markers present
            if (this.annotationMarkers.length < 1) {
                document.getElementById('no-annotation-message-average').style.display = 'block';
                // disable submit button
                $('#runAverage').prop('disabled', true);

            } else {
                document.getElementById('no-annotation-message-average').style.display = 'none';
                $('#runAverage').prop('disabled', false);
            }
        });

        // if task regressors are passed, set up listeners
        if (this.taskDesignInput) {
            // initialize plot of block or hrf convolved task regressors
            $('#toggle-convolution').on('click', (event) => {
                // toggle b/w 'block' and 'hrf' task regressors
                this.taskPlotType = this.taskPlotType == 'hrf' ? 'block' : 'hrf'
                // update correlation selection menu
                this.updateAnalysisMenu();
                // plot with or without grid
                this.plotTimeCourses(this.timePoint);
            });

            // initialize button to increase task regressor scale
            $('#task-increase-scale').on('click', (event) => {
                // increase scale of task regressors by * 2
                 for (let taskReg of this.taskRegressors) {
                    const scaledTaskHRF = taskReg['hrf'].map(
                        x => x * 2
                    )
                    taskReg['hrf'] = scaledTaskHRF;
                    const scaledTaskBlock = taskReg['block'].map(
                        x => x * 2
                    )
                    taskReg['block'] = scaledTaskBlock;
                }
                // plot with rescaled task regressors
                this.plotTimeCourses(this.timePoint);
            });

            // initialize button to decrease task regressor scale
            $('#task-decrease-scale').on('click', (event) => {
                // decrease scale of task regressors by / 2
                for (let taskReg of this.taskRegressors) {
                    const scaledTaskHRF = taskReg['hrf'].map(x => x / 2)
                    taskReg['hrf'] = scaledTaskHRF
                    const scaledTaskBlock = taskReg['block'].map(x => x / 2)
                    taskReg['block'] = scaledTaskBlock
                }
                // plot with rescaled task regressors
                this.plotTimeCourses(this.timePoint);
            });

        } else {
            // if no task design file input, disable menu icons
            $('#toggle-convolution').addClass('disabled');
            $('#task-increase-scale').addClass('disabled');
            $('#task-decrease-scale').addClass('disabled');
        }
    }

    // Initialize time course select
    initializeTimeCoursePlotOptions() {
        // get time course select dropdown
        const tsSelectMenu = document.getElementById('ts-select');

        // Loop through timecourses and append label to select dropdown menu
        for (let ts of this.timeCourses) {
            const label = ts['name'];
            let opt = document.createElement('option');
            opt.value = label;
            opt.textContent = label;
            // set 'data-type' attribute to recognize as 'time course' or 'task'
            opt.setAttribute('data-type', 'ts');
            tsSelectMenu.appendChild(opt);
        };

        // Loop through task labels and append to select dropdown menu
        for (let task of this.taskRegressors) {
            const label = task['name'];
            let opt = document.createElement('option');
            opt.value = label;
            opt.textContent = label;
            // set 'data-type' attribute to recognize as 'time course' or 'task'
            opt.setAttribute('data-type', 'task');
            tsSelectMenu.appendChild(opt);
        };

        // Fill in options with current ts selection, if any input passed
        if (this.userInput) {
            this.refreshTimeCourseOptions();
        }

        // Listen for time course selections
        tsSelectMenu.addEventListener('change', (event) =>
            this.handleTimeCourseSelection(event)
        )
        // Listen for line marker selections
        const lineMarkerMenu = document.getElementById('ts-marker-select');
        lineMarkerMenu.addEventListener('change', (event) =>
            this.handleLineMarkerSelection(event)
        )

        // Listen for opacity slider change
        this.opacitySlider.on('change', this.handleOpacitySliderChange.bind(this));

        // Listen for linewidth slider change
        this.lineWidthSlider.on(
            'change', this.handleLineWidthSliderChange.bind(this)
        );

    }

    // Initialize color change listener in time course plot options
    initializeColorChangeListener() {
        // Time course color change listener
        const colorSelect = document.getElementById('ts-color-select');
        colorSelect.addEventListener('change', (event) => {
            // get current time course selection and index
            const tsSelectMenu = document.getElementById('ts-select');
            const currentSelect = tsSelectMenu.value;
            const currentIndx = tsSelectMenu.selectedIndex;
            // check whether it's a time course or task regression
            const optionType = tsSelectMenu.options[currentIndx].dataset.type;
            if (optionType == 'ts') {
                const selectedTS = this.selectObjectFromArray(
                    this.timeCourses, currentSelect, 'name'
                );
                // Update the selected color, if there is anything to plot
                if (selectedTS) {
                    // change color and replot
                    selectedTS['color'] = event.target.value;
                    this.plotTimeCourses(this.timePoint)
                }
            } else if (optionType == 'task') {
                const selectedTS = this.selectObjectFromArray(
                    this.taskRegressors, currentSelect, 'name'
                );
                // Update the selected color, if there is anything to plot
                if (selectedTS) {
                    // change color and replot
                    selectedTS['color'] = event.target.value;
                    this.plotTimeCourses(this.timePoint)
                }
            }
        });
    }

    // initialize time marker plot option panel listeners
    initializeTimeMarkerPlotOptions() {
        // Time marker color selection
        const colorSelect = document.getElementById('timepoint-color-select');
        colorSelect.value = this.timePointMarkerState['color'];
        // Time marker color change listener
        colorSelect.addEventListener('change', (event) => {
            const color = event.target.value;
            this.timePointMarkerState['color'] = color;
            // replot with new marker color
            this.plotTimeCourses(this.timePoint)
        });

        // Time marker shape change listener
        const shapeSelect = document.getElementById('timepoint-marker-select');
        shapeSelect.value = this.timePointMarkerState['shape'];
        shapeSelect.addEventListener('change', (event) => {
            const shape = event.target.value;
            this.timePointMarkerState['shape'] = shape;
            // replot with new marker shape
            this.plotTimeCourses(this.timePoint)
        });

        // Time marker line width listener
        const lineWidthSlider = $('#timepoint-width-slider');
        lineWidthSlider.on('change', (event) => {
            const lineWidthValue = event.value;
            this.timePointMarkerState['width'] = lineWidthValue.newValue;
            // replot with new line width
            this.plotTimeCourses(this.timePoint)
        });

        // Time marker opacity listener
        const opacitySlider = $('#timepoint-opacity-slider');
        opacitySlider.on('change', (event) => {
            const opacityValue = event.value;
            this.timePointMarkerState['opacity'] = opacityValue.newValue;
            // replot with new opacity
            this.plotTimeCourses(this.timePoint)
        });
    }

    // Initalize normalize and filter switches
    initializeSwitches() {
        // Enable normalization switch
        const enableNormalization = $('#ts-enable-normalization')
        enableNormalization.on('click', () => {
            this.normSwitchEnabled = !this.normSwitchEnabled
            const inputs_norm = document.querySelectorAll('input.ts-norm-option');
            inputs_norm.forEach(
                input => this.normSwitchEnabled ? input.disabled = false : input.disabled = true
            );
        });

        // Enable filtering switch
        const enableFiltering = $('#ts-enable-filtering')
        enableFiltering.on('click', () => {
            this.filterSwitchEnabled = !this.filterSwitchEnabled
            const inputs_filter = document.querySelectorAll(
                'input.ts-filter-option'
            );
            inputs_filter.forEach(
                input => this.filterSwitchEnabled ? input.disabled = false : input.disabled = true
            );
        });

        // Enable annotation enable switch
        $('#enable-annotate').on('click', () => {
            this.annotateState = this.annotateState ? false : true
            // if annotation enabled, enable annotation buttons
            if (this.annotateState){
                $('#left-move-annotate').prop('disabled', false);
                $('#right-move-annotate').prop('disabled', false);
                $('#highlight-annotate').prop('disabled', false);
                $('#undo-annotate').prop('disabled', false);
                $('#remove-annotate').prop('disabled', false);
                $('#peak-finder-popover').prop('disabled', false);
            } else {
                $('#left-move-annotate').prop('disabled', true);
                $('#right-move-annotate').prop('disabled', true);
                $('#highlight-annotate').prop('disabled', true);
                $('#undo-annotate').prop('disabled', true);
                $('#remove-annotate').prop('disabled', true);
                $('#peak-finder-popover').prop('disabled', true);
            }
        });
    }

    // initialize time course preprocessing selection menu event
    initializeTimeCoursePrepSelect() {
        const timeCoursePrepMenu = $('#ts-norm-select')
        // Loop through time courses and append label to select dropdown menu
        for (let ts of this.timeCourses) {
            const label = ts['name'];
            let newOption = $('<option>', { value: label, text: label });
            timeCoursePrepMenu.append(newOption);
        };
        // hack to remove duplicates due to bug
        //https://github.com/snapappointments/bootstrap-select/issues/2738
        timeCoursePrepMenu.selectpicker('destroy');
        timeCoursePrepMenu.selectpicker();
    }

    // Initialize annotation marker listeners
    initializeAnnotationListener() {
        // plotly annotation mark event
        document.getElementById(this.plotId).on('plotly_click', (eventData) => {
            if (this.annotateState) {
                const x = Math.round(eventData.points[0].x);
                // only add if not already present
                if (!this.annotationMarkers.includes(x)) {
                    this.annotationMarkers.push(x);
                    // set annotation selection as current selection
                    this.annotationSelection = x;
                }
                this.plotTimeCourses(this.timePoint);
            };
        });

        // Hide annotation selection highlight toggle
        $('#highlight-annotate').on('click', () => {
            this.annotationSelectionHighlight = this.annotationSelectionHighlight ? false : true;
            // plot time course with/without annotation highlight
            this.plotTimeCourses(this.timePoint);
        });

        // utility function to select annotation highlight in circular approach
        function circularAnnotateSelect(markers, selection, move) {
            // sort before indexing so we can index left to right
            const markersSort = markers.toSorted();
            let selectIndx = markersSort.indexOf(selection);
            if (move == 'right') {
                selectIndx += 1;
            } else if (move == 'left') {
                selectIndx -= 1;
            }
            // circularIndex from utils.js
            const newIndx = circularIndex(markersSort, selectIndx);
            return markersSort[newIndx];
        }

        // move current annotation selection to right
        $('#right-move-annotate').on('click', () => {
            // if no annotation markers, do nothing
            if (this.annotationMarkers.length == 0) {
                return
            }

            this.annotationSelection = circularAnnotateSelect(
                this.annotationMarkers, this.annotationSelection, 'right'
            )
            // Plot with highlight
            this.plotTimeCourses(this.timePoint);

            // update time point on slider
            this.timeSliderElement.slider('setValue',this.annotationSelection, true, true);
        })

        // move current annotation selection to left
        $('#left-move-annotate').on('click', () => {
            // if no annotation markers, do nothing
            if (this.annotationMarkers.length == 0) {
                return
            }

            this.annotationSelection = circularAnnotateSelect(
                this.annotationMarkers, this.annotationSelection, 'left'
            )
            // Plot with highlight
            this.plotTimeCourses(this.timePoint);

            // update time point on slider
            this.timeSliderElement.slider('setValue', this.annotationSelection, true, true);
        })

        // undo most recent annotation
        $('#undo-annotate').on('click', () => {
            // get current selection index
            const selectIndx = this.annotationMarkers.indexOf(this.annotationSelection);
            // If the to-be removed annotation is the last selected index, reselect to left
            if (selectIndx == (this.annotationMarkers.length - 1)) {
                // only select, if there will be any annotations left
                if (this.annotationMarkers.length > 1) {
                    this.annotationSelection = circularAnnotateSelect(
                        this.annotationMarkers, this.annotationSelection, 'left'
                    )
                }
            }
            // remove last selected annotation
            this.annotationMarkers.pop();
            // plot without most recent annotation marker
            this.plotTimeCourses(this.timePoint);
        })

        // remove all annotations
        $('#remove-annotate').on('click', () => {
            this.annotationMarkers = [];
            this.plotTimeCourses(this.timePoint);
        })
    }

    // update correlation select menu
    updateAnalysisMenu() {
        // Get the select menu
        const correlateSelectMenu = document.getElementById('ts-correlate-select')

        // Clear existing options
        correlateSelectMenu.innerHTML = '';

        // Populate select menu with time courses
        for (let ts of this.timeCourses) {
            const option = document.createElement('option');
            const label = ts['name'];
            option.value = label;
            if (ts['preprocessed']) {
                option.textContent = `${label} [Preprocessed]`;
                option.dataset.preprocessed = true;
            } else {
                option.textContent = label;
                option.dataset.preprocessed = false;
            }
            // set type as ts
            option.dataset.type = 'ts';
            correlateSelectMenu.appendChild(option);
        }

        // Populate select menu with task regressors
        for (let task of this.taskRegressors) {
            const option = document.createElement('option');
            const label = task['name'];
            option.value = label;
            option.textContent = `${label} [${this.taskPlotType}]`;
            // set type as task
            option.dataset.type = 'task';
            option.dataset.plotType = this.taskPlotType;
            correlateSelectMenu.appendChild(option);
        }
    }

    initializePeakFinderPopup() {
        // initialize tooltips on popup show
        $('#peak-finder-popover').on('shown.bs.popover', () => {
            const popoverContent = $('.popover');
            popoverContent.find('.toggle-immediate').tooltip({
                html: true, // Enable HTML content in the tooltip
                trigger : 'hover'
            });
            // get select menu from correlation modal and replicate in popup
            const correlateSelectMenu = document.getElementById('ts-correlate-select');
            const peakFinderSelectDiv = document.getElementById('ts-peak-select-container');

            const clonedMenu = correlateSelectMenu.cloneNode(true);
            clonedMenu.id = "ts-peak-select";

            // Append the cloned dropdown to the target element
            peakFinderSelectDiv.appendChild(clonedMenu);

            // Hide popover when clicking outside
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest('.popover, #peak-finder-popover').length) {
                  $('#peak-finder-popover').popover('hide');
                }
            });

            // initialize peak finder submit
            $('#peakFinderForm').on(
                'submit', this.handlePeakFinderSubmit.bind(this)
            );
        })
    }


    // refresh time course option card
    refreshTimeCourseOptions(tsSelect=null, tsIndx=null) {
        // initialize selection variables
        let currentSelect
        let optionType
        // get time course select dropdown
        const tsSelectMenu = document.getElementById('ts-select');
        if (!tsSelect) {
            currentSelect = tsSelectMenu.value;
            // get option type (time course vs task)
            const currentIndx = tsSelectMenu.selectedIndex;
            optionType = tsSelectMenu.options[currentIndx].dataset.type;
        } else {
            currentSelect = tsSelect;
            optionType = tsSelectMenu.options[tsIndx].dataset.type;
        }

        // based on type, select timecourses or task regressors
        let timeCourse
        if (optionType == 'ts') {
            timeCourse = this.timeCourses;
        } else if (optionType == 'task') {
            timeCourse = this.taskRegressors;
        }
        tsSelect = this.selectObjectFromArray(timeCourse, currentSelect, 'name');
        // get ts color dropdown
        const tsColorSelect = document.getElementById('ts-color-select');
        tsColorSelect.value = tsSelect['color'];
        // set line marker dropdown
        const tsMarkerSelect = document.getElementById('ts-marker-select');
        tsMarkerSelect.value = tsSelect['mode'];
        // set value for opacity slider
        const tsOpacity = tsSelect['opacity'];
        this.opacitySlider.slider('setValue', tsOpacity);
        // set value for line width slider
        const tsLineWidth = tsSelect['width'];
        this.lineWidthSlider.slider('setValue', tsLineWidth);
    }


    // update or add fmri time course and replot
    updatefMRITimeCourse(timeCourse, timeCourseLabel, freezeState) {
        // if an fmri time course is already displayed, and fmri time course plotting
        // is not frozen delete most recent fmri time course
        if (!freezeState) {
            this.removeMostRecentTimeCourse();
        }
        // insert fmri time course in timeCourse object
        this.timeCourses.push({
            name: timeCourseLabel,
            ts: timeCourse,
            type: 'fmri',
            preprocessed: false,
            ts_prep: null,
            color: this.colorOptions.shift(),
            plot: true,
            opacity: 1,
            width: 2,
            mode: 'lines+markers'
        });
        // increase number of time courses by 1
        this.timeCoursesN += 1;
        // add new time course selection dropdown
        const tsSelectMenu = document.getElementById('ts-select');
        let opt = document.createElement('option');
        opt.value = timeCourseLabel;
        opt.textContent = timeCourseLabel;
        opt.setAttribute('data-type', 'ts');
        tsSelectMenu.appendChild(opt);

         // add fmri time course to preprocessing selection dropdown
        const timeCoursePrepMenu = $('#ts-norm-select')
        let fmriOption = $('<option>', { value: timeCourseLabel, text: timeCourseLabel });
        timeCoursePrepMenu.append(fmriOption);
        // hack to remove duplicates due to bug
        //https://github.com/snapappointments/bootstrap-select/issues/2738
        timeCoursePrepMenu.selectpicker('destroy');
        timeCoursePrepMenu.selectpicker();

        // Refresh analysis menu
        this.updateAnalysisMenu();
        // plot new fmri time course
        this.plotTimeCourses(this.timePoint)
    }

    // remove most recent or all fmri time course and replot
    removefMRITimeCourse(removeAll=false) {
        // remove all, if specified
        if (removeAll) {
            while (this.removeMostRecentTimeCourse()) {
                console.log("removing fmri time course");
            }
        } else {
            const success = this.removeMostRecentTimeCourse();
            if (success) {
                console.log("removing fmri time course");
            }
        }
    }

    // utililty to remove most recent fmri time course, return to true for success
    removeMostRecentTimeCourse() {
        // get fmri time courses
        const fmriTS = this.selectFmriTimeCourse();
        // if no time courses, do nothing
        if (fmriTS.length < 1) {
            return false
        } else {
            // get most recent fMRI TS selection
            const lastFmriTS = fmriTS[fmriTS.length-1]
            // 'give back' the most recent time course's color
            this.colorOptions.unshift(lastFmriTS['color'])
            // remove fmri time course entry
            this.timeCourses = this.timeCourses.filter(
                ts => ts.name !== lastFmriTS.name
            );
            // Decrease number of time courses by 1
            this.timeCoursesN -= 1;
            // remove last option from time course selection dropdown
            $('#ts-select').find("option:last").remove();
            // remove last option from time course preprocessing dropdown
            $('#ts-norm-select').find("option:last").remove();
            return true
        }
    }

    // Method to plot the time course
    plotTimeCourses(
        timePoint
    ) {
        // update timePoint state
        this.timePoint = timePoint

        // Don't plot if no fmri time course and no input
        if ((this.timeCoursesN < 1) & !this.plotState) {
            // purge plot if there are any traces currently in the plot
            Plotly.purge(this.plotId)
            return
        }

        // initialize trace labels array
        this.traceLabels = []

        // initialize plot data
        let plotData = []
        // add input time courses to plot, if any
        for (let ts of this.timeCourses){
            // keep up with trace labels
            this.traceLabels.push({'label': ts.name, type: 'ts'})
            // whether to plot preprocessed time course
            let plotTimeCourse
            if (ts['preprocessed']) {
                plotTimeCourse = ts['ts_prep'];
            }
            else {
                plotTimeCourse = ts['ts'];
            }
            // create time course line plot
            const tsTrace = {
                x: Array.from({ length: plotTimeCourse.length }, (_, i) => i),
                y: plotTimeCourse,
                type: 'scatter',
                mode: ts['mode'],
                name: ts['name'],
                marker: { color: ts['color'] },
                line: {
                    shape: 'linear',
                    width: ts['width']
                },
                visible: ts['plot'],
                opacity: ts['opacity'],
                hoverinfo: this.plotHoverText ? 'all' : 'none'
            };
            plotData.push(tsTrace)
        }
        // add task regressors to plot, if any
        for (let task of this.taskRegressors) {
            // keep up with trace labels
            this.traceLabels.push({'label': task.name, type: 'task'});
            let plotTimeCourse = task[this.taskPlotType];
            // create time course line plot
            const tsTrace = {
                x: Array.from({ length: plotTimeCourse.length }, (_, i) => i),
                y: plotTimeCourse,
                type: 'scatter',
                mode: task['mode'],
                name: task['name'],
                marker: { color: task['color'] },
                line: {
                    shape: 'linear',
                    width: task['width']
                },
                visible: task['plot'],
                opacity: task['opacity'],
                hoverinfo: this.plotHoverText ? 'all' : 'none'
            };
            plotData.push(tsTrace)
        }
        // create vertical line object to keep up with time point
        let timePointShape = []
        if (this.timePointMarker) {
            timePointShape.push(
                {
                    type: 'line',
                    x0: timePoint,
                    y0: 0,
                    x1: timePoint,
                    y1: 1,
                    yref: 'paper',
                    opacity: this.timePointMarkerState['opacity'],
                    line: {
                        color: this.timePointMarkerState['color'],
                        width: this.timePointMarkerState['width'],
                        dash: this.timePointMarkerState['shape']
                    },
                }
            )
        }
        // create vertical line annotation markers
        for (const marker of this.annotationMarkers) {
            timePointShape.push(
                {
                    type: 'line',
                    x0: marker,
                    y0: 0,
                    x1: marker,
                    y1: 1,
                    yref: 'paper',
                    opacity: 0.5,
                    line: {
                        color: 'rgb(255, 0, 0)',
                        width: 1
                    },
                }
            )
        }
        // if highlight is true, highlight current annotation selection
        if (this.annotationSelectionHighlight && (this.annotationMarkers.length > 0)) {
            timePointShape.push(
                {
                    type: 'line',
                    x0: this.annotationSelection,
                    y0: 0,
                    x1: this.annotationSelection,
                    y1: 1,
                    yref: 'paper',
                    opacity: 0.2,
                    line: {
                        color: 'gray',
                        width: 7
                    },
                }
            )
        }

        // Create layout
        // initialize layout if first plot
        if (!this.plotState) {
            // Get length of time courses from plot data
            let timeLength = plotData[0].length
            this.plotLayout = {
                height: 500,
                xaxis: {
                    title: 'Time Point',
                    range: [0, timeLength],
                    showgrid: this.plotGridLine
                },
                yaxis: {
                    title: 'Signal Intensity',
                    showgrid: this.plotGridLine
                },
                uirevision: 999, // assign a constant value to maintain UI changes
                autosize: true,  // Enable autosizing
                responsive: true, // Make the plot responsive
                margin: {
                    l: 50,  // left margin
                    r: 30,  // right margin
                    t: 40,  // top margin
                    b: 40   // bottom margin
                },
                shapes: timePointShape,
                // always show legend, even with one trace
                showlegend: true,
                // Place legend at bottom of the plot
                legend: {
                    xanchor: 'center',     // Centers the legend horizontally
                    x: 0.5,                // Centers it in the middle (x: 50%)
                    yanchor: 'top',        // Anchors the legend to the top of its container
                    y: -0.25                // Places the legend below the plot (-0.1 moves it just below the plot)
                  }
            };
        } else {
            // leave layout intact except for modifying specific components
            // modify time point marker
            this.plotLayout['shapes'] = timePointShape;
            // modify plot grid
            this.plotLayout['xaxis']['showgrid'] = this.plotGridLine;
            this.plotLayout['yaxis']['showgrid'] = this.plotGridLine;
        }

        // Plot
        Plotly.react(this.plotId, plotData, this.plotLayout);

        // Initialize plotly legend clicks for hiding traces, if first plot
        if (!this.plotState) {
            document.getElementById(this.plotId).on(
                'plotly_legendclick', this.hideTrace.bind(this)
            )
            document.getElementById(this.plotId).on(
                'plotly_legenddoubleclick', this.hideAllTraces.bind(this)
            )
            // initialize annotation listener
            this.initializeAnnotationListener();
            // initialize resize (plot doesn't fill container on first plot)
            this.onWindowResize();
            this.plotState = true
        }
    }

    // Initialize plotly legend click (hide or unhide traces)
    hideTrace(data) {
        // get index of selected trace
        const traceIndex = data.curveNumber;
        const visibility = data.data[traceIndex].visible;
        // set new visibility value based on current value
        const visibilityNew = visibility == 'legendonly' ? true : 'legendonly'
        const traceType = this.traceLabels[traceIndex]['type'];
        let timeCourse
        if (traceType == 'ts') {
            timeCourse = this.timeCourses;
        } else if (traceType == 'task') {
            timeCourse = this.taskRegressors
        }
        const tsSelect = this.selectObjectFromArray(
            timeCourse, this.traceLabels[traceIndex]['label'], 'name'
        );
        tsSelect['plot'] = visibilityNew;
    }

    // Initialize plotly legend double click (hide all other traces)
    hideAllTraces(data) {
        // get index of selected trace
        const traceIndex = data.curveNumber;
        for (const [index, trace] of this.traceLabels.entries()) {
            let timeCourse
            if (trace['type'] == 'ts') {
                timeCourse = this.timeCourses;
            } else if (trace['type'] == 'task') {
                timeCourse = this.taskRegressors;
            }
            const tsSelect = this.selectObjectFromArray(
                timeCourse, trace['label'], 'name'
            );
            if (index == traceIndex) {
                tsSelect['plot'] = true;
            } else {
                tsSelect['plot'] = 'legendonly';
            }
        }
    }

    // Handle selections of time course selection
    handleTimeCourseSelection(event) {
        // Fill in options with current ts selection
        const currentSelect = event.target.value;
        const currentIndx = event.target.selectedIndex;
        this.refreshTimeCourseOptions(currentSelect, currentIndx);
    }

    // Handle selections of line marker type
    handleLineMarkerSelection(event) {
        // get information about selected time course
        const tsSelectMenu = document.getElementById('ts-select');
        const currentSelect = tsSelectMenu.value;
        const currentIndx = tsSelectMenu.selectedIndex;
        // check whether it's a time course or task regressor
        const optionType = tsSelectMenu.options[currentIndx].dataset.type;
        // event.target.value gives the current selected line marker value
        const lineMarker = event.target.value;
        // update line marker value, if anything to plot
        if (optionType == 'ts') {
            const selectedTS = this.selectObjectFromArray(
                this.timeCourses, currentSelect, 'name'
            );
            if (selectedTS) {
                selectedTS['mode'] = lineMarker;
                // replot with new line marker value
                this.plotTimeCourses(this.timePoint)
            }
        } else if (optionType == 'task') {
            const selectedTS = this.selectObjectFromArray(
                this.taskRegressors, currentSelect, 'name'
            );
            if (selectedTS) {
                selectedTS['mode'] = lineMarker;
                this.plotTimeCourses(this.timePoint)
            }
        }
    }

    handleOpacitySliderChange(event) {
        // get information about selected time course
        const tsSelectMenu = document.getElementById('ts-select');
        const currentSelect = tsSelectMenu.value;
        const currentIndx = tsSelectMenu.selectedIndex;
        // check whether it's a time course or task regressor
        const optionType = tsSelectMenu.options[currentIndx].dataset.type;
        // event.value gives the current slider value
        const opacityValue = event.value;
        // update opacity value, if anything to plot
        if (optionType == 'ts') {
            const selectedTS = this.selectObjectFromArray(
                this.timeCourses, currentSelect, 'name'
            );
            if (selectedTS) {
                selectedTS['opacity'] = opacityValue.newValue;
                // replot with new opacity value
                this.plotTimeCourses(this.timePoint)
            }
        } else if (optionType == 'task') {
            const selectedTS = this.selectObjectFromArray(
                this.taskRegressors, currentSelect, 'name'
            );
            if (selectedTS) {
                selectedTS['opacity'] = opacityValue.newValue;
                this.plotTimeCourses(this.timePoint)
            }
        }
    }

    handleLineWidthSliderChange(event) {
        // get information about selected time course
        const tsSelectMenu = document.getElementById('ts-select');
        const currentSelect = tsSelectMenu.value;
        const currentIndx = tsSelectMenu.selectedIndex;
        // check whether it's a time course or task regressor
        const optionType = tsSelectMenu.options[currentIndx].dataset.type;
        // event.value gives the current slider value
        const lineWidth = event.value;
        // update line width value, if anything to plot
        if (optionType == 'ts') {
            const selectedTS = this.selectObjectFromArray(
                this.timeCourses, currentSelect, 'name'
            );
            if (selectedTS) {
                selectedTS['width'] = lineWidth.newValue;
                // replot with new line width value
                this.plotTimeCourses(this.timePoint)
            }
        } else if (optionType == 'task') {
            const selectedTS = this.selectObjectFromArray(
                this.taskRegressors, currentSelect, 'name'
            );
            if (selectedTS) {
                selectedTS['width'] = lineWidth.newValue;
                this.plotTimeCourses(this.timePoint)
            }
        }
    }

    // Validate inputs and initiate normalization button event
    handlePreprocessingButton(event) {
        // Get error message div
        let errorDiv = document.getElementById('ts-error-message-preprocess');
        // Clear previous error message
        errorDiv.style.display = 'none';
        // Initialize error message
        let errorMessage

        // Check whether any time course is selected
        const timeCoursePrepMenu = $('#ts-norm-select')
        const tsSelect = timeCoursePrepMenu.val();
        if (tsSelect.length < 1) {
            errorMessage = 'Please select at least one time course';
            preprocessingInputError(errorDiv, errorMessage);
            return
        }
        // Check normalization options
        const meanCenter = document.getElementById('ts-select-mean-center').checked
        const zScore = document.getElementById('ts-select-z-score').checked
        if (this.normSwitchEnabled) {
            // make sure an option has been provided
            if (!meanCenter && !zScore) {
                errorMessage = 'If normalization is enabled, mean-center or z-score option must be selected';
                preprocessingInputError(errorDiv, errorMessage);
                return
            }
        }

        // Check filter options
        const TR = document.getElementById('ts-filter-tr').value
        const lowCut = document.getElementById('ts-filter-low-cut').value
        const highCut = document.getElementById('ts-filter-high-cut').value
        let filterParamsOK = false
        if (this.filterSwitchEnabled) {
            // Validate inputs
            filterParamsOK = validateFilterInputs(
                TR, lowCut, highCut, errorDiv
            )
            if (!filterParamsOK) {
                return
            }
        }

        // If no options selected, return error message
        if (!meanCenter && !zScore && TR == '' && lowCut == '' && highCut == '') {
            errorMessage = 'No preprocessing options selected';
            preprocessingInputError(errorDiv, errorMessage);
            return
        }

        // package parameters for POST request
        const jsonOut = {
            tsLabels: tsSelect,
            normalize: this.normSwitchEnabled,
            filter: this.filterSwitchEnabled,
            meanCenter,
            zScore,
            TR,
            lowCut,
            highCut
        };

        // Send to preprocessing route and re-plot
        fetch('/preprocess_ts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',  // Sending JSON data
            },
            body: JSON.stringify({ data: jsonOut })  // Converting array to JSON format
        })
        .then(response => response.json())
        .then(data => {
            // loop through preprocessed time courses and update
            for (let ts in data) {
                const timeCourse = this.selectObjectFromArray(this.timeCourses, ts, 'name');
                // set time course as preprocessed
                timeCourse['preprocessed'] = true;
                // store preprocessed time course
                timeCourse['ts_prep'] = data[ts];
            }
            // plot time course
            this.plotTimeCourses(this.timePoint);

            // refresh analysis menu
            this.updateAnalysisMenu();

            // Turn on preprocess alert
            document.getElementById('ts-preprocess-alert').style.display = 'block';
        })
        .catch(error => {
            console.error('Error preprocessing time courses:', error);
            alert('Error preprocessing time courses');
        });
    }

    // initiate reset preprocessing event
    handleResetPreprocess() {
        // Get error message div
        let errorDiv = document.getElementById('ts-error-message-preprocess');
        // Clear previous error message, if any
        errorDiv.style.display = 'none';
        // Set switches to disabled
        document.getElementById('ts-enable-normalization').checked = false
        document.getElementById('ts-enable-filtering').checked = false
        this.filterSwitchEnabled = false
        this.normSwitchEnabled = false

        // Clear parameters
        document.getElementById('ts-select-mean-center').checked = false
        document.getElementById('ts-select-z-score').checked = false
        document.getElementById('ts-filter-tr').value = ''
        document.getElementById('ts-filter-low-cut').value = ''
        document.getElementById('ts-filter-high-cut').value = ''

        // clear all preprocessed time courses, if time courses plotted
        if (this.timeCourses.length > 0) {
            for (let ts of this.timeCourses) {
                ts['preprocessed'] = false;
                ts['ts_prep'] = null;
            }
        }

        // Refresh plot
        this.plotTimeCourses(this.timePoint)

        // refresh analysis menu
        this.updateAnalysisMenu();

        // turn off preprocess alert
        document.getElementById('ts-preprocess-alert').style.display = 'none';
    }

    // trigger 'averege' analysis event
    handleAverageSubmit() {
        event.preventDefault(); // Prevent form submission and page reload
        // trigger 'analysis' submission event
        // remove any duplicates from tagging
        const dataOut = {markers: [...new Set(this.annotationMarkers)]}
        $(document).trigger('averageSubmit', dataOut);
    }

    // gather data from correlation analysis form upon submit
    handleCorrelationSubmit() {
        event.preventDefault(); // Prevent form submission and page reload
        // get time course selection value
        const tsSelect = $('#ts-correlate-select :selected');
        const [label, ts] = this.selectTimeCourseMenu(tsSelect);
        // initialize data out object
        const dataOut = {};
        dataOut['label'] = label;
        dataOut['ts'] = ts;

        // trigger 'correlation' submission event
        $(document).trigger('correlationSubmit', dataOut);
    }

    handlePeakFinderSubmit() {
        // hide popover
        $('#peak-finder-popover').popover('hide');
        // prevent reload
        event.preventDefault();
        // get peak finder parameters
        let formData = new FormData();
        formData.append('peak_height', document.getElementById('peak-height').value);
        formData.append('peak_threshold', document.getElementById('peak-threshold').value);
        formData.append('peak_distance', document.getElementById('peak-distance').value);
        formData.append('peak_prominence', document.getElementById('peak-prominence').value);
        formData.append('peak_width', document.getElementById('peak-width').value);
        // get time course selection value
        const tsSelect = $('#ts-peak-select :selected');
        const [label, ts] = this.selectTimeCourseMenu(tsSelect);
        formData.append('ts',  JSON.stringify(ts));

        // pass parameters and ts to flask peak finder route
        fetch('/find_peaks_ts', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // check if any peaks were detected
            debugger;
            if (data.peaks.length > 0) {
                // set all detected peaks as annotation markers
                this.annotationMarkers.push(...data.peaks);
                // set annotation selection as last element of list
                this.annotationSelection = data.peaks[data.peaks.length - 1];
            }
            // replot with new annotation markers
            this.plotTimeCourses(this.timePoint);
        })
        .catch(error => {
            console.error('Error during peak finding analysis:', error);
        });
    }

    selectTimeCourseMenu(tsSelect) {
        const tsValue = tsSelect.val()
        const tsLabel = tsSelect.text();
        const tsType = tsSelect[0].dataset.type;
        // initialize data out object
        const label = tsValue;
        // get time course or task regressor
        let ts
        if (tsType == 'ts') {
            const timeCourse = this.selectObjectFromArray(
                this.timeCourses, tsValue, 'name'
            );
            if (tsSelect[0].dataset.preprocessed === 'true') {
                ts = timeCourse['ts_prep'];
            } else {
                ts = timeCourse['ts'];
            }
        } else if (tsType == 'task') {
            const plotType = tsSelect[0].dataset.plotType;
            const timeCourse = this.selectObjectFromArray(
                this.taskRegressors, tsValue, 'name'
            );
            ts = timeCourse[plotType];
        }
        return [label, ts]
    }

    // Resize time course plots with window changes
    onWindowResize() {
        Plotly.Plots.resize(document.getElementById(this.plotId));
    }

    // utility function to select object from array of objects based on label
    selectObjectFromArray(array, label, key) {
        let foundObj = null
        for (const obj of array) {
            if (obj[key] == label) {
                foundObj = obj;
            }
        }
        return foundObj
    }

    // utility function to select fmri time courses from time course array
    selectFmriTimeCourse() {
        let fmriTS = [];
        for (let ts of this.timeCourses){
            if (ts['type'] == 'fmri') {
                fmriTS.push(ts)
            }
        };
        return fmriTS
    }

}


export default TimeCourse
