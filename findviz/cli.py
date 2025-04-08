import argparse
import os
import socket
import sys
import webbrowser

from threading import Timer

from findviz import create_app
from findviz.logger_config import setup_logger
from findviz.routes.shared import data_manager
from findviz.viz.io import gifti
from findviz.viz.io import nifti
from findviz.viz.io import cifti
from findviz.viz import exception
from findviz.viz.io.cache import Cache
from findviz.viz.io.upload import FileUpload

logger = setup_logger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='FIND Viewer')

    
    # NIFTI inputs
    nifti_group = parser.add_argument_group('NIFTI inputs', 'NIFTI file inputs')
    nifti_group.add_argument('--nifti-func', help='Functional NIFTI (nii/nii.gz)')
    nifti_group.add_argument('--nifti-anat', help='Anatomical NIFTI (nii/nii.gz)')
    nifti_group.add_argument('--nifti-mask', help='Brain mask NIFTI (nii/nii.gz)')
    
    # GIFTI inputs
    gifti_group = parser.add_argument_group('GIFTI inputs', 'GIFTI file inputs')
    gifti_group.add_argument('--gifti-left-func', help='Left hemisphere functional GIFTI (func.gii)')
    gifti_group.add_argument('--gifti-right-func', help='Right hemisphere functional GIFTI (func.gii)')
    gifti_group.add_argument('--gifti-left-mesh', help='Left hemisphere mesh GIFTI (surf.gii)')
    gifti_group.add_argument('--gifti-right-mesh', help='Right hemisphere mesh GIFTI (surf.gii)')

    # CIFTI inputs
    cifti_group = parser.add_argument_group('CIFTI inputs', 'CIFTI file inputs')
    cifti_group.add_argument('--cifti-dtseries', help='Functional CIFTI (dtseries.nii)')
    cifti_group.add_argument('--cifti-left-mesh', help='Left hemisphere mesh GIFTI (surf.gii)')
    cifti_group.add_argument('--cifti-right-mesh', help='Right hemisphere mesh GIFTI (surf.gii)')
    
    # Optional inputs
    parser.add_argument('--timeseries', nargs='+', help='Time series files')
    parser.add_argument('--ts-labels', nargs='+', help='Labels for time series files')
    parser.add_argument('--ts-headers', nargs='+', 
                        help='Whether time series files have headers (true/false)')
    
    parser.add_argument('--task-design', help='Task design file')
    parser.add_argument('--tr', type=float, help='TR value')
    parser.add_argument('--slicetime-ref', type=float, 
                       help='Slice timing reference (0-1)', default=0.5)
    parser.add_argument('--port', type=int, help='Port number', default=None)
    
    args = parser.parse_args()

    # raise FileInputError if both gifti and nifti files are present
    nifti_input = any([args.nifti_func, args.nifti_anat, args.nifti_mask])
    gifti_input = any([
        args.gifti_left_func, args.gifti_right_func, 
        args.gifti_left_mesh, args.gifti_right_mesh
    ])
    cifti_input = any([
        args.cifti_dtseries, args.cifti_left_mesh, args.cifti_right_mesh
    ])
    # Check if inputs from multiple groups are present
    if sum([nifti_input, gifti_input, cifti_input]) > 1:
        raise exception.FileInputError(
            "Only one file type (NIFTI, GIFTI, or CIFTI) can be used at a time. "
            "Please upload only one file type.",
            file_type=exception.ExceptionFileTypes.NIFTI_GIFTI_CIFTI.value,
            method='cli'
        )
    
    # Set the appropriate group flag based on which arguments are present
    if nifti_input:
        args.file_type = 'nifti'
    elif gifti_input:
        args.file_type = 'gifti'
    elif cifti_input:
        args.file_type = 'cifti'
    return args


