// cypress/integration/upload/timeseries_upload_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('Time Series Upload Tests', () => {
  beforeEach(() => {
    cy.visit('/')
    // Wait for app to load
    cy.get('body').should('be.visible')
  })

  it('should upload NIFTI files with time series and display viewer', () => {
    // NIFTI tab should be selected by default
    cy.get(TEST_DOM_IDS.UPLOAD.TAB_NIFTI).should('have.class', 'active')
    
    // Upload NIFTI with time series
    cy.niftiWithTimeSeriesUpload()
    
    // Check that the fMRI container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    
    // Verify all three slices are visible
    cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).should('be.visible')
    cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2).should('be.visible')
    cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_3).should('be.visible')
    
    // Check that time series plot is visible
    cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
  })

  it('should upload NIFTI with multiple time series files', () => {
    // Upload NIFTI with multiple time series
    cy.niftiWithMultipleTimeSeriesUpload()
    
    // Check that the fMRI container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    
    // Verify all three slices are visible
    cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).should('be.visible')
    cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2).should('be.visible')
    cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_3).should('be.visible')
    
    // Check that time series plot is visible
    cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
    
    // Check that both time series are available in the dropdown
    cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SELECT_TIMECOURSE)
        .find('option')
        .should('have.length.at.least', 2)
  })

  it('should upload GIFTI left hemisphere with time series and display viewer', () => {
    // Upload GIFTI left hemisphere with time series
    cy.giftiLeftHemisphereWithTimeSeriesUpload()
    
    // Check that the fMRI container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    
    // Check that left hemisphere surface is visible
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('be.visible')
    
    // Check that time series plot is visible
    cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
  })

  it('should upload CIFTI with time series and display viewer', () => {
    // Upload CIFTI with time series
    cy.ciftiWithTimeSeriesUpload()
    
    // Check that the fMRI container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    
    // Check that both hemisphere surfaces are visible (CIFTI shows both)
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('be.visible')
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.RIGHT_SURFACE_CONTAINER).should('be.visible')
    
    // Check that time series plot is visible
    cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
  })

  // Upload NIFTI with time series file with header and check header switch
  it('should upload NIFTI with time series file with header and check header switch', () => {
    // Upload NIFTI with time series file with header
    cy.niftiWithTimeSeriesFileWithHeader()

    // click header switch
    cy.get(TEST_DOM_IDS.UPLOAD.TS.HEADER).parent('.custom-switch').click({ position: 'left' })

    // check that header ('#ROI1') appears in the label input
    cy.get(TEST_DOM_IDS.UPLOAD.TS.LABEL).eq(0).should('have.value', '# ROI1')
    
  })
})