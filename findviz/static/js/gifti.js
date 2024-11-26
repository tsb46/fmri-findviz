// gifti.js

class GiftiViewer {
    constructor(
        leftKey,
        rightKey,
        verticesLeft,
        facesLeft,
        verticesRight,
        facesRight,
    ) {
        this.leftKey = leftKey;
        this.rightKey = rightKey;
        this.verticesLeft = verticesLeft;
        this.facesLeft = facesLeft;
        this.verticesRight = verticesRight;
        this.facesRight = facesRight;
        // Initalize current selected hemisphere state as null
        this.selectedHemisphere = null
        // Initialize current selected vertex as null
        this.selectedVertex = null

        // Create containers for plots and initialize them properly
        this.createContainers();

        // Get plot divs after containers are added to the DOM
        this.leftPlotDiv = document.getElementById('left_brain_visualization');
        this.rightPlotDiv = document.getElementById('right_brain_visualization');

        // Add event listener for window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    createContainers() {
        // Create a row container using Bootstrap's grid system
        let rowContainer = document.createElement('div');
        rowContainer.className = 'row';  // Use Bootstrap's row class for the grid
        rowContainer.style.width = '100%';  // Ensure the row takes full width
        rowContainer.style.height = '100%'; // Ensure full height
        rowContainer.style.margin = '0';    // Remove default margin

        // Left hemisphere
        if (this.leftKey) {
            this.createLeftContainer(rowContainer);
        }

        // Right hemisphere
        if (this.rightKey) {
            this.createRightContainer(rowContainer);
        }

        // Colorbar
        let colorbarContainer = document.createElement('div');
        colorbarContainer.className = 'col-md-2';  // Use 2 columns for the colorbar
        colorbarContainer.style.height = '100%';   // Ensure it fits within the height of the row
        colorbarContainer.innerHTML = `
            <div id="colorbar_container_gii" class="d-flex align-items-center justify-content-center" style="height: 100%; padding: 0;">
                <div id="colorbar_gii" style="width: 100%; height: 100%;"></div>
            </div>
        `;
        rowContainer.appendChild(colorbarContainer);

        // Append the row container to the surface container
        const surfaceContainer = document.getElementById('surface_container');
        if (surfaceContainer) {
            surfaceContainer.style.display = 'block';
            surfaceContainer.style.padding = '0';  // Remove padding
            surfaceContainer.appendChild(rowContainer);
        } else {
            console.error('Parent container for surface visualization not found!');
        }
    }

    createLeftContainer(rowContainer) {
        let container = document.createElement('div');
        container.className = 'col-md-5';  // Use 5 columns for left hemisphere
        container.style.height = '100%';    // Ensure full height
        container.innerHTML = `
            <div id="left_brain_visualization_container" class="d-flex align-items-center justify-content-center" style="height: 100%; padding: 0;">
                <div id="left_brain_visualization" style="width: 100%; height: 100%;"></div>
            </div>
        `;
        rowContainer.appendChild(container);
    }

    createRightContainer(rowContainer) {
        let container = document.createElement('div');
        container.className = 'col-md-5';  // Use 5 columns for right hemisphere
        container.style.height = '100%';    // Ensure full height
        container.innerHTML = `
            <div id="right_brain_visualization_container" class="d-flex align-items-center justify-content-center" style="height: 100%; padding: 0;">
                <div id="right_brain_visualization" style="width: 100%; height: 100%;"></div>
            </div>
        `;
        rowContainer.appendChild(container);
    }

