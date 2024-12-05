// file.js

class FileUploader {
    constructor(onUploadComplete) {
      // counter variable to generate unique ids for time series switches
      this.tsFileCounter = 0
      // callback function
      this.onUploadComplete = onUploadComplete;
      // Set up form submission listener
      document.getElementById('uploadForm').onsubmit = async (event) => {
          // prevent page reload
          event.preventDefault();
          // get active tabe in form submission
          let activeTab = document.querySelector('.nav-pills .active').getAttribute('href'); // Get the active tab
          // Check whether the input is nifti or gifti based on active tab
          let fileType
          let uploadURL
          if (activeTab == '#nifti') {
            fileType = 'nifti';
            uploadURL = '/upload_nii';
          }
          else if (activeTab == '#gifti') {
            fileType = 'gifti';
            uploadURL = '/upload_gii';
          }
          this.uploadFiles(event, fileType, uploadURL);
      };

      // Initialize modal listeners
      this.initializeModalListeners();

      // Initialize TR input form listeners
      this.initializeTRFormListeners();
    }

    async uploadFiles(event, fileType, uploadURL) {
        // Get time series, optional
        const [timeSeriesArray, timeSeriesLabelsArray, timeSeriesHeaderArray] = this.getTimeSeries()
        // Validate all file inputs
        const validate = await this.validateInputs(
          fileType, timeSeriesArray, timeSeriesLabelsArray, timeSeriesHeaderArray
        )
        // If validation of files files, fail without form submit
        if (!validate) {
            event.preventDefault();
            return
        }

        // Start spinner to indicate loading of files
        let spinnerOverlayDiv = document.getElementById(
          'file-load-spinner-overlay'
        )
        spinnerOverlayDiv.style.display = 'block'
        let spinnerDiv = document.getElementById('file-load-spinner')
        spinnerDiv.style.display = 'block'

        // collect fmri files
        let formData = this.collectFmriFiles(fileType);

        // pass user inputs to Flask 'upload' route
        try {
          const response = await fetch(
            uploadURL, { method: 'POST', body: formData }
          );
          const data = await response.json();
          if (response.ok) {
              // determine correct file key
              let fileKey
              if (fileType == 'nifti') {
                fileKey = data.file_key;
              } else if (fileType == 'gifti') {
                if (data.left_key === null) {
                  fileKey = data.right_key;
                }
                else {
                  fileKey = data.left_key;
                }
              }
              // If uploaded, load time courses
              if (timeSeriesArray.length > 0) {
                try {
                  // Fetch time courses
                  const [timeCourseResponse, tsData] = await this.fetchTS(
                    timeSeriesArray, timeSeriesLabelsArray, timeSeriesHeaderArray,
                    fileType, fileKey
                  )
                  // If time courses failed, don't proceed
                  if (!timeCourseResponse) {
                    event.preventDefault();
                    // end spinner to indicate loading of files
                    spinnerOverlayDiv.style.display = 'none';
                    spinnerDiv.style.display = 'none';
                    // stop execution.
                    return;
                  }
                  // assign time series output to data
                  Object.assign(data, {timeCourses: tsData})
                } catch (error) {
                    // Handle any unforeseen errors in fetchTS
                    console.error('Error fetching time courses:', error);
                    return;
                }
              } else {
                // If no time courses append empty lists
                Object.assign(data, {timeCourses: {ts: [], tsLabels: []}})
              }
              // get task design files
              const [taskDesignFile, taskDesignTR, taskDesignST] = this.getTaskDesignFiles();
              // if task design passed, load task design files
              if (taskDesignFile) {
                try {
                  const [taskDesignResponse, taskData] = await this.fetchTaskDesign(
                    taskDesignFile, taskDesignTR, taskDesignST, fileType, fileKey
                  );
                  // If task design failed, don't proceed
                  if (!taskDesignResponse) {
                    event.preventDefault();
                    // end spinner to indicate loading of files
                    spinnerOverlayDiv.style.display = 'none';
                    spinnerDiv.style.display = 'none';
                    // stop execution.
                    return;
                  }
                  // assign time series output to data
                  Object.assign(data, {taskConditions: taskData})
                } catch (error) {
                      // Handle any unforeseen errors in fetchTS
                      console.error('Error fetching task design file:', error);
                      return;
                }
              } else {
                // If no task design set null
                Object.assign(data, {taskConditions: null})
              }
              // Show the visualization container after a successful upload
              document.getElementById('fmriVisualizationContainer').style.display = 'block';
              // Call the callback function provided during construction
              this.onUploadComplete(data, fileType);
              // close modal
              $('#uploadModal').modal('hide');
              // after upload listeners
              this.afterUpload()
          } else {
            // if route returns error, display
            let errorMessage = document.getElementById('error-message');
            errorMessage.textContent = data.error;
            errorMessage.style.display = 'block';
            // end spinner
            spinnerOverlayDiv.style.display = 'none';
            spinnerDiv.style.display = 'none';
            // remove file
            this.removeFmriFiles(data.file);
            return
          }
        } catch (error) {
            console.error('Error during file upload:', error);
        }
    }

