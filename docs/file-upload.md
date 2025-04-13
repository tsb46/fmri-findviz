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

<div class="format-section">
  <div class="format-card">
    <h3>NIFTI (.nii, .nii.gz)</h3>
    <ul>
      <li><strong>Functional files</strong>: 4D functional brain images</li>
      <li><strong>Anatomical files</strong>: 3D structural brain images</li>
      <li><strong>Brain mask files</strong>: Binary masks for brain extraction</li>
    </ul>
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_nifti.png' alt="NIFTI upload modal">
  </div>
  
  <div class="format-card">
    <h3>GIFTI (.gii)</h3>
    <ul>
      <li><strong>Functional files</strong>: Surface-based functional data for left and right hemispheres (func.gii)</li>
      <li><strong>Surface geometry files</strong>: 3D representations of the brain's outer surface (surf.gii)</li>
    </ul>
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_gifti.png' alt="GIFTI upload modal">
  </div>
  
  <div class="format-card">
    <h3>CIFTI (.dtseries.nii)</h3>
    <ul>
      <li><strong>Dense time series files</strong>: Combined surface and volume data</li>
      <li><strong>Surface geometry files</strong>: Required for proper visualization of CIFTI data</li>
    </ul>
    <img src='https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/upload_modal_cifti.png' alt="CIFTI upload modal">
  </div>
</div>

## Time Course Files

<div class="card">
  <div class="card-content">
    <p>In addition to fMRI data, FINDVIZ allows you to upload:</p>
    <ul>
      <li><strong>Time series files</strong> (.csv, .txt): Custom time course data for visualization alongside fMRI data</li>
      <li><strong>Task design files</strong> (.csv, .tsv): Experimental design matrices for visualization</li>
    </ul>
  </div>
</div>

## How to Upload Files

<div class="steps-container">
  <div class="step">
    Launch FINDVIZ using the command <code>findviz</code> in your terminal.
  </div>
  <div class="step">
    Click the <strong>Upload Files</strong> button on the welcome screen.
  </div>
  <div class="step">
    In the upload modal:
    <ul>
      <li>Select the appropriate tab for your file format (NIFTI, GIFTI, or CIFTI).</li>
      <li>Upload the required files for your chosen format.</li>
      <li>Optionally add time series files or task design files.</li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <h3>NIFTI Upload</h3>
  </div>
  <div class="card-content">
    <div class="steps-container">
      <div class="step">Select the <strong>NIFTI</strong> tab in the upload modal.</div>
      <div class="step">Upload a <strong>Functional File</strong> (.nii or .nii.gz) - this is required.</div>
      <div class="step">Optionally upload an <strong>Anatomical File</strong> for structural reference.</div>
      <div class="step">Optionally upload a <strong>Brain Mask File</strong> to mask non-brain tissue (required for some preprocessing and analysis features).</div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <h3>GIFTI Upload</h3>
  </div>
  <div class="card-content">
    <div class="steps-container">
      <div class="step">Select the <strong>GIFTI</strong> tab in the upload modal.</div>
      <div class="step">Upload <strong>Left Hemisphere Functional File</strong> (func.gii) and <strong>Surface Geometry File</strong> (surf.gii).</div>
      <div class="step">Upload <strong>Right Hemisphere Functional File</strong> (func.gii) and <strong>Surface Geometry File</strong> (surf.gii).</div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <h3>CIFTI Upload</h3>
  </div>
  <div class="card-content">
    <div class="steps-container">
      <div class="step">Select the <strong>CIFTI</strong> tab in the upload modal.</div>
      <div class="step">Upload a <strong>Dense Time Series File</strong> (.dtseries.nii).</div>
      <div class="step">Upload <strong>Left Hemisphere Surface Geometry File</strong> (surf.gii) and <strong>Right Hemisphere Surface Geometry File</strong> (surf.gii).</div>
    </div>
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

## Important Considerations

<div class="alert alert-warning">
  <h4>File Compatibility</h4>
  <ul>
    <li>Ensure all files have compatible dimensions and resolutions.</li>
    <li>For NIFTI files, the anatomical and functional images should have the same resolution and field of view.</li>
    <li>Brain masks should be binary (1 for brain tissue, 0 for non-brain tissue).</li>
    <li>Time series files must match the number of time points in your fMRI data.</li>
  </ul>
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
# Launch with GIFTI files<br>
findviz --gifti-left-func left.func.gii --gifti-right-func right.func.gii --gifti-left-mesh left.surf.gii --gifti-right-mesh right.surf.gii<br>
<br>
# Launch with CIFTI files<br>
findviz --cifti-dtseries data.dtseries.nii --cifti-left-mesh left.surf.gii --cifti-right-mesh right.surf.gii<br>
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