"""
This module defines the plot options classes for the FIND viewer.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Tuple

from findviz.viz.analysis.scaler import SignalScaler, SignalShifter

class ColorMaps(Enum):
    """
    Enum for color maps
    """
    GREYS = 'Greys'
    YLGNBU = 'YlGnBu'
    GREENS = 'Greens'
    YLORRD = 'YlOrRd'
    BLUERED = 'Bluered'
    RDBU = 'RdBu'
    REDS = 'Reds'
    BLUES = 'Blues'
    PICNIC = 'Picnic'
    RAINBOW = 'Rainbow'
    PORTLAND = 'Portland'
    JET = 'Jet'
    HOT = 'Hot'
    BLACKBODY = 'Blackbody'
    ELECTRIC = 'Electric'
    VIRIDIS = 'Viridis'
    CIVIDIS = 'Cividis'

class TimeCourseColor(Enum):
    """Time course color options."""
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'
    ORANGE = 'orange'
    PURPLE = 'purple'
    BLACK = 'black'
    GREY = 'grey'
    YELLOW = 'yellow'
    BROWN = 'brown'
    DARKRED = 'darkred'
    TOMATO = 'tomato'
    MAGENTA = 'magenta'
    CRIMSON = 'crimson'
    SALMON = 'salmon'
    FIREBRICK = 'firebrick'
    NAVY = 'navy'
    ROYALBLUE = 'royalblue'
    TURQUOISE = 'turquoise'
    CORAL = 'coral'
    SEA_GREEN = 'seagreen'
    FOREST_GREEN = 'forestgreen'
    OLIVE = 'olive'
    DARK_GREEN = 'darkgreen'
    DARK_ORANGE = 'darkorange'
    VIOLET = 'violet'
    SLATE_GREY = 'slategrey'
    SLATE_BLUE = 'slateblue'
    DARK_GREY = 'darkgrey'
    KHAKI = 'khaki'
    TAN = 'tan'


@dataclass
class AnnotationMarkerPlotOptions:
    """Marker plot options.
    
    Attributes:
        opacity: Opacity of the time markers. Default is 0.8
        width: Width of the time markers. Default is 1.5
        shape: Shape of the time markers. Default is 'solid'
        color: Color of the time markers. Default is RED
        highlight: Whether to highlight the time markers. Default is True
    """
    opacity: float = 0.8
    width: float = 1.5
    shape: Literal['solid', 'dash', 'dot', 'longdash', 'dashdot'] = 'solid'
    color: TimeCourseColor = TimeCourseColor.RED
    highlight: bool = True

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'opacity': self.opacity,
            'width': self.width,
            'shape': self.shape,
            'color': self.color.value,
            'highlight': self.highlight
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color':
                setattr(self, key, TimeCourseColor(value))
            else:
                setattr(self, key, value)
    
@dataclass
class DistancePlotOptions:
    """Distance plot options.

    Attributes:
        color_min: Minimum value for color mapping. Default is None
        color_max: Maximum value for color mapping. Default is None
        color_range: Color range for color mapping. Default is None
        color_map: Color map for color mapping. Default is 'RdBu'
        precision: Precision of the color mapping. Default is 6
        slider_step_size: Stepsize of the sliders. Default is 1.0
        allowed_precision: Allowed precision of the sliders. Default is 6
        time_marker_on: Whether time marker is enabled. Default is True
        time_marker_color: Color of the time marker. Default is BLACK
        time_marker_width: Width of the time marker. Default is 1.0
        time_marker_opacity: Opacity of the time marker. Default is 0.8
    """
    color_min: Optional[float] = None
    color_max: Optional[float] = None
    color_range: Optional[Tuple[float, float]] = None
    color_map: ColorMaps = ColorMaps.RDBU
    precision: int = 6
    slider_step_size: float = 1.0
    allowed_precision: int = 6
    time_marker_on: bool = True
    time_marker_color: TimeCourseColor = TimeCourseColor.BLACK
    time_marker_width: float = 1.0
    time_marker_opacity: float = 0.8

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'color_map': self.color_map.value,
            'color_min': self.color_min,
            'color_max': self.color_max,
            'color_range': self.color_range,
            'precision': self.precision,
            'allowed_precision': self.allowed_precision,
            'slider_step_size': self.slider_step_size,
            'time_marker_on': self.time_marker_on,
            'time_marker_color': self.time_marker_color.value,
            'time_marker_width': self.time_marker_width,
            'time_marker_opacity': self.time_marker_opacity
        }
    
    def update_from_dict(self, data: Dict[str, any]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color_map':
                setattr(self, key, ColorMaps(value))
            elif key == 'time_marker_color':
                setattr(self, key, TimeCourseColor(value))
            else:
                setattr(self, key, value)

@dataclass
class FmriPlotOptions:
    """Plot options for fMRI data.
    
    Attributes:
        color_min: Minimum value for color mapping. Default is None
        color_max: Maximum value for color mapping. Default is None
        color_range: Color range for color mapping. Default is None
        colorbar_on: Whether colorbar is enabled. Default is True
        opacity: Opacity of the color mapping. Default is 1
        threshold_min: Minimum value for threshold mapping. Default is 0
        threshold_max: Maximum value for threshold mapping. Default is 0
        threshold_range: Threshold range for threshold mapping. Default is None
        tr_convert_on: Whether TR conversion is enabled. Default is False
        color_map: Color map for color mapping. Default is 'Viridis'
        reverse_colormap: Whether the colormap is reversed. Default is False
        hover_text_on: Whether hover text is enabled. Default is True
        precision: Precision of the color mapping. Default is 6
        play_movie_speed: Speed of the movie (in milliseconds). Default is 500
        slider_step_size: Stepsize of the sliders. Default is 100
        allowed_precision: Allowed precision of the sliders. Default is 6
        view_state: View state ('ortho' or 'montage') for NIFTI data. 
            Default is 'ortho'
        crosshair_on: Whether crosshair is enabled for NIFTI data. 
            Default is True
        direction_marker_on: Whether direction marker is enabled for NIFTI data. 
            Default is False
        freeze_view_on: Whether freeze view is enabled for GIFTI data. 
            Default is False
        fmri_timecourse_enabled: Whether fmri timecourse plottingis enabled. 
            Default is False
        fmri_timecourse_freeze: Whether fmri timecourse plot selections are frozen. 
            Default is False
    """
    # fmri plot options
    color_min: Optional[float] = None
    color_max: Optional[float] = None
    color_range: Optional[Tuple[float, float]] = None
    colorbar_on: bool = True
    opacity: float = 1
    threshold_min: float = 0
    threshold_max: float = 0
    threshold_range: Optional[Tuple[float, float]] = None
    tr_convert_on: bool = False
    color_map: ColorMaps = ColorMaps.VIRIDIS
    reverse_colormap: bool = False
    hover_text_on: bool = True
    precision: int = 6
    play_movie_speed: int = 500
    slider_step_size: int = 100
    allowed_precision: int = 6
    crosshair_on: bool = True
    direction_marker_on: bool = False
    freeze_view_on: bool = False
    fmri_timecourse_enabled: bool = False
    fmri_timecourse_freeze: bool = False

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'color_map': self.color_map.value,
            'reverse_colormap': self.reverse_colormap,
            'color_min': self.color_min,
            'color_max': self.color_max,
            'color_range': self.color_range,
            'colorbar_on': self.colorbar_on,
            'threshold_min': self.threshold_min,
            'threshold_max': self.threshold_max,
            'threshold_range': self.threshold_range,
            'tr_convert_on': self.tr_convert_on,
            'opacity': self.opacity,
            'hover_text_on': self.hover_text_on,
            'precision': self.precision,
            'play_movie_speed': self.play_movie_speed,
            'slider_step_size': self.slider_step_size,
            'allowed_precision': self.allowed_precision,
            'crosshair_on': self.crosshair_on,
            'direction_marker_on': self.direction_marker_on,
            'freeze_view_on': self.freeze_view_on,
            'fmri_timecourse_enabled': self.fmri_timecourse_enabled,
            'fmri_timecourse_freeze': self.fmri_timecourse_freeze
        }
    

    def update_from_dict(self, data: Dict[str, any]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color_map':
                setattr(self, key, ColorMaps(value))
            else:
                setattr(self, key, value)

@dataclass
class TimeCourseGlobalPlotOptions:
    """Global time course plot options.
    
    Attributes:
        global_min: Global minimum value for time course plot - 
            computed from all time courses. Default is None
        global_max: Global maximum value for time course plot - 
            computed from all time courses. Default is None
        default_global_min: Default global minimum value for time course plot. 
            Default is -1.0
        default_global_max: Default global maximum value for time course plot.
             Default is 1.0
        grid_on: Whether grid is enabled for time course plot. Default is True
        hover_text_on: Whether hover text is enabled for time course plot. 
            Default is True
        time_marker_on: Whether time marker is enabled for time course plot. 
            Default is True
        global_convolution: Whether global convolution is enabled for time course plot. 
            Default is True
        shift_unit: Constant shift unit applied to time course data on constant shift changes. 
            Default is 1.0. This value is updated when global min and max are updated.
        shift_update_ratio: Ratio of shift unit updates. 
            Default is 10.
        scale_unit: Scale unit applied to time course data on scale change. 
            Default is 0.1. This value is updated when global min and max are updated.
        scale_update_granularity: Granularity of scale unit updates. 
            Default is 10.
    """
    global_min: Optional[float] = None
    global_max: Optional[float] = None
    default_global_min: float = -1.0
    default_global_max: float = 1.0
    grid_on: bool = True
    global_convolution: bool = True
    hover_text_on: bool = True
    time_marker_on: bool = True
    shift_unit: float = 1.0
    shift_update_ratio: int = 10
    scale_unit: float = 0.1
    scale_update_granularity: int = 10

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'global_min': self.global_min,
            'global_max': self.global_max,
            'grid_on': self.grid_on,
            'hover_text_on': self.hover_text_on,
            'time_marker_on': self.time_marker_on,
            'global_convolution': self.global_convolution,
            'shift_unit': self.shift_unit,
            'shift_update_ratio': self.shift_update_ratio,
            'scale_unit': self.scale_unit,
            'scale_update_granularity': self.scale_update_granularity
        }
    
    def update_from_dict(self, data: Dict[str, any]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)

@dataclass
class TimeCoursePlotOptions:
    """Time course plot options.
    
    Attributes:
        label: Label of the time course. Default is None
        visibility: whether the time course is visible in the plot. Default is True.
        color: Color of the time course. Default is RED
        width: Width of the time course. Default is 2.0
        constant: History of constant shifts to the time course handled by SignalShifter.
        scale: History of scale changes to the time course handled by SignalScaler.
        preprocess_constant: History of constant shifts to the preprocessed time course 
            handled by SignalShifter.
        preprocess_scale: History of scale changes to the preprocessed time course 
            handled by SignalScaler.
        opacity: Opacity of the time course. Default is 1.0
        mode: Mode of the time course. Default is 'lines'
    """
    label: str = None
    visibility: bool = True
    color: TimeCourseColor = TimeCourseColor.RED
    width: float = 2.0
    constant: SignalShifter = field(default_factory=SignalShifter)
    scale: SignalScaler = field(default_factory=SignalScaler)
    preprocess_constant: SignalShifter = field(default_factory=SignalShifter)
    preprocess_scale: SignalScaler = field(default_factory=SignalScaler)
    opacity: float = 1.0
    mode: Literal['lines', 'markers', 'lines+markers'] = 'lines'

    @classmethod
    def with_color(cls, color: TimeCourseColor, **kwargs):
        """Create TimeCoursePlotOptions with a specific color."""
        return cls(color=color, **kwargs)

    @classmethod
    def with_next_color(cls, used_colors: set[TimeCourseColor], **kwargs):
        """Create TimeCoursePlotOptions with the next available color.
        
        Args:
            used_colors: Set of already used TimeCourseColor values
            **kwargs: Additional arguments to pass to constructor
            
        Returns:
            TimeCoursePlotOptions with first unused color from TimeCourseColor enum
        """
        available_colors = set(TimeCourseColor) - used_colors
        if not available_colors:
            # If all colors used, start over with first color
            next_color = list(TimeCourseColor)[0]
        else:
            next_color = list(available_colors)[0]
        return cls(color=next_color, **kwargs)
    
    def clear_preprocess_history(self) -> None:
        """Clear preprocess history."""
        self.preprocess_constant.clear_history()
        self.preprocess_scale.clear_history()

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'label': self.label,
            'visibility': self.visibility,
            'color': self.color.value,
            'width': self.width,
            'constant': self.constant.shift_history,
            'scale': self.scale.scale_history,
            'preprocess_constant': self.preprocess_constant.shift_history,
            'preprocess_scale': self.preprocess_scale.scale_history,
            'opacity': self.opacity,
            'mode': self.mode
        }

    def update_from_dict(self, data: Dict[str, any]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color':
                setattr(self, key, TimeCourseColor(value))
            # handle SignalScaler and SignalShifter
            elif key == 'constant':
                self.constant.set_history(value)
            elif key == 'scale':
                self.scale.set_history(value)
            elif key == 'preprocess_constant':
                self.preprocess_constant.set_history(value)
            elif key == 'preprocess_scale':
                self.preprocess_scale.set_history(value)
            else:
                setattr(self, key, value)

@dataclass
class TimeMarkerPlotOptions:
    """Time marker plot options."""
    opacity: float = 0.5
    width: float = 1.0
    shape: Literal['solid', 'dash', 'dot', 'longdash', 'dashdot'] = 'solid'
    color: TimeCourseColor = TimeCourseColor.GREY

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'opacity': self.opacity,
            'width': self.width,
            'shape': self.shape,
            'color': self.color.value
        }
    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color':
                setattr(self, key, TimeCourseColor(value))
            else:
                setattr(self, key, value)


@dataclass
class TaskDesignPlotOptions:
    """Task design plot options.
    
    Attributes:
        label: Label of the task design. Default is None
        convolution: Whether convolution of task design with hrf is enabled, 
            otherwise block structure is plotted. Default is hrf.
        scale: History of scale changes to the task design handled by SignalScaler.
        constant: History of constant shifts to the task design handled by SignalShifter.
        color: Color of the task design. Default is RED
        width: Width of the task design. Default is 2.0
        opacity: Opacity of the task design. Default is 1.0
        mode: Mode of the task design. Default is 'lines'
    """
    label: str = None
    convolution: Literal['hrf', 'block'] = 'hrf'
    scale: SignalScaler = field(default_factory=SignalScaler)
    constant: SignalShifter = field(default_factory=SignalShifter)
    color: TimeCourseColor = TimeCourseColor.RED
    width: float = 2.0
    opacity: float = 1.0
    mode: Literal['lines', 'markers', 'lines+markers'] = 'lines'

    @classmethod
    def with_color(cls, color: TimeCourseColor, **kwargs):
        """Create TaskDesignPlotOptions with a specific color."""
        return cls(color=color, **kwargs)

    @classmethod
    def with_next_color(cls, used_colors: set[TimeCourseColor], **kwargs):
        """Create TaskDesignPlotOptions with the next available color.
        
        Args:
            used_colors: Set of already used TimeCourseColor values
            **kwargs: Additional arguments to pass to constructor
            
        Returns:
            TimeCoursePlotOptions with first unused color from TimeCourseColor enum
        """
        available_colors = set(TimeCourseColor) - used_colors
        if not available_colors:
            # If all colors used, start over with first color
            next_color = list(TimeCourseColor)[0]
        else:
            next_color = list(available_colors)[0]
        return cls(color=next_color, **kwargs)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'label': self.label,
            'convolution': self.convolution,
            'scale': self.scale.scale_history,
            'constant': self.constant.shift_history,
            'color': self.color.value,
            'width': self.width,
            'opacity': self.opacity,
            'mode': self.mode
        }

    def update_from_dict(self, data: Dict[str, float]) -> None:
        """Update from dictionary."""
        for key, value in data.items():
            # handle enum values
            if key == 'color':
                setattr(self, key, TimeCourseColor(value))
            # handle SignalScaler and SignalShifter
            elif key == 'scale':
                self.scale.set_history(value)
            elif key == 'constant':
                self.constant.set_history(value)
            else:
                setattr(self, key, value)