    // 'simulate' file upload with scene file
    async uploadSceneFile(data) {
      // Start spinner to indicate loading of files
      let spinnerOverlayDiv = document.getElementById(
        'file-load-spinner-overlay'
      )
      spinnerOverlayDiv.style.display = 'block'
      let spinnerDiv = document.getElementById('file-load-spinner')
      spinnerDiv.style.display = 'block'
      // send uploaded scene file in POST request
      const sceneFile = event.target.files[0];
      const formData = new FormData();
      formData.append('scene_file', sceneFile);
      return fetch('/upload_cache', {
          method: 'POST',
          body: formData
      })
      .then(response => {
        if (!response.ok) {
          // if response status is 500, log error message
          if (response.status == 500) {
            response.json().then(errorData => {
              console.log(`Error in upload: ${errorData.Error}`);
              throw new Error('failed server processing of uploaded cache');
            });
          }
          // end spinner to indicate loading of files
          spinnerOverlayDiv.style.display = 'none';
          spinnerDiv.style.display = 'none';
          // show error modal
          $('#errorSceneModal').modal('show');
          throw new Error('failed server processing of uploaded cache');
        }
        return response.json()
      })
      .then(data => {
        // get data and call callback function
        // assign time series output to data
        if (data.ts_enabled) {
          Object.assign(data, {timeCourses: data.timeseries})
        } else {
          // If no time courses append empty lists
          Object.assign(data, {timeCourses: {ts: [], tsLabels: []}})
        }

        if (data.task_enabled) {
          Object.assign(data, {taskConditions: data.task})
        } else {
          Object.assign(data, {taskConditions: null})
        }

        // call callback function
        this.onUploadComplete(data, data.file_type);
        // close modal
        $('#uploadModal').modal('hide');
        // after upload listeners
        this.afterUpload()
      })
      .catch(error => {
        // There was an unspecified error
        console.error('Error during file upload:', error);
        // end spinner to indicate loading of files
        spinnerOverlayDiv.style.display = 'none';
        spinnerDiv.style.display = 'none';
      });

    }

    // collect fmri files
    collectFmriFiles(fmriType) {
      const formData = new FormData();
      // Get nifti files
      if (fmriType == 'nifti') {
        const niftiFile = document.getElementById('nifti_file').files[0];
        // Get anatomical file, optional
        // Get mask file, optional
        const maskFile = document.getElementById('mask_file').files[0]
        const anatomicalFile = document.getElementById(
          'anatomical_file'
        ).files[0];

        formData.append('nifti_file', niftiFile);
        formData.append('anatomical_file', anatomicalFile);
        formData.append('mask_file', maskFile);

      // get gifti files
      } else if (fmriType == 'gifti') {
        // Functional (func.gii) files
          const leftFile = document.getElementById(
            'left_hemisphere_file'
          ).files[0];
          const rightFile = document.getElementById(
            'right_hemisphere_file'
          ).files[0];
          // Surface geometry files (surf.gii) files
          const leftMeshFile = document.getElementById(
            'left_surface_mesh_file'
          ).files[0];
          const rightMeshFile = document.getElementById(
            'right_surface_mesh_file'
          ).files[0];
          // package data for POST request
          formData.append('left_hemisphere_file', leftFile);
          formData.append('right_hemisphere_file', rightFile);
          formData.append('left_hemisphere_mesh_file', leftMeshFile);
          formData.append('right_hemisphere_mesh_file', rightMeshFile);
      }

      return formData

    }

