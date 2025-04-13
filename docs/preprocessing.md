---
layout: default
title: Preprocessing - FINDVIZ
---

# Preprocessing Guide

FINDVIZ offers several preprocessing options to enhance your fMRI data visualization and analysis. While these tools are designed primarily to facilitate visualization rather than serve as a complete preprocessing pipeline, they can significantly improve the quality and interpretability of your visualizations.

## Available Preprocessing Methods

FINDVIZ provides the following preprocessing options:

### Normalization

Normalization adjusts the intensity values of your fMRI data to make them more comparable across voxels, sessions, or subjects.

**Options:**
- **Mean-center**: Subtracts the mean from each voxel/vertex time course
- **Z-score**: Normalizes each voxel/vertex time course to have zero mean and unit variance

**Use Cases:**
- To remove baseline differences between voxels/vertices
- To make activation patterns more comparable across brain regions
- To prepare data for correlation or distance analysis

### Temporal Filtering

Temporal filtering removes unwanted frequency components from your fMRI time courses.

**Options:**
- **High-pass filtering**: Removes low-frequency trends (specify low-cut frequency)
- **Low-pass filtering**: Removes high-frequency noise (specify high-cut frequency)
- **Bandpass filtering**: Keeps frequencies within a specific range (specify both low-cut and high-cut)

**Parameters:**
- **TR**: The repetition time of your fMRI acquisition (in seconds)
- **Low-cut frequency**: The lower frequency cutoff (in Hz)
- **High-cut frequency**: The upper frequency cutoff (in Hz)

**Use Cases:**
- To remove scanner drift (high-pass filter)
- To reduce high-frequency noise (low-pass filter)
- To focus on a specific frequency band of interest (bandpass filter)

### Detrending

Detrending removes linear trends from your fMRI time courses, which are often caused by scanner drift.

**Use Cases:**
- To remove linear signal drift
- To prepare data for correlation analysis
- As a simpler alternative to high-pass filtering

### Spatial Smoothing

Spatial smoothing applies a Gaussian filter to your fMRI volumes, which can enhance the signal-to-noise ratio.

**Parameters:**
- **FWHM**: Full Width at Half Maximum of the Gaussian kernel (in mm)

**Use Cases:**
- To increase signal-to-noise ratio
- To compensate for individual anatomical differences in group studies
- To meet assumptions of Gaussian random field theory for statistical analysis

**Note:** Spatial smoothing is only available for NIFTI data, not for surface-based GIFTI input.

## How to Apply Preprocessing

1. Upload your fMRI data files (see [File Upload Guide](file-upload.html)).
2. In the main interface, locate the **Preprocessing Options** panel in the left sidebar.
3. Enable the preprocessing methods you wish to apply by clicking the corresponding toggle switches.
4. Configure the parameters for each selected method.
5. Click the **Preprocess** button to apply the selected methods.
6. Wait for preprocessing to complete (a spinner will indicate progress).

### Order of Processing

When multiple preprocessing methods are selected, they are applied in the following order:

1. Detrending
2. Normalization
3. Spatial Smoothing
4. Temporal Filtering

## Preprocessing Time Series Data

In addition to preprocessing fMRI data, FINDVIZ also allows you to preprocess uploaded time series data:

1. In the Time Course User Options panel, locate the Preprocessing Options section.
2. Select the time series you wish to preprocess from the dropdown menu.
3. Enable the desired preprocessing methods (normalization, filtering, detrending).
4. Configure the parameters for each method.
5. Click the **Apply** button to preprocess the selected time series.

## Important Considerations

- **Brain Mask**: For NIFTI data, a brain mask is required for many preprocessing operations. If you didn't upload a mask, some preprocessing options may be disabled.
- **Memory Usage**: Preprocessing operations can be memory-intensive for large datasets. If you encounter performance issues, try processing a subset of your data or using less memory-intensive options.
- **Reversibility**: If you're not satisfied with the preprocessing results, you can click the **Reset** button to restore the original data.
- **Validation**: Always visually inspect your data after preprocessing to ensure the operations have had the desired effect.
- **TR Value**: For temporal filtering, make sure to enter the correct TR value for your data acquisition.

## Limitations

Remember that FINDVIZ is primarily a visualization tool. For comprehensive preprocessing of fMRI data, consider using dedicated preprocessing tools such as FMRIPREP, FSL, or SPM before importing into FINDVIZ for visualization and exploration. 