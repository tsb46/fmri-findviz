---
layout: default
title: FINDVIZ - FMRI Interactive Navigation and Discovery Viewer
---

<div class="card" style="text-align: center; padding-top: 2rem;">
  <img src="https://raw.githubusercontent.com/tsb46/fmri-findviz/main/findviz/static/images/FIND.png" width="200" height="200" alt="findviz-logo" style="border-radius: 8px; margin-bottom: 1rem;">
  <div class="card-header">
    <h1>FINDVIZ: FMRI Interactive Navigation and Discovery Viewer</h1>
  </div>
  <div class="card-content">
    <p>FINDVIZ is a browser-based visualization tool for visual exploration of fMRI data with a focus on pattern discovery. It provides an intuitive interface for exploring and analyzing fMRI datasets, supporting multiple neuroimaging file formats and a range of visualization options.</p>
  </div>
</div>

## Features {#features}

<div class="format-section" id='findviz-features'>
  <div class="format-card">
    <h3>Data Support</h3>
    <ul>
      <li><strong>Multi-format Support</strong>: Visualize NIFTI, GIFTI, and CIFTI neuroimaging data</li>
      <li><strong>Time Series Visualization</strong>: Visualize synchronized physiological, experimental design, and other time series data</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Visualization Tools</h3>
    <ul>
      <li><strong>Interactive Visualization</strong>: Explore NIFTI data with orthogonal and montage views, and GIFTI/CIFTI data with 3D surface views</li>
      <li><strong>Customizable Display</strong>: Adjust colormaps, thresholds, and visualization parameters</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Analysis & Processing</h3>
    <ul>
      <li><strong>Preprocessing Tools</strong>: Apply time course normalization, filtering, detrending, and spatial smoothing</li>
      <li><strong>Analysis Tools</strong>: Analysis functions for facilitating fMRI exploration and discovery</li>
      <li><strong>State Management</strong>: Save and load visualization states</li>
    </ul>
  </div>
</div>

## Getting Started {#getting-started}

<div class="card" id='getting-started'>
  <div class="card-header">
    <h3>Installation</h3>
  </div>
  <div class="card-content">
    <p>FINDVIZ is installable through PyPi (via pip):</p>
    <div class="code-block">
      <code>pip install findviz</code>
    </div>
    
    <h4>Documentation</h4>
    <p>Follow the links below to learn how to use FINDVIZ:</p>
    <div class="steps-container">
      <div class="step"><a href="{{ site.baseurl }}/file-upload.html">Upload Files</a> - Learn how to upload and use different file formats</div>
      <div class="step"><a href="{{ site.baseurl }}/navigation.html">Navigate the Interface</a> - Discover how to navigate and control the FINDVIZ interface</div>
      <div class="step"><a href="{{ site.baseurl }}/preprocessing.html">Preprocess Data</a> - Learn about preprocessing options to facilitate visualization of fMRI data</div>
      <div class="step"><a href="{{ site.baseurl }}/analysis.html">Analyze Data</a> - Explore the analysis tools available in FINDVIZ</div>
    </div>
  </div>
</div>

## Data Preparation {#data-preparation}

<div class="card" id='data-preparation'>
  <div class="card-content">
    <p>FINDVIZ does not implement end-to-end volume- or surface-based preprocessing pipelines. We recommend that minimal preprocessing be performed on your fMRI data before visualizing with FINDVIZ. This may include motion correction, slice-time-correction, susceptibility distortion correction, and/or normalization to a standard space (e.g. MNI152). For surface visualization, volume-to-surface preprocessing should have been previously performed.</p>
    
    <p>These preprocessing steps are available in popular fMRI preprocessing platforms:</p>
    
    <div class="format-section">
      <div class="format-card">
        <h3><a href="https://fmriprep.org/">FMRIPREP</a></h3>
        <p>An easily-accessible, robust, minimal fMRI preprocessing pipeline</p>
      </div>
      
      <div class="format-card">
        <h3><a href="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/">FSL</a></h3>
        <p>A comprehensive library of analysis tools for FMRI, MRI and DTI brain imaging data</p>
      </div>
      
      <div class="format-card">
        <h3><a href="https://surfer.nmr.mgh.harvard.edu/">FreeSurfer</a></h3>
        <p>A software suite for processing and analyzing human brain MRI images, including cortical surface reconstruction</p>
      </div>
      
      <div class="format-card">
        <h3><a href="https://www.humanconnectome.org/software/connectome-workbench">Connectome Workbench</a></h3>
        <p>A visualization and discovery tool for human brain data</p>
      </div>
    </div>
  </div>
</div>

## General Advice {#general-advice}

<div class="alert alert-info" id='best-practices'>
  <h4>Best Practices</h4>
  <ul>
    <li><strong>Browser Compatibility</strong>: FINDVIZ is tested and optimized for Google Chrome (v134 or newer).</li>
    <li><strong>Session Management</strong>: Use the "Save Scene" feature to save your visualization state and continue your work later.</li>
    <li><strong>Memory Usage</strong>: FINDVIZ stores all fMRI data in-memory (RAM). For large datasets, ensure your computer has sufficient RAM to handle the data load. Typical 4D fMRI datasets can range from hundreds of MB to several GB in size.</li>
  </ul>
</div>

## Limitations {#limitations}

<div class="alert alert-warning">
  <h4>Important Considerations</h4>
  <ul>
    <li>FINDVIZ displays fMRI data in voxel coordinates and does not support the overlay of images with different spatial resolutions, even in the same coordinate space (e.g., MNI152). Anatomical and/or functional images should be resampled to the same resolution before uploading.</li>
    <li>FINDVIZ is not a comprehensive preprocessing tool. Preprocessing options are limited to those that facilitate visualization. For end-to-end preprocessing, we recommend using more comprehensive tools such as FMRIPREP.</li>
  </ul>
</div> 