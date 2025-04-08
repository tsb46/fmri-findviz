// cypress/integration/visualization/nifti_navigation_spec.js
import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('NIFTI Navigation', () => {
    beforeEach(() => {
        cy.visit('/')
        // Wait for app to load
        cy.get('body').should('be.visible')
    })

    it('should navigate through slices of the NIFTI visualization', () => {
        // upload functional NIFTI file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get current voxel coordinates from the visualization
        let voxelCoordinatesY
        let voxelCoordinatesZ
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.VOXEL_Y).then(($el) => {
            voxelCoordinatesY =  $el.text()
        })
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.VOXEL_Z).then(($el) => {
            voxelCoordinatesZ =  $el.text()
        })
        // Get world coordinates
        let worldCoordinatesY
        let worldCoordinatesZ
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.WORLD_Y).then(($el) => {
            worldCoordinatesY =  $el.text()
        })
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.WORLD_Z).then(($el) => {
            worldCoordinatesZ =  $el.text()
        })

        
        // Compare data of second (Y) slice before and after clicking on a different voxel
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2)
        .then(initialData => {
            // Click on a different voxel in first slice of the NIFTI visualization
            // should change the slice of the second slice
            cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).click(75, 75)
            .then(() => {
                // Get new data
                cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_2)
                .then(newData => {
                    // Check if data has changed
                    cy.compareArraysOfArrays(newData, initialData).then(
                        (result) => {
                            expect(result).to.be.false
                        }
                    )
                })
            })
        })

        // Click the slice 1 (X) container
        cy.get(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1).click(50,50)
        // get new voxel coordinates and check that they are different
        let newVoxelCoordinatesY
        let newVoxelCoordinatesZ
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.VOXEL_Y).then(($el) => {
            newVoxelCoordinatesY =  $el.text()
            expect(newVoxelCoordinatesY).not.to.equal(voxelCoordinatesY)
        })
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.VOXEL_Z).then(($el) => {
            newVoxelCoordinatesZ =  $el.text()
            expect(newVoxelCoordinatesZ).not.to.equal(voxelCoordinatesZ)
        })

        // Get new world coordinates
        let newWorldCoordinatesY
        let newWorldCoordinatesZ
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.WORLD_Y).then(($el) => {
            newWorldCoordinatesY =  $el.text()
            expect(newWorldCoordinatesY).not.to.equal(worldCoordinatesY)
        })
        cy.get(TEST_DOM_IDS.FMRI.COORDINATE.WORLD_Z).then(($el) => {
            newWorldCoordinatesZ =  $el.text()
            expect(newWorldCoordinatesZ).not.to.equal(worldCoordinatesZ)
        })
    })

    it('should change orthogonal to montage view of the NIFTI visualization', () => {
        // upload functional NIFTI file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // compare data of first slice before and after clicking on the montage button
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(initialData => {
            // click the montage button
            cy.get(TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TOGGLE_VIEW_BUTTON).click()
            // Get new data
            cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
            .then(newData => {
                // Check if data has changed
                expect(newData).not.to.equal(initialData)
            })
        })
    })

    it ('should change slice indices on the montage view of the NIFTI visualization', () => {
        // upload functional NIFTI file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // click the montage button
        cy.get(TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TOGGLE_VIEW_BUTTON).click()
        // get current data of first slice
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(initialData => {
            // click on montage popover
            cy.get(TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_POPOVER).click()
            // move slice 1 slider from DOM
            cy.get(`${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_SLICE_SLIDER_CONTAINER}`)
            .find('.slider-handle').eq(0).click().type('{rightarrow}{rightarrow}')
            // Get data of first slice
            cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
            .then(newData => {
                // Check if data has changed
                cy.compareArraysOfArrays(newData, initialData).then(
                    (result) => {
                        expect(result).to.be.false
                    }
                )
            })
        })
    })

    it ('should change slice indices on a change in montage slice direction', () => {
        // upload functional NIFTI file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // click the montage button
        cy.get(TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.TOGGLE_VIEW_BUTTON).click()
        // get current data of first slice
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(initialData => {
            // click on montage popover
            cy.get(TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_POPOVER).click()
            // select coronal ('y') view from dropdown
            cy.get(`.popover ${TEST_DOM_IDS.FMRI.VISUALIZATION_OPTIONS.MONTAGE_SLICE_SELECT}`).select('y')
            cy.wait(100)
            // Get data of first slice
            cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
            .then(newData => {
                // Check if data has changed
                cy.compareArraysOfArrays(newData, initialData).then(
                    (result) => {
                        expect(result).to.be.false
                    }
                )
            })
        })
    })

    it('should change nifti visualization on time slider change', () => {
        // upload functional NIFTI file
        cy.niftiFunctionalUpload()
        // check that the visualization is visible
        cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
        // get initial slice data
        cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
        .then(initialData => {
            // move the time slider
            cy.get(TEST_DOM_IDS.TIME_SLIDER.TIME_SLIDER_CONTAINER)
            .find('.slider-handle').eq(0).click().type('{rightarrow}{rightarrow}')
            // get new slice data
            cy.getNiftiSliceData(TEST_DOM_IDS.FMRI.NIFTI_CONTAINER.SLICE_1)
            .then(newData => {
                // check that the data has changed
                expect(newData).not.to.equal(initialData)
            })
        })
    })
})


