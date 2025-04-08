// task_design_visualization_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('Task Design Visualization', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should toggle convolution of task design time course', () => {
        // upload task design file
        cy.niftiWithTaskDesignFile()
        // add TR and slicetime and submit
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.TR).type('2')
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.SLICETIME).type('0.5')
        cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        cy.wait(400)
        // get current time course data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // get currently selected time course
            cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SELECT_TIMECOURSE)
            .then(selectedTimeCourse => {
                // find the time course in the data object
                const currentTimeCourseData = data.find(d => d.name === selectedTimeCourse.val()).y
                // toggle convolution
                cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONVOLUTION_CHECKBOX).click({ force: true })
                // get new time course data
                cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
                .then(data => {
                    const newTimeCourseData = data.find(d => d.name === selectedTimeCourse.val()).y
                    cy.compareArraysOfArrays(newTimeCourseData, currentTimeCourseData).then(
                        (isEqual) => {
                            expect(isEqual).to.be.false
                        }
                    )
                })
                // toggle convolution back
                cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.CONVOLUTION_CHECKBOX).click({ force: true })
                // get new time course data
                cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
                .then(data => {
                    const newTimeCourseData = data.find(d => d.name === selectedTimeCourse.val()).y
                    cy.compareArraysOfArrays(newTimeCourseData, currentTimeCourseData).then(
                        (isEqual) => {
                            expect(isEqual).to.be.true
                        }
                    )
                })
            })
        })
    })

    it('should toggle global convolution of task design time course', () => {
        // upload task design file
        cy.niftiWithTaskDesignFile()
        // add TR and slicetime and submit
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.TR).type('2')
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.SLICETIME).type('0.5')
        cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        cy.wait(400)
        // get current time course data
        cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
        .then(data => {
            // get currently selected time course
            cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SELECT_TIMECOURSE)
            .then(selectedTimeCourse => {
                // find the time course in the data object
                const currentTimeCourseData = data.find(d => d.name === selectedTimeCourse.val()).y
                // toggle global convolution
                cy.get(TEST_DOM_IDS.TIMECOURSE.VISUALIZATION_OPTIONS.TOGGLE_CONVOLUTION).click({ force: true })
                // get new time course data
                cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
                .then(data => {
                    const newTimeCourseData = data.find(d => d.name === selectedTimeCourse.val()).y
                    cy.compareArraysOfArrays(newTimeCourseData, currentTimeCourseData).then(
                        (isEqual) => {
                            expect(isEqual).to.be.false
                        }
                    )
                })
                // toggle global convolution back
                cy.get(TEST_DOM_IDS.TIMECOURSE.VISUALIZATION_OPTIONS.TOGGLE_CONVOLUTION).click({ force: true })
                // get new time course data
                cy.getTimeseriesData(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT)
                .then(data => {
                    const newTimeCourseData = data.find(d => d.name === selectedTimeCourse.val()).y
                    cy.compareArraysOfArrays(newTimeCourseData, currentTimeCourseData).then(
                        (isEqual) => {
                            expect(isEqual).to.be.true
                        }
                    )
                })
            })
        })
    })
})
