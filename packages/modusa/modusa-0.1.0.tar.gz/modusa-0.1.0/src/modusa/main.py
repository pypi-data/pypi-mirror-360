#!/usr/bin/env python3


from line_profiler import LineProfiler
from modusa.engines.plot_2dmatrix import Plot2DMatrixEngine
import numpy as np

M = np.abs(np.random.rand(1000, 1000))
r = np.linspace(0, 1, M.shape[0])
c = np.linspace(0, 1, M.shape[1])

engine = Plot2DMatrixEngine()

lp = LineProfiler()
lp.add_function(engine.run.__wrapped__)

lp_wrapper = lp(engine.run)
lp_wrapper(
	M, r, c,
	log_compression_factor=None,
	ax=None,
	labels=("Title", "Colorbar", "Y", "X"),
	zoom=None,
	highlight=None,
	cmap="gray_r",
	origin="lower",
	show_colorbar=True,
	cax=None,
	show_grid=False,
	tick_mode="center",
	n_ticks=(10, 10),
	value_range=None
)

lp.print_stats()
