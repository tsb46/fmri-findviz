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
    <p>FINDVIZ offers several preprocessing options for your fMRI and time course data. These tools are not meant to serve as a complete preprocessing pipeline, but are designed to facilitate enhanced visualization and pattern discovery. See our <a href="{{ site.baseurl }}/index.html#data-preparation">data preparation</a> section for more information on preprocessing your data before uploading to FINDVIZ.</p>
  </div>
</div>

## Available Preprocessing Methods

<div class="card">
    <div class="card-header">
        <h3>Preprocessing Methods</h3>
    </div>
    <div class='card-content'>
        <ul class='feature-list'>
            <li>
                Linear Detrending
            </li>
            <li>
                Normalization
            </li>
            <li>
                Temporal Filtering
            </li>
            <li>
                Spatial Smoothing
            </li>
        </ul>
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