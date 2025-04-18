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
        <p>Preprocessing tools can be accessed from the fMRI and time course preprocessing panels in the interface.</p>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div>
                <h4>FMRI Panel</h4>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/preprocess_tools.png' alt= "plot options toolbar" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); width: 48%;">
            </div>
            <div>
                <h4>Timecourse Panel</h4>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/timecourse_preprocess.png' alt= "plot options toolbar" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); width: 48%;">
            </div>
        </div>
        <ul class='feature-list' style='margin-top: 1em;'>
            <li>
                <h4>Linear Detrending</h4>
                <ul>
                    <li>Removes linear trends from fMRI or time series data using a linear least-squares fit.</li>
                    <li><strong>Use when:</strong> Your data shows gradual drift over time that could obscure patterns of interest</li>
                    <li><strong>Implementation:</strong> linear detrending of time courses is performed using SciPy (v1.13.1) <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.detrend.html">detrend</a> algorithm</li>
                </ul>
            </li>
            <li>
                <h4>Time Series Normalization</h4>
                <ul>
                    <li>Mean-center or z-score fMRI or time series data using a linear least-squares fit.</li>
                    <li><strong>Use when:</strong> You need to standardize signal amplitudes across different regions, or when comparing time series with different units or scales</li>
                    <li><strong>Implementation:</strong> mean-centering and z-scoring is perfomed with custom Python algorithms.</li>
                </ul>
            </li>
            <li>
                <h4>Temporal Filtering</h4>
                <ul>
                    <li>Band-pass, low-pass or high-pass fmri or time series data. </li>
                    <li><strong>Parameters</strong>: <b>TR</b> (repetition time of fMRI data), <b>low-cut</b> in hertz (hz), <b>high-cut</b> in hertz(hz). Specify only <b>high-cut</b> to low-pass filter (filter out frequencies above the cut-off). Specify only <b>low-cut</b> to high-pass filter (filter out frequencies below the cut-off). Specify <b>high-cut</b> and <b>low-cut</b> to bandpass filter (filter out frequencies outside the frequencies of the low-cut, high-cut range).</li>
                    <li><strong>Use when:</strong> You want to isolate specific frequency components of your signal, such as removing high-frequency noise or low-frequency drift, or focusing on a specific frequency band of interest (e.g., 0.01-0.1 Hz for resting-state fMRI)</li>
                    <li><strong>Implementation:</strong> Temporal filtering is performed using Nilearn's (v0.10.4) <a href="https://nilearn.github.io/dev/modules/generated/nilearn.signal.butterworth.html">Butterworth</a> filter function (5th order), which applies a zero-phase forward and backward filter to preserve timing relationships in the data</li>
                </ul>
            </li>
            <li>
                Spatial Smoothing
                <div class='alert alert-warning'>
                    <p>Surface smoothing of CIFTI/GIFTI surface plots are not currently supported.</p>
                </div>
                <ul>
                    <li>Gaussian spatial filtering of NIFTI fMRI images </li>
                    <li><strong>Parameters</strong>: <b>FWHM</b> - full-width at half maximum, in millimeters </li>
                    <li><strong>Use when:</strong> You want to increase signal-to-noise ratio of your NIFTI images.</li>
                    <li><strong>Implementation:</strong> Spatial smoothing is performed using Nilearn's (v0.10.4) <a href="https://nilearn.github.io/dev/modules/generated/nilearn.image.smooth_img.html">smooth_img</a> function.</li>
                </ul>
            </li>
        </ul>
    </div>
</div>


### Order of Processing

<div class="card">
  <div class="card-content">
    <p>When multiple preprocessing methods are selected, they are applied in the following order:</p>
    <ol>
      <li>Linear Detrending</li>
      <li>Temporal Filtering</li>
      <li>Time Series Normalization</li>
      <li>Spatial Smoothing</li>
    </ol>
  </div>
</div>

## Important Considerations

<div class="alert alert-warning">
  <h4>Key Points to Remember</h4>
  <ul>
    <li><strong>Brain Mask</strong>: For NIFTI data, a brain mask is required for all preprocessing operations. If you didn't upload a mask, all preprocessing options are disabled.</li>
    <li><strong>Reversibility</strong>: after completion of preprocessing, preprocessed data is directly displayed in the plot (time course or fMRI plots). Only one preprocessed state is stored in FINDVIZ at a time. To restore the original data you can click the <strong>Reset</strong> button.</li>
  </ul>
</div>

## Limitations

<div class="card">
  <div class="card-content">
    <div class="alert alert-info">
      <p>Remember that FINDVIZ is primarily a visualization tool. For comprehensive preprocessing of fMRI data, consider using a dedicated <a href="{{ site.baseurl }}/index.html#data-preparation">fMRI preprocessing software</a></p>
    </div>
  </div>
</div> 