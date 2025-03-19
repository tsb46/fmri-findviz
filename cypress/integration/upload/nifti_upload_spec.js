// cypress/integration/upload/nifti_upload_spec.js

describe('NIFTI File Upload Tests', () => {
    beforeEach(() => {
      cy.visit('/')
      // Wait for app to load
      cy.get('body').should('be.visible')
    })
  
    it('should upload NIFTI files and display viewer', () => {
      // Open file upload modal/form
      cy.get('#upload-file').click()

      // wait for the modal to display
      cy.get('[data-cy="modal"]').contains('button', 'Close').click()
      // cy.get('#upload-modal').should('be.visible')
      
      // NIFTI tab should be selected by default
      cy.get('#nifti-tab').should('have.class', 'active')
      
      // Upload functional NIFTI
      cy.get('#nifti-func').attachFile({
        filePath: 'samples/sample_func.nii.gz',
        encoding: 'binary'
      })
      
      // Upload anatomical NIFTI
      cy.get('#nifti-anat').attachFile({
        filePath: 'samples/sample_anat.nii.gz',
        encoding: 'binary'
      })
      
      // Upload mask NIFTI
      cy.get('#nifti-mask').attachFile({
        filePath: 'samples/sample_mask.nii.gz',
        encoding: 'binary'
      })
      
      // Submit the form
      cy.get('#submit-file').click()
      
      // wait for viewer to load
      cy.get('#fmri-visualization-container').should('be.visible')

      // check that the modal is closed
      cy.get('[data-cy="modal"]').should('not.exist')
      
      // Verify all three slices are visible
      cy.get('#sliceX').should('be.visible')
      cy.get('#sliceY').should('be.visible')
      cy.get('#sliceZ').should('be.visible')
      
      // Take a screenshot for visual testing
      cy.screenshot()
    })
  })