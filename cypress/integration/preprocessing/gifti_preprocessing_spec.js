// // // cypress/integration/preprocessing/gifti_preprocessing_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('GIFTI Preprocessing', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should run preprocessing steps on GIFTI file', () => {
        // upload GIFTI file
        cy.giftiLeftHemisphereUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get gifti data
        let originalData
        cy.getGiftiData(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(data => {
            originalData = data
        })
        // run preprocessing steps
        // normalization
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_NORMALIZATION).parent('.custom-switch').click({ position: 'left' })
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SELECT_MEAN_CENTER).click({ force: true })
        // select detrending
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.ENABLE_DETRENDING).click({ force: true })
        // submit preprocessing
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.SUBMIT_PREPROCESS_BUTTON).click({ force: true })
        cy.wait(200)
        // check that the preprocessing alert is visible
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.PREPROCESS_ALERT).should('be.visible')
        // get new gifti data
        let newData
        cy.getGiftiData(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(data => {
            newData = data
            // check that the new gifti data is different from the original gifti data
            cy.compareArraysOfArrays(newData, originalData).then(isEqual => {
                expect(isEqual).to.be.equal(false)
            })
        })
        // reset preprocessing
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.RESET_PREPROCESS_BUTTON).click({ force: true })
        cy.wait(200)
        // check that the preprocessing alert is not visible
        cy.get(TEST_DOM_IDS.FMRI.PREPROCESSING_OPTIONS.PREPROCESS_ALERT).should('not.be.visible')
        
    })
})
