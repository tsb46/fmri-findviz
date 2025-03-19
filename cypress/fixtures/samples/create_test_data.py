# Sample script to generate test data for Cypress
import csv
import nibabel as nib
import numpy as np
import os

# Create directory for test data
output_dir = "cypress/fixtures/samples"
os.makedirs(output_dir, exist_ok=True)

# Create a sample 4D NIFTI file (functional)
func_data = np.random.rand(10, 10, 10, 20).astype(np.float32)  # x, y, z, time
func_img = nib.Nifti1Image(func_data, affine=np.eye(4))
nib.save(func_img, f"{output_dir}/sample_func.nii.gz")

# Create a sample 3D NIFTI file (anatomical)
anat_data = np.random.rand(10, 10, 10).astype(np.float32)  # x, y, z
anat_img = nib.Nifti1Image(anat_data, affine=np.eye(4))
nib.save(anat_img, f"{output_dir}/sample_anat.nii.gz")

# Create a sample brain mask
mask_data = np.zeros((10, 10, 10))
mask_data[slice(1, 9), slice(1, 9), slice(1, 9)] = 1
mask_img = nib.Nifti1Image(mask_data, affine=np.eye(4))
nib.save(mask_img, f"{output_dir}/sample_mask.nii.gz")

# Create GIFTI surface files
vertices = np.random.rand(100, 3).astype(np.float32)
triangles = np.random.randint(0, 100, (50, 3)).astype(np.int32)

# Left surface mesh
left_surf = nib.gifti.GiftiImage()
left_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(vertices))
left_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(triangles))
nib.save(left_surf, f"{output_dir}/sample_left.surf.gii")

# right surface mesh
right_surf = nib.gifti.GiftiImage()
right_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(vertices))
right_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(triangles))
nib.save(right_surf, f"{output_dir}/sample_right.surf.gii")

# Left functional data
left_func_data = np.random.rand(100, 20).astype(np.float32)  # vertices × time
left_func = nib.gifti.GiftiImage()
for t in range(left_func_data.shape[1]):
    left_func.add_gifti_data_array(
        nib.gifti.GiftiDataArray(left_func_data[:, t])
    )
nib.save(left_func, f"{output_dir}/sample_left.func.gii")

# right functional data
right_func_data = np.random.rand(100, 20).astype(np.float32)  # vertices × time
right_func = nib.gifti.GiftiImage()
for t in range(right_func_data.shape[1]):
    right_func.add_gifti_data_array(
        nib.gifti.GiftiDataArray(right_func_data[:, t])
    )
nib.save(right_func, f"{output_dir}/sample_right.func.gii")

# create cifti dtseres.nii file
# Define parameters
n_timepoints = 100  # Number of time points
n_left_cortex = 100  # Example: Left hemisphere grayordinates
n_right_cortex = 100  # Example: Right hemisphere grayordinates

# Total grayordinates
n_grayordinates = n_left_cortex + n_right_cortex

# Generate random fMRI time series data
data = np.random.rand(n_timepoints, n_grayordinates).astype(np.float32)

# Create a SeriesAxis (time points, assuming TR=2.0s)
time_axis = nib.cifti2.SeriesAxis(start=0, step=2.0, size=n_timepoints)

# Create BrainModelAxis with separate left and right cortex models
# Create BrainModel entries for left and right cortex
left_cortex_model = nib.cifti2.BrainModelAxis.from_mask(
    np.ones(n_left_cortex, dtype=bool),
    name="CIFTI_STRUCTURE_CORTEX_LEFT"
)

right_cortex_model = nib.cifti2.BrainModelAxis.from_mask(
    np.ones(n_right_cortex, dtype=bool),
    name="CIFTI_STRUCTURE_CORTEX_RIGHT",
)

# Concatenate both models into a single BrainModelAxis
brain_model_axis = left_cortex_model + right_cortex_model

# Create the CIFTI-2 Image
img = nib.cifti2.Cifti2Image(data, (time_axis, brain_model_axis))

# Save the image as a dtseries.nii file
nib.save(img, f"{output_dir}/sample_cifti.dtseries.nii")

# Create a sample timeseries CSV
timeseries = np.random.rand(20, 3)  # 20 timepoints, 3 ROIs
np.savetxt(
    f"{output_dir}/sample_timeseries.csv", 
    timeseries, 
    delimiter=",",
    header="ROI1,ROI2,ROI3"
)

# Create a sample task design CSV
values = {
    "onset": [0.0, 10.0, 20.0, 30.0, 40.0],
    "duration": [2.0, 2.0, 2.0, 2.0, 2.0],
    "trial_type": ["lorem", "ipsum", "lorum", "ipsum", "lorum"]
}
# create a csv file with the values
with open(f"{output_dir}/sample_taskdesign.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(values.keys())
    writer.writerows(zip(*values.values()))

print("Sample data generated successfully in:", output_dir)

