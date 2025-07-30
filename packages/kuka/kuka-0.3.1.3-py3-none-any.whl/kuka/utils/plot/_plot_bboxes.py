import numpy as np
import matplotlib.transforms as mtransforms
import matplotlib.patches as patches

from matplotlib.figure import Figure
from .._input_function_validation import _input_function_validation

def bbox_pixels_to_fig_fraction(bbox, fig):
	"""
	Convert a bbox from pixels to figure fraction (0-1).

	Parameters:
	- bbox : matplotlib.transforms.Bbox
	- fig : matplotlib.figure.Figure

	Returns:
	- bbox_fraction : matplotlib.transforms.Bbox
	"""
	fig_width, fig_height = fig.get_size_inches() * fig.dpi

	x0 = bbox.x0 / fig_width
	y0 = bbox.y0 / fig_height
	x1 = bbox.x1 / fig_width
	y1 = bbox.y1 / fig_height

	return mtransforms.Bbox.from_extents(x0, y0, x1, y1)



_input_val_dict = {
    'bbox_list' : ( (list, tuple), None),
    'fig' : ( Figure, None),
	'color': ( str, None),
	'linewidth': ( (int, float), 'range', [0, np.inf]),
	'linestyle': (str, None)
}

@_input_function_validation(_input_val_dict)
def _plot_bboxes(bbox_list, fig, color='red', linewidth=1, linestyle='-'):
	
	"""
	Plot bounding boxes on a matplotlib figure using figure-relative coordinates (0–1).

	This function is useful for debugging or visualizing layout issues by
	overlaying rectangular outlines (patches) corresponding to the positions of
	graphical elements, such as tick labels, texts, or axes objects.

	It internally converts pixel-based bounding boxes to figure fractions and
	draws them directly onto the figure canvas.

	Parameters
	----------
	bbox_list : list or tuple of matplotlib.transforms.Bbox
		A list of bounding boxes to be drawn. These must be in **pixel coordinates**
		(usually obtained via `.get_window_extent(renderer)`).

	fig : matplotlib.figure.Figure
		The target figure where the bounding boxes will be drawn.

	color : str, optional (default='red')
		The color of the bounding box borders.

	linewidth : int or float, optional (default=1)
		The thickness of the rectangle edges.

	linestyle : str, optional (default='-')
		The style of the rectangle edges (e.g., '-', '--', ':', '-.').


	Returns
	-------
	rect_list : list of matplotlib.patches.Rectangle
		A list of the rectangle objects added to the figure.


	Examples
	--------
	´´´python
	fig, ax = plt.subplots()
	bars = ax.bar(['A', 'B', 'C'], [5, 7, 4])
	fig.canvas.draw()
	renderer = fig.canvas.get_renderer()
	´´´

	´´´python
	bbox_list = [bar.get_window_extent(renderer) for bar in bars]
	_plot_bboxes(bbox_list, fig, color='green', linewidth=2, linestyle='--')
	´´´

	´´´python
	# Also works with tick labels or text objects:
	tick_bboxes = [label.get_window_extent(renderer) for label in ax.get_xticklabels()]
	_plot_bboxes(tick_bboxes, fig, color='blue')
	´´´
	"""

	rect_list = []

	for bbox in bbox_list:
		bbox_frac = bbox_pixels_to_fig_fraction(bbox, fig)

		rect = patches.Rectangle(
			(bbox_frac.x0, bbox_frac.y0),
			bbox_frac.width,
			bbox_frac.height,
			linewidth=linewidth,
			edgecolor=color,
			facecolor='none',
			linestyle=linestyle,
			transform=fig.transFigure
		)
		fig.add_artist(rect)
		rect_list.append(rect)

	return rect_list