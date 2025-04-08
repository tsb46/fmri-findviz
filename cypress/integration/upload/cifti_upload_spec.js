// cypress/integration/upload/cifti_upload_spec.js

import { TEST_DOM_IDS } from '../../support/testConstants.js';

describe('CIFTI File Upload tests', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should upload CIFTI file', () => {
    cy.ciftiFullUpload()
    // check the the fmri container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    // check the left hemisphere surface is visible
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('be.visible')
    // check the right hemisphere surface is visible
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.RIGHT_SURFACE_CONTAINER).should('be.visible')
  })

  it('should upload CIFTI left hemisphere file', () => {
    cy.ciftiLeftHemisphereUpload()
    // check the the fmri container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    // check the left hemisphere surface is visible
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('be.visible')
    // check the right hemisphere surface is not visible
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.RIGHT_SURFACE_CONTAINER).should('not.exist')
  })

  it('should upload CIFTI right hemisphere file', () => {
    cy.ciftiRightHemisphereUpload()
    // check the the fmri container is visible
    cy.get(TEST_DOM_IDS.FMRI.CONTAINER).should('be.visible')
    // check the right hemisphere surface is visible
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.RIGHT_SURFACE_CONTAINER).should('be.visible')
    // check the left hemisphere surface is not visible
    cy.get(TEST_DOM_IDS.FMRI.GIFTI_CONTAINER.LEFT_SURFACE_CONTAINER).should('not.exist')
  })



})