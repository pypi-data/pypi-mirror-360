#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from typing import Self, Any
import numpy as np
import matplotlib.pyplot as plt


class Signal1D(ModusaSignal):
	"""

	"""
	
	#--------Meta Information----------
	name = "1D Signal"
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-02"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, y: np.ndarray, x: np.ndarray | None = None):
		
		if y.ndim != 1:
			raise excp.InputValueError(f"`data` must have 1 dimension not {data.ndim}.")
			
		if x is None:
			x = np.arange(y.shape[0])
		else:
			if x.ndim != 1:
				raise excp.InputValueError(f"`x` must have 1 dimension not {x.ndim}.")
			if x.shape[0] != y.shape[0]:
				raise excp.InputValueError(f"`x` and `y` must have same shape.")
		
		super().__init__(data=y, data_idx=x)# Instantiating `ModusaSignal` class

		self._x_unit = "index"
		self._y_unit = ""
		self._title = self.name
		self._y_label = "y"
		self._x_label = "x"
		
	def _with_data(self, new_data: np.ndarray, new_data_idx: np.ndarray) -> Self:
		"""Subclasses must override this to return a copy with new data."""
		new_signal = self.__class__(y=new_data, x=new_data_idx)
		new_signal.set_units(y_unit=self.y_unit, x_unit=self.x_unit)
		new_signal.set_plot_labels(title=self.title, y_label=self.y_label, x_label=self.x_label)
		
		return new_signal
	
	#----------------------
	# From methods
	#----------------------
	@classmethod
	@validate_args_type()
	def from_array(cls, y: np.ndarray, x: np.ndarray | None = None) -> Self:
		"""
		Loads `Signal1D` instance from numpy array or a python list.
		
		Note
		----
		- If you have python `list`, use `.from_list` instead
		"""
		
		signal: Self = cls(y=y, x=x)
			
		return signal
	
	@classmethod
	@validate_args_type()
	def from_list(cls, y: list, x: list | None = None) -> Self:
		"""
		Loads `Signal1D` instance from a python list.
		"""
		y = np.array(y)
		
		if x is not None:
			x = np.array(x)
		
		signal: Self = cls(y=y, x=x)
			
		return signal
	
	
	#----------------------
	# Setters
	#----------------------

	@validate_args_type()
	def set_units(self, y_unit: str | None = None, x_unit: str | None = None) -> Self:
		"""
		Set the physical units for the y-axis and x-axis of the signal.
		
		This method attaches metadata describing the physical units of the signal.
		These units are used for display and labeling purposes (e.g., in plots),
		but do not affect the underlying signal data.
	
		Parameters
		----------
		y_unit : str or None
			Unit of the y-axis (e.g., "V", "Amplitude"). If None, the unit is left unchanged.
		x_unit : str or None
			Unit of the x-axis (e.g., "s", "Hz"). If None, the unit is left unchanged.
	
		Returns
		-------
		Self
			The signal instance with updated unit metadata. Supports method chaining.
	
		Raises
		------
		InputTypeError
			If `y_unit` or `x_unit` is not a string or None.

		Example
		-------
		.. code-block:: python
			
			# Set y-axis to volts and x-axis to seconds
			signal.set_units("V", "s")
		"""
		
		if y_unit is not None:
			self._y_unit = y_unit
		if x_unit is not None:
			self._x_unit = x_unit
			
		return self
	
	@validate_args_type()
	def set_plot_labels(
		self,
		title: str | None = None,
		y_label: str | None = None,
		x_label: str | None = None
	) -> Self:
		"""
		Set plot-related labels: title, y-axis label, and x-axis label.
	
		This method is useful for customizing plots generated from the signal,
		especially when exporting figures or displaying meaningful metadata.
	
		Parameters
		----------
		title : str or None, optional
			The title of the plot (e.g., "Waveform" or "FFT Magnitude").
		y_label : str or None, optional
			Label for the y-axis (e.g., "Amplitude" or "Power (dB)").
		x_label : str or None, optional
			Label for the x-axis (e.g., "Time (s)" or "Frequency (Hz)").

		Returns
		-------
		Self
			A modified instance of the signal class.
	
		Raises
		------
		InputTypeError
			If any provided argument is not a string or None.
	
		Examples
		--------
		.. code-block:: python

			# Set plot title and axis labels for a time-domain signal
			signal.set_plot_labels(
				title="Time-Domain Signal",
				y_label="Amplitude",
				x_label="Time (s)"
				)
			"""
		
		if title is not None:
			self._title = title
		if y_label is not None:
			self._y_label = y_label
		if x_label is not None:
			self._x_label = x_label
			
		return self
	
	
	
	#----------------------
	# Properties
	#----------------------
	@immutable_property("Create a new object instead.")
	def y(self) -> np.ndarray:
		return self.data
	
	@immutable_property("Create a new object instead.")
	def x(self) -> np.ndarray:
		return self._data_idx

	@immutable_property("Use `.set_units` instead.")
	def y_unit(self) -> str:
		return self._y_unit
	
	@immutable_property("Use `.set_units` instead.")
	def x_unit(self) -> str:
		return self._x_unit
	
	@immutable_property("Use `.set_labels` instead.")
	def title(self) -> str:
		return self._title
	
	@immutable_property("Use `.set_labels` instead.")
	def y_label(self) -> str:
		return self._y_label
	
	@immutable_property("Use `.set_labels` instead.")
	def x_label(self) -> str:
		return self._x_label
	
	#----------------------
	# Additional Properties
	#----------------------
	
	@immutable_property(error_msg="Use `.set_labels` instead.")
	def labels(self) -> tuple[str, str, str]:
		"""Labels in a tuple format appropriate for the plots."""
		return (self.title, f"{self.y_label} ({self.y_unit})", f"{self.x_label} ({self.x_unit})")
	
	#----------------------
	# Plugins Access
	#----------------------
	
	def trim(self, region: tuple[float, float]) -> Self:
		"""
		Return a new signal instance trimmed to a specific region of the x-axis.
		
		This method creates a new signal containing only the portion of the data
		where `x` lies within the specified range. It is useful for zooming in on
		a region of interest in time, frequency, or any other x-axis domain.
	
		Parameters
		----------
		region : tuple[float, float]
			The (start, end) range of the x-axis to retain. Must be in the same
			units as the x-axis (e.g., seconds, Hz, samples).
	
		Returns
		-------
		Self
			A new instance of the signal class, trimmed to the specified region.
	
		Raises
		------
		InputTypeError
			If `region` is not a tuple of two floats.
	
		Examples
		--------
		.. code-block:: python

			# Trim the signal to the region between x = 0.2 and x = 0.6
			trimmed = signal.trim((0.2, 0.6))
		"""
		
		from modusa.plugins.trim import Trim1DPlugin
		trimmed_signal: Self = Trim1DPlugin(region=region).apply(self)
		
		return trimmed_signal
	
	
	@validate_args_type()
	def plot(
		self,
		scale_y: tuple[float, float] | None = None,
		scale_x: tuple[float, float] | None = None,
		ax: plt.Axes | None = None,
		color: str = "k",
		marker: str | None = None,
		linestyle: str | None = None,
		stem: bool | None = None,
		labels: tuple[str, str, str] | None = None,
		legend_loc: str | None = None,
		zoom: tuple[float, float] | None = None,
		highlight: list[tuple[float, float]] | None = None,
	) -> plt.Figure:
		"""
		Applies `modusa.plugins.Plot1DPlugin` Plugin.
		"""
		
		from modusa.plugins import Plot1DSignalPlugin
		
		labels = labels or self.labels
		stem = stem or False
		
		fig: plt.Figure = Plot1DSignalPlugin().apply(
			signal=self,
			scale_y=scale_y,
			scale_x=scale_x,
			ax=ax,
			color=color,
			marker=marker,
			linestyle=linestyle,
			stem=stem,
			labels=labels,
			legend_loc=legend_loc,
			zoom=zoom,
			highlight=highlight
		)
		
		return fig
	