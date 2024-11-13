// nifti.js

class NiftiViewer {
    constructor(
        fileKey,
        anatKey,
        maskKey,
        sliceLen
    ) {
        this.fileKey = fileKey;
        this.anatKey = anatKey;
        this.maskKey = maskKey;
        // Calculate middle indices for each axis
        this.currentXSliceIndex = Math.floor(sliceLen.x / 2);
        this.currentYSliceIndex = Math.floor(sliceLen.y / 2);
        this.currentZSliceIndex = Math.floor(sliceLen.z / 2);
        // Store slice midpoints for displaying direction labels
        this.xSliceMid = this.currentXSliceIndex;
        this.ySliceMid = this.currentYSliceIndex;
        this.zSliceMid = this.currentZSliceIndex;
        // Initialize voxel coordinate labels for hover to null
        this.voxelText = {
            X: null,
            Y: null,
            Z: null
        }
        // Set time point as zero for initial plot
        this.timePoint = 0;
        // Initialize crosshair state
        this.crosshairOn = true;
        // Initiliaze direction markers state as false
        this.directionMarkerOn = false;

        // Initialize container to hold nifti X, Y, Z slices
        this.createContainer()

        // Add event listener for window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    createContainer() {
        // Append the row container to the surface container in the DOM
        const slicesContainer = document.getElementById('slices_container');
        if (slicesContainer) {
            slicesContainer.innerHTML = `
            <div id="x_slice_container" class="plot-slice-container"></div>
            <div id="y_slice_container" class="plot-slice-container"></div>
            <div id="z_slice_container" class="plot-slice-container"></div>
            <div id="colorbar_container_nii" class="plot-colorbar-container"></div>
        `;
        slicesContainer.style.display = 'block'
        } else {
            console.error('Parent container for slices visualization not found!');
        }
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
        updateCoord=false,
        updateLayoutOnly=false,
    ) {
        return fetch(`/get_slices?file_key=${this.fileKey}&anat_key=${this.anatKey}&mask_key=${this.maskKey}&x_slice=${this.currentXSliceIndex}&y_slice=${this.currentYSliceIndex}&z_slice=${this.currentZSliceIndex}&time_point=${timePoint}&use_preprocess=${preprocState}&update_voxel_coord=${updateCoord}`)
            .then(response => response.json())
            .then(data => {
                // get lengths of X, Y, and Z slices
                const lenSlices = {
                    lenX: data.x_slice.length,
                    lenY: data.y_slice.length,
                    lenZ: data.z_slice.length
                }
                // update voxel coordinates, if update
                if (updateCoord) {
                    // convert voxel coordinates to text
                    this.voxelText['X'] = data.x_voxel_coords.map(row =>
                        row.map(
                            c => `Voxel: (${c[0]}, ${c[1]}, ${c[2]})`
                        )
                    );
                    this.voxelText['Y'] = data.y_voxel_coords.map(row =>
                        row.map(
                            c => `Voxel: (${c[0]}, ${c[1]}, ${c[2]})`
                        )
                    );
                    this.voxelText['Z'] = data.z_voxel_coords.map(row =>
                        row.map(
                            c => `Voxel: (${c[0]}, ${c[1]}, ${c[2]})`
                        )
                    );
                }
                // mask and threshold slices
                data = this.prepareSlices(data, thresholdMin, thresholdMax)
                // Plot the initial slices with Plotly.newPlot
                this.plotSlice(
                    'x_slice_container', data.x_slice, data.x_slice_anat, 'X',
                    lenSlices, colorMap, colorMin, colorMax, hoverTextOn,
                    updateLayoutOnly
                );
                this.plotSlice(
                    'y_slice_container', data.y_slice, data.y_slice_anat, 'Y',
                     lenSlices, colorMap, colorMin, colorMax, hoverTextOn,
                     updateLayoutOnly
                );
                this.plotSlice(
                    'z_slice_container', data.z_slice, data.z_slice_anat, 'Z',
                     lenSlices, colorMap, colorMin, colorMax, hoverTextOn,
                     updateLayoutOnly
                );
            })
            .catch(error => {
                console.error('Error fetching slices:', error);
                alert('Error fetching slices');
            });
    }