def process_cli_inputs(args) -> None:
    """Process and validate CLI inputs using existing validation logic."""
    logger.info("Processing CLI inputs")
    # Determine file type and create FileUpload instance
    if args.file_type == 'nifti':
        fmri_type = 'nifti'
        logger.info("Nifti file type detected")
        fmri_files = {
            nifti.NiftiFiles.FUNC.value: args.nifti_func,
            nifti.NiftiFiles.ANAT.value: args.nifti_anat,
            nifti.NiftiFiles.MASK.value: args.nifti_mask
        }
    elif args.file_type == 'gifti':
        fmri_type = 'gifti'
        logger.info("Gifti file type detected")
        fmri_files = {
            gifti.GiftiFiles.LEFT_FUNC.value: args.gifti_left_func,
            gifti.GiftiFiles.RIGHT_FUNC.value: args.gifti_right_func,
            gifti.GiftiFiles.LEFT_MESH.value: args.gifti_left_mesh,
            gifti.GiftiFiles.RIGHT_MESH.value: args.gifti_right_mesh
        }
    elif args.file_type == 'cifti':
        fmri_type = 'cifti'
        logger.info("CIFTI file type detected")
        fmri_files = {
            cifti.CiftiFiles.DTSERIES.value: args.cifti_dtseries,
            cifti.CiftiFiles.LEFT_MESH.value: args.cifti_left_mesh,
            cifti.CiftiFiles.RIGHT_MESH.value: args.cifti_right_mesh
        }
    
    # Validate that all files exist
    validate_files(fmri_files)
    logger.info("FMRI files validated successfully")

    # Create additional files dict for validation
    additional_files = {}
    if args.timeseries:
        for i, ts_file in enumerate(args.timeseries):
            additional_files[f'timeseries_{i}'] = ts_file
    if args.task_design:
        additional_files['task_design'] = args.task_design
    
    # Validate additional files
    validate_files(additional_files)
    logger.info("Additional files validated successfully")

    # Create FileUpload instance
    file_upload = FileUpload(
        fmri_type,
        ts_status=bool(args.timeseries),
        task_status=bool(args.task_design),
        method='cli'
    )
    logger.info("FileUpload instance initialized")

    # Process files using existing validation logic
    uploads = file_upload.upload(
        fmri_files=fmri_files,
        ts_files=args.timeseries,
        ts_labels=args.ts_labels,
        ts_headers=args.ts_headers,
        task_file=args.task_design,
        tr=args.tr,
        slicetime_ref=args.slicetime_ref
    )
    logger.info("File uploads processed successfully")
    # pass fmri data to data manager and get viewer data
    if fmri_type == 'nifti':
        data_manager.ctx.create_nifti_state(
            func_img = uploads['nifti'][nifti.NiftiFiles.FUNC.value],
            anat_img = uploads['nifti'][nifti.NiftiFiles.ANAT.value],
            mask_img = uploads['nifti'][nifti.NiftiFiles.MASK.value]
        )
        logger.info("Nifti data manager state created successfully")
    else:
        # cifti or gifti file inputs
        data_manager.ctx.create_gifti_state(
            left_func_img=uploads['gifti'][gifti.GiftiFiles.LEFT_FUNC.value],
            right_func_img=uploads['gifti'][gifti.GiftiFiles.RIGHT_FUNC.value],
            left_mesh=uploads['gifti'][gifti.GiftiFiles.LEFT_MESH.value],
            right_mesh=uploads['gifti'][gifti.GiftiFiles.RIGHT_MESH.value]
        )
        logger.info("Gifti data manager state created successfully")

    # if timecourse data, add to viewer data
    if file_upload.ts_status:
        data_manager.ctx.add_timeseries(uploads['ts'])
        logger.info("Time series data added to viewer data")

    # if task data, add to viewer data
    if file_upload.task_status:
        data_manager.ctx.add_task_design(uploads['task'])
        logger.info("Task design data added to viewer data")

    # get viewer metadata
    viewer_metadata = data_manager.ctx.get_viewer_metadata()
    logger.info("Viewer metadata retrieved successfully")

    # create cache instance
    cache = Cache()
    # save cache
    try:
        cache.save(viewer_metadata)
    except Exception as e:
        logger.error(f"Error saving cache: {e}")

def main():
    args = parse_args()
    # If arguments were provided (besides port number), process them
    # This doesn't seem robust; might need refactoring
    # If only port number provided, skip input processing
    if len(sys.argv) == 2 and args.port:
        pass
    elif len(sys.argv) > 1:
        try:
            process_cli_inputs(args)
        except Exception as e:
            print(f"Error processing inputs: {str(e)}")
            return

    # create app
    app = create_app(clear_cache=False)
    # find free port
    port = args.port if args.port else find_free_port()
    # open browser (wait 1 second to ensure server is running)
    Timer(1, open_browser, args=(port,)).start()
    # run app
    app.run(debug=False, port=port)


def find_free_port():
    """Find an available port on the system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to any available port
        return s.getsockname()[1]  # Return the port number


def open_browser(port):
    """Open the web browser to the Flask app."""
    webbrowser.open_new(f"http://127.0.0.1:{port}")


def validate_files(files_dict: dict):
    """Validate that all provided files exist.
    
    Arguments:
    ----------
    files_dict (dict): Dictionary of file paths to check
        
    Raises:
    -------
        FileNotFoundError: If any specified file doesn't exist
    """
    missing_files = []
    for name, filepath in files_dict.items():
        if filepath and not os.path.exists(filepath):
            missing_files.append(filepath)
    
    if missing_files:
        raise FileNotFoundError(
            f"The following files were not found: {', '.join(missing_files)}"
        )