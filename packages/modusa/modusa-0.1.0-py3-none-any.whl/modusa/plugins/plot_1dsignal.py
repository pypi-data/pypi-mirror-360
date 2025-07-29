#!/usr/bin/env python3


from modusa.plugins.base import ModusaPlugin
from modusa.decorators import immutable_property, validate_args_type, plugin_safety_check
import matplotlib.pyplot as plt

class Plot1DSignalPlugin(ModusaPlugin):
	"""

	"""
	
	#--------Meta Information----------
	name = "Plot 1D Signal Plugin"
	description = "A 1D signal plotter plugin with various features."
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-02"
	#----------------------------------
	
	def __init__(self):
		super().__init__()
	
	@immutable_property(error_msg="Mutation not allowed.")
	def allowed_input_signal_types(self) -> tuple[type, ...]:
		from modusa.signals import Signal1D
		return (Signal1D, )
	
	
	@immutable_property(error_msg="Mutation not allowed.")
	def allowed_output_signal_types(self) -> tuple[type, ...]:
		return (plt.Figure, type(None)) # None is returned when we want to plot on a given axes, no figure is created in that case
	
	
	@plugin_safety_check()
	@validate_args_type()
	def apply(
		self,
		signal: "Signal1D",
		scale_y: tuple[float, float] | None = None,
		scale_x: tuple[float, float] | None = None,
		ax: plt.Axes | None = None,
		color: str | None = "k",
		marker: str | None = None,
		linestyle: str | None = None,
		stem: bool = False,
		labels: tuple[str, str, str] | None = None,
		legend_loc: str | None = None,
		zoom: tuple[float, float] | None = None,
		highlight: list[tuple[float, float], ...] | None = None,
		show_grid: bool | None = False,
	) -> plt.Figure:
		
		# Run the engine here
		from modusa.engines import Plot1DSignalEngine
		
		fig: plt.Figure | None = Plot1DSignalEngine().run(y=signal.data, x=signal.x, scale_y=scale_y, scale_x=scale_x, ax=ax, color=color, marker=marker, linestyle=linestyle, stem=stem, labels=labels, legend_loc=legend_loc, zoom=zoom, highlight=highlight)
		
		return fig 