    plot(
        timePoint,
        colorMap,
        colorMin,
        colorMax,
        thresholdMin,
        thresholdMax,
        hoverTextOn,
        preprocState,
        updateCoord=false, // unused, for consistency with API
        updateLayoutOnly=false,
    ) {
        let formData = new FormData();
        if (this.leftKey) {
            formData.append('left_key', this.leftKey);
        }
        if (this.rightKey) {
            formData.append('right_key', this.rightKey);
        }
        formData.append('time_point', timePoint);
        formData.append('use_preprocess', preprocState);

        return fetch('/get_brain_gii_plot', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (this.leftKey) {
                this.plotHemisphere(
                    this.leftPlotDiv,
                    'left',
                    data.intensity_left,
                    timePoint,
                    colorMap,
                    colorMin,
                    colorMax,
                    thresholdMin,
                    thresholdMax,
                    hoverTextOn,
                    updateLayoutOnly,
                );
            }
            if (this.rightKey) {
                this.plotHemisphere(
                    this.rightPlotDiv,
                    'right',
                    data.intensity_right,
                    timePoint,
                    colorMap,
                    colorMin,
                    colorMax,
                    thresholdMin,
                    thresholdMax,
                    hoverTextOn,
                    updateLayoutOnly
                );
            }
        })
        .catch(error => {
            console.error('Error fetching gifti data:', error);
            alert('Error fetching gifti data');
        });
    }

    plotHemisphere(
        plotDiv,
        hemisphere,
        intensityValues,
        timePoint,
        colorMap,
        colorMin,
        colorMax,
        thresholdMin,
        thresholdMax,
        hoverTextOn,
        updateLayoutOnly
    ) {
        // Apply thresholds by filtering out values outside the threshold range
        if (thresholdMin != 0 || thresholdMax != 0) {
            intensityValues = this.applyThreshold(
                intensityValues,
                thresholdMin,
                thresholdMax
            );
        }

        // set plot data based on hemisphere
        let plotTitle
        let vertices
        let faces
        if (hemisphere == 'left') {
            plotTitle = 'Left Hemisphere';
            vertices = this.verticesLeft;
            faces =  this.facesLeft;
        } else if (hemisphere == 'right') {
            plotTitle = 'Right Hemisphere';
            vertices = this.verticesRight;
            faces = this.facesRight;
        }

        let plotData = {
            type: 'mesh3d',
            x: vertices.map(v => v[0]),
            y: vertices.map(v => v[1]),
            z: vertices.map(v => v[2]),
            i: faces.map(f => f[0]),
            j: faces.map(f => f[1]),
            k: faces.map(f => f[2]),
            intensity: intensityValues,
            colorscale: colorMap,
            cmin: colorMin,
            cmax: colorMax,
            showscale: false,
            text: intensityValues,
            hoverinfo: hoverTextOn ? 'x+y+z' : 'none',
            hovertemplate: hoverTextOn ? 'Intensity: %{text:.3f}<br>x: %{x}<br>y: %{y}<br>z: %{z} <extra></extra>': null
        };

        let layout = {
            title: plotTitle,
            autosize: true,  // Enable autosizing
            responsive: true, // Make the plot responsive
            uirevision:'true',
            scene: {
                xaxis: {
                    visible: false,  // Hide the X axis
                    showgrid: false, // Hide grid lines
                    zeroline: false, // Hide zero lines
                    showline: false, // Hide axis lines
                    showticklabels: false, // Hide axis tick labels
                },
                yaxis: {
                    visible: false,  // Hide the Y axis
                    showgrid: false, // Hide grid lines
                    zeroline: false, // Hide zero lines
                    showline: false, // Hide axis lines
                    showticklabels: false, // Hide axis tick labels
                },
                zaxis: {
                    visible: false,  // Hide the Z axis
                    showgrid: false, // Hide grid lines
                    zeroline: false, // Hide zero lines
                    showline: false, // Hide axis lines
                    showticklabels: false, // Hide axis tick labels
                },
            },
            margin: { l: 5, r: 5, b: 5, t: 30 },
        };

        // Plot using react
        if (updateLayoutOnly) {
            Plotly.restyle(plotDiv, {
                colorscale: colorMap,
                cmin: colorMin,
                cmax: colorMax
            });
        } else {
            Plotly.react(plotDiv, [plotData], layout);
        }
    }

    plotlyClickHandler(clickCallBack=null) {
        if (this.leftKey) {
            this.clickHandler(this.leftPlotDiv, 'left', clickCallBack);
        }
        if (this.rightKey) {
            this.clickHandler(this.rightPlotDiv, 'right', clickCallBack);
        }
    }

    clickHandler(plotDiv, hemisphere, clickCallBack) {
        plotDiv.on('plotly_click', (eventData) => {
            // update selected hemisphere and vertex
            const vertexIndex = eventData.points[0].pointNumber;
            this.selectedVertex = vertexIndex;
            this.selectedHemisphere = hemisphere;
            // execute calback function provided to plotlyClickHandler
            if (clickCallBack) {
                clickCallBack();
            }
        });
    }

    // fetch preprocessed gifti data or remove ('reset') back to raw data
    fetchPreprocessed(
        userParams,
        normSwitchEnabled,
        filterSwitchEnabled,
        smoothSwitchEnabled, // unused for surface files
        reset=false
    ){
        // pass parameters if reset=false, otherwise null
        let paramsQueryString
        if (!reset) {
            paramsQueryString = new URLSearchParams(userParams).toString();
        } else{
            paramsQueryString = null
        }
        // Perform the fetch for preprocessing
        return fetch(`/preprocess_gii?left_key=${this.leftKey}&right_key=${this.rightKey}&${paramsQueryString}&normalize_enabled=${normSwitchEnabled}&filter_enabled=${filterSwitchEnabled}&reset=${reset}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error in response from server during gifti preprocessing')
                }
                return response.json()
            }).catch(error => {
                console.error('Error during gifti preprocessing:', error);
            });
    }

    fetchTimeCourse(preprocState) {
        // get file key
        let fileKey = null
        if (this.selectedHemisphere == 'right') {
            fileKey = this.rightKey
        }
        else {
            fileKey = this.leftKey
        }
        // Fetch the time course data for the selected vertex
        return fetch(`/get_time_course_gii?file_key=${fileKey}&vertex_index=${this.selectedVertex}&use_preprocess=${preprocState}&hemisphere=${this.selectedHemisphere}`)
            .then(response => response.json())
            .then(data => {
                const coordLabels = `Vertex: ${this.selectedVertex}`
                return {
                    label: coordLabels,
                    timeCourse: data.time_course
                }
            })
            .catch(error => {
                console.error('Error fetching time course data:', error);
                alert('Error fetching time course data');
            });
    }

    onWindowResize() {
        if (this.leftKey) {
            Plotly.Plots.resize(document.getElementById('left_brain_visualization'));
        }
        if (this.rightKey) {
            Plotly.Plots.resize(document.getElementById('right_brain_visualization'));
        }
    }

    // Method to apply the threshold to surface data
    applyThreshold(vertexData, thresholdMin, thresholdMax) {
        return vertexData.map(value => {
            // If the value is inside the threshold range, set it to NaN (or another background value)
            return (value >= thresholdMin && value <= thresholdMax) ? NaN : value;
        });
    }
}

export default GiftiViewer;
