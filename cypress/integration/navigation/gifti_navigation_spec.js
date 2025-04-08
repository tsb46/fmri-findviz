// cypress/integration/visualization/gifti_navigation_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('GIFTI Navigation', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    // TODO: gifti click navigation spec

    it('should change the GIFTI visualization on time slider change', () => {
        // upload GIFTI file
        cy.giftiLeftHemisphereUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get initial slice data
        cy.getGiftiData(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).then(
            (initialData) => {
                // move the time slider
                cy.get(TEST_DOM_IDS.TIME_SLIDER.TIME_SLIDER_CONTAINER)
                .find('.slider-handle').eq(0).click().type('{rightarrow}{rightarrow}')
                // check that the visualization has changed
                cy.getGiftiData(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).then(
                    (newData) => {
                        cy.compareArraysOfArrays(newData, initialData).then(
                            (isEqual) => {
                                expect(isEqual).to.be.false
                            }
                        )
                    }
                )
            }
        )
    })
})