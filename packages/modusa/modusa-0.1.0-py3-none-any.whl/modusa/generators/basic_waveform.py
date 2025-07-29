#!/usr/bin/env python3


from modusa.decorators import validate_args_type
from modusa.generators.base import ModusaGenerator
from modusa.signals import UniformTimeDomainSignal, AudioSignal
from typing import Any
import numpy as np

class BasicWaveformGenerator(ModusaGenerator):
	"""

	"""
	
	#--------Meta Information----------
	name = ""
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-04"
	#----------------------------------
	
	def __init__(self, signal_cls: Any | None = None):
		if signal_cls is None:
			signal_cls = self.allowed_output_signal_types[0] # Automatically select the first signal
		super().__init__(signal_cls)
	
	
	@property
	def allowed_output_signal_types(self) -> tuple[type, ...]:
		return (UniformTimeDomainSignal, AudioSignal)
	
	#----------------------------
	# Generate functions
	#----------------------------
	
	def generate_example(self):
		"""
		Generates an instance of `TimeDomainSignal` to test out the features quicky.
		"""
		
		T = 0.01 # Time period
		
		t = np.arange(0, 10, T)
		y = np.sin(2 * np.pi * 10 * t)
		signal: UniformTimeDomainSignal | AudioSignal = self.signal_cls(y=y, t=t)
		signal.set_units(t_unit="sec")
		signal.set_name("Random")
		signal.set_plot_labels(title=signal.name, y_label="Amplitude", t_label="Time")
		
		return signal
	
	def generate_random(self):
		"""
		Generates an instance of `TimeDomainSignal` with random initialisation.
		Good for testing purposes.
		"""
		
		T = np.random.random()
		
		t = np.arange(0, np.random.randint(10, 40), T)
		y = np.random.random(size=t.shape[0])
		signal: UniformTimeDomainSignal | AudioSignal = self.signal_cls(y=y, t=t)
		signal.set_units(t_unit="sec")
		signal.set_name("Random")
		signal.set_plot_labels(title=signal.name, y_label="Amplitude", t_label="Time")
		
		return signal

	@validate_args_type()
	def generate_sinusoid(
		self,
		A: float | int = 1.0,
		f: float | int = 10.0,
		phi: float | int = 0.0,
		duration: float | int = 1.0,
		Ts: float | int = 0.01,
	):
		"""
		Generates a sinusoidal `TimeDomainSignal` with specified frequency, duration, sampling period, and phase.
		"""
		
		A, f, phi, duration, Ts = float(A), float(f), float(phi), float(duration), float(Ts)
		
		
		t = np.arange(0, duration, Ts)
		y = A * np.sin(2 * np.pi * f * t + phi)
		
		signal = self.signal_cls(y=y, t=t)
		signal.set_name(name=f"Sinusoid: {f}Hz")
		signal.set_plot_labels(
			title=signal.name,
			y_label="Amplitude",
			t_label="Time"
		)
		
		return signal


	@validate_args_type()
	def generate_square(
		self,
		A: float | int = 1.0,
		f: float | int = 10.0,
		phi: float | int = 0.0,
		duration: float | int = 1.0,
		Ts: float | int = 0.01,
	):
		"""
		Generates a square wave
		"""
		
		A, f, phi, duration, Ts = float(A), float(f), float(phi), float(duration), float(Ts)
		
		t = np.arange(0, duration, Ts)
		y = A * np.sign(np.sin(2 * np.pi * f * t + phi))
		
		signal: UniformTimeDomainSignal | AudioSignal = self.signal_cls(y=y, t=t)
		signal.set_units(t_unit="sec")
		signal.set_name(name=f"Square: {f}Hz")
		signal.set_plot_labels(
			title=signal.name,
			y_label="Amplitude",
			t_label="Time"
		)
		
		return signal

	@validate_args_type()
	def generate_sawtooth(
		self,
		A: float | int = 1.0,
		f: float | int = 10.0,
		phi: float | int = 0.0,
		duration: float | int = 1.0,
		Ts: float | int = 0.01,
	):
		"""
		Generates a sawtooth wave.
		"""
		
		A, f, phi, duration, Ts = float(A), float(f), float(phi), float(duration), float(Ts)
		
		t = np.arange(0, duration, Ts)
		y = A * (2 * (t * f + phi) % 1 - 1)
		
		signal: UniformTimeDomainSignal | AudioSignal = self.signal_cls(y=y, t=t)
		signal.set_units(t_unit="sec")
		signal.set_name(name=f"Sawtooth: {f}Hz")
		signal.set_plot_labels(
			title=signal.name,
			y_label="Amplitude",
			t_label="Time"
		)
		
		return signal

	@validate_args_type()
	def generate_triangle(
		self,
		A: float | int = 1.0,
		f: float | int = 10.0,
		phi: float | int = 0.0,
		duration: float | int = 1.0,
		Ts: float | int = 0.01,
	):
		"""
		Generates a triangle wave
		"""
		
		A, f, phi, duration, Ts = float(A), float(f), float(phi), float(duration), float(Ts)
		
		t = np.arange(0, duration, Ts)
		signal = A * np.abs(2 * (t * f + phi) % 1 - 1)
		
		signal: UniformTimeDomainSignal | AudioSignal = self.signal_cls(y=y)
		signal.set_units(t_unit="sec")
		signal.set_name(name=f"Triangle: {f}Hz")
		signal.set_plot_labels(
			title=signal.name,
			y_label="Amplitude",
			t_label="Time"
		)
		
		return signal