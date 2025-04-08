// cypress/integration/upload/nifti_upload_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('NIFTI File Upload Tests', () => {
    beforeEach(() => {
      cy.visit('/')
      // Wait for app to load
      cy.get('body').should('be.visible')
    })
  
    it('should upload all Nifti files (functional, anatomical, mask) and display viewer', () => {
      // NIFTI tab should be selected by default
      cy.get(TEST_DOM_IDS.UPLOAD.TAB_NIFTI).should('have.class', 'active')
      
      // Full upload flow
      cy.niftiFullUpload()
      
      // check the the fmri container is visible
      cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
      
      // Verify all three slices are visible
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).should('be.visible')
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2).should('be.visible')
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_3).should('be.visible')
      
    })

    it('should upload functional and anatomical Nifti files and display viewer', () => {
      // Functional and anatomical upload flow
      cy.niftiFunctionalAndAnatomicalUpload()

      // check the the fmri container is visible
      cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
      
      // Verify all three slices are visible
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).should('be.visible')
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2).should('be.visible')
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_3).should('be.visible')
    })

    it('should upload functional and mask Nifti files and display viewer', () => {
      // Functional and mask upload flow
      cy.niftiFunctionalAndMaskUpload()

      // check the the fmri container is visible
      cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
      
      // Verify all three slices are visible
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).should('be.visible')
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2).should('be.visible')
      cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_3).should('be.visible')
    })

    it('should upload functional Nifti file and display viewer', () => {
      // Functional upload flow
      cy.niftiFunctionalUpload()

      // check the the fmri container is visible
      cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    })

    it('should upload serialized .fvstate file and display viewer', () => {
      // Serialized .fvstate upload flow
      cy.fvstateUploadNifti()

      // check the the fmri container is visible
      cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    })
  })