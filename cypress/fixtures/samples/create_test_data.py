# Sample script to generate test data for Cypress
import csv
import nibabel as nib
import numpy as np
import os

# Create directory for test data
output_dir = "cypress/fixtures/samples"
os.makedirs(output_dir, exist_ok=True)

# Create sample 4D NIFTI files (functional)
# Create a 10x10x10x20 array with 20 time points
func_data_10 = np.random.rand(10, 10, 10, 20).astype(np.float32)  # x, y, z, time
func_img_10 = nib.Nifti1Image(func_data_10, affine=np.eye(4))
nib.save(func_img_10, f"{output_dir}/sample_func_v10iso_t20.nii.gz")

# Create a 10x10x10x30 array with 30 time points
func_data_30 = np.random.rand(10, 10, 10, 30).astype(np.float32)  # x, y, z, time
func_img_30 = nib.Nifti1Image(func_data_30, affine=np.eye(4))
nib.save(func_img_30, f"{output_dir}/sample_func_v10iso_t30.nii.gz")

# Create a 20x20x20x20 array with 20 time points
func_data_20 = np.random.rand(20, 20, 20, 20).astype(np.float32)  # x, y, z, time
func_img_20 = nib.Nifti1Image(func_data_20, affine=np.eye(4))
nib.save(func_img_20, f"{output_dir}/sample_func_v20iso_t20.nii.gz")

# Create a 3d (should be 4d) NIFTI file
func_data_3d = np.random.rand(10, 10, 10).astype(np.float32)  # x, y, z
func_img_3d = nib.Nifti1Image(func_data_3d, affine=np.eye(4))
nib.save(func_img_3d, f"{output_dir}/sample_func_v10iso_3d.nii.gz")

# Create a sample 3D NIFTI file (anatomical)
anat_data = np.random.rand(10, 10, 10).astype(np.float32)  # x, y, z
anat_img = nib.Nifti1Image(anat_data, affine=np.eye(4))
nib.save(anat_img, f"{output_dir}/sample_anat_v10iso.nii.gz")

# Create a sample brain mask
mask_data = np.zeros((10, 10, 10))
mask_data[slice(1, 9), slice(1, 9), slice(1, 9)] = 1
mask_img = nib.Nifti1Image(mask_data, affine=np.eye(4))
nib.save(mask_img, f"{output_dir}/sample_mask_v10iso.nii.gz")

# Create a faulty brain mask - not binary
mask_data = np.random.rand(10, 10, 10)
mask_img = nib.Nifti1Image(mask_data, affine=np.eye(4))
nib.save(mask_img, f"{output_dir}/sample_mask_v10iso_notbinary.nii.gz")

# Create GIFTI surface files
vertices_100 = np.random.rand(100, 3).astype(np.float32)
triangles_100 = np.random.randint(0, 100, (50, 3)).astype(np.int32)

vertices_50 = np.random.rand(50, 3).astype(np.float32)
triangles_50 = np.random.randint(0, 50, (25, 3)).astype(np.int32)

# Left surface mesh
left_surf = nib.gifti.GiftiImage()
left_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(vertices_100))
left_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(triangles_100))
nib.save(left_surf, f"{output_dir}/sample_left_v100.surf.gii")

# right surface mesh
right_surf = nib.gifti.GiftiImage()
right_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(vertices_100))
right_surf.add_gifti_data_array(nib.gifti.GiftiDataArray(triangles_100))
nib.save(right_surf, f"{output_dir}/sample_right_v100.surf.gii")

# create a left surface mesh with 50 vertices
left_surf_50 = nib.gifti.GiftiImage()
left_surf_50.add_gifti_data_array(nib.gifti.GiftiDataArray(vertices_50))
left_surf_50.add_gifti_data_array(nib.gifti.GiftiDataArray(triangles_50))
nib.save(left_surf_50, f"{output_dir}/sample_left_v50.surf.gii")

# Left gifti functional data (20 time points)
left_func_data_20 = np.random.rand(100, 20).astype(np.float32)  # vertices × time
left_func = nib.gifti.GiftiImage()
for t in range(left_func_data_20.shape[1]):
    left_func.add_gifti_data_array(
        nib.gifti.GiftiDataArray(left_func_data_20[:, t])
    )
nib.save(left_func, f"{output_dir}/sample_left_v100_t20.func.gii")

# Left gifti functional data 100 vertices (30 time points)
left_func_data_30 = np.random.rand(100, 30).astype(np.float32)  # vertices × time
left_func_30 = nib.gifti.GiftiImage()
for t in range(left_func_data_30.shape[1]):
    left_func_30.add_gifti_data_array(
        nib.gifti.GiftiDataArray(left_func_data_30[:, t])
    )
