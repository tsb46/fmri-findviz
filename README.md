<div style="display: flex; align-items: center; gap: 20px;">
<img src="findviz/static/images/FIND.png" width="100" height="100" alt="findviz-logo">
<h1>FINDVIZ: FMRI Interactive Navigation and Discovery Viewer</h1>
</div>

## Introduction

FINDVIZ was created as a user-friendly tool for incorporating visual exploration into fMRI research methodology. While the field has developed sophisticated analysis techniques, researchers often don't spend enough time directly visualizing and exploring their data before applying statistical models.

Traditional neuroimaging visualization platforms, while powerful, are often designed as general-purpose medical imaging tools that lack intuitive interfaces for pattern discovery in fMRI data specifically. FINDVIZ provides a framework that makes visual exploration of complex spatiotemporal patterns accessible and efficient.

By enabling researchers to interactively navigate through their data, FINDVIZ supports:
- Discovery of unexpected patterns that might be missed by hypothesis-driven analyses
- Intuitive understanding of signal characteristics across brain regions
- Exploration of relationships between fMRI data and simultaneous recorded physiological data, head motion, and/or experimental design.

This visualization-driven approach complements traditional analysis pipelines and can lead to more informed hypotheses and interpretations of fMRI results.

## Installation

### Using pip

```bash
pip install findviz
```

## Quick Start

To launch the application, run the following command in your terminal:

```bash
findviz
```

This will launch the application in your default browser. FINDVIZ was tested on Google Chrome (v134). We recommend using Chrome for the best experience. 

### Command Line Interface

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

For detailed documentation, visit...

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
