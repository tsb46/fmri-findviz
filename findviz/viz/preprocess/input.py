"""Input validation of user inputs for preprocessing"""

from typing import Literal, List
from findviz.logger_config import setup_logger

from findviz.viz.preprocess.fmri import PreprocessFMRIInputs
from findviz.viz.preprocess.timecourse import PreprocessTimecourseInputs
from findviz.viz.exception import PreprocessInputError
from findviz.viz.preprocess.validate import (
    validate_cutoff_exists, validate_cutoff_nyquist,
    validate_cutoff_order, validate_normalization,
    validate_tr_exists, validate_tr_positive,
    validate_fwhm_positive,
)

# Set up a logger for the app
logger = setup_logger(__name__)

class FMRIPreprocessInputValidator:
    """Class to validate user inputs for preprocessing"""
    def __init__(
        self,
        fmri_file_type: Literal['nifti', 'gifti']
    ):
        self.fmri_file_type = fmri_file_type

    def validate_preprocess_input(
        self, 
        input: PreprocessFMRIInputs
    ) -> bool:
        """Validate user inputs for fmri preprocessing

        Parameters
        ----------
        input : PreprocessFMRIInputs
            User inputs for preprocessing

        Returns
        -------
        bool
            True if inputs are valid, False otherwise
        """
        try:
            self._validate_any_input(input)
            # validate normalization parameters
            if input['normalize']:
                validate_normalization(input['mean_center'], input['zscore'])
            # validate filtering parameters
            if input['filter']:
                validate_tr_exists(input['tr'])
                validate_tr_positive(input['tr'])
                validate_cutoff_exists(input['low_cut'], input['high_cut'])
                # validate below nyquist frequency
                validate_cutoff_nyquist(
                    input['low_cut'], input['tr'], 'low cutoff'
                )
                validate_cutoff_nyquist(
                    input['high_cut'], input['tr'], 'high cutoff'
                )
                # validate cutoff order
                validate_cutoff_order(input['low_cut'], input['high_cut'])
            # validate smoothing parameters
            if input['smooth']:
                validate_fwhm_positive(input['fwhm'])

            return True
        # raise error to handle higher up
        except Exception as e:
            raise e
    
    def _validate_any_input(
        self,
        input: PreprocessFMRIInputs | PreprocessTimecourseInputs
    ) -> None:
        """Validate that at least one preprocessing parameter is passed"""
        input_missing = [
            input['detrend'] is False,
            input['mean_center'] is False,
            input['zscore'] is False,
            input['tr'] is None,
            input['low_cut'] is None,
            input['high_cut'] is None,
            input['fwhm'] is None
        ]
        if all(input_missing):
            logger.error('No preprocessing options selected')
            raise PreprocessInputError('No preprocessing options selected')


class TimecoursePreprocessInputValidator:
    """Class to validate user inputs for timecourse preprocessing"""
    def __init__(
        self,
    ):
        pass

        
    def validate_preprocess_input(
        self, 
        input: PreprocessTimecourseInputs,
        ts_labels: List[str]
    ) -> bool:
        """Validate user inputs for timecourse preprocessing

        Parameters
        ----------
        input : PreprocessTimecourseInputs
            User inputs for preprocessing
        ts_labels : List[str]
            Time course labels

        Returns
        -------
        bool
            True if inputs are valid, False otherwise
        """
        try:
            # validate that at least one time course is selected
            self._validate_ts_selected(ts_labels)
            # validate that at least one preprocessing parameter is passed
            self._validate_any_input(input)
            # validate normalization parameters
            if input['normalize']:
                validate_normalization(input['mean_center'], input['zscore'])
            # validate filtering parameters
            if input['filter']:
                validate_tr_exists(input['tr'])
                validate_tr_positive(input['tr'])
                validate_cutoff_exists(input['low_cut'], input['high_cut'])
                # validate below nyquist frequency
                validate_cutoff_nyquist(
                    input['low_cut'], input['tr'], 'low cutoff'
                )
                validate_cutoff_nyquist(
                    input['high_cut'], input['tr'], 'high cutoff'
                )
                # validate cutoff order
                validate_cutoff_order(input['low_cut'], input['high_cut'])

            return True
        # raise error to handle higher up
        except Exception as e:
            raise e
    
    def _validate_any_input(
        self,
        input: PreprocessTimecourseInputs
    ) -> None:
        """Validate that at least one preprocessing parameter is passed"""
        param_missing = [
            input['detrend'] is False,
            input['mean_center'] is False,
            input['zscore'] is False,
            input['tr'] is None,
            input['low_cut'] is None,
            input['high_cut'] is None,
        ]
        
        # check if any parameters are missing
        if all(param_missing):
            raise PreprocessInputError('No preprocessing options selected')
    
    def _validate_ts_selected(
        self,
        ts_labels: List[str]
    ) -> None:
        """Validate that at least one time course is selected"""
        if ts_labels is None or len(ts_labels) < 1:
            raise PreprocessInputError('No time courses selected')
