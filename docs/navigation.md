---
layout: default
title: Navigation - FINDVIZ
---

# Navigation Guide

<div class="card">
  <div class="card-header">
    <h3>Overview</h3>
  </div>
  <div class="card-content">
    <p>This guide will help you navigate through the FINDVIZ interface and understand how to interact with the various visualization and control components.</p>
  </div>
</div>

## Main Interface Layout

<div class="card">
  <div class="card-content">
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/layout_nifti.png' width=800 height=400 style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  </div>
</div>

## Interface Components

<div class="card">
    <div class='card-header'>
        <h3>Toolbox</h3>
    </div>
    <div class="card-content">
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/toolbox.png' style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <p>The toolbox component provides analysis functions to facilitate visualization and discovery of patterns in your fMRI data. Available functions:</p>
        <ul class='feature-list'>
            <li>
                <span><strong>Transform Data</strong> <span class="coming-soon-badge">Coming Soon</span>: this feature provides common dimension-reduction analyses (PCA, ICA) to be performed on your data</span>
            </li>
            <li> <strong>Time Point Distance</strong>: compute the whole-brain distance between the selected time point and all other time points.</li>
            <li>
                <span><strong>Comparison</strong> <span class="coming-soon-badge">Coming Soon</span>: this feature provides a means to upload fMRI maps (in the same space and voxel dimensions as your fMRI data) and quantitatively compare the similarity to time points in your fMRI data.</span>
            </li>
        </ul>
        <span>More details on available analysis functions are provided at:</span>
        <a href="{{ site.baseurl }}/analysis.html">Analysis</a>
    </div>
</div>

<div class="card">
    <div class='card-header'>
        <h3>FMRI Color Options</h3>
    </div>
    <div class="card-content">
        <p>The colormap selector and sliders allow you to customize the coloring of your plot</p>
        <h4>Color Map Selection</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/colormap.gif' alt= "color map selection" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <h4>Color Sliders</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/color_sliders.gif' alt= "color sliders" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
    </div>
</div>

<div class="card">
    <div class='card-header'>
        <h3>FMRI Preprocessing</h3>
    </div>
    <div class="card-content">
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/preprocess_fmri.gif' alt= "preprocess fmri" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <div>
            <h4>Available Preprocessing Methods:</h4>
            <ul class='feature-list'>
                <li>Linear Detrending</li>
                <li>Time Course Normalization (applied to each voxel/vertex time course)</li>
                <li>Temporal Filtering (Band-pass, low-pass, high-pass) specified in Hertz (Hz).</li>
                <li>
                    Spatial Smoothing for Nifti Files
                    <div class='alert alert-warning' style='margin-top:1em;'>
                        <span>Surface smoothing for CIFTI/GIFTI images is not supported</span>
                    </div>
                </li>
            </ul>
        </div>
        <span>More details on available preprocessing functions (including their order of application) are provided at:</span>
        <a href="{{ site.baseurl }}/preprocessing.html">Preprocessing</a>
    </div>
</div>

<div class="card">
    <div class='card-header'>
        <h3>Plot Options Toolbar</h3>
    </div>
    <div class="card-content">
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/plot_options.png' alt= "plot options toolbar" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <p>FINDVIZ offers several display tools to manipulate the information displayed in the plot</p>
        <ul class='feature-list'>
            <li>
                <h4>Convert Time Point Display To Seconds based on TR</h4>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/time_convert.gif' alt= "convert time points" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
                <div class="alert alert-warning">
                    This will also update the x-axis labels in the time course plot (see below).
                </div>
            </li>
            <li>
                <h4>Toggle between Orthogonal and Montage Views (for Nifti images)</h4>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/montage.gif' alt= "montage view" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
                <div class="alert alert-warning">
                    Only 3 slices are supported in montage view 
                </div>
            </li>
            <li>
                <h4>Other plot options</h4>
                <ul>
                    <li>Crosshair toggle (NIFTI)</li>
                    <li>Hoverbox toggle</li>
                    <li>Hide/Display direction markers (NIFTI)</li>
                    <li>Hide/Display colorbar</li>
                    <li>Reverse colormap</li>
                    <li>Freeze surface view</li>
                    <li>Screen capture</li>
                    <li>Movie play</li>
                </ul>
            </li>
        </ul>
    </div>
</div>