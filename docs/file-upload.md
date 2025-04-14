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

## FMRI File Formats

<div class="card">
    <div class='content-card'>
        <h3>NIFTI (.nii, .nii.gz)</h3>
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
        <div class="alert alert-info">
            <h4>Important Notes</h4>
            <ul>
            <li>All NIFTI images must have the same voxel dimensions, even if in the same coordinate space (e.g. MNI152).</li>
            <li>Brain masks should be binary (1 for brain tissue, 0 for non-brain tissue).</li>
            <li>A functional file is required, but you can visualize it without an anatomical file or mask.</li>
            </ul>
        </div>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_nifti.png' alt="NIFTI upload modal">
    </div>
</div>

<div class="card">
    <div class='content-card'>
        <h3>GIFTI (.gii)</h3>
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
            <li><span class="conditional-indicator">*</span>You need either both left hemisphere files OR both right hemisphere files (functional and geometry). You can also upload all four files for complete visualization.</li>
            <li>Each hemisphere requires both its functional file and geometry file to work properly.</li>
            <li>Surface geometry files provide the 3D mesh on which functional data will be displayed.</li>
            </ul>
        </div>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_gifti.png' alt="GIFTI upload modal">
    </div>
</div>

<div class="card">
    <div class='content-card'>
        <h3>CIFTI (.dtseries.nii)</h3>
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
            <li>The dense time series file is always required.</li>
            <li><span class="conditional-indicator">*</span>You need at least one hemisphere geometry file (either left or right). You can upload both for complete visualization.</li>
            <li>CIFTI files combine both surface and volume data into a single file.</li>
            </ul>
        </div>
        <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_cifti.png' alt="CIFTI upload modal">
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
    <h3>Time Course Files</h3>
  </div>
  <div class="card-content">
    <div class="steps-container">
      <div class="step">Click the <strong>Add Another File</strong> button in the Time Course Files section.</div>
      <div class="step">Upload .csv or .txt files containing time course data.</div>
      <div class="step">
        These files should:
        <ul>
          <li>Have the same number of time points as your fMRI data</li>
          <li>Be arranged in one column</li>
          <li>Be temporally aligned with your fMRI data</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <h3>Task Design Files</h3>
  </div>
  <div class="card-content">
    <div class="steps-container">
      <div class="step">Upload a .csv or .tsv file in the Task Design File section.</div>
      <div class="step">
        The file must contain:
        <ul>
          <li>An 'onset' column with values in seconds</li>
          <li>A 'duration' column with values in seconds</li>
          <li>Optionally, a 'trial_type' column for multiple event types</li>
        </ul>
      </div>
      <div class="step">Specify the TR (repetition time) value.</div>
      <div class="step">Specify the Slicetime Reference value (default is 0.5).</div>
    </div>
  </div>
</div>

## Command Line Upload (Alternative)

<div class="card">
  <div class="card-header">
    <h3>Command Line Options</h3>
  </div>
  <div class="card-content">
    <p>You can also upload files directly from the command line:</p>

    <div class="code-block">
      <code>
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
findviz --nifti-func func.nii.gz --timeseries timeseries1.csv timeseries2.csv
      </code>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <h3>Developer Notes</h3>
  </div>
  <div class="card-content">
    <p>FINDVIZ uses the Python neuroimaging library <a href="https://nipy.org/nibabel/">nibabel</a> to read and write neuroimaging files. This allows FINDVIZ to support a variety of file formats commonly used in neuroimaging research.</p>
  </div>
</div>