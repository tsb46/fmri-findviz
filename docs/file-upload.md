---
layout: default
title: File Upload - FINDVIZ
---

# File Upload Guide

FINDVIZ supports multiple fMRI file formats. This guide explains how to upload files and what formats are supported.

<img src='https://github.com/tsb46/fmri-findviz-misc/blob/main/gifs/upload.gif' width=500 height=300>

## Supported File Formats

FINDVIZ supports uploading of three fMRI file formats:

### NIFTI (.nii, .nii.gz)
- **Functional files**: 4D functional brain images
- **Anatomical files**: 3D structural brain images
- **Brain mask files**: Binary masks for brain extraction

<img src='https://github.com/tsb46/fmri-findviz-misc/blob/main/pics/' width=500 height=300>


### GIFTI (.gii)
- **Functional files**: Surface-based functional data for left and right hemispheres (func.gii)
- **Surface geometry files**: 3D representations of the brain's outer surface (surf.gii)

### CIFTI (.dtseries.nii)
- **Dense time series files**: Combined surface and volume data 
- **Surface geometry files**: Required for proper visualization of CIFTI data

## Time Course Files

In addition to fMRI data, FINDVIZ allows you to upload:
- **Time series files** (.csv, .txt): Custom time course data for visualization alongside fMRI data
- **Task design files** (.csv, .tsv): Experimental design matrices for visualization

## How to Upload Files

1. Launch FINDVIZ using the command `findviz` in your terminal.
2. Click the **Upload Files** button on the welcome screen.
3. In the upload modal:
   - Select the appropriate tab for your file format (NIFTI, GIFTI, or CIFTI).
   - Upload the required files for your chosen format.
   - Optionally add time series files or task design files.

### NIFTI Upload

For NIFTI files:
1. Select the **NIFTI** tab in the upload modal.
2. Upload a **Functional File** (.nii or .nii.gz) - this is required.
3. Optionally upload an **Anatomical File** for structural reference.
4. Optionally upload a **Brain Mask File** to mask non-brain tissue (required for some preprocessing and analysis features).

### GIFTI Upload

For GIFTI files:
1. Select the **GIFTI** tab in the upload modal.
2. Upload **Left Hemisphere Functional File** (func.gii) and **Surface Geometry File** (surf.gii).
3. Upload **Right Hemisphere Functional File** (func.gii) and **Surface Geometry File** (surf.gii).

### CIFTI Upload

For CIFTI files:
1. Select the **CIFTI** tab in the upload modal.
2. Upload a **Dense Time Series File** (.dtseries.nii).
3. Upload **Left Hemisphere Surface Geometry File** (surf.gii) and **Right Hemisphere Surface Geometry File** (surf.gii).

## Time Course Files

To add time course data:
1. Click the **Add Another File** button in the Time Course Files section.
2. Upload .csv or .txt files containing time course data.
3. These files should:
   - Have the same number of time points as your fMRI data
   - Be arranged in one column
   - Be temporally aligned with your fMRI data

## Task Design Files

To add a task design file:
1. Upload a .csv or .tsv file in the Task Design File section.
2. The file must contain:
   - An 'onset' column with values in seconds
   - A 'duration' column with values in seconds
   - Optionally, a 'trial_type' column for multiple event types
3. Specify the TR (repetition time) value.
4. Specify the Slicetime Reference value (default is 0.5).

## Important Considerations

- Ensure all files have compatible dimensions and resolutions.
- For NIFTI files, the anatomical and functional images should have the same resolution and field of view.
- Brain masks should be binary (1 for brain tissue, 0 for non-brain tissue).
- Time series files must match the number of time points in your fMRI data.

## Command Line Upload (Alternative)

You can also upload files directly from the command line:

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

# Developer Notes

FINDVIZ uses the Python neuroimaging library [nibabel](https://nipy.org/nibabel/) to read and write neuroimaging files. This allows FINDVIZ to support a variety of file formats commonly used in neuroimaging research.