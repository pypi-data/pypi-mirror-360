#!/usr/bin/env python3

from modusa import excp
from modusa.decorators import validate_args_type, immutable_property
from modusa.signals import ModusaSignal
from abc import ABC, abstractmethod
from typing import Any

class ModusaGenerator(ABC):
	"""
	Base class for any generator.
	
	Generates instance of different `ModusaSignal` subclass.
	"""
	
	#--------Meta Information----------
	name = ""
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-04"
	#----------------------------------
	
	def __init__(self, signal_cls: Any):
		
		if not issubclass(signal_cls, ModusaSignal):
			raise excp.InputValueError(f"`signal_cls` must be a subclass of ModusaSignal, got {signal_cls.__name__}")
		if signal_cls not in self.allowed_output_signal_types:
			raise excp.InputValueError(f"`signal_cls` must be a one of the allowed types {self.allowed_output_signal_types}, got {signal_cls.__name__}") 

		self._signal_cls = signal_cls
	
	@immutable_property("Mutation not allowed.")
	def signal_cls(self) -> Any:
		return self._signal_cls
	
	@property
	@abstractmethod
	def allowed_output_signal_types(self) -> tuple[type, ...]:
		return