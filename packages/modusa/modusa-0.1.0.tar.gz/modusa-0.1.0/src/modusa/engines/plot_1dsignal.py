#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import validate_args_type
from modusa.engines.base import ModusaEngine
from typing import Any
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class Plot1DSignalEngine(ModusaEngine):
	"""

	"""
	
	#--------Meta Information----------
	name = "Plot 1D Signal"
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-02"
	#----------------------------------
	
	def __init__(self):
		super().__init__()
	
	
	@validate_args_type()
	def run(
		self,
		y: np.ndarray,
		x: np.ndarray | None,
		scale_y: tuple[float, float] | None,
		scale_x: tuple[float, float] | None ,
		ax: plt.Axes | None,
		color: str,
		marker: str | None,
		linestyle: str | None,
		stem: bool | None,
		labels: tuple[str, str, str] | None,
		legend_loc: str | None,
		zoom: tuple | None,
		highlight: list[tuple[float, float], ...] | None,
	) -> plt.Figure | None:
				
		
		# Validate the important args and get the signal that needs to be plotted
		if y.ndim != 1:
			raise excp.InputValueError(f"`y` must be of dimension 1 not {y.ndim}.")
		if y.shape[0] < 1:
			raise excp.InputValueError(f"`y` must not be empty.")
			
		if x is None:
			x = np.arange(y.shape[0])
		elif x.ndim != 1:
			raise excp.InputValueError(f"`x` must be of dimension 1 not {x.ndim}.")
		elif x.shape[0] < 1:
			raise excp.InputValueError(f"`x` must not be empty.")
		
		if x.shape[0] != y.shape[0]:
			raise excp.InputValueError(f"`y` and `x` must be of same shape")
		
		# Scale the signal if needed
		if scale_y is not None:
			if len(scale_y) != 2:
				raise excp.InputValueError(f"`scale_y` must be tuple of two values (1, 2) => 1y+2")
			a, b = scale_y
			y = a * y + b
		
		if scale_x is not None:
			if len(scale_x) != 2:
				raise excp.InputValueError(f"`scale_x` must be tuple of two values (1, 2) => 1x+2")
			a, b = scale_x
			x = a * x + b
			
		# Create a figure
		if ax is None:
			fig, ax = plt.subplots(figsize=(15, 2))
			created_fig = True
		else:
			fig = ax.get_figure()
			created_fig = False 
		
		# Plot the signal with right configurations
		plot_label = labels[0] if labels is not None and len(labels) > 0 else None
		if stem:
			ax.stem(x, y, linefmt=color, markerfmt='o', label=plot_label)
		elif marker is not None:
			ax.plot(x, y, c=color, linestyle=linestyle, lw=1.5, marker=marker, label=plot_label)
		else:
			ax.plot(x, y, c=color, linestyle=linestyle, lw=1.5, label=plot_label)
			
		# Add legend
		if plot_label is not None:
			legend_loc = "upper right" if legend_loc is None else legend_loc
			ax.legend(loc=legend_loc)
		
		# Set the labels
		if labels is not None:
			if len(labels) > 0:
				ax.set_title(labels[0])
			if len(labels) > 1:
				ax.set_ylabel(labels[1])
			if len(labels) > 2:
				ax.set_xlabel(labels[2])
	
		# Zoom into a region
		if zoom is not None:
			ax.set_xlim(zoom)
		
		# Highlight a list of regions
		if highlight is not None:
			for highlight_region in highlight:
				if len(highlight_region) != 2:
					raise excp.InputValueError(f"`highlight should be a list of tuple of 2 values (left, right) => (1, 10.5)")
				l, r = highlight_region
				ax.add_patch(Rectangle((l, np.min(y)), r - l, np.max(y) - np.min(y), color='red', alpha=0.2, zorder=10))
		
		# Show/Return the figure as per needed
		if created_fig:
			fig.tight_layout()
			try:
				get_ipython
				plt.close(fig) # Without this, you will see two plots in the jupyter notebook
				return fig
			except NameError:
				plt.show()
				return fig