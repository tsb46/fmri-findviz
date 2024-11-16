// timecourse.js

// Import filter parameter validation
import { validateFilterInputs, preprocessingInputError } from './utils.js';

class TimeCourse {
    constructor(
        timeLength,
        timeCourses=null,
        timeCourseLabels=null,
        taskConditions=null
    ) {
        this.timeLength = timeLength;
        // get time plot container
        this.timeCourseContainer = document.getElementById(
            'time-course-plot-container'
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
            this.timeCourseContainer.style.display = 'block'
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
        // initilialize time course container
        this.timeCourses = {}
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
                this.timeCourses[timeCourseLabels[index]] = {
                    // trace name in plot
                    name: timeCourseLabels[index],
                    // time course
                    ts: timeCourse,
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
                }
            }
        }
        // initialize task regressors container
        this.taskRegressors = {}
        // if task design file passed, store regressors and attributes
        if (this.taskDesignInput) {
            // Loop through task conditions and assign properties
            for (const [index, cLabel] of taskConditions.labels.entries()) {
                // start index over if loop index exceeds color list length
                colorIndex = index % this.colorOptions.length
                this.taskRegressors[cLabel] = {
                    // trace name in plot
                    name: `Task: ${cLabel}`,
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
                }
            }
        }
        // create proxies for task regressors and time courses to catch updates
        this.initializeProxyHandlers()
        // get time course plot div
        this.plotId = 'ts-plot';
        // Flag to track if fmri time course generation is enabled
        this.fmriEnabled = false;
        // initialize time point state variable
        this.timePoint = 0;
        // Set states of preprocessing switches
        this.normSwitchEnabled = false
        this.filterSwitchEnabled = false
        // set plot state
        this.plotState = false;
        // initialize task design plot state
        this.taskPlotState = true;
        // Initialize annotation state
        this.annotateState = false;
        // Annotation markers
        this.annotationMarkers = [];
        // initialize task plot type - hrf vs block
        this.taskPlotType = 'hrf';
        // initialize time point marker as true
        this.timePointMarker = true;
        // initialize grid line markers as true
        this.plotGridLine = true;
        // Initialize plot layout as null
        this.plotLayout = null;
        // initialize fmri time course switch listener
        this.initializefMRISwitch();
        // Initialize user options
        this.initializeOptions();
        // Initialize correlation analysis submission event
        $('#correlationForm').on(
            'submit', this.handleCorrelationSubmit.bind(this)
        );
        // Add event listener for window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    // Initialize time course user options
    initializeOptions() {
        this.opacitySlider = $('#ts-opacity-slider');
        // Initialize opacity slider
        this.opacitySlider.slider({
            min: 0,
            max: 1,
            step: 0.01,
            value: 1,
            tooltip: 'show',
        });
        // Initialize line width slider
        this.lineWidthSlider = $('#ts-width-slider');
        // Initialize opacity slider
        this.lineWidthSlider.slider({
            min: 0.5,
            max: 10,
            step: 0.1,
            value: 2,
            tooltip: 'show',
        });
        // Initialize time course selection listener
        this.initializeTimeCourseSelect();
        // Initialize the color change listener once the card is loaded
        this.initializeColorChangeListener();
        // Initialize switches
        this.initializeSwitches();
        // Initialize preprocessing time course selection menu
        this.initializeTimeCoursePrepSelect();
        // Initialize selection menu
        this.updateCorrelateMenu();
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

        // initialize time marker icon button listener
        $('#toggle-time-marker').on('click', (event) => {
            // if checked
            this.timePointMarker = !this.timePointMarker;
            // plot with or without time point marker
            this.plotTimeCourses(this.timePoint);
        });

        // initialize plot grid button listener
        $('#toggle-grid').on('click', (event) => {
            // if checked
            this.plotGridLine = !this.plotGridLine;
            // plot with or without grid
            this.plotTimeCourses(this.timePoint);
        });

        // set max and min of lag input in correlation modal
        const timeLengthMid = Math.floor(this.timeLength / 2);
        document.getElementById('correlateNegativeLag').min = -timeLengthMid;
        document.getElementById('correlatePositiveLag').max = timeLengthMid;

        // if task regressors are passed, set up listeners
        if (this.taskDesignInput) {
            // initialize plot of block or hrf convolved task regressors
            $('#toggle-convolution').on('click', (event) => {
                // toggle b/w 'block' and 'hrf' task regressors
                this.taskPlotType = this.taskPlotType == 'hrf' ? 'block' : 'hrf'
                // update correlation selection menu
                this.updateCorrelateMenu();
                // plot with or without grid
                this.plotTimeCourses(this.timePoint);
            });

            // initialize button to increase task regressor scale
            $('#task-increase-scale').on('click', (event) => {
                // increase scale of task regressors by * 2
                 for (let label in this.taskRegressors) {
                    const scaledTaskHRF = this.taskRegressors[label]['hrf'].map(
                        x => x * 2
                    )
                    this.taskRegressors[label]['hrf'] = scaledTaskHRF;
                    const scaledTaskBlock = this.taskRegressors[label]['block'].map(
                        x => x * 2
                    )
                    this.taskRegressors[label]['block'] = scaledTaskBlock;
                }
                // plot with rescaled task regressors
                this.plotTimeCourses(this.timePoint);
            });

            // initialize button to decrease task regressor scale
            $('#task-decrease-scale').on('click', (event) => {
                // decrease scale of task regressors by / 2
                 for (let label in this.taskRegressors) {
                    const scaledTaskHRF = this.taskRegressors[label]['hrf'].map(
                        x => x / 2
                    )
                    this.taskRegressors[label]['hrf'] = scaledTaskHRF
                    const scaledTaskBlock = this.taskRegressors[label]['block'].map(
                        x => x / 2
                    )
                    this.taskRegressors[label]['block'] = scaledTaskBlock
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

    // Initialize the button to enable/disable time course plotting
    initializefMRISwitch() {
        const enableSwitch = document.getElementById('enable-time-course');
        enableSwitch.addEventListener('click', () => {
            this.fmriEnabled = !this.fmriEnabled;
            // If there is no input data, hide the time point container
            if (!this.userInput) {
                this.timeCourseContainer.style.display = this.fmriEnabled ? 'block' : 'none';
            }
            // clear fmri time courses if disabled
            if (!this.fmriEnabled) {
                // check whether a time course has been selected in the viewer
                if ('fmri' in this.timeCourses) {
                    // 'give back' the color used by fmri time course
                    this.colorOptions.unshift(this.timeCourses['fmri']['color'])
                    // delete fmri time course from time course object
                    delete this.timeCourses['fmri']
                    // remove fmri time course from selection menu
                    const tsSelectMenu = document.getElementById('ts-select');
                    // Find the option with the matching value using querySelector
                    let fmriOptionSelect = tsSelectMenu.querySelector(
                        'option[value="fmri"]'
                    );
                    // if found, remove
                    if (fmriOptionSelect) {
                        fmriOptionSelect.remove();
                    }
                    // remove fmri time course from preprocessing menu
                    let fmriOptionPrep = this.timeCoursePrepMenu.find(
                        "option[value='fmri']"
                    );
                    // if found, remove
                    if (fmriOptionPrep) {
                        fmriOptionPrep.remove();
                        // hack to remove duplicates due to bug
                        //https://github.com/snapappointments/bootstrap-select/issues/2738
                        this.timeCoursePrepMenu.selectpicker('destroy');
                        this.timeCoursePrepMenu.selectpicker();
                    }
                    // refresh time coure options with fmri ts removed, if time courses were passed
                    if (this.timeCourseInput) {
                        this.refreshTimeCourseOptions();
                    }
                    // replot without fmri time course
                    this.plotTimeCourses(this.timePoint);
                }
            }
        });
    }

    // Initialize time course select
    initializeTimeCourseSelect() {
        // get time course select dropdown
        const tsSelectMenu = document.getElementById('ts-select');
        // get time course labels
        const tsLabels = Object.keys(this.timeCourses);
        // Loop through ts labels and append to select dropdown menu
        tsLabels.forEach(label => {
            let opt = document.createElement('option');
            opt.value = label;
            opt.textContent = label;
            // set 'data-type' attribute to recognize as 'time course' or 'task'
            opt.setAttribute('data-type', 'ts');
            tsSelectMenu.appendChild(opt);
        });

        // get task condition labels
        const taskLabels = Object.keys(this.taskRegressors);
        // Loop through task labels and append to select dropdown menu
        taskLabels.forEach(label => {
            let opt = document.createElement('option');
            opt.value = label;
            opt.textContent = label;
            // set 'data-type' attribute to recognize as 'time course' or 'task'
            opt.setAttribute('data-type', 'task');
            tsSelectMenu.appendChild(opt);
        });

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

    // Initialize color change listener
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
                // Update the selected color, if there is anything to plot
                if (currentSelect in this.timeCourses) {
                    this.timeCourses[currentSelect]['color'] = event.target.value;
                    // replot with new color
                    this.plotTimeCourses(this.timePoint)
                }
            } else if (optionType == 'task') {
                // Update the selected color, if there is anything to plot
                if (currentSelect in this.taskRegressors) {
                    this.taskRegressors[currentSelect]['color'] = event.target.value;
                    // replot with new color
                    this.plotTimeCourses(this.timePoint)
                }
            }
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
    }

    // initialize time course preprocessing selection menu event
    initializeTimeCoursePrepSelect() {
        this.timeCoursePrepMenu = $('#ts-norm-select')
        // get time course labels
        const tsLabels = Object.keys(this.timeCourses);

        // Loop through ts labels and create an option element
        tsLabels.forEach(label => {
            let newOption = $('<option>', { value: label, text: label });
            this.timeCoursePrepMenu.append(newOption);
        });
        // hack to remove duplicates due to bug
        //https://github.com/snapappointments/bootstrap-select/issues/2738
        this.timeCoursePrepMenu.selectpicker('destroy');
        this.timeCoursePrepMenu.selectpicker();
    }

    // initialize proxy handles to catch updates timecourses
    initializeProxyHandlers() {
        const handler = {
            set: (target, property, value) => {
                const isNewKey = !(property in target);
                target[property] = value;

                // catch when fmri time course is added
                if (isNewKey) {
                    this.updateCorrelateMenu();
                }
                // If preprocessing is performed on timeCourses, update the selection
                // to reflect the timecourse is preprocessed
                else if (property === 'preprocessed') {
                    this.updateCorrelateMenu();
                }

                return true;
            },
            // catch when fMRI time course is removed
            deleteProperty: (target, property) => {
                if (property in target) {
                    delete target[property];
                    // Update the menu when a key is deleted
                    this.updateCorrelateMenu();
                }
                return true;
            }
        };

        // Helper function to create recursive proxies
        const createProxy = (obj) => {
            for (const key in obj) {
                if (typeof obj[key] === 'object' && obj[key] !== null) {
                    // Recursively wrap nested objects in proxies
                    obj[key] = createProxy(obj[key]);
                }
            }
            return new Proxy(obj, handler);
        };

        // Overwrite timeCourses with recursive proxies
        this.timeCourses = createProxy(this.timeCourses);
    }

    // update correlation select menu
    updateCorrelateMenu() {
        // Get the select menu
        const selectMenu = document.getElementById('ts-correlate-select')

        // Clear existing options
        selectMenu.innerHTML = '';

        // Populate select menu with time courses
        for (let ts in this.timeCourses) {
            const option = document.createElement('option');
            option.value = ts;
            if (this.timeCourses[ts]['preprocessed']) {
                option.textContent = `${ts} [Preprocessed]`;
                option.dataset.preprocessed = true;
            } else {
                option.textContent = ts;
                option.dataset.preprocessed = false;
            }
            // set type as task
            option.dataset.type = 'ts';
            selectMenu.appendChild(option);
        }

        // Populate select menu with task regressors
        for (let task in this.taskRegressors) {
            const option = document.createElement('option');
            option.value = task;
            option.textContent = `${task} [${this.taskPlotType}]`;
            // set type as task
            option.dataset.type = 'task';
            option.dataset.plotType = this.taskPlotType;
            selectMenu.appendChild(option);
        }
    }

    // gather data from correlation analysis form upon submit
    handleCorrelationSubmit() {
        event.preventDefault(); // Prevent form submission and page reload
        // get time course selection value
        const tsSelect = $('#ts-correlate-select :selected');
        const tsValue = tsSelect.val()
        const tsLabel = tsSelect.text();
        const tsType = tsSelect[0].dataset.type;
        // initialize data out object
        const dataOut = {};
        dataOut['label'] = tsValue;
        // get time course or task regressor
        if (tsType == 'ts') {
            const timeCourse = this.timeCourses[tsValue];
            if (tsSelect[0].dataset.preprocessed === 'true') {
                dataOut['ts'] = timeCourse['ts_prep'];
            } else {
                dataOut['ts'] = timeCourse['ts'];
            }
        } else if (tsType == 'task') {
            const plotType = tsSelect[0].dataset.plotType;
            dataOut['ts'] = this.taskRegressors[tsValue][plotType];
        }
        // trigger 'correlation' submission event
        $(document).trigger('correlationSubmit', dataOut);
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
        // get ts color dropdown
        const tsColorSelect = document.getElementById('ts-color-select');
        tsColorSelect.value = timeCourse[currentSelect]['color'];
        // set line marker dropdown
        const tsMarkerSelect = document.getElementById('ts-marker-select');
        tsMarkerSelect.value = timeCourse[currentSelect]['mode'];
        // set value for opacity slider
        const tsOpacity = timeCourse[currentSelect]['opacity'];
        this.opacitySlider.slider('setValue', tsOpacity);
        // set value for line width slider
        const tsLineWidth = timeCourse[currentSelect]['width'];
        this.lineWidthSlider.slider('setValue', tsLineWidth);
    }

    // update fmri time course and plot
    updatefMRITimeCourse(timeCourse, coordLabels) {
        // if an fmri time course is already displayed, 'give back' its color
        if ('fmri' in this.timeCourses) {
            this.colorOptions.unshift(this.timeCourses['fmri']['color'])
        } else {
            // if no fmri time course already exists to time course selection dropdown
            const tsSelectMenu = document.getElementById('ts-select');
            let opt = document.createElement('option');
            opt.value = 'fmri';
            opt.textContent = 'fmri';
            opt.setAttribute('data-type', 'ts');
            tsSelectMenu.appendChild(opt);

             // add fmri time course to preprocessing selection dropdown
            let fmriOption = $('<option>', { value: 'fmri', text: 'fmri' });
            this.timeCoursePrepMenu.append(fmriOption);
            // hack to remove duplicates due to bug
            //https://github.com/snapappointments/bootstrap-select/issues/2738
            this.timeCoursePrepMenu.selectpicker('destroy');
            this.timeCoursePrepMenu.selectpicker();
        }
        // initialize fmri time course in timeCourse object
        this.timeCourses['fmri'] = {
            name: coordLabels,
            ts: timeCourse,
            preprocessed: false,
            ts_prep: null,
            color: this.colorOptions.shift(),
            plot: true,
            opacity: 1,
            width: 2,
            mode: 'lines+markers'
        }

        // plot new fmri time course
        this.plotTimeCourses(this.timePoint)
    }

    // Method to plot the time course
    plotTimeCourses(
        timePoint
    ) {
        // update timePoint state
        this.timePoint = timePoint

        // Don't plot if no fmri time course and no input
        if (!this.fmriEnabled && !this.userInput) {
            return;
        }

        // initialize trace labels array
        this.traceLabels = []

        // initialize plot data
        let plotData = []
        // add input time courses to plot, if any
        for (let tsLabel in this.timeCourses){
            // keep up with trace labels
            this.traceLabels.push({'label': tsLabel, type: 'ts'})
            // whether to plot preprocessed time course
            let plotTimeCourse
            if (this.timeCourses[tsLabel]['preprocessed']) {
                plotTimeCourse = this.timeCourses[tsLabel]['ts_prep'];
            }
            else {
                plotTimeCourse = this.timeCourses[tsLabel]['ts'];
            }
            // create time course line plot
            const tsTrace = {
                x: Array.from({ length: plotTimeCourse.length }, (_, i) => i),
                y: plotTimeCourse,
                type: 'scatter',
                mode: this.timeCourses[tsLabel]['mode'],
                name: this.timeCourses[tsLabel]['name'],
                marker: { color: this.timeCourses[tsLabel]['color'] },
                line: {
                    shape: 'linear',
                    width: this.timeCourses[tsLabel]['width']
                },
                visible: this.timeCourses[tsLabel]['plot'],
                opacity: this.timeCourses[tsLabel]['opacity']
            };
            plotData.push(tsTrace)
        }
        // add task regressors to plot, if any
        for (let taskLabel in this.taskRegressors) {
            // keep up with trace labels
            this.traceLabels.push({'label': taskLabel, type: 'task'});
            let plotTimeCourse = this.taskRegressors[taskLabel][this.taskPlotType];
            // create time course line plot
            const tsTrace = {
                x: Array.from({ length: plotTimeCourse.length }, (_, i) => i),
                y: plotTimeCourse,
                type: 'scatter',
                mode: this.taskRegressors[taskLabel]['mode'],
                name: this.taskRegressors[taskLabel]['name'],
                marker: { color: this.taskRegressors[taskLabel]['color'] },
                line: {
                    shape: 'linear',
                    width: this.taskRegressors[taskLabel]['width']
                },
                visible: this.taskRegressors[taskLabel]['plot'],
                opacity: this.taskRegressors[taskLabel]['opacity']
            };
            plotData.push(tsTrace)
        }
        // create vertical line object to keep up with time point
        let timePointShape = null
        if (this.timePointMarker) {
            timePointShape = [
                {
                    type: 'line',
                    x0: timePoint,
                    y0: 0,
                    x1: timePoint,
                    y1: 1,
                    yref: 'paper',
                    opacity: 0.5,
                    line: {
                        color: 'rgb(127, 127, 127)',
                        width: 1
                    },
                }
            ]
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
        if (traceType == 'ts') {
            this.timeCourses[this.traceLabels[traceIndex]['label']]['plot'] = visibilityNew;
        } else if (traceType == 'task') {
            this.taskRegressors[this.traceLabels[traceIndex]['label']]['plot'] = visibilityNew;
        }
    }

    // Initialize plotly legend double click (hide all other traces)
    hideAllTraces(data) {
        // get index of selected trace
        const traceIndex = data.curveNumber;
        for (const [index, trace] of this.traceLabels.entries()) {
            let timeCourse
            if (trace['label'] == 'ts') {
                timeCourse = this.timeCourses;
            } else if (trace['label'] == 'task') {
                timeCourse = this.taskRegressors;
            }
            if (index == traceIndex) {
                timeCourse[trace['label']]['plot'] = true;
            } else {
                timeCourse[trace['label']]['plot'] = 'legendonly'
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
            if (currentSelect in this.timeCourses) {
                this.timeCourses[currentSelect]['mode'] = lineMarker;
                // replot with new line marker value
                this.plotTimeCourses(this.timePoint)
            }
        } else if (optionType == 'task') {
            if (currentSelect in this.taskRegressors) {
                this.taskRegressors[currentSelect]['mode'] = lineMarker;
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
            if (currentSelect in this.timeCourses) {
                this.timeCourses[currentSelect]['opacity'] = opacityValue.newValue;
                // replot with new opacity value
                this.plotTimeCourses(this.timePoint)
            }
        } else if (optionType == 'task') {
            if (currentSelect in this.taskRegressors) {
                this.taskRegressors[currentSelect]['opacity'] = opacityValue.newValue;
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
            if (currentSelect in this.timeCourses) {
                this.timeCourses[currentSelect]['width'] = lineWidth.newValue;
                // replot with new line width value
                this.plotTimeCourses(this.timePoint)
            }
        } else if (optionType == 'task') {
            if (currentSelect in this.taskRegressors) {
                this.taskRegressors[currentSelect]['width'] = lineWidth.newValue;
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
        const tsSelect = this.timeCoursePrepMenu.val();
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
            for (let tsLabel in data) {
                // set time course as preprocessed
                this.timeCourses[tsLabel]['preprocessed'] = true;
                // store preprocessed time course
                this.timeCourses[tsLabel]['ts_prep'] = data[tsLabel];
            }
            // plot time course
            this.plotTimeCourses(this.timePoint);

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
        if (Object.keys(this.timeCourses).length > 0) {
            for (let tsLabel in this.timeCourses) {
                this.timeCourses[tsLabel]['preprocessed'] = false;
                this.timeCourses[tsLabel]['ts_prep'] = null;
            }
        }

        // Refresh plot
        this.plotTimeCourses(this.timePoint)

        // turn off preprocess alert
        document.getElementById('ts-preprocess-alert').style.display = 'none';
    }


    // Resize time course plots with window changes
    onWindowResize() {
        Plotly.Plots.resize(document.getElementById(this.plotId));
    }

}


export default TimeCourse
