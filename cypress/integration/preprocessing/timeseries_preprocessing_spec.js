// // // cypress/integration/preprocessing/timeseries_preprocessing_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('Timeseries Preprocessing', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should run preprocessing steps on timeseries file', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_CONTAINER).should('be.visible')
        // get timeseries data
        let originalData
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // account for the first index being dummy data
            originalData = data[1].y
        })
        // select time course from menu
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.SELECT_TIMECOURSE)
        .select(0, {force: true})
        // run preprocessing steps
        // normalization
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.ENABLE_NORMALIZATION).parent('.custom-switch').click({ position: 'left' })
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.SELECT_MEAN_CENTER).click({ force: true })
        // select detrending
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.ENABLE_DETRENDING).click({ force: true })
        // submit preprocessing
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.SUBMIT_PREPROCESS_BUTTON).click({ force: true })
        cy.wait(200)
        // check that the preprocessing alert is visible
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESS_ALERT).should('be.visible')
        // get timeseries data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // account for the first index being dummy data
            const processedData = data[1].y
            // ensure data has changed
            cy.compareArraysOfArrays(originalData, processedData).then(result => {
                expect(result).to.be.false
            })
        })
        // reset preprocessing
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESSING_OPTIONS.RESET_PREPROCESS_BUTTON).click({ force: true })
        cy.wait(200)
        // check that the preprocessing alert is now invisible
        cy.get(TEST_DOM_IDS.TIMECOURSE.PREPROCESS_ALERT).should('be.not.visible')
        // get timeseries data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // account for the first index being dummy data
            const processedData = data[1].y
            // ensure data has changed
            cy.compareArraysOfArrays(originalData, processedData).then(result => {
                expect(result).to.be.true
            })
        })
    })
})
