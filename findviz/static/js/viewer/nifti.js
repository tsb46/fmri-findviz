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
        // Calculate middle indices for ortho view
        this.orthoSliceIndex = {
            x: Math.floor(sliceLen.x / 2),
            y: Math.floor(sliceLen.y / 2),
            z: Math.floor(sliceLen.z / 2)
        }
        this.sliceLen = sliceLen;
        // initialize montage slice indices at zero
        this.montageSliceIndex = {
            // First level is slice direction (e.g. 'x' is sagittal)
            x: {
                // Second level is slice coordinates
                slice1: {x: 0, y: 0, z: 0},
                slice2: {x: 0, y: 0, z: 0},
                slice3: {x: 0, y: 0, z: 0}
            },
            y: {
                slice1: {x: 0, y: 0, z: 0},
                slice2: {x: 0, y: 0, z: 0},
                slice3: {x: 0, y: 0, z: 0}
            },
            z: {
                slice1: {x: 0, y: 0, z: 0},
                slice2: {x: 0, y: 0, z: 0},
                slice3: {x: 0, y: 0, z: 0}
            },

        }
        // Store slice midpoints for displaying direction labels in Ortho view
        this.orthoSliceMid = {
            x: this.orthoSliceIndex['x'],
            y: this.orthoSliceIndex['y'],
            z: this.orthoSliceIndex['z'],
        }
        // Initialize voxel coordinate labels for hover to null
        this.voxelText = {
            x: null,
            y: null,
            z: null
        }
        // Initialize viewer state (ortho, montage)
        this.viewerState = 'ortho'
        // Initialize montage direction
        this.montageSliceDirection = 'z' // sagittal
        // Initialize active montage slice ('slice1', 'slice2', 'slice3')
        this.montageActiveSlice = 'slice1'
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

    // Change view state from Ortho to Montage, and vice versa
    changeViewState(changeView, sliceDirection=null, sliceUpdate=null) {
        if (changeView) {
            this.viewerState = this.viewerState == 'ortho' ? 'montage' : 'ortho'
        }
        // update montage slice indices if montage state
        if (this.viewerState == 'montage') {
            // distribute slice containers evenly
            document.getElementById('x_slice_container').style.width = '33%';
            document.getElementById('y_slice_container').style.width = '33%';
            document.getElementById('z_slice_container').style.width = '33%';

            if (sliceDirection) {
                this.montageSliceDirection = sliceDirection;
            }
            if (sliceUpdate) {
                const sliceIndex = this.montageSliceIndex[this.montageSliceDirection]
                sliceIndex['slice1'][this.montageSliceDirection] = sliceUpdate['slice1Slider'];
                sliceIndex['slice2'][this.montageSliceDirection] = sliceUpdate['slice2Slider'];
                sliceIndex['slice3'][this.montageSliceDirection] = sliceUpdate['slice3Slider'];
            }
        } else {
            // if ortho view, give more room to first slice
            document.getElementById('x_slice_container').style.width = '38%';
            document.getElementById('y_slice_container').style.width = '31%';
            document.getElementById('z_slice_container').style.width = '31%';

        }
    }

    plot(
        timePoint,
        colorMap,
        colorMin,
        colorMax,
        thresholdMin,
        thresholdMax,
        opacity,
        hoverTextOn,
        preprocState,
        updateCoord=false,
        updateLayoutOnly=false,
    ) {
        // pass data in form
        let formData = new FormData();
        formData.append('file_key', this.fileKey);
        formData.append('anat_key', this.anatKey);
        formData.append('mask_key', this.maskKey);
        formData.append('view_state', this.viewerState);
        formData.append('montage_slice_dir', this.montageSliceDirection);
        if (this.viewerState == 'ortho') {
            formData.append('x_slice', this.orthoSliceIndex['x']);
            formData.append('y_slice', this.orthoSliceIndex['y']);
            formData.append('z_slice', this.orthoSliceIndex['z']);
        } else if (this.viewerState = 'montage') {
            formData.append(
                'x_slice', this.montageSliceIndex[this.montageSliceDirection]['slice1'][this.montageSliceDirection]);
            formData.append(
                'y_slice', this.montageSliceIndex[this.montageSliceDirection]['slice2'][this.montageSliceDirection]);
            formData.append(
                'z_slice', this.montageSliceIndex[this.montageSliceDirection]['slice3'][this.montageSliceDirection]);
        }
        formData.append('time_point', timePoint);
        formData.append('use_preprocess', preprocState);
        formData.append('update_voxel_coord', updateCoord);
        return fetch('/get_slices', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // update voxel coordinate labels in hover, if specified
            if (updateCoord) {
                let coordIndex = {}
                // set coordinate index differently for montage vs ortho view
                if (this.viewerState == 'montage') {
                    if (this.montageSliceDirection == 'x') {
                        coordIndex['x'] = [0,1,2];
                        coordIndex['y'] = [0,1,2];
                        coordIndex['z'] = [0,1,2];
                    } else if (this.montageSliceDirection == 'y') {
                        coordIndex['x'] = [1,0,2];
                        coordIndex['y'] = [1,0,2];
                        coordIndex['z'] = [1,0,2];
                    } else if (this.montageSliceDirection == 'z') {
                        coordIndex['x'] = [1,2,0];
                        coordIndex['y'] = [1,2,0];
                        coordIndex['z'] = [1,2,0];
                    }

                } else if (this.viewerState == 'ortho') {
                    coordIndex['x'] = [0,1,2];
                    coordIndex['y'] = [1,0,2];
                    coordIndex['z'] = [1,2,0];
                }
                // assign coordinate labels
                for (const coord of ['x', 'y', 'z']) {
                    const voxelCoords = data[`${coord}_voxel_coords`];
                    this.voxelText[coord] = voxelCoords.map(row =>
                    row.map(
                        c => `Voxel: (${c[coordIndex[coord][0]]}, ${c[coordIndex[coord][1]]}, ${c[coordIndex[coord][2]]})`
                        )
                    );

                }

            }
            // mask and threshold slices
            data = this.prepareSlices(data, thresholdMin, thresholdMax)

            // plot three slices individually
            this.plotSlice(
                'x_slice_container', data.x_slice, data.x_slice_anat, 'x',
                colorMap, colorMin, colorMax, opacity, hoverTextOn, updateLayoutOnly
            );
            this.plotSlice(
                'y_slice_container', data.y_slice, data.y_slice_anat, 'y',
                 colorMap, colorMin, colorMax, opacity, hoverTextOn, updateLayoutOnly
            );
            this.plotSlice(
                'z_slice_container', data.z_slice, data.z_slice_anat, 'z',
                 colorMap, colorMin, colorMax, opacity, hoverTextOn, updateLayoutOnly
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
        colorMap,
        colorMin,
        colorMax,
        opacity,
        hoverTextOn,
        updateLayoutOnly
    ) {
        // Determine whether to plot crosshairs
        let crosshairLines
        if (this.crosshairOn) {
            crosshairLines = this.getCrosshairShapes(axisLabel);
        } else {
            crosshairLines = null
        }

        let directionMark
        // Get direction marker labels, if true
        if (this.directionMarkerOn) {
            directionMark = this.createDirectionMarkers(axisLabel);
        }
        const data = [{
            z: sliceData,
            name: 'fMRI',
            type: 'heatmap',
            colorscale: colorMap,
            zmin: colorMin,
            zmax: colorMax,
            opacity: opacity,
            showscale: false,
            hoverinfo: hoverTextOn ? 'all' : 'none',
            // Display voxel coordinates
            text: this.voxelText[axisLabel],
            hovertemplate: hoverTextOn ? 'Intensity: %{z}<br> %{text}<extra></extra>': null
        }];

        const layout = {
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

    clickHandler = (containerId, updateX, updateY, updateZ, clickCallBack) => {
        // Function to handle click events
        document.getElementById(containerId).on('plotly_click', (eventData) => {
            const x = Math.round(eventData.points[0].x);
            const y = Math.round(eventData.points[0].y);

            // Update slice indices based on the click data
            this.updateSliceIndices(x, y, updateX, updateY, updateZ);

            // if montage, set active montage slice
            if (this.viewerState == 'montage'){
                if (updateX) {
                    this.montageActiveSlice = 'slice1'
                } else if (updateY) {
                    this.montageActiveSlice = 'slice2'
                } else if (updateZ) {
                    this.montageActiveSlice = 'slice3'
                }
            }
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
        let sliceIndex
        if (this.viewerState == 'montage') {
            sliceIndex = this.montageSliceIndex[this.montageSliceDirection][this.montageActiveSlice];
        } else if (this.viewerState == 'ortho') {
            sliceIndex = this.orthoSliceIndex;
        }
        // Fetch the time course data for the selected voxel
        return fetch(`/get_time_course_nii?file_key=${this.fileKey}&x=${sliceIndex['x']}&y=${sliceIndex['y']}&z=${sliceIndex['z']}&use_preprocess=${preprocState}`)
            .then(response => response.json())
            .then(data => {
                return {
                    label: data.time_course_label,
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
        fetch(`/get_world_coords?file_key=${this.fileKey}&x=${this.orthoSliceIndex['x']}&y=${this.orthoSliceIndex['y']}&z=${this.orthoSliceIndex['z']}`)
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
    updateSliceIndices(x, y, updateX, updateY, updateZ) {
        // coordinate locations for orthogonal view
        let xIndex, yIndex, zIndex
        if (this.viewerState == 'ortho') {
            xIndex = updateZ ? x : updateY ? x : this.orthoSliceIndex['x'];
            yIndex = updateZ ? y : updateX ? x : this.orthoSliceIndex['y'];
            zIndex = updateX ? y : updateY ? y : this.orthoSliceIndex['z'];
            // update ortho slice indices
            this.orthoSliceIndex['x'] = xIndex;
            this.orthoSliceIndex['y'] = yIndex;
            this.orthoSliceIndex['z'] = zIndex;
        } else if (this.viewerState == 'montage') {
            for (const montageSlice of ['slice1', 'slice2', 'slice3']) {
                if (this.montageSliceDirection == 'x') {
                    this.montageSliceIndex[this.montageSliceDirection][montageSlice]['y'] = x
                    this.montageSliceIndex[this.montageSliceDirection][montageSlice]['z'] = y
                } else if (this.montageSliceDirection == 'y') {
                    this.montageSliceIndex[this.montageSliceDirection][montageSlice]['x'] = x
                    this.montageSliceIndex[this.montageSliceDirection][montageSlice]['z'] = y
                } else if (this.montageSliceDirection == 'z') {
                    this.montageSliceIndex[this.montageSliceDirection][montageSlice]['x'] = x
                    this.montageSliceIndex[this.montageSliceDirection][montageSlice]['y'] = y
                }
            }
        }
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
            // apply mask to functional
            data.x_slice = this.applyMask(data.x_slice, data.x_slice_mask)
            data.y_slice = this.applyMask(data.y_slice, data.y_slice_mask)
            data.z_slice = this.applyMask(data.z_slice, data.z_slice_mask)
            // apply mask to anatomical, if passed
            if (this.anatKey) {
                data.x_slice_anat = this.applyMask(data.x_slice_anat, data.x_slice_mask)
                data.y_slice_anat = this.applyMask(data.y_slice_anat, data.y_slice_mask)
                data.z_slice_anat = this.applyMask(data.z_slice_anat, data.z_slice_mask)
            }

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

    // set location and length of crosshairs
    getCrosshairShapes(axis) {
        const crosshairColor = 'red';
        const crosshairWidth = 1;
        let xIndex, yIndex, lenX, lenY;
        // crosshair location behavior differs based on viewer state (ortho vs. montage)
        let axisCrossHair
        let sliceIndices
        if (this.viewerState == 'ortho') {
            // For ortho view, crosshair location differs across all slices
            axisCrossHair = axis;
            sliceIndices = this.orthoSliceIndex;
            if (axis == 'x') {
                lenX = this.sliceLen['y'] - 1;
                lenY = this.sliceLen['z'] - 1;
            } else if (axis == 'y') {
                lenX = this.sliceLen['x'] - 1;
                lenY = this.sliceLen['z'] - 1;
            } else if (axis == 'z') {
                lenX = this.sliceLen['x'] - 1;
                lenY = this.sliceLen['y'] - 1;
            }
        } else if (this.viewerState == 'montage') {
            // For montage view, crosshair location is the same across all slices
            axisCrossHair = this.montageSliceDirection;
            let slice
            // convert axis label to slice number
            if (axis == 'x') {
                slice = 'slice1';
            } else if (axis == 'y') {
                slice = 'slice2'
            } else if (axis == 'z') {
                slice = 'slice3'
            }
            // set crosshair length for montage view
            if (this.montageSliceDirection == 'x') {
                lenX = this.sliceLen['y'] - 1;
                lenY = this.sliceLen['z'] - 1;
            } else if (this.montageSliceDirection == 'y') {
                lenX = this.sliceLen['x'] - 1;
                lenY = this.sliceLen['z'] - 1;
            } else if (this.montageSliceDirection == 'z') {
                lenX = this.sliceLen['x'] - 1;
                lenY = this.sliceLen['y'] - 1;
            }
            sliceIndices = this.montageSliceIndex[this.montageSliceDirection][slice]
        }
        // Determine which slice indices to use based on the axis
        switch (axisCrossHair) {
            case 'x':
                xIndex = sliceIndices['y'];
                yIndex = sliceIndices['z'];
                break;
            case 'y':
                xIndex = sliceIndices['x'];
                yIndex = sliceIndices['z'];
                break;
            case 'z':
                xIndex = sliceIndices['x'];
                yIndex = sliceIndices['y'];
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

    // Create direction marker labels
    createDirectionMarkers(axisLabel) {
        // Create direction marker annotations
        let annotation, sliceDir
        if (this.viewerState == 'montage') {
            sliceDir = this.montageSliceDirection
        } else {
            sliceDir = axisLabel
        }
        if (sliceDir == 'x') {
            annotation = [
            {
                x: 1,
                y: this.orthoSliceMid['z'],
                xref: 'x',
                yref: 'y',
                text: 'P',
                showarrow: false
            },
            {
                x: this.sliceLen['y'] - 2,
                y: this.orthoSliceMid['z'],
                xref: 'x',
                yref: 'y',
                text: 'A',
                showarrow: false
            }
          ]
        } else if (sliceDir == 'y') {
            annotation = [
            {
                x: 1,
                y: this.orthoSliceMid['z'],
                xref: 'x',
                yref: 'y',
                text: 'L',
                showarrow: false
            },
            {
                x: this.sliceLen['x'] - 2,
                y: this.orthoSliceMid['z'],
                xref: 'x',
                yref: 'y',
                text: 'R',
                showarrow: false
            }
          ]
        } else if (sliceDir == 'z') {
            annotation = [
            {
                x: 1,
                y: this.orthoSliceMid['y'],
                xref: 'x',
                yref: 'y',
                text: 'L',
                showarrow: false
            },
            {
                x: this.sliceLen['x'] - 2,
                y: this.orthoSliceMid['y'],
                xref: 'x',
                yref: 'y',
                text: 'R',
                showarrow: false
            },
            {
                x: this.orthoSliceMid['x'],
                y: 1,
                xref: 'x',
                yref: 'y',
                text: 'P',
                showarrow: false
            },
            {
                x: this.orthoSliceMid['z'],
                y: this.sliceLen['y']-2,
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
