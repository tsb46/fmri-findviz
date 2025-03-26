// cypress/integration/visualization/timeseries_visualization_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('Timeseries Visualization', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should change color min max of timeseries visualization', () => {
        // upload timeseries file
        // Upload NIFTI with multiple time series
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // change color of line plot
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.COLOR_SELECT).select('red')
        // check that the color has changed to red
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.COLOR_SELECT)
        .should('have.value', 'red')
        // change color of line plot
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.COLOR_SELECT).select('blue')
        // check that the color has changed to blue
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.COLOR_SELECT)
        .should('have.value', 'blue')
    })

    it('should change line marker shape of timeseries visualization', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // change color of line plot
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.MARKER_SELECT).select('lines+markers')
        // check that the color has changed to red
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.MARKER_SELECT)
        .should('have.value', 'lines+markers')
        // change color of line plot
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.MARKER_SELECT).select('lines')
        // check that the color has changed to blue
        cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.MARKER_SELECT)
        .should('have.value', 'lines')
    })

    it('should change line width of timeseries visualization', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get current line width
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            const currentLineWidth = data[1].line.width
            // change line width
            cy.get(`${TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.WIDTH_SLIDER_CONTAINER}`)
            .find('.slider-handle').eq(0).click()
            .type('{rightarrow}{rightarrow}{rightarrow}{rightarrow}{rightarrow}{rightarrow}')
            // get new line width
            cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
            .then(data => {
                const newLineWidth = data[1].line.width
                expect(newLineWidth).to.be.greaterThan(currentLineWidth)
            })
        })
    })

    it('should change line opacity of timeseries visualization', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get current line opacity
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            const currentLineOpacity = data[1].opacity
            // change line opacity
            cy.get(`${TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.OPACITY_SLIDER_CONTAINER}`)
            .find('.slider-handle').eq(0).click()
            .type('{leftarrow}{leftarrow}')
            // get new line opacity
            cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
            .then(data => {
                const newLineOpacity = data[1].opacity
                expect(newLineOpacity).to.be.lessThan(currentLineOpacity)
            })
        })
    })

    it('should shift up time course data', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get current time course data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            const currentTimeCourseDataFirstSlice = data[1].y[0]
            // shift up time course data
            cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONSTANT_SHIFT_INCREASE).click()
            // get new time course data
            cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
            .then(data => {
                const newTimeCourseDataFirstSlice = data[1].y[0]
                expect(newTimeCourseDataFirstSlice).to.be.greaterThan(currentTimeCourseDataFirstSlice)
            })
        })
    })

    it('should remove shift history from time course data', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get current time course data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            const currentTimeCourseDataFirstSlice = data[1].y[0]
            // shift up time course data
            cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONSTANT_SHIFT_INCREASE)
            .click().click()
            // remove shift history
            cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONSTANT_SHIFT_RESET).click()
            // get new time course data
            cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
            .then(data => {
                const newTimeCourseDataFirstSlice = data[1].y[0]
                expect(newTimeCourseDataFirstSlice).to.be.equal(currentTimeCourseDataFirstSlice)
            })
        })
    })

    it('should convert display of time points (TR) to time units in seconds', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get current time course data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            const currentXAxis = data[1].x
            // fill in TR in form
            cy.get(TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TR_CONVERT_FORM)
            .type('2')
            // convert display of time points (TR) to time units in seconds
            cy.get(TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TR_CONVERT_BUTTON).click({ force: true })
            // get new time course data
            cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
            .then(data => {
                const newXAxis = data[1].x
                expect(newXAxis).to.be.not.equal(currentXAxis)
            })
        })
    })

    it('should annotate time course data', () => {
        // upload timeseries file
        cy.niftiWithTimeSeriesUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // enable annotation
        cy.get(TEST_DOM_IDS.TIMECOURSE.ANNOTATE.ENABLE_ANNOTATE).parent('.custom-switch').click({ position: 'left' })
        // click on time course plot
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).click(100, 100)
        // get annotation shapes from time course plot
        cy.getAnnotationData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // there should be 1 shape for time point marker, 
            // 1 shape for the annotation highlight, 
            // and 1 shape for the annotation line
            expect(data.length).to.be.equal(3)
        })
        // remove annotation
        cy.get(TEST_DOM_IDS.TIMECOURSE.ANNOTATE.REMOVE_ANNOTATE).click()
        // get annotation shapes from time course plot
        cy.getAnnotationData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // there should be 1 shape for time point marker
            expect(data.length).to.be.equal(1)
        })
    })
})