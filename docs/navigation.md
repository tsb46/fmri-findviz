---
layout: default
title: Navigation - FINDVIZ
---

# Navigation Guide

This guide will help you navigate through the FINDVIZ interface and understand how to interact with the various visualization and control components.

## Main Interface Layout

After uploading your files, the FINDVIZ interface is organized into several key areas:

1. **Analytics Toolbox** - Located at the top of the screen, provides access to analysis tools
2. **FMRI Container** - The main visualization area for your fMRI data
   - **FMRI User Options** - Controls for visualization settings (left sidebar)
   - **FMRI Visualization** - The main display area for your brain data
3. **Time Course Container** - Displays time series data when available
   - **Time Course User Options** - Controls for time series visualization (left sidebar)
   - **Time Course Visualization** - Displays your time series data

## Navigation Controls

### FMRI Visualization Controls

For NIFTI data, you can navigate through the brain using:

- **Slice Selection** - Use sliders to change the currently displayed slice
- **Crosshair Navigation** - Click anywhere on a slice to position the crosshair
- **View Selection** - Switch between different view orientations:
  - Orthogonal view (axial, sagittal, coronal)
  - Montage view (grid display of multiple slices)

For GIFTI and CIFTI data, you can:

- **Rotate the 3D Surface** - Click and drag to rotate the brain surface
- **Zoom** - Use the scroll wheel to zoom in and out
- **Reset View** - Return to the default view orientation

### Time Course Navigation

When viewing time series data:

- **Time Point Selection** - Click on the time course graph to select a specific time point
- **Linked Navigation** - Time point selection is synchronized between the brain visualization and time course
- **Time Marker** - A vertical line indicates the currently selected time point
- **Range Selection** - Drag to select a range of time points for analysis
- **Zoom** - Use zoom controls to focus on specific parts of the time series

## Using the Analytics Toolbox

The Analytics Toolbox provides access to several analysis functions:

- **Transform** - Apply mathematical transformations to your data
- **Distance** - Calculate and visualize distances between time points
- **Compare** - Compare different regions or time points
- **Save Scene** - Save your current visualization state for later use

To use these tools:
1. Click on the desired tool button in the Analytics Toolbox
2. Configure the analysis parameters in the modal that appears
3. Click Apply to run the analysis
4. Use the trash icon button to remove an applied analysis

## Customizing Visualizations

### FMRI Visualization Options

In the FMRI User Options panel, you can adjust:

- **Colormap** - Change the color palette used for displaying values
- **Color Range** - Adjust the minimum and maximum values for color mapping
- **Opacity** - Change the transparency of the visualization
- **Display Mode** - Switch between different visualization modes

### Time Course Visualization Options

In the Time Course User Options panel, you can adjust:

- **Line Color** - Change the color of time series lines
- **Line Thickness** - Adjust the thickness of time series lines
- **Time Marker Settings** - Customize the appearance of the time marker
- **Display Options** - Show/hide specific time series

## Keyboard Shortcuts

FINDVIZ supports several keyboard shortcuts to enhance your navigation experience:

- **Arrow Keys** - Navigate through slices in NIFTI view
- **Spacebar** - Toggle between different view modes
- **R** - Reset the view to default
- **S** - Save the current scene

## Tips for Efficient Navigation

- Use the crosshair tool to synchronize views across different orientations
- Take advantage of the "Save Scene" feature to bookmark important findings
- Link time course and fMRI visualizations to explore temporal patterns
- Use the montage view to get a comprehensive overview of volumetric data
- Rotate 3D surfaces to examine activation patterns from different angles 