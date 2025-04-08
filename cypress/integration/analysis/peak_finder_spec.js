// cypress/integration/analysis/peak_finder_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('Peak Finder', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should find peaks in timeseries data', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_CONTAINER).should('be.visible')
        // get timeseries data
        let timeSeriesMean
        let timeSeriesLabel
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // account for the first index being dummy data
            // calculate mean of time series
            timeSeriesMean = data[1].y.reduce((a, b) => a + b, 0) / data[1].y.length
            timeSeriesLabel = data[1].name

            // click on peak finder popover
            cy.get(TEST_DOM_IDS.TIMECOURSE.PEAK_FINDER.POPOVER).click()
            // select time course from dropdown
            cy.get(TEST_DOM_IDS.TIMECOURSE.PEAK_FINDER.SELECT_TIMECOURSE)
            .select(timeSeriesLabel, {force: true})
            // set peak height on the mean
            cy.get(TEST_DOM_IDS.TIMECOURSE.PEAK_FINDER.PEAK_HEIGHT)
            .type(timeSeriesMean)
            // run peak finder
            cy.get(TEST_DOM_IDS.TIMECOURSE.PEAK_FINDER.SUBMIT_PEAK_FINDER).click({ force: true })
            cy.wait(100)
            // check that detected peaks are annotated
            cy.getAnnotationData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
            .then(data => {
                // there should be 1 shape for time point marker
                expect(data.length).to.be.greaterThan(1)
            })
        })
    })

    
})