    plotSlice(
        containerId,
        sliceData,
        sliceDataAnat,
        axisLabel,
        lenSlices,
        colorMap,
        colorMin,
        colorMax,
        hoverTextOn,
        updateLayoutOnly
    ) {
        // Determine whether to plot crosshairs
        let crosshairLines
        if (this.crosshairOn) {
            crosshairLines = this.getCrosshairShapes(axisLabel, lenSlices);
        } else {
            crosshairLines = null
        }

        let directionMark
        // Get direction marker labels, if true
        if (this.directionMarkerOn) {
            directionMark = this.createDirectionMarkers(axisLabel, lenSlices);
        }

        const data = [{
            z: sliceData,
            name: 'fMRI',
            type: 'heatmap',
            colorscale: colorMap,
            zmin: colorMin,
            zmax: colorMax,
            showscale: false,
            hoverinfo: hoverTextOn ? 'all' : 'none',
            // Display voxel coordinates
            text: this.voxelText[axisLabel],
            hovertemplate: hoverTextOn ? 'Intensity: %{z}<br> %{text}<extra></extra>': null
        }];

        const layout = {
            title: `${axisLabel} Slice`,
            shapes: crosshairLines,
            autosize: true,  // Enable autosizing
            responsive: true, // Make the plot responsive
            width: null,
            height: null,
            hovermode: 'closest',
            xaxis: {
                title: `${axisLabel} Axis`,
                fixedrange: true,
                visible: false,  // Hide the X axis
                showgrid: false, // Hide grid lines
                zeroline: false, // Hide zero lines
                showline: false, // Hide axis lines
                showticklabels: false, // Hide axis tick labels
            },
            yaxis: {
                title: 'Slice',
                fixedrange: true,
                visible: false,  // Hide the X axis
                showgrid: false, // Hide grid lines
                zeroline: false, // Hide zero lines
                showline: false, // Hide axis lines
                showticklabels: false, // Hide axis tick labels
            },
            margin: { l: 0, r: 0, t: 0, b: 0 },  // Remove any margins,
            annotations: this.directionMarkerOn ? directionMark : null
        };

        if (sliceDataAnat) {
            // Add the anatomical image as a background layer
            data.unshift({
                z: sliceDataAnat,
                name: 'anat',
                type: 'heatmap',
                colorscale: 'Greys',  // Use a grayscale colormap for the anatomical brain
                showscale: false,
                opacity: 0.5  // Set opacity for the anatomical background
            });
        }
        // Plot using react
        if (updateLayoutOnly) {
            Plotly.restyle(containerId, {
                colorscale: colorMap,
                zmin: colorMin,
                zmax: colorMax
            });
        } else {
            Plotly.react(containerId, data, layout);
        }

    }

    getCrosshairShapes(axis, lenSlices) {
        const crosshairColor = 'red';
        const crosshairWidth = 1;
        let xIndex, yIndex, lenX, lenY;

        // Determine which slice indices to use based on the axis
        switch (axis) {
            case 'X':
                xIndex = this.currentYSliceIndex;
                yIndex = this.currentZSliceIndex;
                lenX = lenSlices['lenZ'] - 1;
                lenY = lenSlices['lenX'] - 1;
                break;
            case 'Y':
                xIndex = this.currentXSliceIndex;
                yIndex = this.currentZSliceIndex;
                lenX = lenSlices['lenY'] - 1;
                lenY = lenSlices['lenY'] - 1;
                break;
            case 'Z':
                xIndex = this.currentXSliceIndex;
                yIndex = this.currentYSliceIndex;
                lenX = lenSlices['lenX'] - 1;
                lenY = lenSlices['lenZ'] - 1;
                break;
        }
        return [
            {
                type: 'line',
                x0: 0,
                y0: yIndex,
                x1: lenX,
                y1: yIndex,
                line: { color: crosshairColor, width: crosshairWidth }
            },
            {
                type: 'line',
                x0: xIndex,
                y0: 0,
                x1: xIndex,
                y1: lenY,
                line: { color: crosshairColor, width: crosshairWidth }
            }
        ];
    }

    clickHandler = (containerId, updateX, updateY, updateZ, clickCallBack) => {
        // Function to handle click events
        document.getElementById(containerId).on('plotly_click', (eventData) => {
            const x = Math.round(eventData.points[0].x);
            const y = Math.round(eventData.points[0].y);

            // Update slice indices based on the click data
            this.updateSliceIndices(
                updateZ ? x : updateY ? x : this.currentXSliceIndex,
                updateZ ? y : updateX ? x : this.currentYSliceIndex,
                updateX ? y : updateY ? y : this.currentZSliceIndex
            );

            // execute calback function provided to plotlyClickHandler
            if (clickCallBack) {
                clickCallBack();
            }

            // Fetch World coordinates
            this.fetchWorldCoords()
        });
    };

    // Register click handlers for each slice container using the clickHandler function
    plotlyClickHandler(clickCallBack=null) {
        // register a handler for each slice
        this.clickHandler('x_slice_container', true, false, false, clickCallBack);
        this.clickHandler('y_slice_container', false, true, false, clickCallBack);
        this.clickHandler('z_slice_container', false, false, true, clickCallBack);
    }

