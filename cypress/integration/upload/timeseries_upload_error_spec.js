// cypress/integration/upload/timeseries_upload_error_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('Timeseries Upload Error Tests', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should display error when time series file is incompatible', () => {
        cy.niftiIncompatibleTimeSeriesFile()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when time series file has string values', () => {
        cy.niftiTimeSeriesFileWithStringValues()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })
})