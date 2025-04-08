// cypress/integration/upload/gifti_upload.spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('Gifti File Upload Tests', () => {
    beforeEach(() => {
      cy.visit('/')
      // Wait for app to load
      cy.get('body').should('be.visible')
    })

    it('should upload all Gifti files and display viewer', () => {
        // Gifti full upload flow
        cy.giftiFullUpload()
        // check the the fmri container is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // Verify left and right hemisphere functional files are visible
        cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('be.visible')
        cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.RIGHT_SURFACE_CONTAINER).should('be.visible')
    })

    it('should upload left hemisphere files and display viewer', () => {
        cy.giftiLeftHemisphereUpload()
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('be.visible')
        cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.RIGHT_SURFACE_CONTAINER).should('not.exist')
    })

    it('should upload right hemisphere files and display viewer', () => {
      cy.giftiRightHemisphereUpload()
      cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('not.exist')
        cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.RIGHT_SURFACE_CONTAINER).should('be.visible')
    })

    it('should upload serialized .fvstate file and display viewer', () => {
      cy.fvstateUploadGifit()
      cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
      cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('be.visible')
    })
})


