---
layout: default
title: Analysis - FINDVIZ
---

# Analysis Guide

<div class="card">
  <div class="card-header">
    <h3>Overview</h3>
  </div>
  <div class="card-content">
    <p>FINDVIZ offers several analysis tools to help you explore patterns in your fMRI data. This guide explains the available analysis methods and how to use them effectively.</p>
    <img src="https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/analytics_toolbox.png" alt="Analytics Toolbox" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  </div>
</div>

## Analysis Tools Overview

<div class="card">
  <div class="card-content">
    <p>The analysis tools in FINDVIZ are accessible through the Analytics Toolbox at the top of the interface. These tools are designed to facilitate exploratory data analysis and pattern discovery in your fMRI data.</p>
  </div>
</div>

## Transform Tool

<div class="card">
  <div class="card-header">
    <h3>Transform Tool</h3>
  </div>
  <div class="card-content">
    <p>The Transform tool allows you to apply mathematical transformations to your fMRI data, creating new visualizations that highlight specific aspects of the data.</p>
    
    <h4>Available Transformations</h4>
    <div class="format-section">
      <div class="format-card">
        <h3>Averaging</h3>
        <p>Calculate the average across a range of time points</p>
      </div>
      <div class="format-card">
        <h3>Correlation</h3>
        <p>Compute correlation between a seed region and all other voxels/vertices</p>
      </div>
      <div class="format-card">
        <h3>Distance Metric</h3>
        <p>Calculate distance metrics between time points</p>
      </div>
    </div>
    
    <h4>How to Use the Transform Tool</h4>
    <div class="steps-container">
      <div class="step">Click the <strong>Transform</strong> button in the Analytics Toolbox.</div>
      <div class="step">
        In the Transform modal:
        <ul>
          <li>Select the type of transformation (Average, Correlation, Distance)</li>
          <li>Configure the parameters specific to the selected transformation</li>
          <li>Click <strong>Apply Transform</strong> to run the analysis</li>
        </ul>
      </div>
    </div>
  </div>
</div>

## Transformation Methods

<div class="format-section">
  <div class="format-card">
    <h3>Averaging Transformation</h3>
    <p>The Averaging transformation calculates the mean value across specified time points.</p>
    
    <h4>Parameters:</h4>
    <ul>
      <li><strong>Time Point Range</strong>: Select a range of time points to average</li>
      <li><strong>Custom Time Points</strong>: Specify individual time points to include in the average</li>
    </ul>
    
    <h4>Use Cases:</h4>
    <ul>
      <li>Create a summary image across a task block</li>
      <li>Reduce noise by averaging multiple time points</li>
      <li>Compare average activation between different task conditions</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Correlation Transformation</h3>
    <p>The Correlation transformation calculates the correlation between a seed region and all other voxels/vertices.</p>
    
    <h4>Parameters:</h4>
    <ul>
      <li><strong>Seed Selection Method</strong>: Choose how to select the seed region (coordinates, peak voxel, etc.)</li>
      <li><strong>Correlation Method</strong>: Pearson or Spearman correlation</li>
      <li><strong>Time Point Range</strong>: Limit correlation calculation to specific time points</li>
    </ul>
    
    <h4>Use Cases:</h4>
    <ul>
      <li>Identify functionally connected brain regions</li>
      <li>Find voxels/vertices with similar time courses</li>
      <li>Map functional networks based on temporal correlation</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Distance Metric Transformation</h3>
    <p>The Distance transformation calculates various distance metrics between time points or regions.</p>
    
    <h4>Parameters:</h4>
    <ul>
      <li><strong>Distance Metric</strong>: Select the distance measure (Euclidean, Manhattan, correlation-based)</li>
      <li><strong>Reference Time Point</strong>: Choose a reference time point for comparison</li>
    </ul>
    
    <h4>Use Cases:</h4>
    <ul>
      <li>Identify similar or dissimilar patterns across time</li>
      <li>Detect state transitions in the brain</li>
      <li>Compare spatial patterns between different time points</li>
    </ul>
  </div>
</div>

## Distance Plot

