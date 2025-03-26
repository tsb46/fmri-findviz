// cypress/integration/analysis/correlate.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('Correlation Analysis', () => {
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

    it('should run correlate analysis on Nifti data', () => {
        // upload Nifti file
        cy.niftiFullWithTimeSeriesUpload()
        // time course plot should be visible
        cy.get(TEST_DOM_IDS.TIMECOURSE.TIME_COURSE_PLOT).should('be.visible')
        // click on correlate modalbutton
        cy.get(TEST_DOM_IDS.CORRELATE.MODAL_BUTTON).click()
        // set negative and positive lag
        cy.get(TEST_DOM_IDS.CORRELATE.NEGATIVE_LAG).invoke('val', '-1')
        cy.get(TEST_DOM_IDS.CORRELATE.POSITIVE_LAG).invoke('val', '1')
        // submit correlation form
        cy.get(TEST_DOM_IDS.CORRELATE.CORRELATE_FORM).submit()
    })
})