    fetchTimeCourse(preprocState) {
        // Fetch the time course data for the selected voxel
        return fetch(`/get_time_course_nii?file_key=${this.fileKey}&x=${this.currentXSliceIndex}&y=${this.currentYSliceIndex}&z=${this.currentZSliceIndex}&use_preprocess=${preprocState}`)
            .then(response => response.json())
            .then(data => {
                // create coordinate labels title
                const coordLabels = `Voxel: (x=${this.currentXSliceIndex}, y=${this.currentYSliceIndex}, z=${this.currentZSliceIndex})`
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

    // fetch preprocessed nifti data or remove ('reset') back to raw data
    fetchPreprocessed(
        userParams,
        normSwitchEnabled,
        filterSwitchEnabled,
        smoothSwitchEnabled,
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
        return fetch(`/preprocess_nii?file_key=${this.fileKey}&${paramsQueryString}&normalize_enabled=${normSwitchEnabled}&filter_enabled=${filterSwitchEnabled}&smooth_enabled=${smoothSwitchEnabled}&mask_key=${this.maskKey}&reset=${reset}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error in response from server during nifti preprocessing')
                }
                return response.json()
            }).catch(error => {
                console.error('Error during nifti preprocessing:', error);
            });
    }

    fetchWorldCoords() {
        fetch(`/get_world_coords?file_key=${this.fileKey}&x=${this.currentXSliceIndex}&y=${this.currentYSliceIndex}&z=${this.currentZSliceIndex}`)
            .then(response => response.json())
            .then(data => {
                // display World coordinates
                const xWorld = document.getElementById('x-world');
                const yWorld = document.getElementById('y-world');
                const zWorld = document.getElementById('z-world');
                xWorld.innerHTML = data.x;
                yWorld.innerHTML = data.y;
                zWorld.innerHTML = data.z;
            })
            .catch(error => {
                console.error('Error during fetch of MNI coordinates:', error);
            });
    }

    // Update slice indices
    updateSliceIndices(xIndex, yIndex, zIndex) {
        this.currentXSliceIndex = xIndex;
        this.currentYSliceIndex = yIndex;
        this.currentZSliceIndex = zIndex;
    }

    // resize plotly plots to window resizing
    onWindowResize() {
        Plotly.Plots.resize(document.getElementById('x_slice_container'));
        Plotly.Plots.resize(document.getElementById('y_slice_container'));
        Plotly.Plots.resize(document.getElementById('z_slice_container'));
        Plotly.Plots.resize(document.getElementById('colorbar_container_nii'));
    }

    // Prepare slices for plotting (masking and threshold)
    prepareSlices(data, thresholdMin, thresholdMax) {
        // Apply mask, if provided
        if (this.maskKey) {
            data.x_slice = this.applyMask(data.x_slice, data.x_slice_mask)
            data.y_slice = this.applyMask(data.y_slice, data.y_slice_mask)
            data.z_slice = this.applyMask(data.z_slice, data.z_slice_mask)
        }

        // Apply thresholds by filtering out values outside the threshold range
        if (thresholdMin != 0 || thresholdMax != 0) {
            data.x_slice = this.applyThreshold(
                data.x_slice, thresholdMin, thresholdMax
            );
            data.y_slice = this.applyThreshold(
                data.y_slice, thresholdMin, thresholdMax
            );
            data.z_slice = this.applyThreshold(
                data.z_slice, thresholdMin, thresholdMax
            );
        }
        return data
    }

    // Create direction marker labels
    createDirectionMarkers(axisLabel, lenSlices) {
        // Create direction marker annotations
        let annotation
        if (axisLabel == 'X') {
            annotation = [
            {
                x: 1,
                y: this.zSliceMid,
                xref: 'x',
                yref: 'y',
                text: 'P',
                showarrow: false
            },
            {
                x: lenSlices['lenZ'] - 2,
                y: this.zSliceMid,
                xref: 'x',
                yref: 'y',
                text: 'A',
                showarrow: false
            }
          ]
        } else if (axisLabel == 'Y') {
            annotation = [
            {
                x: 1,
                y: this.zSliceMid,
                xref: 'x',
                yref: 'y',
                text: 'L',
                showarrow: false
            },
            {
                x: lenSlices['lenY'] - 2,
                y: this.zSliceMid,
                xref: 'x',
                yref: 'y',
                text: 'R',
                showarrow: false
            }
          ]
        } else if (axisLabel == 'Z') {
            annotation = [
            {
                x: 1,
                y: this.ySliceMid,
                xref: 'x',
                yref: 'y',
                text: 'L',
                showarrow: false
            },
            {
                x: lenSlices['lenX'] - 2,
                y: this.ySliceMid,
                xref: 'x',
                yref: 'y',
                text: 'R',
                showarrow: false
            },
            {
                x: this.xSliceMid,
                y: 1,
                xref: 'x',
                yref: 'y',
                text: 'P',
                showarrow: false
            },
            {
                x: this.xSliceMid,
                y: lenSlices['lenZ']-2,
                xref: 'x',
                yref: 'y',
                text: 'A',
                showarrow: false
            },

          ]
        }
        return annotation
    }

    // Method to NaN out voxel values not in mask
    applyMask(sliceData, sliceMask) {
        return sliceData.map((row, i) => row.map((value, j) => {
            // If mask value is 1, keep value, otherwise NaN
            return (sliceMask[i][j] == 1) ? value : NaN;
        }));
    }

    // Method to apply the threshold to an slice data
    applyThreshold(data, thresholdMin, thresholdMax) {
    return data.map(row => row.map(value => {
        // If the value is inside the threshold range, set it to NaN (or another background value)
        return (value >= thresholdMin && value <= thresholdMax) ? NaN : value;
    }));
}
}

export default NiftiViewer;