    // remove fmri files
    removeFmriFiles(fmriType, file) {
      // Get nifti files
      if (fmriType == 'nifti') {
        if (file == 'func' || file == 'all') {
          document.getElementById('nifti_file').value = '';
        }
        else if (file == 'anat' || file == 'all'){
          document.getElementById('anatomical_file').value = '';
        }
        else if (file == 'mask' || file == 'all'){
          document.getElementById('mask_file').value = '';
        }
      // remove gifti files
      } else if (fmriType == 'gifti') {
        if (file == 'left' || file == 'all') {
          document.getElementById('left_hemisphere_file').value = ''
        } else if (file == 'right' || file == 'all') {
          document.getElementById('right_hemisphere_file').value = ''
        } else if (file == 'left_mesh' || file == 'all') {
          document.getElementById('left_surface_mesh_file').value = ''
        } else if (file == 'right_mesh' || file == 'all') {
          document.getElementById('right_surface_mesh_file').value = ''
        }
      }
    }

    // initialize modal listeners
    initializeModalListeners() {
      // create reference to self
      const self = this;
      // Clear inputs and error messages on tab switch
      document.querySelectorAll('.nav-pills .nav-link').forEach(tab => {
        tab.addEventListener('click', function () {
          document.getElementById('error-message').style.display = 'none'; // Clear error message on tab switch
          // Get the currently active tab
          let activeTab = document.querySelector('.nav-pills .active').getAttribute('href');
          let fileType
          if (activeTab == '#nifti') {
            fileType = 'nifti';
          }
          else if (activeTab == '#gifti') {
            fileType = 'gifti';
          }
          // Reset only the FMRI inputs (Nifti or Gifti based on active tab)
          self.removeFmriFiles(fileType, 'all');
        });
      });

      // Open file dialog when user clicks upload scene
      const uploadSceneButton = $('#uploadScene');
      const sceneFileDiv = $('#fileScene');
      uploadSceneButton.on('click', () => {
        // open file dialog
        sceneFileDiv.click();
      });

      // on scene file upload pass to flask route
      sceneFileDiv.on('change', (event) => {
        this.uploadSceneFile();
      });

      // Add event listener for bootstrap model close to clear error message
      $('#uploadModal').on('hidden.bs.modal', function (e) {
          document.getElementById('error-message').style.display = 'none';
      });

      // Event listener for add physio file
      let addTSDiv = document.getElementById('addTimeSeries')
      addTSDiv.addEventListener('click', this.addTimeSeriesFile.bind(this))

      // On document ready add one time series file
      $(document).ready(function() {
          self.addTimeSeriesFile()
      });
    }

    // dynamically update TR input fields if one field gets input
    initializeTRFormListeners() {
      // Get references to the input fields for TRs
      // TR input field in modal for Task Design File
      const TRInput1 = document.getElementById('task-design-tr');
      // TR input field for fmri preprocessing
      const TRInput2 = document.getElementById('filter-tr');
      // TR input field for time course preprocessing
      const TRInput3 = document.getElementById('ts-filter-tr');

      // Function to update all other TR fields
      function synchronizeInput(sourceInput, targetInputs) {
          sourceInput.addEventListener('input', function() {
              targetInputs.forEach(input => {
                  input.value = sourceInput.value;
              });
          });
      }

      // Synchronize all TR input fields fields
      synchronizeInput(TRInput1, [TRInput2, TRInput3]);
      synchronizeInput(TRInput2, [TRInput1, TRInput3]);
      synchronizeInput(TRInput3, [TRInput1, TRInput2]);
    }