nib.save(left_func_30, f"{output_dir}/sample_left_v100_t30.func.gii")

# right gifti functional data 100 vertices (20 time points)
right_func_data_20 = np.random.rand(100, 20).astype(np.float32)  # vertices × time
right_func_20 = nib.gifti.GiftiImage()
for t in range(right_func_data_20.shape[1]):
    right_func_20.add_gifti_data_array(
        nib.gifti.GiftiDataArray(right_func_data_20[:, t])
    )
nib.save(right_func_20, f"{output_dir}/sample_right_v100_t20.func.gii")

# right gifti functional data 100 vertices (30 time points)
right_func_data_30 = np.random.rand(100, 30).astype(np.float32)  # vertices × time
right_func_30 = nib.gifti.GiftiImage()
for t in range(right_func_data_30.shape[1]):
    right_func_30.add_gifti_data_array(
        nib.gifti.GiftiDataArray(right_func_data_30[:, t])
    )
nib.save(right_func_30, f"{output_dir}/sample_right_v100_t30.func.gii")

# create cifti dtseres.nii file
# Define parameters
n_timepoints = 20  # Number of time points
n_left_cortex = 100  # Example: Left hemisphere grayordinates
n_right_cortex = 100  # Example: Right hemisphere grayordinates

# Total grayordinates
n_grayordinates = n_left_cortex + n_right_cortex

# Generate random fMRI time series data
data = np.random.rand(n_timepoints, n_grayordinates).astype(np.float32)

# Create a SeriesAxis (time points, assuming TR=2.0s)
time_axis = nib.cifti2.SeriesAxis(start=0, step=2.0, size=n_timepoints)

# Create BrainModelAxis with separate left and right cortex models
left_cortex_model = nib.cifti2.BrainModelAxis.from_mask(
    np.ones(n_left_cortex, dtype=bool),
    name="CIFTI_STRUCTURE_CORTEX_LEFT"
)

right_cortex_model = nib.cifti2.BrainModelAxis.from_mask(
    np.ones(n_right_cortex, dtype=bool),
    name="CIFTI_STRUCTURE_CORTEX_RIGHT",
)

# Create the CIFTI-2 Image
brain_model_axis = left_cortex_model + right_cortex_model
img = nib.cifti2.Cifti2Image(data, (time_axis, brain_model_axis))

# Save the image as a dtseries.nii file
nib.save(img, f"{output_dir}/sample_cifti.dtseries.nii")

# Create sample timeseries CSV
# create a sample time series csv file with 20 timepoints
timeseries = np.random.rand(20, 1)  # 20 timepoints, 1 ROI
np.savetxt(
    f"{output_dir}/sample_timeseries_t20_header.csv", 
    timeseries, 
    delimiter=",",
    header="ROI1"
)

# create a sample time series csv file with 20 timepoints (w/o header)
np.savetxt(
    f"{output_dir}/sample_timeseries_t20.csv", 
    timeseries, 
    delimiter=","
)

# create a second sample time series csv file with 20 timepoints (w/o header)
timeseries = np.random.rand(20, 1)  # 20 timepoints, 1 ROI
np.savetxt(
    f"{output_dir}/sample_timeseries_t20_2.csv", 
    timeseries, 
    delimiter=","
)

# create a sample time series csv file with 30 timepoints (w/o header)
timeseries = np.random.rand(30, 1)  # 30 timepoints, 1 ROI
np.savetxt(
    f"{output_dir}/sample_timeseries_t30.csv", 
    timeseries, 
    delimiter=","
)

# create a sample time series csv file with 20 timepoints but string values
timeseries = ['a']*20  # 20 timepoints, 1 ROI
np.savetxt(
    f"{output_dir}/sample_timeseries_t20_string.csv", 
    timeseries, 
    delimiter=",",
    fmt="%s"
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

# create a sample task design missing onset
values = {
    "duration": [2.0, 2.0, 2.0, 2.0, 2.0],
    "trial_type": ["lorem", "ipsum", "lorum", "ipsum", "lorum"]
}
# create a csv file with the values
with open(f"{output_dir}/sample_taskdesign_missing_onset.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(values.keys())
    writer.writerows(zip(*values.values()))

# create a sample task design with string values for onset
values = {
    "onset": ["a", "b", "c", "d", "e"],
    "duration": [2.0, 2.0, 2.0, 2.0, 2.0],
    "trial_type": ["lorem", "ipsum", "lorum", "ipsum", "lorum"]
}
# create a csv file with the values
with open(f"{output_dir}/sample_taskdesign_string_onset.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(values.keys())
    writer.writerows(zip(*values.values()))






print("Sample data generated successfully in:", output_dir)

