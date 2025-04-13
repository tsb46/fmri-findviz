---
layout: default
title: FINDVIZ - FMRI Interactive Navigation and Discovery Viewer
---
<img src="https://raw.githubusercontent.com/tsb46/fmri-findviz/main/findviz/static/images/FIND.png" width="200" height="200" alt="findviz-logo">

# FINDVIZ: FMRI Interactive Navigation and Discovery Viewer

FINDVIZ is a browser-based visualization tool for visual exploration of fMRI data with a focus on pattern discovery. It provides an intuitive interface for exploring and analyzing fMRI datasets, supporting multiple neuroimaging file formats and a range of visualization options.

## Features

- **Multi-format Support**: Visualize NIFTI, GIFTI, and CIFTI neuroimaging data
- **Interactive Visualization**: Explore nifti data with orthogonal and montage views, and GIFTI and CIFTI data with 3D surface views
- **Time Series Visualization**: Visualize synchronized physiological, experimental design, and other time series data
- **Preprocessing Tools**: Apply normalization, filtering, detrending, and smoothing
- **Analysis Tools**: Analysis functions for facilitating fMRI exploration and discovery
- **Customizable Display**: Adjust colormaps, thresholds, and visualization parameters
- **State Management**: Save and load visualization states

## Getting Started

FINDVIZ is installabe through PyPi (via pip):

```bash
pip install findviz
```

 Follow the links below to learn how to:

- [Upload Files](file-upload.html) - Learn how to upload and use different file formats
- [Navigate the Interface](navigation.html) - Discover how to navigate and control the FINDVIZ interface
- [Preprocess Data](preprocessing.html) - Learn about preprocessing options for your fMRI data
- [Analyze Data](analysis.html) - Explore the analysis tools available in FINDVIZ

## General Advice

- **Browser Compatibility**: FINDVIZ is tested and optimized for Google Chrome (v134 or newer).
- **Data Preparation**: For best results, ensure that all data files (functional, anatomical, and mask) have the same spatial resolution.
- **Session Management**: Use the "Save Scene" feature to save your visualization state and continue your work later.
- **Memory Usage**: FINDVIZ stores all fMRI data in-memory (RAM). For large datasets, ensure your computer has sufficient RAM to handle the data load. Typical 4D fMRI datasets can range from hundreds of MB to several GB in size.

## Limitations

- FINDVIZ displays fMRI data in voxel coordinates and does not support the overlay of images with different spatial resolutions, even in the same coordinate space (e.g., MNI152). Anatomical and/or functional images should be resampled to the same resolution before uploading.
- FINDVIZ is not a comprehensive preprocessing tool. Preprocessing options are limited to those that facilitate visualization. For end-to-end preprocessing, we recommend using more comprehensive tools such as FMRIPREP. 