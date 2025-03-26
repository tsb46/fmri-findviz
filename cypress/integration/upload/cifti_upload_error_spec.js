// cypress/integration/upload/cifti_upload_error_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('CIFTI Upload Error Tests', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should display error when both mesh files are missing', () => {
        cy.ciftiMissingBothMeshFiles()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when mesh file is incompatible', () => {
        cy.ciftiIncompatibleMeshFile()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })
})