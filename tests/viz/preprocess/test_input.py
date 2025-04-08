"""Tests for preprocessing input validation"""
import pytest

from findviz.viz.preprocess.input import (
    FMRIPreprocessInputValidator,
    TimecoursePreprocessInputValidator
)
from findviz.viz.preprocess.fmri import PreprocessFMRIInputs
from findviz.viz.preprocess.timecourse import PreprocessTimecourseInputs
from findviz.viz.exception import PreprocessInputError


@pytest.fixture
def valid_fmri_inputs():
    """Create valid fMRI preprocessing inputs"""
    return PreprocessFMRIInputs(
        normalize=True,
        filter=True,
        smooth=True,
        detrend=True,
        mean_center=True,
        zscore=True,
        tr=2.0,
        low_cut=0.01,
        high_cut=0.1,
        fwhm=6.0
    )


@pytest.fixture
def valid_timecourse_inputs():
    """Create valid timecourse preprocessing inputs"""
    return PreprocessTimecourseInputs(
        normalize=True,
        filter=True,
        detrend=True,
        mean_center=True,
        zscore=True,
        tr=2.0,
        low_cut=0.01,
        high_cut=0.1
    )


class TestFMRIPreprocessInputValidator:
    """Test FMRI preprocessing input validation"""

    def test_validate_valid_inputs(self, valid_fmri_inputs):
        """Test validation with valid inputs"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        assert validator.validate_preprocess_input(valid_fmri_inputs) is True

        # Test with gifti file type
        validator = FMRIPreprocessInputValidator(fmri_file_type='gifti')
        assert validator.validate_preprocess_input(valid_fmri_inputs) is True

    def test_validate_no_preprocessing(self):
        """Test validation with no preprocessing options selected"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        inputs = PreprocessFMRIInputs(
            normalize=False,
            filter=False,
            smooth=False,
            detrend=False,
            mean_center=False,
            zscore=False,
            tr=None,
            low_cut=None,
            high_cut=None,
            fwhm=None
        )
        
        with pytest.raises(PreprocessInputError, match="No preprocessing options selected"):
            validator.validate_preprocess_input(inputs)

    def test_validate_normalization_error(self, valid_fmri_inputs):
        """Test validation with invalid normalization parameters"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        
        # Set normalize=True but both mean_center and zscore to False
        inputs = valid_fmri_inputs.copy()
        inputs['normalize'] = True
        inputs['mean_center'] = False
        inputs['zscore'] = False
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs)

    def test_validate_filter_missing_tr(self, valid_fmri_inputs):
        """Test validation with missing TR for filtering"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        
        # Set filter=True but tr=None
        inputs = valid_fmri_inputs.copy()
        inputs['filter'] = True
        inputs['tr'] = None
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs)

    def test_validate_filter_negative_tr(self, valid_fmri_inputs):
        """Test validation with negative TR for filtering"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        
        # Set filter=True but tr negative
        inputs = valid_fmri_inputs.copy()
        inputs['filter'] = True
        inputs['tr'] = -2.0
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs)

    def test_validate_filter_missing_cutoffs(self, valid_fmri_inputs):
        """Test validation with missing cutoffs for filtering"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        
        # Set filter=True but cutoffs=None
        inputs = valid_fmri_inputs.copy()
        inputs['filter'] = True
        inputs['low_cut'] = None
        inputs['high_cut'] = None
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs)

    def test_validate_filter_nyquist_violation(self, valid_fmri_inputs):
        """Test validation with cutoffs above Nyquist frequency"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        
        # Set filter=True but high_cut above Nyquist
        inputs = valid_fmri_inputs.copy()
        inputs['filter'] = True
        inputs['tr'] = 2.0  # Nyquist = 0.25 Hz
        inputs['high_cut'] = 0.3  # Above Nyquist
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs)

    def test_validate_filter_cutoff_order(self, valid_fmri_inputs):
        """Test validation with low cutoff > high cutoff"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        
        # Set filter=True but low_cut > high_cut
        inputs = valid_fmri_inputs.copy()
        inputs['filter'] = True
        inputs['low_cut'] = 0.2
        inputs['high_cut'] = 0.1
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs)

    def test_validate_smooth_negative_fwhm(self, valid_fmri_inputs):
        """Test validation with negative FWHM for smoothing"""
        validator = FMRIPreprocessInputValidator(fmri_file_type='nifti')
        
        # Set smooth=True but fwhm negative
        inputs = valid_fmri_inputs.copy()
        inputs['smooth'] = True
        inputs['fwhm'] = -6.0
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs)