    // Physio file add
    addTimeSeriesFile() {
      const container = document.getElementById('time-series-container');
      const filePair = document.createElement('div');

      // increase counter
      this.tsFileCounter += 1
      // create unique id for switch input
      const uniqueID = `hasHeader-${this.tsFileCounter}`;

      filePair.className = 'times-series-file-pair row mb-2';
      filePair.innerHTML = `
        <div class="col-6">
          <span class="d-inline-block text-secondary">Time Series File (.txt, .csv, optional)</span>
          <input type="file" class="form-control-file time-series-file pt-2">
        </div>
        <div class="col-4">
          <div class="custom-control custom-switch">
            <input type="checkbox" class="custom-control-input hasHeader" id="${uniqueID}">
            <label class="custom-control-label" for="${uniqueID}">Header</label>
            <span class="fa fa-info-circle ml-1 toggle-immediate" data-toggle="tooltip" data-placement="top" title="Does the file have a header (i.e. name) in the first row?" aria-hidden="true"></span>
          </div>
          <textarea class="form-control time-series-label" placeholder="Label" rows="1"></textarea>
        </div>
        <div class="col-2 mt-4">
          <button type="button" class="removeTimeSeries btn btn-danger btn-sm">x</button>
        </div>
      `;
      // Append the new file input to the container
      container.appendChild(filePair);

      // Enable the tooltip
      const tooltip = filePair.querySelector('.toggle-immediate');
      $(tooltip).tooltip()
      // Select the file input we just added
      const newFileInput = filePair.querySelector('.time-series-file');

       // Select the header switch we just added and add the event listener
      const headerSwitch = filePair.querySelector('.custom-control-input');
      const labelTextarea = filePair.querySelector('.time-series-label');

      headerSwitch.addEventListener('change', () => {
        if (headerSwitch.checked) {
          this.handleHeaderSwitch(newFileInput, labelTextarea);
        } else {
          // Clear label if switch is toggled off
          labelTextarea.value = '';
        }
      });

      // Select the remove button we just added and add the event listener
      const removeButton = filePair.querySelector('button');
      removeButton.addEventListener('click', () => {
        this.removeTimeSeriesFile(removeButton);
      });
    }

    // physio file remove
    removeTimeSeriesFile(button) {
      const filePair = button.closest('.times-series-file-pair');
      filePair.remove();
      // decrease file counter
      this.tsFileCounter -= 1
    }

    // handle header switch and get header
    handleHeaderSwitch(fileInput, labelTextarea) {
      const file = fileInput.files[0];

      // Check if the file is .txt or .csv
      if (file && (file.name.endsWith('.txt') || file.name.endsWith('.csv'))) {
        const reader = new FileReader();

        reader.onload = function(event) {
          const fileContent = event.target.result;
          const lines = fileContent.split('\n');

          // Check if the file has more than one column
          const firstRow = lines[0].split(/[,\t]/); // Split by comma or tab
          if (firstRow.length > 1) {
            this.displayHeaderError(
              'The file must have only one column.', fileInput
            );
            return;
          }

          // Read the first line as the header
          const header = firstRow[0].trim();

          // Set the header into the textarea
          labelTextarea.value = header;
        };

        // Read the file
        reader.readAsText(file);
      } else {
        this.displayHeaderError(
          'Please upload a valid .txt or .csv file.', fileInput
        );
      }
    }

    displayHeaderError(message, fileInput) {
      // Display header error
      const errorMessage = document.getElementById('error-message');
      errorMessage.textContent = message;
      errorMessage.style.display = 'block';
      // reset the file input
      fileInput.value = ''
      // Clear error message after 5 seconds
      setTimeout(function() {
          errorMessage.style.display = 'none';
      }, 5000);
    }

    // Changes to DOM after upload
    afterUpload(){
      const uploadButton = document.getElementById('uploadFile')
      // Change button color
      uploadButton.classList.add('btn-secondary');
      uploadButton.classList.remove('btn-primary');
      // Change button text to reupload file
      uploadButton.innerHTML = 'Reupload Files'
      // Set listener to refresh page when user clicks reupload files
      uploadButton.addEventListener("click", () => {
        // clear cache
        window.location.href = '/clear_cache';
        location.reload()
      });
      // set saveScene button to display
      const saveSceneDisplay = document.getElementById('saveSceneDisplay');
      saveSceneDisplay.style.display = 'block';
    }

    // Get uploaded time series (if any)
    getTimeSeries() {
      // initialize time series containers
      // container for time series files
      let timeSeriesArray = [];
      // container for time series labels (either file or label, if provided)
      let timeSeriesLabelsArray = [];
      // container for whether a header was provided for each time series
      let timeSeriesHeaderArray = [];
      // get time series file information from form
      let timeSeriesInput = document.querySelectorAll(".time-series-file");
      let timeSeriesInputLabel = document.querySelectorAll(".time-series-label");
      let timeSeriesHeader = document.querySelectorAll(".hasHeader");
      let tsLabel
      // loop through file inputs and get info
      for (const [index, ts] of timeSeriesInput.entries()) {
        // If empty, do nothing
        if (ts.files.length > 0) {
          timeSeriesArray.push(ts.files[0]);
          // if label is not provided use file name as label
          tsLabel = timeSeriesInputLabel[index].value
          if (tsLabel == '') {
            tsLabel = ts.files[0].name
          }
          timeSeriesLabelsArray.push(tsLabel);
          // Check whether the file has a header
          timeSeriesHeaderArray.push(timeSeriesHeader[index].checked)
        }
      }
      return [timeSeriesArray, timeSeriesLabelsArray, timeSeriesHeaderArray]
    }

