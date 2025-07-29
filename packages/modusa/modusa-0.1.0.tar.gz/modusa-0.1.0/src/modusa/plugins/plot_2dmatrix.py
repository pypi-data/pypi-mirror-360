#!/usr/bin/env python3


from modusa.plugins.base import ModusaPlugin
from modusa.decorators import immutable_property, validate_args_type, plugin_safety_check
import matplotlib.pyplot as plt

class Plot2DMatrixPlugin(ModusaPlugin):
	"""

	"""
	
	#--------Meta Information----------
	name = "Plot 2D Matrix Plugin"
	description = "A 2D matrix plotter plugin with various features."
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-02"
	#----------------------------------
	
	def __init__(self):
		super().__init__()
		
	@immutable_property(error_msg="Mutation not allowed.")
	def allowed_input_signal_types(self) -> tuple[type, ...]:
		from modusa.signals import Signal2D
		return (Signal2D, )
	
	
	@immutable_property(error_msg="Mutation not allowed.")
	def allowed_output_signal_types(self) -> tuple[type, ...]:
		return (plt.Figure, type(None)) # None is returned when we want to plot on a given axes, no figure is created in that case
	
	
	@plugin_safety_check()
	@validate_args_type()
	def apply(self,
		signal: "Signal2D",
		log_compression_factor: int | float | None = None,
		ax: plt.Axes | None = None,
		labels: tuple[str, str, str, str] | None = None,
		zoom: tuple[float, float, float, float] | None = None,  # (r1, r2, c1, c2)
		highlight: list[tuple[float, float, float, float]] | None = None,
		cmap: str = "gray_r",
		origin: str = "upper",  # or "lower"
		show_colorbar: bool = True,
		cax: plt.Axes | None = None,
		show_grid: bool = False,
		tick_mode: str = "center",  # or "edge"
		n_ticks: tuple[int, int] = (11, 21),
		value_range: tuple[float, float] | None = None,
		
	) -> "Signal2D":
		
		# Run the engine here
		from modusa.engines import Plot2DMatrixEngine
		
		fig: plt.Figure = Plot2DMatrixEngine().run(
			M=signal.M,
			r=signal.r,
			c=signal.c,
			log_compression_factor=log_compression_factor,
			ax=ax,
			labels=signal.labels,
			zoom=zoom,
			highlight=highlight,
			cmap=cmap,
			origin=origin,
			show_colorbar=show_colorbar,
			cax=cax,
			show_grid=show_grid,
			tick_mode=tick_mode,
			n_ticks=n_ticks,
			value_range=value_range)
		
		return fig