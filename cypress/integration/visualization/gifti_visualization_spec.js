// cypress/integration/visualization/gifti_visualization_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('GIFTI Visualization', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should change color min max of gifti visualization', () => {
        // upload GIFTI file
        cy.giftiLeftHemisphereUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get color min max
        let originalColorMinMax
        cy.getGiftiColorMinMax(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(colorMinMax => {
            originalColorMinMax = colorMinMax;
            
        })
        // change max color on color range slider
        cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLOR_RANGE_SLIDER_FORM}`)
        .find('.max-slider-handle').eq(0).click().type('{rightarrow}{rightarrow}')
        // get color min max again
        cy.getGiftiColorMinMax(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(newColorMinMax => {
            // check that color min max has changed
            expect(newColorMinMax.max).not.equal(originalColorMinMax.max)
        })
    })

    it('should threshold gifti visualization', () => {
        // upload gifti file
        cy.giftiLeftHemisphereUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        cy.getGiftiData(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(initialData => {
            // change threshold on threshold slider
            cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.THRESHOLD_SLIDER_FORM}`)
                .find('.max-slider-handle').eq(0).click()
                .type('{rightarrow}{rightarrow}{rightarrow}')
            // get gifti slice data again
            cy.getGiftiData(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
            .then(newData => {
                // check that data has changed
                cy.compareArraysOfArrays(newData, initialData).then(
                    (result) => {
                        expect(result).to.be.false
                    }
                )
            })
        })
    })

    it('should change opacity of gifti visualization', () => {
        // upload gifti file
        cy.giftiLeftHemisphereUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get opacity
        let originalOpacity
        cy.getGiftiOpacity(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(opacity => {
            originalOpacity = opacity;
        })
        // change opacity on opacity slider
        cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.OPACITY_SLIDER_FORM}`)
            .find('.slider-handle').eq(0).click().type('{leftarrow}{leftarrow}')
        // get opacity again
        cy.getGiftiOpacity(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(newOpacity => {
            // check that opacity has changed
            expect(newOpacity).not.equal(originalOpacity)
        })
    })

    it('should change colormap of gifti visualization', () => {
        // upload gifti file
        cy.giftiLeftHemisphereUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get colormap
        let originalColormap
        cy.getGiftiColormap(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(colormap => {
            originalColormap = colormap;
        })
        // change colormap on colormap dropdown
        cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_TOGGLE}`)
            .click().get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_MENU}`)
            .find('li').eq(1).click()
        // get colormap again
        cy.getGiftiColormap(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER)
        .then(newColormap => {
            // check that colormap has changed
            expect(newColormap).not.equal(originalColormap)
        })
    })
})
