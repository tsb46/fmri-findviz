// // cypress/integration/preprocessing/nifti_preprocessing_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('NIFTI Preprocessing', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should run preprocessing steps on NIFTI file', () => {
        // upload NIFTI file
        cy.niftiFunctionalAndMaskUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get nifti data
        let originalData
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(data => {
            originalData = data
        })
        // run preprocessing steps
        // normalization
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_NORMALIZATION).parent('.custom-switch').click({ position: 'left' })
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SELECT_MEAN_CENTER).click({ force: true })
        // select detrending
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_DETRENDING).click({ force: true })
        // enable smoothing
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_SMOOTHING).parent('.custom-switch').click({ position: 'left' })
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SMOOTHING_FWHM).type('2')
        // submit preprocessing
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SUBMIT_PREPROCESS_BUTTON).click({ force: true })
        cy.wait(200)
        // check that the preprocessing alert is visible
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.PREPROCESS_ALERT).should('be.visible')
        // get new nifti data
        let newData
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(data => {
            newData = data
            // check that the new nifti data is different from the original nifti data
            cy.compareArraysOfArrays(newData, originalData).then(isEqual => {
                expect(isEqual).to.be.equal(false)
            })
        })
        // reset preprocessing
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.RESET_PREPROCESS_BUTTON).click({ force: true })
        cy.wait(200)
        // check that the preprocessing alert is not visible
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.PREPROCESS_ALERT).should('not.be.visible')
        // get new nifti data
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(data => {
            // check that the new nifti data is different from the original nifti data
            cy.compareArraysOfArrays(data, originalData).then(isEqual => {
                expect(isEqual).to.be.equal(true)
            })
        })
    })
})