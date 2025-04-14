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
    <p>After uploading your files, the FINDVIZ interface is organized into several key areas:</p>
    <ol>
      <li><strong>Analytics Toolbox</strong> - Located at the top of the screen, provides access to analysis tools</li>
      <li><strong>FMRI Container</strong> - The main visualization area for your fMRI data
        <ul>
          <li><strong>FMRI User Options</strong> - Controls for visualization settings (left sidebar)</li>
          <li><strong>FMRI Visualization</strong> - The main display area for your brain data</li>
        </ul>
      </li>
      <li><strong>Time Course Container</strong> - Displays time series data when available
        <ul>
          <li><strong>Time Course User Options</strong> - Controls for time series visualization (left sidebar)</li>
          <li><strong>Time Course Visualization</strong> - Displays your time series data</li>
        </ul>
      </li>
    </ol>
    <img src="https://raw.githubusercontent.com/tsb46/fmri-findviz-misc/main/pics/interface_layout.png" alt="FINDVIZ Interface Layout" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  </div>
</div>

## Navigation Controls

<div class="format-section">
  <div class="format-card">
    <h3>NIFTI Data Navigation</h3>
    <p>For NIFTI data, you can navigate through the brain using:</p>
    <ul>
      <li><strong>Slice Selection</strong> - Use sliders to change the currently displayed slice</li>
      <li><strong>Crosshair Navigation</strong> - Click anywhere on a slice to position the crosshair</li>
      <li><strong>View Selection</strong> - Switch between different view orientations:
        <ul>
          <li>Orthogonal view (axial, sagittal, coronal)</li>
          <li>Montage view (grid display of multiple slices)</li>
        </ul>
      </li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Surface Data Navigation</h3>
    <p>For GIFTI and CIFTI data, you can:</p>
    <ul>
      <li><strong>Rotate the 3D Surface</strong> - Click and drag to rotate the brain surface</li>
      <li><strong>Zoom</strong> - Use the scroll wheel to zoom in and out</li>
      <li><strong>Reset View</strong> - Return to the default view orientation</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Time Course Navigation</h3>
    <p>When viewing time series data:</p>
    <ul>
      <li><strong>Time Point Selection</strong> - Click on the time course graph to select a specific time point</li>
      <li><strong>Linked Navigation</strong> - Time point selection is synchronized between the brain visualization and time course</li>
      <li><strong>Time Marker</strong> - A vertical line indicates the currently selected time point</li>
      <li><strong>Range Selection</strong> - Drag to select a range of time points for analysis</li>
      <li><strong>Zoom</strong> - Use zoom controls to focus on specific parts of the time series</li>
    </ul>
  </div>
</div>

## Using the Analytics Toolbox

<div class="card">
  <div class="card-header">
    <h3>Analytics Tools</h3>
  </div>
  <div class="card-content">
    <p>The Analytics Toolbox provides access to several analysis functions:</p>
    
    <div class="steps-container">
      <div class="step">
        <strong>Transform</strong> - Apply mathematical transformations to your data
      </div>
      <div class="step">
        <strong>Distance</strong> - Calculate and visualize distances between time points
      </div>
      <div class="step">
        <strong>Compare</strong> - Compare different regions or time points
      </div>
      <div class="step">
        <strong>Save Scene</strong> - Save your current visualization state for later use
      </div>
    </div>
    
    <p>To use these tools:</p>
    <ol>
      <li>Click on the desired tool button in the Analytics Toolbox</li>
      <li>Configure the analysis parameters in the modal that appears</li>
      <li>Click Apply to run the analysis</li>
      <li>Use the trash icon button to remove an applied analysis</li>
    </ol>
  </div>
</div>

## Customizing Visualizations

<div class="format-section">
  <div class="format-card">
    <h3>FMRI Visualization Options</h3>
    <p>In the FMRI User Options panel, you can adjust:</p>
    <ul>
      <li><strong>Colormap</strong> - Change the color palette used for displaying values</li>
      <li><strong>Color Range</strong> - Adjust the minimum and maximum values for color mapping</li>
      <li><strong>Opacity</strong> - Change the transparency of the visualization</li>
      <li><strong>Display Mode</strong> - Switch between different visualization modes</li>
    </ul>
  </div>
  
  <div class="format-card">
    <h3>Time Course Visualization Options</h3>
    <p>In the Time Course User Options panel, you can adjust:</p>
    <ul>
      <li><strong>Line Color</strong> - Change the color of time series lines</li>
      <li><strong>Line Thickness</strong> - Adjust the thickness of time series lines</li>
      <li><strong>Time Marker Settings</strong> - Customize the appearance of the time marker</li>
      <li><strong>Display Options</strong> - Show/hide specific time series</li>
    </ul>
  </div>
</div>

## Keyboard Shortcuts

<div class="card">
  <div class="card-content">
    <p>FINDVIZ supports several keyboard shortcuts to enhance your navigation experience:</p>
    <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
      <tr style="background-color: #f6f8fa; border-bottom: 1px solid #dce6f0;">
        <th style="padding: 0.5rem 1rem; text-align: left;">Shortcut</th>
        <th style="padding: 0.5rem 1rem; text-align: left;">Function</th>
      </tr>
      <tr style="border-bottom: 1px solid #dce6f0;">
        <td style="padding: 0.5rem 1rem;"><strong>Arrow Keys</strong></td>
        <td style="padding: 0.5rem 1rem;">Navigate through slices in NIFTI view</td>
      </tr>
      <tr style="border-bottom: 1px solid #dce6f0;">
        <td style="padding: 0.5rem 1rem;"><strong>Spacebar</strong></td>
        <td style="padding: 0.5rem 1rem;">Toggle between different view modes</td>
      </tr>
      <tr style="border-bottom: 1px solid #dce6f0;">
        <td style="padding: 0.5rem 1rem;"><strong>R</strong></td>
        <td style="padding: 0.5rem 1rem;">Reset the view to default</td>
      </tr>
      <tr style="border-bottom: 1px solid #dce6f0;">
        <td style="padding: 0.5rem 1rem;"><strong>S</strong></td>
        <td style="padding: 0.5rem 1rem;">Save the current scene</td>
      </tr>
    </table>
  </div>
</div>

## Tips for Efficient Navigation

<div class="alert alert-info">
  <h4>Best Practices</h4>
  <ul>
    <li>Use the crosshair tool to synchronize views across different orientations</li>
    <li>Take advantage of the "Save Scene" feature to bookmark important findings</li>
    <li>Link time course and fMRI visualizations to explore temporal patterns</li>
    <li>Use the montage view to get a comprehensive overview of volumetric data</li>
    <li>Rotate 3D surfaces to examine activation patterns from different angles</li>
  </ul>
</div> 