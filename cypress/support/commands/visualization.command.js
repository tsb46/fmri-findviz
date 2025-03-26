// visualization.command.js
import { TEST_DOM_IDS } from '../../support/testConstants.js'

Cypress.Commands.add('getNiftiColorMinMax', (sliceId) => {
    cy.get(sliceId)
    .should('exist')
    .then($container => {
        let colorMinMax
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(sliceId)
            if (plotDiv) {
                colorMinMax = {
                    min: plotDiv.data[0].zmin,
                    max: plotDiv.data[0].zmax
                }
                return colorMinMax
            }
        })
    })
})

Cypress.Commands.add('getGiftiColorMinMax', (surfaceId) => {
    cy.get(surfaceId).find('.plot-container')
    .should('exist')
    .then($plot => {
        let colorMinMax
        cy.window().then(win => { 
            const plotDiv = win.document.querySelector(surfaceId)
            if (plotDiv) {
                colorMinMax = {
                    min: plotDiv.data[0].cmin,
                    max: plotDiv.data[0].cmax
                }
                return colorMinMax
            }
        })
    })
})

Cypress.Commands.add('getNiftiColormap', (sliceId) => {
    cy.get(sliceId)
    .should('exist')
    .then($container => {
        let colormap
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(sliceId)
            if (plotDiv) {
                colormap = plotDiv.data[0].colorscale
                return colormap
            }
        })
    })
})

Cypress.Commands.add('getGiftiColormap', (surfaceId) => {
    cy.get(surfaceId).find('.plot-container')
    .should('exist')
    .then($plot => {
        let colormap
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(surfaceId)
            if (plotDiv) {
                colormap = plotDiv.data[0].colorscale
                return colormap
            }
        })
    })
})

Cypress.Commands.add('getNiftiOpacity', (sliceId) => {
    cy.get(sliceId)
    .should('exist')
    .then($container => {
        let opacity
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(sliceId)
            if (plotDiv) {
                opacity = plotDiv.data[0].opacity
                return opacity
            }
        })
    })
})

Cypress.Commands.add('getGiftiOpacity', (surfaceId) => {
    cy.get(surfaceId).find('.plot-container')
    .should('exist')
    .then($plot => {
        let opacity
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(surfaceId)
            if (plotDiv) {
                opacity = plotDiv.data[0].opacity
                return opacity
            }
        })
    })
})

Cypress.Commands.add('getAnnotationData', (plotId) => {
    cy.get(plotId)
    .should('exist')
    .then($plot => {
        let annotationData
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(plotId)
            if (plotDiv) {
                annotationData = plotDiv.layout.shapes
                return annotationData
            }
        })
    })
})