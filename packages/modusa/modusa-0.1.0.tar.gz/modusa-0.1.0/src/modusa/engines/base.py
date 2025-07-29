#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Any

class ModusaEngine(ABC):
	"""
	Base class for all core logic components in the Modusa system.
	Every subclass must implement the `run` method.
	"""
	
	@abstractmethod
	def run(self, *args, **kwargs) -> Any:
		pass