// commands.js
import { TEST_DOM_IDS } from '../testConstants.js';
import 'cypress-file-upload';

// Nifti functional upload flow
Cypress.Commands.add('niftiFunctionalUpload', () => {
  // open modal
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // submit form
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  // check that the modal is closed
  cy.get('[data-cy="modal"]').should('not.exist')
})

// Nifti functional and anatomical upload flow
Cypress.Commands.add('niftiFunctionalAndAnatomicalUpload', () => {
  // open modal
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload functional file
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload anatomical file
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.ANAT).attachFile({
    filePath: 'samples/sample_anat_v10iso.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// Nifti functional and mask upload flow
Cypress.Commands.add('niftiFunctionalAndMaskUpload', () => {
  // open modal
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.MASK).attachFile({
    filePath: 'samples/sample_mask_v10iso.nii.gz',
    encoding: 'binary'
  })
  // submit form
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// Full NIFTI upload flow
Cypress.Commands.add('niftiFullUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload functional file
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.ANAT).attachFile({
    filePath: 'samples/sample_anat_v10iso.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.MASK).attachFile({
    filePath: 'samples/sample_mask_v10iso.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// Nifti Error upload flows
// Nifti 3d (should be 4d) upload flow
Cypress.Commands.add('nifti3dUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_3d.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// Nifti incompatible mask dimension upload flow
Cypress.Commands.add('niftiIncompatibleMaskUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v20iso_t20.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.MASK).attachFile({
    filePath: 'samples/sample_mask_v10iso.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// Nifti non-binary mask upload flow
Cypress.Commands.add('niftiNonBinaryMaskUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.MASK).attachFile({
    filePath: 'samples/sample_mask_v10iso_notbinary.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// Gifti full upload flow
Cypress.Commands.add('giftiFullUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_FUNC).attachFile({
    filePath: 'samples/sample_left_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_FUNC).attachFile({
    filePath: 'samples/sample_right_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// Gifti left hemisphere upload flow
Cypress.Commands.add('giftiLeftHemisphereUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload left hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_FUNC).attachFile({
    filePath: 'samples/sample_left_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  // submit form
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
})

// Gifti right hemisphere upload flow
Cypress.Commands.add('giftiRightHemisphereUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload right hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_FUNC).attachFile({
    filePath: 'samples/sample_right_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
})

// Gifti left hemisphere upload flow with missing mesh file
Cypress.Commands.add('giftiLeftHemisphereUploadMissingMesh', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload left hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_FUNC).attachFile({
    filePath: 'samples/sample_left_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// Gifti right hemisphere upload flow with missing mesh file
Cypress.Commands.add('giftiRightHemisphereUploadMissingMesh', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload right hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_FUNC).attachFile({
    filePath: 'samples/sample_right_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// Gifti left hemisphere upload flow with missing functional file
Cypress.Commands.add('giftiLeftHemisphereUploadMissingFunctional', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload left hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// Gifti right hemisphere upload flow with missing functional file
Cypress.Commands.add('giftiRightHemisphereUploadMissingFunctional', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload right hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_FUNC).attachFile({
    filePath: 'samples/sample_right_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
}) 

// Gifti left hemisphere upload flow with incompatible mesh files
Cypress.Commands.add('giftiLeftHemisphereUploadIncompatibleMesh', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload left hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_FUNC).attachFile({
    filePath: 'samples/sample_left_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v50.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// Gifti left and right hemispheres upload flow with incompatible time length
Cypress.Commands.add('giftiLeftAndRightHemisphereUploadIncompatibleTimeSeries', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload left hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_FUNC).attachFile({
    filePath: 'samples/sample_left_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_FUNC).attachFile({
    filePath: 'samples/sample_right_v100_t30.func.gii',
    encoding: 'binary'
  })  
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// CIFTI full upload flow
Cypress.Commands.add('ciftiFullUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to CIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_CIFTI).click()
  // upload CIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.DTSERIES).attachFile({
    filePath: 'samples/sample_cifti.dtseries.nii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// CIFTI left hemisphere upload flow
Cypress.Commands.add('ciftiLeftHemisphereUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to CIFTI tab  
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_CIFTI).click()
  // upload CIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.DTSERIES).attachFile({
    filePath: 'samples/sample_cifti.dtseries.nii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// CIFTI right hemisphere upload flow
Cypress.Commands.add('ciftiRightHemisphereUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to CIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_CIFTI).click()
  // upload CIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.DTSERIES).attachFile({
    filePath: 'samples/sample_cifti.dtseries.nii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// CIFTI upload flow missing both mesh files
Cypress.Commands.add('ciftiMissingBothMeshFiles', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to CIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_CIFTI).click()
  // upload CIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.DTSERIES).attachFile({
    filePath: 'samples/sample_cifti.dtseries.nii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// CIFTI upload flow with incompatible mesh file
Cypress.Commands.add('ciftiIncompatibleMeshFile', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to CIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_CIFTI).click()
  // upload CIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.DTSERIES).attachFile({
    filePath: 'samples/sample_cifti.dtseries.nii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v50.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// NIFTI with time series upload flow
Cypress.Commands.add('niftiWithTimeSeriesUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload functional file
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// NIFTI full upload with time series flow
Cypress.Commands.add('niftiFullWithTimeSeriesUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload functional file
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.ANAT).attachFile({
    filePath: 'samples/sample_anat_v10iso.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.MASK).attachFile({
    filePath: 'samples/sample_mask_v10iso.nii.gz',
    encoding: 'binary'
  })
  // upload time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// NIFTI with multiple time series upload flow
Cypress.Commands.add('niftiWithMultipleTimeSeriesUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload functional file
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload first time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20.csv',
    encoding: 'utf8'
  })
  // add another time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.ADD_TS).eq(0).click()
  // upload second time series file select by class
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).eq(1).attachFile({
    filePath: 'samples/sample_timeseries_t20_2.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// GIFTI left hemisphere with time series upload flow
Cypress.Commands.add('giftiLeftHemisphereWithTimeSeriesUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload left hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_FUNC).attachFile({
    filePath: 'samples/sample_left_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  // upload time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// GIFTI both hemispheres with time series upload flow
Cypress.Commands.add('giftiBothHemispheresWithTimeSeriesUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to GIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_GIFTI).click()
  // upload left hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_FUNC).attachFile({
    filePath: 'samples/sample_left_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  // upload right hemisphere files
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_FUNC).attachFile({
    filePath: 'samples/sample_right_v100_t20.func.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.GIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  // upload time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

// CIFTI with time series upload flow
Cypress.Commands.add('ciftiWithTimeSeriesUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to CIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_CIFTI).click()
  // upload CIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.DTSERIES).attachFile({
    filePath: 'samples/sample_cifti.dtseries.nii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  // upload time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// CIFTI with multiple time series upload flow
Cypress.Commands.add('ciftiWithMultipleTimeSeriesUpload', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to CIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_CIFTI).click()
  // upload CIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.DTSERIES).attachFile({
    filePath: 'samples/sample_cifti.dtseries.nii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.LEFT_MESH).attachFile({
    filePath: 'samples/sample_left_v100.surf.gii',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.CIFTI.RIGHT_MESH).attachFile({
    filePath: 'samples/sample_right_v100.surf.gii',
    encoding: 'binary'
  })
  // upload first time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20.csv',
    encoding: 'utf8'
  })
  // add another time series
  cy.get(TEST_DOM_IDS.UPLOAD.TS.ADD_TS).click()
  // upload second time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).eq(1).attachFile({
    filePath: 'samples/sample_timeseries_t20_2.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
  // error in force close modal - skip for now
})

// Nifti upload flow with time series file with header
Cypress.Commands.add('niftiWithTimeSeriesFileWithHeader', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload functional file
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20_header.csv',
    encoding: 'utf8'
  })
  // Don't close the modal - header switch is handled in the test
})

// NIFTI upload flow with incompatible time series file
Cypress.Commands.add('niftiIncompatibleTimeSeriesFile', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')

  // upload NIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t30.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// NIFTI upload flow with time series file with string values
Cypress.Commands.add('niftiTimeSeriesFileWithStringValues', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload functional file 
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload time series file
  cy.get(TEST_DOM_IDS.UPLOAD.TS.FILE).attachFile({
    filePath: 'samples/sample_timeseries_t20_string.csv',
    encoding: 'utf8'
  })
  cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
})

// NIFTI upload flow with task design file
Cypress.Commands.add('niftiWithTaskDesignFile', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to NIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_NIFTI).click()
  // upload NIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload task design file
  cy.get(TEST_DOM_IDS.UPLOAD.TASK.FILE).attachFile({
    filePath: 'samples/sample_taskdesign.csv',
    encoding: 'utf8'
  })
  // do not close the modal - task design upload is handled in the test
})


// NIFTI upload flow with task design file missing onset
Cypress.Commands.add('niftiWithTaskDesignFileMissingOnset', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to NIFTI tab
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_NIFTI).click()
  // upload NIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload task design file
  cy.get(TEST_DOM_IDS.UPLOAD.TASK.FILE).attachFile({
    filePath: 'samples/sample_taskdesign_missing_onset.csv',
    encoding: 'utf8'
  })
  // do not close the modal - task design upload is handled in the test
})

// NIFTI upload flow with task design file with string values for onset
Cypress.Commands.add('niftiWithTaskDesignFileWithStringValues', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // switch to NIFTI tab  
  cy.get(TEST_DOM_IDS.UPLOAD.TAB_NIFTI).click()
  // upload NIFTI files
  cy.get(TEST_DOM_IDS.UPLOAD.NIFTI.FUNC).attachFile({
    filePath: 'samples/sample_func_v10iso_t20.nii.gz',
    encoding: 'binary'
  })
  // upload task design file
  cy.get(TEST_DOM_IDS.UPLOAD.TASK.FILE).attachFile({
    filePath: 'samples/sample_taskdesign_string_onset.csv',
    encoding: 'utf8'
  })
  // do not close the modal - task design upload is handled in the test
})

// Serialized .fvstate upload flow
Cypress.Commands.add('fvstateUploadNifti', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload .fvstate file
  cy.get(TEST_DOM_IDS.UPLOAD.SCENE.FILE).attachFile({
    filePath: 'samples/sample_func_v10iso_t20_scene.fvstate',
    encoding: 'binary'
  })
  // submit file
  cy.get(TEST_DOM_IDS.UPLOAD.SCENE.BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})

Cypress.Commands.add('fvstateUploadGifit', () => {
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL_BUTTON).click()
  cy.get(TEST_DOM_IDS.UPLOAD.MODAL).should('be.visible')
  // upload .fvstate file
  cy.get(TEST_DOM_IDS.UPLOAD.SCENE.FILE).attachFile({
    filePath: 'samples/sample_left_v100_scene.fvstate',
    encoding: 'binary'
  })
  // submit file
  cy.get(TEST_DOM_IDS.UPLOAD.SCENE.BUTTON).click()
  // force close modal
  cy.get('[data-cy="modal"]').contains('button', 'Close').click()
  cy.get('[data-cy="modal"]').should('not.exist')
})