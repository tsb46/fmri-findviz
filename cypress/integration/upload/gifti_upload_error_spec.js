// cypress/integration/upload/gifti_upload_error_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('Gifti File Upload Error Tests', () => {
    beforeEach(() => {
        cy.visit('/')
        cy.get('body').should('be.visible')
    })

    it('should display error when left hemisphere mesh file is not present', () => {
        cy.giftiLeftHemisphereUploadMissingMesh()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when right hemisphere mesh file is not present', () => {
        cy.giftiRightHemisphereUploadMissingMesh()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when left hemisphere functional file is not present', () => {
        cy.giftiLeftHemisphereUploadMissingFunctional()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when right hemisphere functional file is not present', () => {
        cy.giftiRightHemisphereUploadMissingFunctional()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when left hemisphere mesh file is incompatible', () => {
        cy.giftiLeftHemisphereUploadIncompatibleMesh()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when left and right hemispheres have incompatible time series', () => {
        cy.giftiLeftAndRightHemisphereUploadIncompatibleTimeSeries()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })
    
})