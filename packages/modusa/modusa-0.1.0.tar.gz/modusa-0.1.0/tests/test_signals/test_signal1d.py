#!/usr/bin/env python3

from modusa import excp
from modusa.signals import Signal1D
import numpy as np

def assert_common_signal_properties(signal):
	assert signal.y.ndim == 1
	

def test_constructor_random_array():
	size = 9
	signal = Signal1D(y=np.random.random(size))
	
	assert signal.y.ndim == 1
	assert signal.y.shape == (size, )
	assert signal.x.ndim == 1
	assert signal.x.shape == (size, )
	assert signal.name == "1D Signal"
	assert signal.y_unit == ""
	assert signal.x_unit == "index"
	assert signal.title == signal.name
	assert signal.y_label == "y"
	assert signal.x_label == "x"

def test_constructor_array():
	signal = Signal1D(y=np.array([1, 2, 3]))
	
	assert signal.y.ndim == 1
	assert signal.y.shape == (3, )
	assert signal.x.ndim == 1
	assert signal.x.shape == (3, )
	assert signal.name == "1D Signal"
	assert signal.y_unit == ""
	assert signal.x_unit == "index"
	assert signal.title == signal.name
	assert signal.y_label == "y"
	assert signal.x_label == "x"

def test_constructor_empty_array():
	signal = Signal1D(y=np.array([]))
	
	assert signal.y.ndim == 1
	assert signal.y.shape == (0, )
	assert signal.x.ndim == 1
	assert signal.x.shape == (0, )
	assert signal.name == "1D Signal"
	assert signal.y_unit == ""
	assert signal.x_unit == "index"
	assert signal.title == signal.name
	assert signal.y_label == "y"
	assert signal.x_label == "x"