    // get task design files
    getTaskDesignFiles() {
      // get task design file
      const taskDesignFile = document.getElementById('task-design-file').files[0];
      // fmri TR
      const taskDesignTR = document.getElementById('task-design-tr').value;
      // slicetime reference
      const taskDesignST = document.getElementById('task-design-slicetime').value;
      return [taskDesignFile, taskDesignTR, taskDesignST];
    }

    // process and fetch uploaded time course files
    async fetchTS(
      tsFiles,
      tsFileLabels,
      tsFileHeaders,
      fmriFileType,
      fileKey=null,
    ) {
        const formData = new FormData();
        // Append each time series file
        tsFiles.forEach((file, index) => {
            formData.append('ts_files', file);
        });
        // Append the corresponding labels for the time series files
        tsFileLabels.forEach((label, index) => {
            formData.append('ts_labels', label);
        });
        // Append the header flags for the time series files
        tsFileHeaders.forEach((headerFlag, index) => {
            formData.append('ts_headers', headerFlag);
        });
        // append fmri file type
        formData.append('fmri_file_type', fmriFileType);
        // append file key
        formData.append('file_key', fileKey);
        // pass to Flask route
        try {
            const response = await fetch('/upload_ts', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                return [true, data]; // Success, return true
            } else {
                // if failed, display error in div element
                let errorMessage = document.getElementById('error-message');
                errorMessage.textContent = data.error;
                errorMessage.style.display = 'block';
                return [false, null]; // Error, return false
            }
        } catch (error) {
            console.error('Error during fetch of time courses:', error);
            return [false, null]; // Error, return false
      }
    }

    // process and fetch task design file
    async fetchTaskDesign(
      taskDesignFile,
      taskTR,
      taskSliceTimeRef,
      fmriFileType,
      fileKey=null
    ) {
      const formData = new FormData();
      // add task file, tr and slicetime ref to request
      formData.append('task_file', taskDesignFile);
      formData.append('task_tr', taskTR);
      formData.append('task_slicetime_ref', taskSliceTimeRef);
      formData.append('fmri_file_type', fmriFileType);
      formData.append('file_key', fileKey);
      // Pass to Flask route
      try {
            const response = await fetch('/upload_task', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                return [true, data]; // Success, return true
            } else {
                // if failed, display error in div element
                let errorMessage = document.getElementById('error-message');
                errorMessage.textContent = data.error;
                errorMessage.style.display = 'block';
                return [false, null]; // Error, return false
            }
        } catch (error) {
            console.error('Error during fetch of task design:', error);
            return [false, null]; // Error, return false
      }
    }

