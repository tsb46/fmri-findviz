"""Validate user inputs for preprocessing"""

from typing import Literal, Tuple

from findviz.viz.exception import PreprocessInputError


def validate_cutoff_exists(low_cut: float, high_cut: float) -> bool:
    """Validate at least one cutoff frequency exists
    
    Parameters
    ----------
    low_cut : float
        Low cutoff frequency in Hz
    high_cut : float
        High cutoff frequency in Hz
        
    Returns
    -------
    bool
        Validation status
    """
    if (low_cut is None or low_cut == '') and (high_cut is None or high_cut == ''):
        error_msg = 'at least lowCut or highCut (in Hz) must be provided'
        raise PreprocessInputError(error_msg, 'filtering')
    return True

def validate_cutoff_nyquist(
    freq: float, 
    tr: float, 
    cutoff_type: Literal['low', 'high']
) -> bool:
    """Validate cutoff frequency is below Nyquist frequency
    
    Parameters
    ----------
    freq : float
        Cutoff frequency in Hz
    tr : float
        Repetition time in seconds
    cutoff_type : str
        Type of cutoff ('lowCut' or 'highCut')
        
    Returns
    -------
    bool
        Validation status
    """
    if freq is not None and freq != '':
        nyquist_freq = (1/tr)/2
        if float(freq) > nyquist_freq:
            error_msg = f'{cutoff_type} must be less than Nyquist frequency: {nyquist_freq}'
            raise PreprocessInputError(error_msg, 'filtering')
    return True

def validate_cutoff_order(low_cut: float, high_cut: float) -> bool:
    """Validate low cutoff is less than high cutoff
    
    Parameters
    ----------
    low_cut : float
        Low cutoff frequency in Hz
    high_cut : float
        High cutoff frequency in Hz
        
    Returns
    -------
    bool
        Validation status
    """
    if (low_cut is not None and low_cut != '') and (high_cut is not None and high_cut != ''):
        if float(low_cut) >= float(high_cut):
            error_msg = 'lowCut must be less than highCut'
            raise PreprocessInputError(error_msg, 'filtering')
    return True

def validate_normalization(mean_center: bool, zscore: bool) -> bool:
    """Validate normalization options
    
    Parameters
    ----------
    mean_center : bool
        Whether to mean center the data
    zscore : bool
        Whether to z-score the data
        
    Returns
    -------
    bool
        Validation status
    """
    if not mean_center and not zscore:
        error_msg = 'If normalization is enabled, mean-center or z-score option must be selected'
        raise PreprocessInputError(error_msg, 'normalization')
    return True

def validate_fwhm_positive(fwhm: float) -> bool:
    """Validate FWHM is positive
    
    Parameters
    ----------
    full_width_half_max : float
        FWHM in mm
        
    Returns
    -------
    bool
        Validation status
    """
    if fwhm < 0:
        error_msg = 'FWHM values must be positive'
        raise PreprocessInputError(error_msg, 'smoothing')
    return True

def validate_tr_exists(tr: float) -> bool:
    """Validate TR exists and is not empty
    
    Parameters
    ----------
    tr : float
        Repetition time in seconds
        
    Returns
    -------
    bool
        Validation status
    """
    if tr is None or tr == '':
        error_msg = 'TR (repetition time) of functional time courses must be provided'
        raise PreprocessInputError(error_msg, 'filtering')
    return True

def validate_tr_positive(tr: float) -> bool:
    """Validate TR is positive
    
    Parameters
    ----------
    tr : float
        Repetition time in seconds
        
    Returns
    -------
    bool
        Validation status
    """
    if tr < 0:
        error_msg = 'TR (repetition time) must be a positive number'
        raise PreprocessInputError(error_msg, 'filtering')
    return True
