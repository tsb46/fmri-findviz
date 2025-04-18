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

## Table of Contents
{:.no-bullets}

- [FMRI Interface Layout]({{ site.baseurl }}{{ page.url }}#fmri-interface-layout)
- [FMRI Interface Components]({{ site.baseurl }}{{ page.url }}#fmri-interface-components)
  - [Toolbox]({{ site.baseurl }}{{ page.url }}#toolbox)
  - [FMRI Color Options]({{ site.baseurl }}{{ page.url }}#fmri-color-options)
  - [FMRI Preprocessing]({{ site.baseurl }}{{ page.url }}#fmri-preprocessing)
  - [Plot Options Toolbar]({{ site.baseurl }}{{ page.url }}#plot-options-toolbar)
  - [Plot FMRI Time Courses]({{ site.baseurl }}{{ page.url }}#plot-fmri-time-courses)
- [Timecourse Interface Layout]({{ site.baseurl }}{{ page.url }}#timecourse-interface-layout)
- [Timecourse Interface Components]({{ site.baseurl }}{{ page.url }}#timecourse-interface-components)
  - [Timecourse Plot Options]({{ site.baseurl }}{{ page.url }}#timecourse-plot-options)
  - [Timecourse Preprocessing]({{ site.baseurl }}{{ page.url }}#timecourse-preprocessing)
  - [Timecourse Annotation]({{ site.baseurl }}{{ page.url }}#timecourse-annotation)
- [Save and Load State](#save-scene)

## FMRI Interface Layout

<div class="card">
  <div class="card-content">
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/layout_nifti.png' width=800 height=400 style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  </div>
</div>

## FMRI Interface Components

<div class="card">
    <div class='card-header'>
        <h3 id="toolbox">Toolbox</h3>
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
        <h3 id="fmri-color-options">FMRI Color Options</h3>
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
        <h3 id="fmri-preprocessing">FMRI Preprocessing</h3>
    </div>
    <div class="card-content">
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/preprocess_fmri.gif' alt= "preprocess fmri" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <div>
            <h4>Available FMRI Preprocessing Methods:</h4>
            <ul class='feature-list'>
                <li>Linear Detrending</li>
                <li>Time Course Normalization (applied to each voxel/vertex time course)</li>
                <li>Temporal Filtering (Band-pass, low-pass, high-pass) specified in hertz (Hz).</li>
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
        <h3 id="plot-options-toolbar">Plot Options Toolbar</h3>
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
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/crosshair.png' alt= "crosshair toggle" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Crosshair toggle (NIFTI)</span>
                    </li>
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/hover.png' alt= "hover toggle" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Plotly hoverbox toggle</span>
                    </li>
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/direction_label.png' alt= "direction label toggle" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Hide/Display direction markers (NIFTI; e.g Anterior-Posterior)</span>
                    </li>
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/hide_colorbar.png' alt= "colorbar toggle" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Hide/Display color bar</span>
                    </li>
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/reverse_color.png' alt= "reverse color map" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Reverse colormap</span>
                    </li>
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/freeze_surface.png' alt= "freeze surface view" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Freeze/lock surface view to current position (CIFTI/GIFTI)</span>
                    </li>
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/screenshot.png' alt= "screenshot" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Screen capture (screenshot of current fMRI plot)</span>
                    </li>
                    <li>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/play_movie.png' alt="play movie" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                        <span>Play movie (cycle through timepoints)</span>
                    </li>
                </ul>
            </li>
        </ul>
    </div>
</div>

<div class="card">
    <div class='card-header'>
        <h3 id="plot-fmri-time-courses">Plot FMRI Time Courses</h3>
    </div>
    <div class="card-content">
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/enable_fmri_timecourse.png' alt= "enable fmri time course" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <p>FINDVIZ allows plotting of voxel/fMRI fMRI time courses of selected voxels/vertices</p>
        <h4>Plotting fMRI time courses</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/fmri_timecourse.gif' alt= "enable fmri time course vid" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <h4>Locking Time Course Selections</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/lock_fmri_timecourse.gif' alt= "lock fmri time course" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <ul class='feature-list'>
            <h4>Remove selected time courses</h4>
            <li>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/undo_fmri_timecourse.png' alt="undo fmri time course" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                <span>Remove most recent time course selection</span>
            </li>
            <li>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/remove_fmri_timecourse.png' alt="remove all fmri time course" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                <span>Remove all time course selections</span>
            </li>
        </ul>
    </div>
</div>

## Timecourse Interface Layout

<div class="card">
  <div class="card-content">
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/layout_time_course.png' alt="time course layout" width=800 height=400 style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  </div>
</div>

## Timecourse Interface Components
<div class="card">
    <div class='card-header'>
        <h3 id="timecourse-plot-options">Timecourse Plot Options</h3>
    </div>
    <div class="card-content">
        <h4>Time Course Plot Options</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/time_course_line_plot.gif' alt= "time course line plot options" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <h4>Constant and Scale Shifts</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/timecourse_shift_scale.gif' alt= "time course shift and scale" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <div class="alert alert-info">
            <ul>
                <li><strong>Constant shift</strong>: increase/decrease the baseline of the time course via a constant shift</li>
                <li><strong>Scale shift</strong>: increase/decrease the scale of the time course via a scale shift (constant remains the same through scale change)</li>
            </ul>
        </div>
        <h4>Task Convolution</h4>
        <p>Toggle between convolved (canonical HRF) and block task design time courses</p>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/convolution.gif' alt= "time course shift and scale" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <ul class='feature-list' style="margin-top: 1em;">
            <li>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/global_convolution.png' alt="play movie" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                <span>Toggle convolution for all task design time courses</span>
            </li>
        </ul>
        <h4>Time Marker Plot Options</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/marker_plot_options.gif' alt= "marker plot options" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
    </div>
</div>

<div class="card">
    <div class='card-header'>
        <h3 id="timecourse-preprocessing">Timecourse Preprocessing</h3>
    </div>
    <div class="card-content">
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/timecourse_preprocess.gif' alt= "preprocess timecourse" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <div>
            <h4>Available Time Course Preprocessing Methods:</h4>
            <ul class='feature-list'>
                <li>Linear Detrending</li>
                <li>Time Course Normalization</li>
                <li>Temporal Filtering (Band-pass, low-pass, high-pass) specified in Hertz (Hz).</li>
            </ul>
        </div>
        <span>More details on available preprocessing functions (including their order of application) are provided at:</span>
        <a href="{{ site.baseurl }}/preprocessing.html">Preprocessing</a>
    </div>
</div>


<div class="card">
    <div class='card-header'>
        <h3 id="timecourse-annotation">Timecourse Annotation</h3>
    </div>
    <div class="card-content">
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/annotation.png' alt= "annotate timecourse toolbar" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <p>Annotate the time course plot with time points of interest and navigate through them by clicking the 'annotation' switch.</p>
        <h4>Enabling Annotation</h4>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/annotation.gif' alt= "annotate timecourse" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <div class="alert alert-info">
            <p>The currently selected annotation marker is marked by a highlight around the marker. Click the left and right arrows to move the selected marker left or right.</p>
        </div>
        <h4>Removing Annotations</h4>
        <ul class='feature-list'>
            <li>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/undo_fmri_timecourse.png' alt="undo annotation" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                <span>Remove most recent annotation</span>
            </li>
            <li>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/remove_fmri_timecourse.png' alt="remove all annotations" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;" width=40 height=40>
                <span>Remove all annotations</span>
            </li>
        </ul>
        <h4>Marker Plot Options</h4>
        <p>Modify the plot properties through the marker pop over</p>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/annotation_marker_plot_options.png' alt="annotation marker plot options" width=800 height=350 style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h4>Marking Time Point Peaks</h4>
        <p>Find peaks in your time course via a local maxima detection algorithm. Hover over the tooltips for information about each parameter.</p>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/peak_finding.gif' alt= "find peaks" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
        <div class="alert alert-info">
            <h4>Developer Note</h4>
            <p>FINDVIZ uses the SciPy (v1.13.1) <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html">find_peaks</a> algorithm for peak detection. For algorithm details, please refer to the documentation.</p>
        </div>
    </div>
</div>

## Save and Load State
<div class="card" id='save-scene'>
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
          <div class="step">The scene will be loaded with all its visualization settings.</div>
        </div>
      </div>
    </div>
  </div>
</div>
