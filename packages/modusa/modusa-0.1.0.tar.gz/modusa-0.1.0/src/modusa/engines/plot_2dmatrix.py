#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import validate_args_type
from modusa.engines.base import ModusaEngine
from typing import Any
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator

class Plot2DMatrixEngine(ModusaEngine):
	"""

	"""
	
	#--------Meta Information----------
	name = "Plot 2D Matrix"
	description = ""
	author_name = "Ankit Anand"
	author_email = "ankit0.anand0@gmail.com"
	created_at = "2025-07-02"
	#----------------------------------
	
	def __init__(self):
		super().__init__()
		
	
	@staticmethod
	def compute_centered_extent(r: np.ndarray, c: np.ndarray, origin: str) -> list[float]:
		"""
		
		"""
		dc = np.diff(c).mean() if len(c) > 1 else 1
		dr = np.diff(r).mean() if len(r) > 1 else 1
		left   = c[0] - dc / 2
		right  = c[-1] + dc / 2
		bottom = r[0] - dr / 2
		top    = r[-1] + dr / 2
		return [left, right, top, bottom] if origin == "upper" else [left, right, bottom, top]
	
	
	@validate_args_type()
	def run(
		self,
		M: np.ndarray,
		r: np.ndarray,
		c: np.ndarray,
		log_compression_factor: int | float | None,
		ax: plt.Axes | None,
		labels: tuple[str, str, str, str] | None,
		zoom: tuple[float, float, float, float] | None,  # (r1, r2, c1, c2)
		highlight: list[tuple[float, float, float, float]] | None,
		cmap: str,
		origin: str,  # or "lower"
		show_colorbar: bool,
		cax: plt.Axes | None,
		show_grid: bool,
		tick_mode: str,  # "center" or "edge"
		n_ticks: tuple[int, int],
		value_range: tuple[float, float] | None,
	) -> plt.Figure:
		pass
		
		# Validate the important args and get the signal that needs to be plotted
		if M.ndim != 2:
			raise excp.InputValueError(f"`M` must have 2 dimension not {M.ndim}")
		if r.ndim != 1 and c.ndim != 1:
			raise excp.InputValueError(f"`r` and `c` must have 2 dimension not r:{r.ndim}, c:{c.ndim}")
			
		if r.shape[0] != M.shape[0]:
			raise excp.InputValueError(f"`r` must have shape as `M row` not {r.shape}")
		if c.shape[0] != M.shape[1]:
			raise excp.InputValueError(f"`c` must have shape as `M column` not {c.shape}")
			
		# Scale the signal if needed
		if log_compression_factor is not None:
			M = np.log1p(float(log_compression_factor) * M)
		
		# Create a figure
		if ax is None:
			fig, ax = plt.subplots(figsize=(15, 4))
			created_fig = True
		else:
			fig = ax.get_figure()
			created_fig = False
		
		# Plot the signal with right configurations
		# Compute extent
		extent = Plot2DMatrixEngine.compute_centered_extent(r, c, origin)
		
		# Plot image
		im = ax.imshow(
			M,
			aspect="auto",
			cmap=cmap,
			origin=origin,
			extent=extent,
			vmin=value_range[0] if value_range else None,
			vmax=value_range[1] if value_range else None,
		)
		
		# Set the ticks and labels
		if tick_mode == "center":
			ax.yaxis.set_major_locator(MaxNLocator(nbins=n_ticks[0]))
			ax.xaxis.set_major_locator(MaxNLocator(nbins=n_ticks[1]))  # limits ticks
			
		elif tick_mode == "edge":
			dc = np.diff(c).mean() if len(c) > 1 else 1
			dr = np.diff(r).mean() if len(r) > 1 else 1
			ax.set_xticks(np.append(c, c[-1] + dc) - dc / 2)
			ax.set_yticks(np.append(r, r[-1] + dr) - dr / 2)
		
		if labels is not None:
			if len(labels) > 0:
				ax.set_title(labels[0])
			if len(labels) > 2:
				ax.set_ylabel(labels[2])
			if len(labels) > 3:
				ax.set_xlabel(labels[3])
		
		# Zoom into a region
		if zoom is not None:
			r1, r2, c1, c2 = zoom
			ax.set_xlim(min(c1, c2), max(c1, c2))
			ax.set_ylim(
				(min(r1, r2), max(r1, r2)) if origin == "lower" else (max(r1, r2), min(r1, r2))
			)
			
		# Highlight a list of regions
		if highlight is not None:
			for r1, r2, c1, c2 in highlight:
				row_min, row_max = min(r1, r2), max(r1, r2)
				col_min, col_max = min(c1, c2), max(c1, c2)
				width = col_max - col_min
				height = row_max - row_min
				ax.add_patch(Rectangle((col_min, row_min), width, height, color='red', alpha=0.2, zorder=10))
		
		# Show colorbar
		if show_colorbar is not None:
			cbar = fig.colorbar(im, ax=ax, cax=cax)
			if len(labels) > 1:
				cbar.set_label(labels[1])
		
		# Show grid
		if show_grid:
			ax.grid(True, color="gray", linestyle="--", linewidth=0.5) # TODO

		# Show/Return the figure as per needed
		if created_fig:
			fig.tight_layout()
			try:
				get_ipython
				plt.close(fig)
				return fig
			except NameError:
				plt.show()
				return fig