<div class="card">
  <div class="card-header">
    <h3>Distance Plot Tool</h3>
  </div>
  <div class="card-content">
    <p>The Distance Plot tool creates a visualization of the distances between all pairs of time points, helping you identify patterns and changes over time.</p>
    
    <h4>How to Use the Distance Plot</h4>
    <div class="steps-container">
      <div class="step">Click the <strong>Distance</strong> button in the Analytics Toolbox.</div>
      <div class="step">
        In the Distance modal:
        <ul>
          <li>Select the distance metric to use</li>
          <li>Configure display options</li>
          <li>Click <strong>Generate Distance Plot</strong> to create the visualization</li>
        </ul>
      </div>
    </div>
    
    <h4>Customization Options:</h4>
    <ul>
      <li><strong>Colormap</strong>: Change the color scheme of the distance plot</li>
      <li><strong>Color Range</strong>: Adjust the scaling of the color map</li>
      <li><strong>Time Marker Width</strong>: Set the width of the time marker line</li>
      <li><strong>Time Marker Opacity</strong>: Adjust the transparency of the time marker</li>
    </ul>
    
    <h4>Use Cases:</h4>
    <ul>
      <li>Identify repeating patterns in fMRI data</li>
      <li>Detect state transitions in resting-state data</li>
      <li>Visualize temporal structure in task-based experiments</li>
    </ul>
    
    <img src="https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/distance_plot.png" alt="Distance Plot Example" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-top: 1rem;">
  </div>
</div>

## Compare Tool

<div class="card">
  <div class="card-header">
    <h3>Compare Tool</h3>
  </div>
  <div class="card-content">
    <p>The Compare tool allows you to directly compare different aspects of your data, such as comparing different time points or regions.</p>
    
    <h4>How to Use the Compare Tool</h4>
    <div class="steps-container">
      <div class="step">Click the <strong>Compare</strong> button in the Analytics Toolbox.</div>
      <div class="step">
        In the Compare modal:
        <ul>
          <li>Select what you want to compare (time points, regions, etc.)</li>
          <li>Set the comparison parameters</li>
          <li>Click <strong>Apply Comparison</strong> to generate the result</li>
        </ul>
      </div>
    </div>
    
    <h4>Use Cases:</h4>
    <ul>
      <li>Compare activation patterns between different task conditions</li>
      <li>Visualize differences between task and rest periods</li>
      <li>Examine changes in connectivity patterns over time</li>
    </ul>
  </div>
</div>

## Save Scene

<div class="card">
  <div class="card-header">
    <h3>Save Scene Function</h3>
  </div>
  <div class="card-content">
    <p>The Save Scene function allows you to save your current visualization state, including all applied transformations and analysis results, for later use.</p>
    
    <div class="format-section">
      <div class="format-card">
        <h3>How to Save a Scene</h3>
        <div class="steps-container">
          <div class="step">Click the <strong>Save Scene</strong> button in the Analytics Toolbox.</div>
          <div class="step">
            In the Save Scene modal:
            <ul>
              <li>Enter a name for the scene (optional)</li>
              <li>Click <strong>Save</strong> to download the scene file</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="format-card">
        <h3>How to Load a Scene</h3>
        <div class="steps-container">
          <div class="step">Click the <strong>Upload Scene</strong> button in the file upload modal.</div>
          <div class="step">Select a previously saved scene file.</div>
          <div class="step">The scene will be loaded with all its visualization settings and analysis results.</div>
        </div>
      </div>
    </div>
  </div>
</div>

## Tips for Effective Analysis

<div class="card">
  <div class="card-header">
    <h3>Best Practices</h3>
  </div>
  <div class="card-content">
    <div class="format-section">
      <div class="format-card">
        <h3>Preparation</h3>
        <ul>
          <li><strong>Preprocess your data</strong>: Apply appropriate preprocessing steps before analysis to improve results.</li>
          <li><strong>Use multiple approaches</strong>: Combine different analysis methods to gain more comprehensive insights.</li>
        </ul>
      </div>
      
      <div class="format-card">
        <h3>Workflow</h3>
        <ul>
          <li><strong>Save important findings</strong>: Use the Save Scene feature to preserve significant results.</li>
          <li><strong>Validate patterns</strong>: Cross-check findings using different analysis methods or subsets of data.</li>
        </ul>
      </div>
      
      <div class="format-card">
        <h3>Exploration</h3>
        <ul>
          <li><strong>Explore interactively</strong>: Use the time course selection to examine specific time points of interest.</li>
          <li><strong>Combine with time series</strong>: Link fMRI visualizations with time series data to understand temporal patterns.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

## Limitations

<div class="alert alert-warning">
  <h4>Important Considerations</h4>
  <ul>
    <li>Analysis tools in FINDVIZ are designed for exploration, not statistical hypothesis testing.</li>
    <li>For NIFTI data, a brain mask is required for most analysis functions.</li>
    <li>Some analyses may be computationally intensive for large datasets.</li>
    <li>Results should be interpreted with caution and validated with appropriate statistical methods when used for research purposes.</li>
  </ul>
</div> 