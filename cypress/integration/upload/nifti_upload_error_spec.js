// cypress/integration/upload/nifti_upload_error_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('Nifti File Upload Error Tests', () => {
    beforeEach(() => {
        cy.visit('/')
        cy.get('body').should('be.visible')
    })

    it('should display error when functional file is not 4D', () => {
        cy.nifti3dUpload()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when mask dimension is incompatible', () => {
        cy.niftiIncompatibleMaskUpload()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })

    it('should display error when mask is not binary', () => {
        cy.niftiNonBinaryMaskUpload()
        cy.get(TEST_DOM_IDS.UPLOAD.ERROR_MESSAGE).should('be.visible')
    })
})