    // validate uploaded files
    async validateInputs(
      fileType,
      timeSeries,
      timeSeriesLabelsArray,
      timeSeriesHeader
    ) {
      // ensure user files uploaded and certain conditions are met

      // Clear previous error message
      let errorMessage = document.getElementById('error-message');
      errorMessage.style.display = 'none';

      // Validate Nifti Tab
      if (fileType === 'nifti') {
        const funcErrorMessage = 'Please upload a Nifti file (.nii or .nii.gz). for functional file';
        let niftiFile = document.getElementById('nifti_file').files[0];
        if (!niftiFile) {
          // Show error if no Nifti file is uploaded
          errorMessage.textContent = funcErrorMessage;
          errorMessage.style.display = 'block';
          // Reset input field
          document.getElementById('nifti_file').value = '';
          return false;
        }
        // check file extension
        const niftiFileExtOK = this.checkFileExt(niftiFile, 'nifti')
        if (!niftiFileExtOK) {
          // Show error if unrecognized file extenstion
          errorMessage.textContent = funcErrorMessage;
          errorMessage.style.display = 'block';
          // Reset input field
          document.getElementById('nifti_file').value = '';
          return false;
        }
        // If anatomical file was uploaded, check file extension
        const anatomicalFile = document.getElementById('anatomical_file').files[0]
        if (anatomicalFile) {
          // check file extension
          const anatFileExtOK = this.checkFileExt(anatomicalFile, 'nifti')
          if (!anatFileExtOK) {
            // Show error if unrecognized file extenstion
            errorMessage.textContent = 'Please upload a Nifti file (.nii or .nii.gz) for anatomical file.';
            errorMessage.style.display = 'block';
            // Reset input field
            document.getElementById('anatomical_file').value=''
            return false;
          }
        }
        // If mask file was uploaded, check file extension
        const maskFile = document.getElementById('mask_file').files[0]
        if (maskFile) {
          // check file extension
          const maskFileExtOK = this.checkFileExt(maskFile, 'nifti')
          if (!maskFileExtOK) {
            // Show error if unrecognized file extenstion
            errorMessage.textContent = 'Please upload a Nifti file (.nii or .nii.gz) for mask file.';
            errorMessage.style.display = 'block';
            // Reset input field
            document.getElementById('mask_file').value=''
            return false
          }
        }

      // Validate Gifti Tab
      } else if (fileType === 'gifti') {
        // Functional (func.gii) files
        const leftHemisphereFile = document.getElementById(
          'left_hemisphere_file'
        ).files[0];
        const rightHemisphereFile = document.getElementById(
          'right_hemisphere_file'
        ).files[0];
        // Surface geometry files (surf.gii) files
        const leftHemisphereMeshFile = document.getElementById(
          'left_surface_mesh_file'
        ).files[0];
        const rightHemisphereMeshFile = document.getElementById(
          'right_surface_mesh_file'
        ).files[0];

        // Check at least one functional file has been uploaded
        if (!leftHemisphereFile && !rightHemisphereFile) {
          errorMessage.textContent = 'Please upload at least one functional file (LH or RH).';
          errorMessage.style.display = 'block';
          return false
        }

        // Check that a surface geometry file has been uploaded w/ functional
        if (leftHemisphereFile && !leftHemisphereMeshFile) {
          errorMessage.textContent = 'Please upload both a surface geometry (surf.gii) and functional file (func.gii) for the left hemisphere';
          errorMessage.style.display = 'block';
          return false
        }

        if (rightHemisphereFile && !rightHemisphereMeshFile) {
          errorMessage.textContent = 'Please upload both a surface geometry (surf.gii) and functional file (func.gii) for the right hemisphere';
          errorMessage.style.display = 'block';
          return false
        }

        // Check left hemisphere file extensions
        if (leftHemisphereFile) {
          // check file extension for functional file (func.gii)
          const lhFileExtOK = this.checkFileExt(leftHemisphereFile, 'gifti_func');
          if (!lhFileExtOK) {
            // Show error if unrecognized file extenstion
            errorMessage.textContent = 'please provide functional gifti file (func.gii) for left hemisphere file';
            errorMessage.style.display = 'block';
            // Reset input field
            document.getElementById('left_hemisphere_file').value = ''
            return false
          }
          // check file extenstion for surface geometry file (surf.gii)
          const lhMeshFileExtOK = this.checkFileExt(
            leftHemisphereMeshFile, 'gifti_surf'
          );
          if (!lhMeshFileExtOK) {
            // Show error if unrecognized file extenstion
            errorMessage.textContent = 'please provide surface geometry gifti file (surf.gii) for left hemisphere file';
            errorMessage.style.display = 'block';
            // Reset input field
            document.getElementById('left_surface_mesh_file').value = ''
            return false
          }

        }

        // Check right hemisphere file extensions
        if (rightHemisphereFile) {
          // check file extension
          const rhFileExtOK = this.checkFileExt(rightHemisphereFile, 'gifti_func')
          if (!rhFileExtOK) {
            // Show error if unrecognized file extenstion
            errorMessage.textContent = 'please provide functional gifti file (func.gii) for right hemisphere file';
            errorMessage.style.display = 'block';
            // Reset input field
            document.getElementById('right_hemisphere_file').value = ''
            return false
          }
          // check file extenstion for surface geometry file (surf.gii)
          const rhMeshFileExtOK = this.checkFileExt(
            rightHemisphereMeshFile, 'gifti_surf'
          );
          if (!rhMeshFileExtOK) {
            // Show error if unrecognized file extenstion
            errorMessage.textContent = 'please provide surface geometry gifti file (surf.gii) for right hemisphere file';
            errorMessage.style.display = 'block';
            // Reset input field
            document.getElementById('right_surface_mesh_file').value = ''
            return false
          }
        }
      }

      // Validate time courses
      if (timeSeries.length > 0) {
        // First, check for duplicates in labels
        const dups = this.findDuplicates(timeSeriesLabelsArray);
        if (dups.length > 0) {
          // Show error if duplicate labels found
          errorMessage.textContent = `Duplicate labels were found (if uploading files with the same file name, enter distinct labels). Duplicate labels: ${dups}`;
          errorMessage.style.display = 'block';
          return false
        }

        // Check whether fmri is passed as a label, this is a reserved label
        if (timeSeriesLabelsArray.includes('fmri')) {
          // Show error if duplicate labels found
          errorMessage.textContent = '"fmri" is a reserved label for the application, please choose another label.';
          errorMessage.style.display = 'block';
          return false
        }

        // Loop through time series inputs and check files
        for (const [index, ts] of timeSeries.entries()) {
          // check file extenstion
          const tsFileExtOK = this.checkFileExt(ts, 'timeCourse')
          if (!tsFileExtOK) {
            // Show error if unrecognized file extenstion
            errorMessage.textContent = `please upload a .txt or .csv file for time course (${ts.name})`;
            errorMessage.style.display = 'block';
            // Reset input field
            ts.value = ''
            return false
          }
          // check whether file is all numeric
          const fileNumeric = await this.isTimeSeriesNumeric(
            ts, timeSeriesHeader[index]
          );
            if (!fileNumeric) {
              let errorMessage = document.getElementById('error-message');
              errorMessage.textContent = `all elements of time series file must be numeric (hint: check for undeclared header or empty lines at end of file) (${ts.name})`;
              errorMessage.style.display = 'block';
              // Reset input field
              ts.value = ''
              return false
            }
          }
      }

      // Check task design file, if passed
      const taskDesignFile = document.getElementById('task-design-file').files[0];
      if (taskDesignFile) {
        // First, check file extension (.tsv and .csv)
        const [taskFileExtOK, taskFileExt] = this.checkFileExt(
          taskDesignFile, 'taskDesign'
        )
        if (!taskFileExtOK) {
          // Show error if unrecognized file extenstion
          errorMessage.textContent = `please upload a .csv or .tsv file for task design file`;
          errorMessage.style.display = 'block';
          // Reset input field
          document.getElementById('task-design-file').value = ''
          return false
        }
        // Check whether a TR has been provided
        const taskDesignTR = document.getElementById('task-design-tr').value;
        if (taskDesignTR == '') {
          errorMessage.textContent = 'the TR (repitition time) of the functional (fmri) data must be supplied with the task design file';
          errorMessage.style.display = 'block';
          return false
        }
        // Don't allow negative TR values
        if (taskDesignTR < 0) {
          errorMessage.textContent = 'the TR (repitition time) must be a positive number';
          errorMessage.style.display = 'block';
          // Reset input field
          document.getElementById('task-design-tr').value = ''
          return false
        }

        // Check whether slicetime ref is between 0 and 1
        const taskDesignST = document.getElementById('task-design-slicetime').value;
        if (taskDesignST <= 0 || taskDesignST >= 1) {
          errorMessage.textContent = 'The slicetime reference value must be between 0 and 1.';
          errorMessage.style.display = 'block';
          // Reset input field
          document.getElementById('task-design-slicetime').value = ''
          return false
        }

        // Check header of task file
        try {
          const [taskFileValid, errorMsg] = await this.checkTaskFileHeader(
            taskDesignFile, taskFileExt
          );
        } catch(errorMsg) {
          errorMessage.textContent = errorMsg
          errorMessage.style.display = 'block';
          document.getElementById('task-design-file').value = '';
          return false
        }
      }
      // return true if all checks pass
      return true
    };

