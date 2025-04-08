// navigation.command.js
import { TEST_DOM_IDS } from '../testConstants.js';

Cypress.Commands.add('getNiftiSliceData', (sliceId) => {
    cy.get(sliceId).find('.plot-container')
    .should('exist')
    .then($plot => {
        let data
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(sliceId)
            if (plotDiv) {
                data = plotDiv.data[0].z
                return data
            }
        })
    })
})

Cypress.Commands.add('getGiftiData', (surfaceId) => {
    cy.get(surfaceId).find('.plot-container')
    .should('exist')
    .then($plot => {
        let data
        cy.window().then(win => { 
            const plotDiv = win.document.querySelector(surfaceId)
            if (plotDiv) {
                data = plotDiv.data[0].intensity
                return data
            }
        })
    })
})

Cypress.Commands.add('getTimeseriesData', (plotId) => {
    cy.get(plotId).find('.plot-container')
    .should('exist')
    .then($plot => {
        let data
        cy.window().then(win => {
            const plotDiv = win.document.querySelector(plotId)
            if (plotDiv) {
                data = plotDiv.data
                return data
            }
        })
    })
})

Cypress.Commands.add('compareArraysOfArrays', (arr1, arr2) => {
    const compareArraysOfArrays = (arr1, arr2) => {
        if (!Array.isArray(arr1) || !Array.isArray(arr2)) {
            return false;
        }
  
        if (arr1.length !== arr2.length) {
            return false;
        }
    
        for (let i = 0; i < arr1.length; i++) {
            if (Array.isArray(arr1[i]) && Array.isArray(arr2[i])) {
                if (!compareArraysOfArrays(arr1[i], arr2[i])) {
                    return false;
                }
            } else if (arr1[i] !== arr2[i]) {
                return false;
            }
        }
        return true;
    }
    return compareArraysOfArrays(arr1, arr2)
})