class TestTimecoursePreprocessInputValidator:
    """Test timecourse preprocessing input validation"""

    def test_validate_valid_inputs(self, valid_timecourse_inputs):
        """Test validation with valid inputs"""
        validator = TimecoursePreprocessInputValidator()
        assert validator.validate_preprocess_input(valid_timecourse_inputs, ['ts1', 'ts2']) is True

    def test_validate_no_preprocessing(self):
        """Test validation with no preprocessing options selected"""
        validator = TimecoursePreprocessInputValidator()
        inputs = PreprocessTimecourseInputs(
            normalize=False,
            filter=False,
            detrend=False,
            mean_center=False,
            zscore=False,
            tr=None,
            low_cut=None,
            high_cut=None
        )
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs, ['ts1'])

    def test_validate_no_timecourses(self, valid_timecourse_inputs):
        """Test validation with no timecourses selected"""
        validator = TimecoursePreprocessInputValidator()
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(valid_timecourse_inputs, [])
            
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(valid_timecourse_inputs, None)

    def test_validate_normalization_error(self, valid_timecourse_inputs):
        """Test validation with invalid normalization parameters"""
        validator = TimecoursePreprocessInputValidator()
        
        # Set normalize=True but both mean_center and zscore to False
        inputs = valid_timecourse_inputs.copy()
        inputs['normalize'] = True
        inputs['mean_center'] = False
        inputs['zscore'] = False
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs, ['ts1'])

    def test_validate_filter_missing_tr(self, valid_timecourse_inputs):
        """Test validation with missing TR for filtering"""
        validator = TimecoursePreprocessInputValidator()
        
        # Set filter=True but tr=None
        inputs = valid_timecourse_inputs.copy()
        inputs['filter'] = True
        inputs['tr'] = None
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs, ['ts1'])

    def test_validate_filter_negative_tr(self, valid_timecourse_inputs):
        """Test validation with negative TR for filtering"""
        validator = TimecoursePreprocessInputValidator()
        
        # Set filter=True but tr negative
        inputs = valid_timecourse_inputs.copy()
        inputs['filter'] = True
        inputs['tr'] = -2.0
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs, ['ts1'])

    def test_validate_filter_missing_cutoffs(self, valid_timecourse_inputs):
        """Test validation with missing cutoffs for filtering"""
        validator = TimecoursePreprocessInputValidator()
        
        # Set filter=True but cutoffs=None
        inputs = valid_timecourse_inputs.copy()
        inputs['filter'] = True
        inputs['low_cut'] = None
        inputs['high_cut'] = None
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs, ['ts1'])

    def test_validate_filter_nyquist_violation(self, valid_timecourse_inputs):
        """Test validation with cutoffs above Nyquist frequency"""
        validator = TimecoursePreprocessInputValidator()
        
        # Set filter=True but high_cut above Nyquist
        inputs = valid_timecourse_inputs.copy()
        inputs['filter'] = True
        inputs['tr'] = 2.0  # Nyquist = 0.25 Hz
        inputs['high_cut'] = 0.3  # Above Nyquist
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs, ['ts1'])

    def test_validate_filter_cutoff_order(self, valid_timecourse_inputs):
        """Test validation with low cutoff > high cutoff"""
        validator = TimecoursePreprocessInputValidator()
        
        # Set filter=True but low_cut > high_cut
        inputs = valid_timecourse_inputs.copy()
        inputs['filter'] = True
        inputs['low_cut'] = 0.2
        inputs['high_cut'] = 0.1
        
        with pytest.raises(PreprocessInputError):
            validator.validate_preprocess_input(inputs, ['ts1'])
