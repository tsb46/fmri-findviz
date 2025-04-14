---
layout: default
title: Preprocessing - FINDVIZ
---

# Preprocessing Guide

<div class="card">
  <div class="card-header">
    <h3>Overview</h3>
  </div>
  <div class="card-content">
    <p>FINDVIZ offers several preprocessing options to enhance your fMRI data visualization and analysis. While these tools are designed primarily to facilitate visualization rather than serve as a complete preprocessing pipeline, they can significantly improve the quality and interpretability of your visualizations.</p>
    <img src="https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/preprocessing_panel.png" alt="Preprocessing Panel" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  </div>
</div>

## Available Preprocessing Methods

<div class="format-section">
  <div class="format-card">
    <h3>Normalization</h3>
    <p>Normalization adjusts the intensity values of your fMRI data to make them more comparable across voxels, sessions, or subjects.</p>
    <h4>Options:</h4>
    <ul>
      <li><strong>Mean-center</strong>: Subtracts the mean from each voxel/vertex time course</li>
      <li><strong>Z-score</strong>: Normalizes each voxel/vertex time course to have zero mean and unit variance</li>
    </ul>
    <h4>Use Cases:</h4>
    <ul>
      <li>To remove baseline differences between voxels/vertices</li>
      <li>To make activation patterns more comparable across brain regions</li>
      <li>To prepare data for correlation or distance analysis</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Temporal Filtering</h3>
    <p>Temporal filtering removes unwanted frequency components from your fMRI time courses.</p>
    <h4>Options:</h4>
    <ul>
      <li><strong>High-pass filtering</strong>: Removes low-frequency trends (specify low-cut frequency)</li>
      <li><strong>Low-pass filtering</strong>: Removes high-frequency noise (specify high-cut frequency)</li>
      <li><strong>Bandpass filtering</strong>: Keeps frequencies within a specific range (specify both low-cut and high-cut)</li>
    </ul>
    <h4>Parameters:</h4>
    <ul>
      <li><strong>TR</strong>: The repetition time of your fMRI acquisition (in seconds)</li>
      <li><strong>Low-cut frequency</strong>: The lower frequency cutoff (in Hz)</li>
      <li><strong>High-cut frequency</strong>: The upper frequency cutoff (in Hz)</li>
    </ul>
    <h4>Use Cases:</h4>
    <ul>
      <li>To remove scanner drift (high-pass filter)</li>
      <li>To reduce high-frequency noise (low-pass filter)</li>
      <li>To focus on a specific frequency band of interest (bandpass filter)</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Detrending</h3>
    <p>Detrending removes linear trends from your fMRI time courses, which are often caused by scanner drift.</p>
    <h4>Use Cases:</h4>
    <ul>
      <li>To remove linear signal drift</li>
      <li>To prepare data for correlation analysis</li>
      <li>As a simpler alternative to high-pass filtering</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Spatial Smoothing</h3>
    <p>Spatial smoothing applies a Gaussian filter to your fMRI volumes, which can enhance the signal-to-noise ratio.</p>
    <h4>Parameters:</h4>
    <ul>
      <li><strong>FWHM</strong>: Full Width at Half Maximum of the Gaussian kernel (in mm)</li>
    </ul>
    <h4>Use Cases:</h4>
    <ul>
      <li>To increase signal-to-noise ratio</li>
      <li>To compensate for individual anatomical differences in group studies</li>
      <li>To meet assumptions of Gaussian random field theory for statistical analysis</li>
    </ul>
    <div class="alert alert-warning" style="margin-top: 10px; padding: 10px;">
      <p><strong>Note:</strong> Spatial smoothing is only available for NIFTI data, not for surface-based GIFTI input.</p>
    </div>
  </div>
</div>

## How to Apply Preprocessing

<div class="card">
  <div class="card-content">
    <div class="steps-container">
      <div class="step">Upload your fMRI data files (see <a href="file-upload.html">File Upload Guide</a>).</div>
      <div class="step">In the main interface, locate the <strong>Preprocessing Options</strong> panel in the left sidebar.</div>
      <div class="step">Enable the preprocessing methods you wish to apply by clicking the corresponding toggle switches.</div>
      <div class="step">Configure the parameters for each selected method.</div>
      <div class="step">Click the <strong>Preprocess</strong> button to apply the selected methods.</div>
      <div class="step">Wait for preprocessing to complete (a spinner will indicate progress).</div>
    </div>
  </div>
</div>

### Order of Processing

<div class="card">
  <div class="card-content">
    <p>When multiple preprocessing methods are selected, they are applied in the following order:</p>
    <ol>
      <li>Detrending</li>
      <li>Normalization</li>
      <li>Spatial Smoothing</li>
      <li>Temporal Filtering</li>
    </ol>
  </div>
</div>

## Preprocessing Time Series Data

<div class="card">
  <div class="card-header">
    <h3>Time Series Preprocessing</h3>
  </div>
  <div class="card-content">
    <p>In addition to preprocessing fMRI data, FINDVIZ also allows you to preprocess uploaded time series data:</p>
    <div class="steps-container">
      <div class="step">In the Time Course User Options panel, locate the Preprocessing Options section.</div>
      <div class="step">Select the time series you wish to preprocess from the dropdown menu.</div>
      <div class="step">Enable the desired preprocessing methods (normalization, filtering, detrending).</div>
      <div class="step">Configure the parameters for each method.</div>
      <div class="step">Click the <strong>Apply</strong> button to preprocess the selected time series.</div>
    </div>
  </div>
</div>

## Important Considerations

<div class="alert alert-warning">
  <h4>Key Points to Remember</h4>
  <ul>
    <li><strong>Brain Mask</strong>: For NIFTI data, a brain mask is required for many preprocessing operations. If you didn't upload a mask, some preprocessing options may be disabled.</li>
    <li><strong>Memory Usage</strong>: Preprocessing operations can be memory-intensive for large datasets. If you encounter performance issues, try processing a subset of your data or using less memory-intensive options.</li>
    <li><strong>Reversibility</strong>: If you're not satisfied with the preprocessing results, you can click the <strong>Reset</strong> button to restore the original data.</li>
    <li><strong>Validation</strong>: Always visually inspect your data after preprocessing to ensure the operations have had the desired effect.</li>
    <li><strong>TR Value</strong>: For temporal filtering, make sure to enter the correct TR value for your data acquisition.</li>
  </ul>
</div>

## Limitations

<div class="card">
  <div class="card-content">
    <div class="alert alert-info">
      <p>Remember that FINDVIZ is primarily a visualization tool. For comprehensive preprocessing of fMRI data, consider using dedicated preprocessing tools such as FMRIPREP, FSL, or SPM before importing into FINDVIZ for visualization and exploration.</p>
    </div>
  </div>
</div> 