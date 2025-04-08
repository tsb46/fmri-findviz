// nifti_visualization_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

describe('NIFTI Visualization', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should change color min max of nifti visualization', () => {
        // upload nifti file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get color min max
        let originalColorMinMax
        cy.getNiftiColorMinMax(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(colorMinMax => {
            originalColorMinMax = colorMinMax;
        })
        // change max color on color range slider
        cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLOR_RANGE_SLIDER_FORM}`)
            .find('.max-slider-handle').eq(0).click().type('{rightarrow}{rightarrow}')
        // get color min max again
        cy.getNiftiColorMinMax(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(newColorMinMax => {
            // check that color min max has changed
            expect(newColorMinMax.max).not.equal(originalColorMinMax.max)
        })
    })

    it('should threshold nifti visualization', () => {
        // upload nifti file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2)
        .then(initialData => {
            // change threshold on threshold slider
            cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.THRESHOLD_SLIDER_FORM}`)
                .find('.max-slider-handle').eq(0).click()
                .type('{rightarrow}{rightarrow}{rightarrow}')
            // get nifti slice data again
            cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2)
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

    it('should change opacity of nifti visualization', () => {
        // upload nifti file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get opacity
        let originalOpacity
        cy.getNiftiOpacity(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(opacity => {
            originalOpacity = opacity;
        })
        // change opacity on opacity slider
        cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.OPACITY_SLIDER_FORM}`)
            .find('.slider-handle').eq(0).click().type('{leftarrow}{leftarrow}')
        // get opacity again
        cy.getNiftiOpacity(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(newOpacity => {
            // check that opacity has changed
            expect(newOpacity).not.equal(originalOpacity)
        })
    })

    it('should change colormap of nifti visualization', () => {
        // upload nifti file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get colormap
        let originalColormap
        cy.getNiftiColormap(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(colormap => {
            originalColormap = colormap;
        })
        // change colormap on colormap dropdown
        cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_TOGGLE}`)
            .click().get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.COLORMAP_DROPDOWN_MENU}`)
            .find('li').eq(1).click()
        // get colormap again
        cy.getNiftiColormap(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(newColormap => {
            // check that colormap has changed
            expect(newColormap).not.equal(originalColormap)
        })
    })
})

