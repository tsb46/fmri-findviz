// timeseries_navigation_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('Timeseries Navigation', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should plot timeseries from nifti visualization click', () => {
        // upload timeseries file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // click enable fmri time series button
        cy.get(TEST_DOM_IDS.TIMECOURSE.FMRI.ENABLE_FMRI_TIMECOURSE).parent('.custom-switch').click({ position: 'left' })
        cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).click(75, 75)
        .then(() => {
            // check that the timeseries plot is visible
            cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
            // get timeseries data
            cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
            .then(data => {
                // check that length of data is 1 (i.e. there is only one time series)
                expect(data.length).to.equal(1)
            })
        })

        // disable fmri time series button
        cy.get(TEST_DOM_IDS.TIMECOURSE.FMRI.ENABLE_FMRI_TIMECOURSE).parent('.custom-switch').click({ position: 'left' })
        // check that the timeseries visibility attribute is hidden
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_CONTAINER).should('have.attr', 'style', 'visibility: hidden;')
    })

    it('should plot multiple time series from nifti visualization click with freeze, unfreeze, and remove', () => {
        // upload timeseries file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // click enable fmri time series button
        cy.get(TEST_DOM_IDS.TIMECOURSE.FMRI.ENABLE_FMRI_TIMECOURSE).parent('.custom-switch').click({ position: 'left' })
        // click freeze fmri time series button
        cy.get(TEST_DOM_IDS.TIMECOURSE.FMRI.FREEZE_FMRI_TIMECOURSE).parent('.custom-switch').click({ position: 'left' })
         // check that the timeseries plot is visible
         cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
        // click on multiple slices
        cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).click(75, 75)
        cy.wait(150)
        cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2).click(50, 50)
        cy.wait(150)
        // get timeseries data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // account for dummy data in first position of array
            // check that length of data is 3 (i.e. there are two time series and dummy)
            expect(data.length).to.equal(3)
        })
        // click undo fmri time series button
        cy.get(TEST_DOM_IDS.TIMECOURSE.FMRI.UNDO_FMRI_TIMECOURSE).click()
        cy.wait(150)
        // get timeseries data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // check that length of data is 2 (i.e. there are two time series and dummy)
            expect(data.length).to.equal(2)
        })
        // click remove fmri time series button
        cy.get(TEST_DOM_IDS.TIMECOURSE.FMRI.REMOVE_FMRI_TIMECOURSE).click()
        cy.wait(150)
        // get timeseries data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // check that length of data is 1 (i.e. only dummy)
            expect(data.length).to.equal(1)
        })
    })

    it('should plot fmri time series with user-input time series', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get timeseries data
        cy.wait(100)
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // check that length of data is 2 (i.e. there is one time series and dummy)
            expect(data.length).to.equal(2)
        })
        // enable fmri time series button
        cy.get(TEST_DOM_IDS.TIMECOURSE.FMRI.ENABLE_FMRI_TIMECOURSE).parent('.custom-switch').click({ position: 'left' })
        // click on multiple slices
        cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).click(75, 75)
        cy.wait(100)
        // get timeseries data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // check that length of data is 3 (i.e. there are two time series and dummy)
            expect(data.length).to.equal(3)
        })
        
    })

})