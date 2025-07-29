#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from typing import Self, Any
import numpy as np
import matplotlib.pyplot as plt

class Signal2D(ModusaSignal):
	"""

	"""
	
	#--------Meta Information----------
	name = "2D Signal"
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-02"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, M: np.ndarray, r: np.ndarray | None = None, c: np.ndarray | None = None):
		
		if M.ndim != 2:
			raise excp.InputValueError(f"`M` must have 2 dimensions not {M.ndim}.")
		
		if r is None:
			r = np.arange(M.shape[0])
		else:
			if r.ndim != 1:
				raise excp.InputValueError(f"`r` must have 1 dimension not {r.ndim}.")
			if r.shape != M.shape[0]:
				raise excp.InputValueError(f"`r` must have shape compatible with `M`.")
		
		if c is None:
			c = np.arange(M.shape[0])
		else:
			if c.ndim != 1:
				raise excp.InputValueError(f"`c` must have 1 dimension not {c.ndim}.")
			if c.shape != M.shape[1]:
				raise excp.InputValueError(f"`c` must have shape compatible with `M`.")
		
		super().__init__(data=M, data_idx={0: r, 1: c})# Instantiating `ModusaSignal` class
		
		self._M_unit = ""
		self._r_unit = "index"
		self._c_unit = "index"
		
		self._title = self.__class__.name
		self._M_label = "Matrix"
		self._r_label = "Row"
		self._c_label = "Column"
	
	def _with_data(self, new_data: np.ndarray, new_data_idx: dict) -> Self:
		"""Subclasses must override this to return a copy with new data."""
		new_signal = self.__class__(M=new_data, r=new_data_idx[0], c=new_data_idx[1])
		new_signal.set_units(M_unit=self.M_unit, y_unit=self.y_unit, x_unit=self.x_unit)
		new_signal.set_plot_labels(title=self.title, M_label=self.M_label, y_label=self.y_label, x_label=self.x_label)
		
		return new_signal
	
	#----------------------
	# From methods
	#----------------------
	@classmethod
	@validate_args_type()
	def from_array(cls, M: np.ndarray, r: np.ndarray | None = None, c: np.ndarray | None = None) -> Self:
		
		signal: Self = cls(M=M, r=r, c=c)
		
		return signal
	
	@classmethod
	@validate_args_type()
	def from_list(cls, M: list, r: list | None = None, c: list | None = None) -> Self:
		
		M = np.array(M)
		if r is not None:
			r = np.array(r)
		if c is not None:
			c = np.array(c)
			
		signal: Self = cls(M=M, r=r, c=c)
		
		return signal
	
	#----------------------
	# Setters
	#----------------------
	
	@validate_args_type()
	def set_plot_labels(
		self,
		title: str | None = None,
		M_label: str | None = None,
		r_label: str | None = None,
		c_label: str | None = None
	) -> Self:
		
		if title is not None:
			self._title = title
		if M_label is not None:
			self._M_label = M_label
		if r_label is not None:
			self._r_label = r_label
		if c_label is not None:
			self._c_label = c_label
			
		return self
	
	@validate_args_type()
	def set_units(
		self,
		M_unit: str | None = None,
		r_unit: str | None = None,
		c_unit: str | None = None
	) -> Self:
			
		if M_unit is not None:
			self._M_unit = M_unit
		if r_unit is not None:
			self._r_unit = r_unit
		if c_unit is not None:
			self._c_unit = c_unit
			
		return self
	
	
	
	#----------------------
	# Properties
	#----------------------
	
	@immutable_property("Create a new object instead.")
	def M(self) -> np.ndarray:
		return self.data
	
	@immutable_property("Create a new object instead.")
	def r(self) -> np.ndarray:
		return self.data_idx[0]
	
	@immutable_property("Create a new object instead.")
	def c(self) -> np.ndarray:
		return self.data_idx[1]
	
	@immutable_property("Use `.set_units` instead.")
	def M_unit(self) -> str:
		return self._M_unit
	
	@immutable_property("Use `.set_units` instead.")
	def r_unit(self) -> str:
		return self._r_unit
	
	
	@immutable_property("Use `.set_units` instead.")
	def c_unit(self) -> str:
		return self._c_unit
	
	@immutable_property("Use `.set_labels` instead.")
	def title(self) -> str:
		return self._title
	
	
	@immutable_property("Use `.set_labels` instead.")
	def M_label(self) -> str:
		return self._M_label
	
	
	@immutable_property("Use `.set_labels` instead.")
	def r_label(self) -> str:
		return self._r_label
	
	
	@immutable_property("Use `.set_labels` instead.")
	def c_label(self) -> str:
		return self._c_label
	
	
	@property
	def labels(self) -> tuple[str, str, str, str]:
		"""Labels in a format appropriate for the plots."""
		return (self.title, f"{self.M_label} ({self.M_unit})", f"{self.r_label} ({self.r_unit})", f"{self.c_label} ({self.c_unit})")
	
	#----------------------
	# Plugins Access
	#----------------------
	def plot(
		self,
		log_compression_factor: int | None = None,
		ax: plt.Axes | None = None,
		labels: tuple[str, str, str, str] | None = None,
		zoom: tuple[float, float, float, float] | None = None,
		highlight: list[tuple[float, float, float, float]] | None = None,
		cmap: str = "gray_r",
		origin: str = "upper",
		show_colorbar: bool = False,
		cax: plt.Axes | None = None,
		show_grid: bool = False,
		tick_mode: str = "center", # or "edge"
		value_range: tuple[float, float] | None = None
	) -> plt.Figure:
		"""
		Applies `modusa.plugins.Plot2DPlugin`.
		"""
		from modusa.plugins import Plot2DMatrixPlugin
		
		fig = Plot2DMatrixPlugin().apply(
			signal=self,
			ax=ax,
			labels=labels or self.labels,
			zoom=zoom,
			highlight=highlight,
			log_compression_factor=log_compression_factor,
			cmap=cmap,
			origin=origin,
			show_colorbar=show_colorbar,
			cax=cax,
			show_grid=show_grid,
			tick_mode=tick_mode,
			value_range=value_range
		)
		return fig
	