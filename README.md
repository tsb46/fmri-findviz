<div style="display: flex; align-items: center; gap: 20px;">
<img src="findviz/static/images/FIND.png" width="100" height="100" alt="findviz-logo">
<h1>FINDVIZ: FMRI Interactive Navigation and Discovery Viewer</h1>
</div>

## Background

FINDVIZ is a browser-based visualization tool for visual exploration of fMRI data with a focus on pattern discovery. It supports the visualization of NIFTI, GIFTI, and CIFTI file formats, and time series data. Visualizations are produced using PlotlyJS. 


## Installation

### Using pip

```bash
pip install findviz
```

## Quick Start

To launch the application and upload an fMRI dataset through the web interface, run the following command in your terminal:

```bash
findviz
```

This will launch the application in your default browser. FINDVIZ was tested on Google Chrome (v134). We recommend using Chrome for the best experience. 

### Command Line Interface
FINDVIZ also supports uploading fMRI data from the command line:

```bash
# Launch with NIFTI files
findviz --nifti-func func.nii.gz --nifti-anat anat.nii.gz

# Launch with GIFTI files
findviz --gifti-left-func left.func.gii --gifti-right-func right.func.gii --gifti-left-mesh left.surf.gii --gifti-right-mesh right.surf.gii

# Launch with CIFTI files
findviz --cifti-dtseries data.dtseries.nii --cifti-left-mesh left.surf.gii --cifti-right-mesh right.surf.gii

# Add time series data
findviz --nifti-func func.nii.gz --timeseries timeseries1.csv timeseries2.csv
```

## Features

- **Multi-format Support**: Visualize NIFTI, GIFTI, and CIFTI neuroimaging data
- **Interactive Visualization**: Explore nifti data with orthogonal and montage views, and GIFTI and CIFTI data with 3D surface views
- **Time Series Visualization**: Visualize synchronized physiological, experimental design, and other time series data.
- **Preprocessing Tools**: Apply normalization, filtering, detrending, and smoothing
- **Analysis Tools**: Analysis functions for facilitating fMRI exploration and discovery
- **Customizable Display**: Adjust colormaps, thresholds, and visualization parameters
- **State Management**: Save and load visualization states

## Data Formats

FINDVIZ supports the following neuroimaging data formats:

- **NIFTI** (.nii, .nii.gz): 3D and 4D functional and anatomical brain images
- **GIFTI** (.gii): Surface-based brain data for left and right hemispheres
- **CIFTI** (.dtseries.nii): Combined surface and volume data
- **Time Series** (.csv, .txt): Custom time course data for visualization alongside fMRI data
- **Task Design** (.csv, .tsv): Experimental design matrices for visualization alongside fMRI data

## Documentation

Coming soon!

## Limitations

- FINDVIZ displays fMRI data in voxel coordinates, and does not support the overlay of images with different spatial resolutions, even in the same coordinate space (e.g. MNI152). Thus, anatomical and/or functional images should be resampled to the same resolution before uploading.

- FINDVIZ is not a preprocessing tool. Preprocessing options are limited to options that faciliate visualization, including normalization, detrending, smoothing, and temporal filtering. For end-to-end preprocessing, we recommend using more comprehensive tools such as FMRIPREP.



## Requirements

- Python 3.10+
- Flask 3.0.3+
- Matplotlib 3.9.2+
- Nilearn 0.10.4+
- Plotly 5.23.0+

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use FINDVIZ in your research, please cite:

```
Bolt, T. (2025). FINDVIZ: FMRI Interactive Navigation and Discovery Viewer. 
https://github.com/tsb46/fmri-findviz
```
