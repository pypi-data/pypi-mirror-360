#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import immutable_property, validate_args_type
from modusa.signals.base import ModusaSignal
from typing import Self, Any
import numpy as np

class {class_name}(ModusaSignal):
	"""

	"""
	
	#--------Meta Information----------
	name = ""
	description = ""
	author_name = "{author_name}"
	author_email = "{author_email}"
	created_at = "{date_created}"
	#----------------------------------
	
	def __init__(self):
		super().__init__() # Instantiating `ModusaSignal` class
	
	
	def _with_data(self, new_data: np.ndarray) -> Self:
		"""Subclasses must override this to return a copy with new data."""
		raise NotImplementedError("Subclasses must implement _with_data")
		
	
	#----------------------
	# From methods
	#----------------------
	@classmethod
	def from_array(cls) -> Self:
		pass
		
	
	#----------------------
	# Setters
	#----------------------
	
	
	
	
	#----------------------
	# Properties
	#----------------------
	@immutable_property("Create a new object instead.")
	def data(self) -> np.ndarray:
		""""""
		pass
	
	#----------------------
	# Plugins Access
	#----------------------
	def plot(self) -> Any:
		"""
		
		"""
		pass
	