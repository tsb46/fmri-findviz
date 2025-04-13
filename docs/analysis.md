---
layout: default
title: Analysis - FINDVIZ
---

# Analysis Guide

FINDVIZ offers several analysis tools to help you explore patterns in your fMRI data. This guide explains the available analysis methods and how to use them effectively.

## Analysis Tools Overview

The analysis tools in FINDVIZ are accessible through the Analytics Toolbox at the top of the interface. These tools are designed to facilitate exploratory data analysis and pattern discovery in your fMRI data.

## Transform Tool

The Transform tool allows you to apply mathematical transformations to your fMRI data, creating new visualizations that highlight specific aspects of the data.

### Available Transformations

- **Averaging**: Calculate the average across a range of time points
- **Correlation**: Compute correlation between a seed region and all other voxels/vertices
- **Distance Metric**: Calculate distance metrics between time points

### How to Use the Transform Tool

1. Click the **Transform** button in the Analytics Toolbox.
2. In the Transform modal:
   - Select the type of transformation (Average, Correlation, Distance)
   - Configure the parameters specific to the selected transformation
   - Click **Apply Transform** to run the analysis

### Averaging Transformation

The Averaging transformation calculates the mean value across specified time points.

**Parameters:**
- **Time Point Range**: Select a range of time points to average
- **Custom Time Points**: Specify individual time points to include in the average

**Use Cases:**
- Create a summary image across a task block
- Reduce noise by averaging multiple time points
- Compare average activation between different task conditions

### Correlation Transformation

The Correlation transformation calculates the correlation between a seed region and all other voxels/vertices.

**Parameters:**
- **Seed Selection Method**: Choose how to select the seed region (coordinates, peak voxel, etc.)
- **Correlation Method**: Pearson or Spearman correlation
- **Time Point Range**: Limit correlation calculation to specific time points

**Use Cases:**
- Identify functionally connected brain regions
- Find voxels/vertices with similar time courses
- Map functional networks based on temporal correlation

### Distance Metric Transformation

The Distance transformation calculates various distance metrics between time points or regions.

**Parameters:**
- **Distance Metric**: Select the distance measure (Euclidean, Manhattan, correlation-based)
- **Reference Time Point**: Choose a reference time point for comparison

**Use Cases:**
- Identify similar or dissimilar patterns across time
- Detect state transitions in the brain
- Compare spatial patterns between different time points

## Distance Plot

The Distance Plot tool creates a visualization of the distances between all pairs of time points, helping you identify patterns and changes over time.

### How to Use the Distance Plot

1. Click the **Distance** button in the Analytics Toolbox.
2. In the Distance modal:
   - Select the distance metric to use
   - Configure display options
   - Click **Generate Distance Plot** to create the visualization

**Customization Options:**
- **Colormap**: Change the color scheme of the distance plot
- **Color Range**: Adjust the scaling of the color map
- **Time Marker Width**: Set the width of the time marker line
- **Time Marker Opacity**: Adjust the transparency of the time marker

**Use Cases:**
- Identify repeating patterns in fMRI data
- Detect state transitions in resting-state data
- Visualize temporal structure in task-based experiments

## Compare Tool

The Compare tool allows you to directly compare different aspects of your data, such as comparing different time points or regions.

### How to Use the Compare Tool

1. Click the **Compare** button in the Analytics Toolbox.
2. In the Compare modal:
   - Select what you want to compare (time points, regions, etc.)
   - Set the comparison parameters
   - Click **Apply Comparison** to generate the result

**Use Cases:**
- Compare activation patterns between different task conditions
- Visualize differences between task and rest periods
- Examine changes in connectivity patterns over time

## Save Scene

The Save Scene function allows you to save your current visualization state, including all applied transformations and analysis results, for later use.

### How to Save a Scene

1. Click the **Save Scene** button in the Analytics Toolbox.
2. In the Save Scene modal:
   - Enter a name for the scene (optional)
   - Click **Save** to download the scene file

### How to Load a Scene

1. Click the **Upload Scene** button in the file upload modal.
2. Select a previously saved scene file.
3. The scene will be loaded with all its visualization settings and analysis results.

## Tips for Effective Analysis

- **Preprocess your data**: Apply appropriate preprocessing steps before analysis to improve results.
- **Use multiple approaches**: Combine different analysis methods to gain more comprehensive insights.
- **Save important findings**: Use the Save Scene feature to preserve significant results.
- **Validate patterns**: Cross-check findings using different analysis methods or subsets of data.
- **Explore interactively**: Use the time course selection to examine specific time points of interest.
- **Combine with time series**: Link fMRI visualizations with time series data to understand temporal patterns.

## Limitations

- Analysis tools in FINDVIZ are designed for exploration, not statistical hypothesis testing.
- For NIFTI data, a brain mask is required for most analysis functions.
- Some analyses may be computationally intensive for large datasets.
- Results should be interpreted with caution and validated with appropriate statistical methods when used for research purposes. 