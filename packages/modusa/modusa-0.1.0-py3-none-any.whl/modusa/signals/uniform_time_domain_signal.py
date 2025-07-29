#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from typing import Self, Any
import numpy as np
import matplotlib.pyplot as plt


class UniformTimeDomainSignal(ModusaSignal):
	"""

	"""
	
	#--------Meta Information----------
	name = "Uniform Time Domain Signal"
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-02"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, y: np.ndarray, t: np.ndarray | None = None):
		if y.ndim != 1:
			raise excp.InputValueError(f"`y` must have 1 dimension not {y.ndim}.")
		if y.shape[0] < 1:
			raise excp.InputValueError(f"`y` must have atleast 1 element.")
		
		if t is None:
			t = np.arange(y.shape[0])
		else:
			if t.ndim != 1:
				raise excp.InputValueError(f"`t` must have 1 dimension not {t.ndim}.")
			if t.shape[0] != y.shape[0]:
				raise excp.InputValueError(f"`t` and `y` must have same shape.")
			
		super().__init__(data=y, data_idx=t) # Instantiating `ModusaSignal` class
		
		self._y_unit = ""
		self._t_unit = "index"
		
		self._title = "aa"
		self._y_label = ""
		self._t_label = "Time"
	
	def _with_data(self, new_data: np.ndarray, new_data_idx: np.ndarray) -> Self:
		"""Subclasses must override this to return a copy with new data."""
		Ts = new_data_idx[1] - new_data_idx[0]
		new_signal = self.__class__(y=new_data, Ts=self.Ts)
		new_signal.set_units(y_unit=self.y_unit, t_unit=self.t_unit)
		new_signal.set_plot_labels(title=self.title, y_label=self.y_label, t_label=self.t_label)
		
		return new_signal
	
	#----------------------
	# From methods
	#----------------------
	@classmethod
	@validate_args_type()
	def from_array(cls, y: np.ndarray, t: np.ndarray | None = None, t_unit: str | None = None) -> Self:
		
		signal: Self = cls(y=y, t=t)
		
		if t_unit is not None:
			signal.set_units(t_unit=t_unit)
		
		return signal
	
	@classmethod
	@validate_args_type()
	def from_array_with_Ts(cls, y: np.ndarray, Ts: float | None = None, t_unit: str | None = None) -> Self:
		
		t = np.arange(y.shape[0]) * Ts
		signal: Self = cls(y=y, t=t)
		
		if t_unit is not None:
			signal.set_units(t_unit=t_unit)
			
		return signal
	
	#----------------------
	# Setters
	#----------------------
	
	@validate_args_type()
	def set_units(
		self,
		y_unit: str | None = None,
		t_unit: str | None = None,
	) -> Self:
		if y_unit is not None:
			self._y_unit = y_unit
		if t_unit is not None:
			self._t_unit = t_unit
			
		return self
	
	@validate_args_type()
	def set_plot_labels(
		self,
		title: str | None = None,
		y_label: str | None = None,
		t_label: str | None = None
	) -> Self:
		""""""
		if title is not None:
			self._title = title
		if y_label is not None:
			self._y_label = y_label
		if t_label is not None:
			self._t_label = t_label
			
		return self
	
	
	
	#----------------------
	# Properties
	#----------------------
	
	@immutable_property("Create a new object instead.")
	def y(self) -> np.ndarray:
		return self.data
	
	@immutable_property("Create a new object instead.")
	def t(self) -> np.ndarray:
		return self.data_idx
	
	@immutable_property("Use `.set_t` instead.")
	def y_unit(self) -> str:
		return self._y_unit
	
	@immutable_property("Use `.set_t` instead.")
	def t_unit(self) -> str:
		return self._t_unit
	
	@immutable_property("Use `.labels` instead.")
	def title(self) -> str:
		return self._title
	
	@immutable_property("Use `.set_t` instead.")
	def y_label(self) -> str:
		return self._y_label
	
	@immutable_property("Use `.set_t` instead.")
	def t_label(self) -> str:
		return self._t_label
	
	@immutable_property("Use `.resample` instead.")
	def Ts(self) -> float:
		"""Sampling period of the signal."""
		return self.t[1] - self.t[0]
	
	@immutable_property("Use `.resample` instead.")
	def sr(self) -> float:
		"""
		Sampling rate of the signal.
		"""
		return 1.0 / self.Ts
	
	@immutable_property(error_msg="Use `.set_labels` instead.")
	def labels(self) -> tuple[str, str, str]:
		"""Labels in a format appropriate for the plots."""
		return (self.title, f"{self.y_label} ({self.y_unit})", f"{self.t_label} ({self.t_unit})")
	
	#----------------------
	# Plugins Access
	#----------------------
	@validate_args_type()
	def plot(
		self,
		scale_y: tuple[float, float] | None = None,
		scale_t: tuple[float, float] | None = None,
		ax: plt.Axes | None = None,
		color: str = "b",
		marker: str | None = None,
		linestyle: str | None = None,
		stem: bool | None = None,
		labels: tuple[str, str, str] | None = None,
		legend_loc: str | None = None,
		zoom: tuple[float, float] | None = None,
		highlight: list[tuple[float, float]] | None = None,
	) -> plt.Figure:
		"""
		Applies `modusa.plugins.PlotTimeDomainSignal` Plugin.
		"""
		
		from modusa.plugins import PlotTimeDomainSignalPlugin
		
		labels = labels or self.labels
		stem = stem or False
		
		fig: plt.Figure | None = PlotTimeDomainSignalPlugin().apply(
			signal=self,
			scale_y=scale_y,
			scale_t=scale_t,
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
	