// cypress/integration/analysis/average.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('Windowed Average Analysis', () => {
    beforeEach(() => {
        // stub window.open to handle opening of new window after average analysis
        cy.on('window:before:load', (win) => {
            cy.stub(win, 'open').as('windowOpen').callsFake(url => {
                cy.visit(url);
                // check that fmri container is visible in new window
                cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
            })
        })
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should run average analysis on Nifti data', () => {
        // upload Nifti file
        cy.niftiFullWithTimeSeriesUpload()
        // time course plot should be visible
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
        // enable annotation
        cy.get(TEST_DOM_IDS.TIMECOURSE.ANNOTATE.ENABLE_ANNOTATE).parent('.custom-switch').click({ position: 'left' })
        // click on time course plot
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).click(100, 100)
        // click on time course plot again
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).click(150, 100)
        // click on average analysis button
        cy.get(TEST_DOM_IDS.AVERAGE.MODAL_BUTTON).click()
        // submit average form
        cy.get(TEST_DOM_IDS.AVERAGE.AVERAGE_FORM).submit()
    })
})