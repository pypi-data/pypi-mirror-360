#!/usr/bin/env python3

from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from abc import ABC, abstractmethod
from typing import Self
import numpy as np
import matplotlib.pyplot as plt

class ModusaSignal(ABC):
	"""
	Base class prototype for any signal.
	
	Note
	----
	- Serves as the foundation for all signal types in the Modusa framework
	- Intended to be subclassed
	- Subclass shoud implement a **read-only** `data` property (e.g., amplitude or spectral data) and a `plot()` method to visualize the signal

	Warning
	-------
	- You cannot create a subclass without `data` and `plot()` implemented. It will throw an error on instantiating the subclass.
	
	Example
	-------
	.. code-block:: python
			
		from modusa.signals import ModusaSignal
		from modusa.decorators import validate_args_type

		class MySignal(ModusaSignal):
			
			@validate_args_type()
			def __init__(self, y: nd.ndarray):
				super().__init__() # Very important for proper initialisation
				self._y = y
	
			@property
			def data(self):
				return self._y
			
			@validate_args_type()
			def plot(self):
				# Your plotting logic here
				pass
	"""
	
	#--------Meta Information----------
	name = "Modusa Signal"
	description = "Base class for any signal types in the Modusa framework."
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-06-23"
	#----------------------------------
	
	@validate_args_type()
	def __init__(self, data: np.ndarray, data_idx: np.ndarray):
		self._data = data
		self._data_idx = data_idx
		self._plugin_chain = []
		
	#----------------------------
	# Setters
	#----------------------------
	@validate_args_type()
	def set_name(self, name: str) -> Self:
		self.name = name
		
		return name
	
	
	#----------------------------
	# Properties
	#----------------------------
	
	@property
	def data(self) -> np.ndarray:
		"""
		The core signal data as a NumPy array.
		
		Note
		----
		- Different signals might need to have different variable names to store data, e.g. y(t) -> y, M(x, y) -> M, x(t) -> x
		- This `data` property must return the correct data for any given subclass (y for y(t), M for M(x, y)), see the example.
		- Must return `np.ndarray`
		"""
		return self._data
	
	@immutable_property("Create a new object instead.")
	def data_idx(self) -> np.ndarray:
		"""
		The coordinate values associated with each element of the signal `data`.
	
		Note
		----
		- This is often a 1D array of the same length as the first axis of `data`.
		- For time-domain signals, this typically represents timestamps.
		- For spectrograms or other 2D signals, you may use a dict mapping axes to coordinate arrays.
		- This property is read-only; to modify it, create a new signal object.
		
		Returns
		-------
		np.ndarray
			An array of coordinates or indices corresponding to the signal data.
		"""
		return self._data_idx
	
	@immutable_property("Read-only property.")
	def shape(self) -> tuple[int]:
		"""Shape of the signal."""
		return self.data.shape
	
	
	@immutable_property("plugin_chain is read-only. It is automatically updated.")
	def plugin_chain(self) -> list[str]:
		"""
		List of plugin names applied to the signal.
		
		Note
		----
		- Reflects the signal’s processing history
		- Ordered by application sequence
		- Managed automatically (read-only)
		- Use `info` for a formatted summary
		"""
		return self._plugin_chain.copy()
	
	@immutable_property("Mutation not allowed, generated automatically.")
	def info(self) -> None:
		"""
		Prints a quick summary of the signal.
		
		Note
		----
		- Output is printed to the console.
		- Returns nothing.

		"""
		
		print("\n".join([
			f"{self.__class__.__name__}(",
			f"  Signal Name: '{self.name}',",
			f"  Inheritance: {' → '.join(cls.__name__ for cls in self.__class__.mro()[:-1])}",
			f"  Plugin Chain: {' → '.join(self._plugin_chain) or '(none)'}",
			f")"
		]))
		
	#-------------------------------
	# Basic functionalities
	#-------------------------------
		
	@abstractmethod
	def plot(self) -> plt.Figure:
		"""
		Plot a visual representation of the signal.
		
		Note
		----
		- For any signal, one must implement `plot` method with useful features to make users happy
		- Try to return `matplotlib.figure.Figure` for customization/saving but other plotting libraries are also welcome
		"""
		pass
	
	@abstractmethod
	def _with_data(self, new_data: np.ndarray, new_data_idx: np.ndarray) -> Self:
		"""Subclasses must override this to return a copy with new data."""
		pass
		
	
	def trim(self, start: float | None = None, stop: float | None = None):
		"""
		Returns a new signal trimmed between two data_idx values.
	
		Parameters
		----------
		start : float or None
			The starting data_idx value (inclusive). If None, starts from the beginning.
		stop : float or None
			The stopping data_idx value (exclusive). If None, goes till the end.
	
		Returns
		-------
		ModusaSignal
			A new signal with trimmed data and data_idx.
		"""
		# Define bounds
		start_v = -np.inf if start is None else start
		stop_v = np.inf if stop is None else stop
	
		# Build a mask over data_idx values
		mask = (self.data_idx >= start_v) & (self.data_idx < stop_v)
		idx = np.where(mask)[0]
	
		return self._with_data(new_data=self.data[idx], new_data_idx=self.data_idx[idx])
	
	#----------------------------
	# Dunder method
	#----------------------------
	
	
	#----------------------------
	# Slicing
	#----------------------------
	
	def __getitem__(self, key):
		if isinstance(key, (int, slice)):
			# Normal Python-style slicing by index
			sliced_data = self.data[key]
			sliced_idx = self.data_idx[key]
			return self._with_data(new_data=sliced_data, new_data_idx=sliced_idx)
		
		else:
			raise TypeError(f"Indexing with type {type(key)} is not supported. Use int or slice.")
			
	

	def __str__(self):
		cls = self.__class__.__name__
		data = self.data
		
		arr_str = np.array2string(
			data,
			separator=", ",
			threshold=50,       # limit number of elements shown
			edgeitems=3,          # show first/last 3 rows and columns
			max_line_width=120,   # avoid wrapping
			formatter={'float_kind': lambda x: f"{x:.4g}"}
		)
		
		return f"{cls}({arr_str}, shape={data.shape})"
	
	def __repr__(self):
		cls = self.__class__.__name__
		data = self.data
		
		arr_str = np.array2string(
			data,
			separator=", ",
			threshold=50,       # limit number of elements shown
			edgeitems=3,          # show first/last 3 rows and columns
			max_line_width=120,   # avoid wrapping
			formatter={'float_kind': lambda x: f"{x:.4g}"}
		)
		
		return f"{cls}({arr_str}, shape={data.shape})"
	
	
	#----------------------------
	# Math ops
	#----------------------------
	
	def __array__(self, dtype=None):
		return self.data if dtype is None else self.data.astype(dtype)
	
	def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
		if method != '__call__':
			return NotImplemented
		
		# Replace ModusaSignal instances with their data
		new_inputs = [i.data if isinstance(i, ModusaSignal) else i for i in inputs]
		
		try:
			result = ufunc(*new_inputs, **kwargs)
		except Exception as e:
			raise TypeError(f"Ufunc {ufunc.__name__} failed: {e}")
			
		return self._with_data(result)
	
	def _apply_op(self, other, op, label):
		if isinstance(other, ModusaSignal):
			other = other.data  # extract data
			
		try:
			result = op(self.data, other)
		except Exception as e:
			raise TypeError(f"Operation {label} failed: {e}")
			
		return self._with_data(result)
	
	def __add__(self, other): return self._apply_op(other, np.add, "+")
	def __sub__(self, other): return self._apply_op(other, np.subtract, "-")
	def __mul__(self, other): return self._apply_op(other, np.multiply, "*")
	def __truediv__(self, other): return self._apply_op(other, np.divide, "/")
	def __pow__(self, other): return self._apply_op(other, np.power, "**")
		
	def __radd__(self, other): return self.__add__(other)
	def __rsub__(self, other): return self._apply_op(other, lambda a, b: b - a, "r-")
	def __rmul__(self, other): return self.__mul__(other)
	def __rtruediv__(self, other): return self._apply_op(other, lambda a, b: b / a, "r/")
	def __rpow__(self, other): return self._apply_op(other, lambda a, b: b ** a, "r**")
		
	def __neg__(self): return self._with_data(-self.data)
	def __abs__(self): return self._with_data(np.abs(self.data))
		