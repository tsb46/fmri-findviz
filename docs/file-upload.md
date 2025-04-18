---
layout: default
title: File Upload - FINDVIZ
---

# File Upload Guide

<div class="card">
    <div class="card-header">
        <h3>Overview</h3>
    </div>
    <div class="card-content">
        <p>FINDVIZ supports multiple fMRI file formats. This guide explains how to upload files and what formats are supported.</p>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/upload.gif' width=600 height=300 style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    </div>
</div>

## Table of Contents
{:.no-bullets}

- [FMRI File Formats]({{ site.baseurl }}{{ page.url }}#fmri-file-formats)
  - [NIFTI (.nii, .nii.gz)]({{ site.baseurl }}{{ page.url }}#nifti)
  - [GIFTI (.gii)]({{ site.baseurl }}{{ page.url }}#gifti)
  - [CIFTI (.dtseries.nii)]({{ site.baseurl }}{{ page.url }}#cifti)
- [Time Course Files]({{ site.baseurl }}{{ page.url }}#time-course-files)
  - [Time Course Files Format]({{ site.baseurl }}{{ page.url }}#time-course-files-format)
  - [Task Design Files]({{ site.baseurl }}{{ page.url }}#task-design-files)
- [Command Line Upload]({{ site.baseurl }}{{ page.url }}#command-line-upload-alternative)
  - [Command Line Options]({{ site.baseurl }}{{ page.url }}#command-line-options)
  - [Developer Notes]({{ site.baseurl }}{{ page.url }}#developer-notes)

## FMRI File Formats

<div class="card">
    <div class="card-header">
        <h3 id="nifti">NIFTI (.nii, .nii.gz)</h3>
    </div>
    <div class='card-content'>
        <ul>
            <li class="file-item">
                <span class="file-badge required-badge">Required</span>
                <span class="file-item-content"><strong>Functional file</strong>: 4D functional brain images (.nii or .nii.gz)</span>
            </li>
            <li class="file-item">
                <span class="file-badge optional-badge">Optional</span>
                <span class="file-item-content"><strong>Anatomical file</strong>: 3D structural brain images (.nii or .nii.gz)</span>
            </li>
            <li class="file-item">
                <span class="file-badge optional-badge">Optional</span>
                <span class="file-item-content"><strong>Brain mask file</strong>: Binary masks for brain extraction (required for some analysis functions)</span>
            </li>
        </ul>
        <div class='alert alert-warning'>
            <span>All preprocessing and analysis functions for nifti files require a brain mask.</span>
        </div>
        <div class="alert alert-info">
            <h4>Important Notes</h4>
            <ul>
                <li>All NIFTI images must have the same voxel dimensions, even if in the same coordinate space (e.g. MNI152).</li>
                <li>A functional file is required, but you can visualize it without an anatomical file or mask.</li>
            </ul>
        </div>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_nifti.png' alt="NIFTI upload modal" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h3 id="gifti">GIFTI (.gii)</h3>
    </div>
    <div class='card-content'>
        <ul>
            <li class="file-item">
                <span class="file-badge required-badge">Required<span class="conditional-indicator">*</span></span>
                <span class="file-item-content"><strong>Left hemisphere functional file</strong>: Surface-based functional data (func.gii)</span>
            </li>
            <li class="file-item">
                <span class="file-badge required-badge">Required<span class="conditional-indicator">*</span></span>
                <span class="file-item-content"><strong>Left hemisphere geometry file</strong>: 3D representation of the brain's outer surface (surf.gii)</span>
            </li>
            <li class="file-item">
                <span class="file-badge required-badge">Required<span class="conditional-indicator">*</span></span>
                <span class="file-item-content"><strong>Right hemisphere functional file</strong>: Surface-based functional data (func.gii)</span>
            </li>
            <li class="file-item">
                <span class="file-badge required-badge">Required<span class="conditional-indicator">*</span></span>
                <span class="file-item-content"><strong>Right hemisphere geometry file</strong>: 3D representation of the brain's outer surface (surf.gii)</span>
            </li>
        </ul>
        <div class="alert alert-info">
            <h4>Important Notes</h4>
            <ul>
                <li>
                    <span class="conditional-indicator">*</span>You need either both left hemisphere files OR both right hemisphere files (functional and geometry). You can also upload all four files for complete visualization.
                </li>
                <li>Each hemisphere requires both its functional file and geometry file.</li>
                <li>Surface geometry files (surf.gii) provide the 3D mesh on which functional data will be displayed.</li>
            </ul>
        </div>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_gifti.png' alt="GIFTI upload modal" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h3 id="cifti">CIFTI (.dtseries.nii)</h3>
    </div>
    <div class='card-content'>
        <ul>
            <li class="file-item">
                <span class="file-badge required-badge">Required</span>
                <span class="file-item-content"><strong>Dense time series file</strong>: Combined surface and volume data (.dtseries.nii)</span>
            </li>
            <li class="file-item">
                <span class="file-badge required-badge">Required<span class="conditional-indicator">*</span></span>
                <span class="file-item-content"><strong>Left hemisphere geometry file</strong>: 3D representation of the brain's outer surface (surf.gii)</span>
            </li>
            <li class="file-item">
                <span class="file-badge required-badge">Required<span class="conditional-indicator">*</span></span>
                <span class="file-item-content"><strong>Right hemisphere geometry file</strong>: 3D representation of the brain's outer surface (surf.gii)</span>
            </li>
        </ul>
        <div class="alert alert-info">
            <h4>Important Notes</h4>
            <ul>
                <li>
                    <span class="conditional-indicator">*</span>You need at least one hemisphere geometry file (either left or right). You can upload both for complete visualization.</li>
                <li>CIFTI files combine both surface and volume data into a single file. However, FINDVIZ currently only supports visualization of the surface data.</li>
            </ul>
        </div>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_cifti.png' alt="CIFTI upload modal" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    </div>
</div>

## Time Course Files

<div class="card">
    <div class="card-content">
        <p>In addition to fMRI data, FINDVIZ allows you to upload:</p>
        <ul>
            <li class="file-item">
                <span class="file-badge optional-badge">Optional</span>
                <span class="file-item-content"><strong>Time series files</strong> (.csv, .txt): Custom time course data for visualization alongside fMRI data</span>
            </li>
            <li class="file-item">
                <span class="file-badge optional-badge">Optional</span>
                <span class="file-item-content"><strong>Task design files</strong> (.csv, .tsv): Experimental design matrices for visualization</span>
            </li>
        </ul>
  </div>
</div>

<div class="card">
    <div class="card-header">
        <h3 id="time-course-files-format">Time Course Files</h3>
    </div>
    <div class="card-content">
        <div class="steps-container">
            <div class="step">
                <span>Upload .csv or .txt files containing time course data.</span>
                <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_ts.png' alt="Timecourse upload modal" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
            </div>
            <div class="step">
                These files should:
                <ul>
                    <li>
                        Have the same number of time points as your fMRI data. For concurrently recorded physiological signals, this typically means resampling/aligning your signals to the fMRI sampling times. Several open-source solutions in the Python ecosystem offer this functionality, e.g. <a href="https://neuropsychology.github.io/NeuroKit/">NeuroKit2</a>.
                    </li>
                    <li>Be arranged in one column</li>
                    <li>Be temporally aligned with your fMRI data</li>
                </ul>
            </div>
            <div class="step">
                <span class="file-badge optional-badge">Optional</span>
                <ul>
                    <li>You can provide a custom label for the time course. If not specified, the display label will be the file name.</li>
                    <li>
                        <span>It's common to have a column label or header at the top of your time course file. If you do, simply click the header switch for FINDVIZ to recognize the custom label in the header. Note, uploading a time course file with a header will raise an error if the header option switch is not clicked on upload.</span>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/ts_header.gif' alt= "header switch" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
                    </li>
                </ul>
            </div>
            <div class="step">
                <ul>
                    <li>
                        <span>If you want to add another time course. Click the <strong>Add Another File</strong> button in the Time Course Files section.</span>
                        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/gifs/ts_add_file.gif' style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>

<div class="card">
  <div class="card-header">
    <h3 id="task-design-files">Task Design Files</h3>
  </div>
  <div class="card-content">
    <div class="steps-container">
      <div class="step">
        <span>Upload a .csv or .tsv file in the Task Design File section.</span>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_task.png' alt="Timecourse upload modal" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-top: 1em;">
    </div>
      <div class="step">
        The file must contain:
        <ul>
          <li>An 'onset' column with values in seconds</li>
          <li>A 'duration' column with values in seconds</li>
          <li>Optionally, a 'trial_type' column for multiple event types</li>
        </ul>
        <p>Example File:</p>
        <img src="https://raw.githubusercontent.com/tsb46/fmri-findviz/main/findviz/static/images/task_design_file.png" width="400" height="200" alt="findviz-task-design" style="border-radius: 8px; margin-bottom: 1rem;">
      </div>
      <div class="step">Specify the TR (repetition time) of your fMRI data. This is needed for aligning the task events with the fmri data.</div>
      <div class="step">Specify the slicetime 'reference value' (default is 0.5) - the time of the reference slice used in the fmri slice timing correction algorithm. It is expressed as a percentage of the TR (repetition time): 0 - 1. For example, if slicetiming was referenced to the slice at the middle of the fmri acquisition, it would be 0.5. Default is 0.5, which is commonly used in fmri slice-timing algorithms.</div>
    </div>
  </div>
</div>

## Command Line Upload (Alternative)

<div class="card">
    <div class="card-header">
        <h3 id="command-line-options">Command Line Options</h3>
    </div>
    <div class="card-content">
        <p>You can also upload files directly from the command line:</p>

        <div class="code-block">
            <code>
                <br>
                # Launch with NIFTI files<br>
                findviz --nifti-func func.nii.gz --nifti-anat anat.nii.gz<br>
                <br>
                # Launch with GIFTI files (all four files)<br>
                findviz --gifti-left-func left.func.gii --gifti-right-func right.func.gii --gifti-left-mesh left.surf.gii --gifti-right-mesh right.surf.gii<br>
                <br>
                # Launch with GIFTI files (left hemisphere only)<br>
                findviz --gifti-left-func left.func.gii --gifti-left-mesh left.surf.gii<br>
                <br>
                # Launch with GIFTI files (right hemisphere only)<br>
                findviz --gifti-right-func right.func.gii --gifti-right-mesh right.surf.gii<br>
                <br>
                # Launch with CIFTI files (both hemispheres)<br>
                findviz --cifti-dtseries data.dtseries.nii --cifti-left-mesh left.surf.gii --cifti-right-mesh right.surf.gii<br>
                <br>
                # Launch with CIFTI files (left hemisphere only)<br>
                findviz --cifti-dtseries data.dtseries.nii --cifti-left-mesh left.surf.gii<br>
                <br>
                # Add time series data<br>
                findviz --nifti-func func.nii.gz --timeseries timeseries1.csv timeseries2.csv<br>
                <br>
                # Add task-design data<br>
                findviz --nifti-func func.nii.gz --task-design task.csv --tr 2.0 <br>--slicetime-ref 0.5
            </code>
        </div>
    </div>
</div>

<div class="card">
  <div class="card-header">
    <h3 id="developer-notes">Developer Notes</h3>
  </div>
  <div class="card-content">
    <p>FINDVIZ uses the Python neuroimaging library <a href="https://nipy.org/nibabel/">nibabel</a> to read and write neuroimaging files.</p>
  </div>
</div>