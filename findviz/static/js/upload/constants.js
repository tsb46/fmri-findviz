// constants.js

// file upload form fields
const FILE_UPLOAD_FIELDS = {
  FMRI: {
    GIFTI: {
      LEFT_FUNC: 'left-hemisphere-gifti-func',
      RIGHT_FUNC: 'right-hemisphere-gifti-func',
      LEFT_MESH: 'left-hemisphere-gifti-mesh',
      RIGHT_MESH: 'right-hemisphere-gifti-mesh'
    },
    NIFTI: {
      FUNC: 'nifti-func',
      ANAT: 'nifti-anat',
      MASK: 'nifti-mask',
    },
  },
  TS: {
    FILE: 'time-series-file',
    LABEL: 'time-series-label',
    HEADER: 'has-header'
  },
  TASK: {
    FILE: 'task-design-file',
    TR: 'task-design-tr',
    SLICETIME: 'task-design-slicetime'
  }
}

// FMRI file types - gifti or nifti
const FMRI_FILE_TYPES = {
    NIFTI: 'nifti',
    GIFTI: 'gifti'
};

// endpoints for uploading files
const UPLOAD_ENDPOINTS = {
    FILES: '/upload',
    HEADER: '/get_header',
    SCENE: '/upload_cache'
};

export { FILE_UPLOAD_FIELDS, FMRI_FILE_TYPES, UPLOAD_ENDPOINTS };
