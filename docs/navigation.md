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
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/layout_nifti.png' width=600 height=300 style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
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
        <ul>
            <li>
                <span class="coming-soon-badge">Coming Soon</span>
                <span>Transform Data: this feature provides common dimension-reduction analyses (PCA, ICA) to be performed on your data</span>
            </li>
            <li> Time Point Distance: compute the whole-brain distance between the selected time point and all other time points.</li>
            <li>
                <span class="coming-soon-badge">Coming Soon</span>
                <span>Comparison: this feature provides a means to upload fMRI maps (in the same space and voxel dimensions as your fMRI data) and quantitatively compare the similarity to time points in your fMRI data.</span>
            </li>
        </ul>
        <span>More details on available analysis functions are provided at:</span>
        <a href="{{ site.baseurl }}/analysis.html">Analysis</a>
    </div>
</div>