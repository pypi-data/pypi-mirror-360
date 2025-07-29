#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from typing import Self, Any
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class AudioSignal(ModusaSignal):
	"""

	"""

	#--------Meta Information----------
	name = "Audio Signal"
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-04"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, y: np.ndarray, t: np.ndarray | None = None):
		
		if y.ndim != 1: # Mono
			raise excp.InputValueError(f"`y` must have 1 dimension not {y.ndim}.")
		if t.ndim != 1:
			raise excp.InputValueError(f"`t` must have 1 dimension not {t.ndim}.")
		
		if t is None:
			t = np.arange(y.shape[0])
		else:
			if t.shape[0] != y.shape[0]:
				raise excp.InputValueError(f"`y` and `t` must have same shape.")
			dts = np.diff(t)
			if not np.allclose(dts, dts[0]):
				raise excp.InputValueError("`t` must be equally spaced")
		
		super().__init__(data=y, data_idx=t) # Instantiating `ModusaSignal` class
		
		self._y_unit = ""
		self._t_unit = "sec"
		
		self._title = "Audio Signal"
		self._y_label = "Amplitude"
		self._t_label = "Time"
	
	def _with_data(self, new_data: np.ndarray, new_data_idx: np.ndarray) -> Self:
		"""Subclasses must override this to return a copy with new data."""
		new_signal = self.__class__(y=new_data, t=new_data_idx)
		new_signal.set_units(y_unit=self.y_unit, t_unit=self.t_unit)
		new_signal.set_plot_labels(title=self.title, y_label=self.y_label, t_label=self.t_label)
		
		return new_signal
	
	#----------------------
	# From methods
	#----------------------
	@classmethod
	def from_array(cls, y: np.ndarray, t: np.ndarray | None = None) -> Self:
		
		signal = cls(y=y, t=t)
		
		return signal
	
	@classmethod
	def from_array_with_sr(cls, y: np.ndarray, sr: int) -> Self:
		t = np.arange(y.shape[0]) * (1.0 / sr)
		
		signal = cls(y=y, t=t)
		
		return signal
	
	@classmethod
	def from_list(cls, y: list, t: list) -> Self:
		
		y = np.array(y)
		t = np.array(t)
		signal = cls(y=y, t=t)
		
		return signal
	
	@classmethod
	def from_file(cls, fp: str | Path, sr: int | None = None) -> Self:
		
		import librosa
		
		fp = Path(fp)
		y, sr = librosa.load(fp, sr=sr)
		t = np.arange(y.shape[0]) * (1.0 / sr)
		
		signal = cls(y=y, t=t)
		signal.set_plot_labels(title=fp.stem)
		
		return signal
		
	#----------------------
	# Setters
	#----------------------
	
	@validate_args_type()
	def set_units(self, y_unit: str | None = None, t_unit: str | None = None) -> Self:
		
		if y_unit is not None:
			self._y_unit = y_unit
		if t_unit is not None:
			self._t_unit = t_unit
		
		return self
	
	@validate_args_type()
	def set_plot_labels(self, title: str | None = None, y_label: str | None = None, t_label: str | None = None) -> Self:
		
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
		""""""
		return self.data
	
	@immutable_property("Create a new object instead.")
	def t(self) -> np.ndarray:
		""""""
		return self.data_idx
	
	@immutable_property("Create a new object instead.")
	def sr(self) -> np.ndarray:
		""""""
		return 1.0 / self.t[1] - self.t[0]
	
	@immutable_property("Use `.set_units` instead.")
	def y_unit(self) -> str:
		""""""
		return self._y_unit
	
	@immutable_property("Use `set_units` instead.")
	def t_unit(self) -> str:
		""""""
		return self._t_unit
	
	@immutable_property("Use `.set_plot_labels` instead.")
	def title(self) -> str:
		""""""
		return self._title
	
	@immutable_property("Use `.set_plot_labels` instead.")
	def y_label(self) -> str:
		""""""
		return self._y_label
	
	@immutable_property("Use `.set_plot_labels` instead.")
	def t_label(self) -> str:
		""""""
		return self._t_label
	
	@immutable_property("Mutation not allowed.")
	def Ts(self) -> int:
		""""""
		return self.t[1] - self.t[0]
	
	@immutable_property("Mutation not allowed.")
	def duration(self) -> int:
		""""""
		return self.t[-1]
	
	@immutable_property("Use `.set_labels` instead.")
	def labels(self) -> tuple[str, str, str]:
		"""Labels in a tuple format appropriate for the plots."""
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
	