    // Check input file extensions
    checkFileExt(file, fileType){
      // Get file extension
      let fileSplit = file.name.split('.');
      const fileExt = fileSplit.pop();
      // Handle nifti files (.nii, .nii.gz)
      if (fileType == 'nifti') {
        if (fileExt == 'nii') {
          // correct file extension
          return [true, fileExt]
          // handle .nii.gz extensions
        } else if (fileExt == 'gz') {
          const fileExtExt = fileSplit.pop()
          if (fileExtExt == 'nii') {
            return [true, fileExt]
          } else {
            // error if nii isn't before gz
            return [false, fileExt]
          }
        }
        else {
          return [false, fileExt]
        }
      }
      // Handle functional gifti files (func.gii)
      else if (fileType == 'gifti_func') {
        if (fileExt == 'gii') {
          const fileExtExt = fileSplit.pop()
          if (fileExtExt == 'func') {
            return [true, fileExt]
          }
          else {
            return [false, fileExt]
          }
        }
      }
      // Handle surface geometry gifti files (surf.gii)
      else if (fileType == 'gifti_surf') {
        if (fileExt == 'gii') {
          const fileExtExt = fileSplit.pop()
          if (fileExtExt == 'surf') {
            return [true, fileExt]
          }
          else {
            return [false, fileExt]
          }
        }
      }
      // Handle time course files (.csv or .txt)
      else if (fileType == 'timeCourse') {
        if (fileExt == 'txt') {
          return [true, fileExt]
        }
        else if (fileExt == 'csv') {
          return [true, fileExt]
        }
        else {
          return [false, fileExt]
        }
      }
      // Handle task design file (.csv or .tsv)
      else if (fileType == 'taskDesign') {
        if (fileExt == 'csv') {
          return [true, fileExt]
        }
        else if (fileExt == 'tsv') {
          return [true, fileExt]
        }
        else {
          return [false, fileExt]
        }
      }
    }

