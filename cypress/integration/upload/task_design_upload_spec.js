// Task design upload spec
import { TEST_DOM_IDS } from '../../support/testConstants.js';
describe('Task Design Upload', () => {
  beforeEach(() => {
    cy.visit('/')
    // Wait for app to load
    cy.get('body').should('be.visible')
  })

  it('should upload task design', () => {
    cy.niftiWithTaskDesignFile()
    // add TR and slicetime
    cy.get(TEST_DOM_IDS.UPLOAD.TASK.TR).type('2')
    cy.get(TEST_DOM_IDS.UPLOAD.TASK.SLICETIME).type('0.5')
    cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
    // check that the fMRI container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    // check that the time course plot is visible
    cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
    // check for multiple time series in the dropdown
    cy.get(TEST_DOM_IDS.TIMECOURSE.LINE_PLOT_OPTIONS.SELECT_TIMECOURSE)
        .find('option')
        .should('have.length.at.least', 2)
  })
})
