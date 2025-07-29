#!/usr/bin/env python3


#----------------------------------------
# Base class errors
#----------------------------------------
class MusaBaseError(Exception):
	"""
	Ultimate base class for any kind of custom errors.
	"""
	pass

class TypeError(MusaBaseError):
	pass
	
class InputError(MusaBaseError):
	"""
	Any Input type error.
	"""

class InputTypeError(MusaBaseError):
	"""
	Any Input type error.
	"""

class InputValueError(MusaBaseError):
	"""
	Any Input type error.
	"""
	
class ImmutableAttributeError(MusaBaseError):
	"""Raised when attempting to modify an immutable attribute."""
	pass
	
class FileNotFoundError(MusaBaseError):
	"""Raised when file does not exist."""
	pass
	
	
class PluginInputError(MusaBaseError):
	pass

class PluginOutputError(MusaBaseError):
	pass
	
class AttributeNotFoundError(MusaBaseError):
	pass
	
class ParsingError(MusaBaseError):
	"""
	Base class for any parsing related issues
	"""
	pass

class ValidationError(MusaBaseError):
	"""
	Base class for all input validation error
	"""
	pass

class GenerationError(MusaBaseError):
	"""
	Error when generation fails
	"""
	pass

class FileLoadingError(MusaBaseError):
	"""
	Error loading a file
	"""
	pass