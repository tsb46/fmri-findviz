// cypress/integration/upload/task_design_upload_error_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('Task Design Upload Error', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should display error when task design file is missing onset', () => {
        cy.niftiWithTaskDesignFileMissingOnset()
        // add TR and slicetime
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.TR).type('2')
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.SLICETIME).type('0.5')
        cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
        // check that the error message is visible
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when task design file has string values for onset', () => {
        cy.niftiWithTaskDesignFileWithStringValues()
        // add TR and slicetime
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.TR).type('2')
        cy.get(TEST_DOM_IDS.UPLOAD.TASK.SLICETIME).type('0.5')
        cy.get(TEST_DOM_IDS.UPLOAD.SUBMIT_BUTTON).click()
    })
})
