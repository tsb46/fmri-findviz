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
  </div>
</div>

## Table of Contents
{:.no-bullets}

- [Analysis Methods](#analysis-methods)
  - [Time Point Distance](#time-point-distance)
  - [Time Course Correlation Map](#time-course-correlation-map)
  - [Windowed Average](#windowed-average)

## Analysis Methods

<div class="card">
  <div class="card-header">
    <h3 id="time-point-distance">Time Point Distance</h3>
  </div>
  <div class="card-content">
    <p>The Time Point Distance tool calculates the similarity or distance between a selected time point and all other time points in your fMRI data. This analysis helps identify repeating patterns, state transitions, and temporal structure in your data. The distance is computed using whole-brain activity patterns, allowing you to see when similar brain states occur throughout the scan.</p>
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/distance.gif' alt= "time point distance" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
    <h4>Available Distance Metrics</h4>
    <ul>
        <li>Euclidean</li>
        <li>Squared Euclidean</li>
        <li>Cosine</li>
        <li>City Block</li>
        <li>Correlation</li>
    </ul>
    <h4> Distance Plot Options</h4>
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/distance_plot_options.png' alt="distance plot options" width=800 height=450 style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <ul class='feature-list' style='margin-top: 1em;'>
        <li>Choose distance plot colormap</li>
        <li>Modify distance plot color range</li>
        <li>Modify time marker width</li>
        <li>Modify time marker opacity</li>
        <li>
            <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/remove_distance_plot.png' alt= "hover toggle" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
            <span>Clear distance plot</span>
        </li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <h3 id="time-course-correlation-map">Time Course Correlation Map</h3>
  </div>
  <div class="card-content">
    <p>Compute a correlation map between an uploaded time course, task design time course, or seed voxel/vertex time course with each voxel/vertex in your fMRI data.</p>
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/correlation.gif' alt= "time point distance" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
    <h3>Steps</h3>
    <div class="steps-container">
        <div class="step">
            <p>Select a timecourse (uploaded time course, task design time course, or seed voxel/vertex time course). See the <a href="{{ site.baseurl }}/navigation.html#plot-fmri-time-courses">fMRI time course plotting tool</a> for extracting a seed voxel/vertex time course.</p>
        </div>
        <div class="step">
            <p>Input negative or positive lags into the correlation interface to see correlation maps at lags of the time course.</p>
        </div>
        <div class="step">
            <p>After completion of the correlation map computation, the correlation map(s) will appear in new window with a new FINDVIZ fMRI plot interface (ensure that pop-ups are not blocked).</p>
        </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <h3 id="windowed-average">Windowed Average</h3>
  </div>
  <div class="card-content">
    <p>Compute windowed average around selected time points.</p>
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/average.gif' alt= "time point distance" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
    <h3>Steps</h3>
    <div class="steps-container">
        <div class="step">
            <p><a href="{{ site.baseurl }}/navigation.html#timecourse-annotation">Annotate</a> time points in the time course plot manually (or automatically with the peak finding algorithm.)</p>
        </div>
        <div class="step">
            <p>Specify the size of the window using negative and positive edge values (specified in time points).</p>
        </div>
        <div class="step">
            <p>After completion of the windowed average computation, the windowed average fMRI map will appear in new window with a new FINDVIZ fMRI plot interface (ensure that pop-ups are not blocked).</p>
        </div>
    </div>
  </div>
</div>


## Limitations

<div class="alert alert-info">
  <h4>Key Points to Remember</h4>
  <ul>
    <li><strong>Brain Mask</strong>: For NIFTI data, a brain mask is required for all analysis tools. If you didn't upload a mask, all analysis options are disabled.</li>
  </ul>
</div>