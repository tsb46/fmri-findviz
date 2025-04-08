// cypress/integration/analysis/distance.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('Distance Analysis', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should run distance analysis on Nifti data', () => {
        // upload Nifti file
        cy.niftiFunctionalAndMaskUpload()
        // click on distance analysis button
        cy.get(TEST_DOM_IDS.DISTANCE.MODAL_BUTTON).click()
        // submit distance form
        cy.get(TEST_DOM_IDS.DISTANCE.DISTANCE_FORM).submit()
        // force close modal
        cy.get('[data-cy="modal"]').contains('button', 'Close').click()
        cy.get('[data-cy="modal"]').should('not.exist')
        // check that the distance plot is visible
        cy.get(TEST_DOM_IDS.DISTANCE.PLOT).should('be.visible')
        // remove distance plot
        cy.get(TEST_DOM_IDS.DISTANCE.REMOVE_DISTANCE_BUTTON).click()
        cy.get(TEST_DOM_IDS.DISTANCE.PLOT).should('not.be.visible')
    })

    it('should run distance analysis on Gifti data', () => {
        // upload Gifti file
        cy.giftiLeftHemisphereUpload()
        // click on distance analysis button
        cy.get(TEST_DOM_IDS.DISTANCE.MODAL_BUTTON).click()
        // submit distance form
        cy.get(TEST_DOM_IDS.DISTANCE.DISTANCE_FORM).submit()
        // force close modal
        cy.get('[data-cy="modal"]').contains('button', 'Close').click()
        cy.get('[data-cy="modal"]').should('not.exist')
        // check that the distance plot is visible
        cy.get(TEST_DOM_IDS.DISTANCE.PLOT).should('be.visible')
        // remove distance plot
        cy.get(TEST_DOM_IDS.DISTANCE.REMOVE_DISTANCE_BUTTON).click()
        cy.get(TEST_DOM_IDS.DISTANCE.PLOT).should('not.be.visible')
    })

    it('should change time point with slider and run distance analysis', () => {
        // upload Nifti file
        cy.niftiFunctionalAndMaskUpload()
        // move the time slider
        cy.get(TEST_DOM_IDS.TIME_SLIDER.TIME_SLIDER_CONTAINER)
        .find('.slider-handle').eq(0).click().type('{rightarrow}{rightarrow}')
        // click on distance analysis button
        cy.get(TEST_DOM_IDS.DISTANCE.MODAL_BUTTON).click()
        // submit distance form
        cy.get(TEST_DOM_IDS.DISTANCE.DISTANCE_FORM).submit()
        // force close modal
        cy.get('[data-cy="modal"]').contains('button', 'Close').click()
        cy.get('[data-cy="modal"]').should('not.exist')
        // check that the distance plot is visible
    })
})