    // Check task design header
    checkTaskFileHeader(taskFile, taskFileExt) {
      return new Promise((resolve, reject) => {
          // Required columns
          const requiredColumns = ['duration', 'onset'];
          const optionalColumns = ['trial_type']; // Optional column

          // Initialize file reader
          const reader = new FileReader();

          // When the file is read
          reader.onload = function(e) {
              const text = e.target.result;
              const delimiter = (taskFileExt === 'csv') ? ',' : '\t';
              const lines = text.split('\n'); // Split by line

              let msg;
              if (lines.length > 0) {
                  // Case-sensitive match
                  const headers = lines[0].trim().split(delimiter); // Get header row and split by delimiter

                  // Check for required columns
                  let missingColumns = requiredColumns.filter(col => !headers.includes(col));
                  let optionalColumnMissing = !headers.includes(optionalColumns[0]);

                  if (missingColumns.length > 0) {
                      msg = 'Missing required columns in task design file: ' + missingColumns.join(', ');
                      reject(msg);  // Reject the Promise with error message
                  } else if (optionalColumnMissing) {
                      msg = 'Optional column "trial_type" is missing, but the file is valid.';
                      resolve([true, msg]);  // Resolve with true and optional column message
                  } else {
                      resolve([true, null]);  // Resolve with true and no message if the file is valid
                  }
              }
              else {
                msg = 'No lines found in task design file'
                reject(msg)
              }
          };

          // Read the file as text
          reader.readAsText(taskFile);
      });
    }

    // utility function to identify whether time course is ALL numeric
    isTimeSeriesNumeric(tsFile, header) {
      return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = function(event) {
              const fileContent = event.target.result;
              // Split the file content into lines
              const lines = fileContent.split(/\r\n|\n/);

              // Optional: If you want to skip the header, assume it's the first line
              let startLine = 0;
              if (header) {
                startLine = 1;
              }

              // Iterate over the remaining lines
              for (let i = startLine; i < lines.length; i++) {
                  const value = lines[i].trim(); // Remove any extra whitespace
                  if (value !== '' && isNaN(value)) {
                      console.error(`Non-numeric value found: ${value} on line ${i + 1}`);
                      resolve(false); // Resolve with false on error
                      return;
                  }
              }
              resolve(true); // Resolve with true if all values are numeric
          };
          reader.onerror = function(error) {
              reject(error); // Reject the promise on file read error
          };
          reader.readAsText(tsFile);
      });
  }

  // Utility function for identifying duplicates in an array
  findDuplicates(arr) {
      let seen = new Set();
      let duplicates = new Set();

      for (let item of arr) {
          if (seen.has(item)) {
              duplicates.add(item);  // Add to duplicates if already seen
          } else {
              seen.add(item);  // Otherwise, add to the seen set
          }
      }
      return Array.from(duplicates);  // Convert duplicates set to an array
  }


}


export default FileUploader;
