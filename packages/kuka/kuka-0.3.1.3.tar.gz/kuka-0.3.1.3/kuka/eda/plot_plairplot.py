import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import Patch

from .. import utils

from ..utils.plot import _adjust_obj_to_ref

def _add_aling_and_adjust_labels_manually(
		axs_plots:list,
		fig:Figure,
		xlabels:list, 
		ylabels:list,
		kargs_labels:dict,
		):
	
	fig.canvas.draw()
	renderer = fig.canvas.get_renderer()
	
	# Get the minimum y0-coord of xticklabels:
	min_y0_xticklabels = np.inf
	for ax in axs_plots[-1]:
		for ticklabel in ax.get_xticklabels():
			if ticklabel.get_text():
				ticklabel_bbox = ticklabel.get_window_extent(renderer=renderer)
				min_y0_xticklabels = ticklabel_bbox.y0 if (ticklabel_bbox.y0 < min_y0_xticklabels) else min_y0_xticklabels
	# Get the minimum x0-coord of yticklabels:
	first_col_ax = [lista[0] for lista in axs_plots]
	min_x0_yticklabels = np.inf
	for ax in first_col_ax:
		for ticklabel in ax.get_yticklabels():
			if ticklabel.get_text():
				ticklabel_bbox = ticklabel.get_window_extent(renderer=renderer)
				min_x0_yticklabels = ticklabel_bbox.x0 if (ticklabel_bbox.x0 < min_x0_yticklabels) else min_x0_yticklabels
	
	min_y0_xticklabels = axs_plots[-1][0].get_window_extent(renderer=renderer).y0 if min_y0_xticklabels==np.inf else min_y0_xticklabels
	min_x0_yticklabels = first_col_ax[0].get_window_extent(renderer=renderer).x0 if min_x0_yticklabels==np.inf else min_x0_yticklabels

	xlabels_obj = []
	ylabels_obj = []

	# Put labels in x axis
	for ax, text in zip(axs_plots[-1], xlabels):
		# Put the xlabels
		bbox_axis = ax.get_window_extent(renderer)
		xy0 = fig.transFigure.inverted().transform((bbox_axis.x0, bbox_axis.y0))
		obj = fig.text(xy0[0], xy0[1], text, 
				horizontalalignment='center',
				verticalalignment='center',
				**kargs_labels
				)
		
		# center the labels on x-axis and place them at the same height
		bbox = obj.get_window_extent(renderer)
		x_bbox = (bbox.x0 + bbox.width/2) + bbox_axis.width/2
		y_bbox = min_y0_xticklabels - 0.15*bbox_axis.height
		xy = fig.transFigure.inverted().transform((x_bbox, y_bbox))
		obj.set_position( (xy[0], xy[1]) )
		xlabels_obj.append(obj)

	# Put labels in y axis
	for ax, text in zip(first_col_ax, ylabels):
		# Put the ylabels
		bbox_axis = ax.get_window_extent(renderer)
		xy0 = fig.transFigure.inverted().transform((bbox_axis.x0, bbox_axis.y0))
		obj = fig.text(xy0[0], xy0[1], text, 
				horizontalalignment='center', 
				verticalalignment='center', 
				rotation = 'vertical',
				**kargs_labels
				)
		
		# center the labels on x-axis and place them at the same height
		bbox = obj.get_window_extent(renderer)
		x_bbox = min_x0_yticklabels - 0.15*bbox_axis.width
		y_bbox = (bbox.y0 + bbox.height/2) + bbox_axis.height/2
		xy = fig.transFigure.inverted().transform((x_bbox, y_bbox))
		obj.set_position( (xy[0], xy[1]) )
		# obj.set_position( (xy[0], obj.get_position()[1]) )
		ylabels_obj.append(obj)

	
	# Adjust x labels
	_adjust_obj_to_ref(
		fig,
		xlabels_obj,
		list(axs_plots[-1]),
		'w',
		['wrap_until_fit'],
		)
	xticklabels_of_last_row = np.array([obj.get_xticklabels() for obj in axs_plots[-1]]).ravel()
	_adjust_obj_to_ref(
		fig,
		xlabels_obj,
		list(xticklabels_of_last_row) + list(axs_plots[-1]),
		'w',
		['move_until_no_overlaps'],
		move_rate=(0, -0.015),
		)
	# Adjust y labels
	_adjust_obj_to_ref(
		fig,
		ylabels_obj,
		first_col_ax,
		'h',
		['wrap_until_fit'],
		)
	yticklabels_of_first_col = np.array([obj.get_yticklabels() for obj in first_col_ax]).ravel()
	_adjust_obj_to_ref(
		fig,
		ylabels_obj,
		list(yticklabels_of_first_col) + list(first_col_ax),
		'w',
		['move_until_no_overlaps'],
		move_rate=(-0.015, 0),
		)






_input_val_dict = {
	'df': ( pd.DataFrame, None ), 
	'columns' : ( (list, tuple), None ),
	'by': ( (str, None.__class__), None ),
	
	'colors_reference': ( (list, tuple), None ),
	'dict_colors_of_variable_by': ((None.__class__ , dict), None),
	'zorder': ((list, tuple, None.__class__), None),
	'markers': ((list, None.__class__), None),

	'fontsize': ( (float, int, None.__class__), 'range', [0, np.inf] ),
	'kargs_labels': ( dict, None ),

	'figsize': ( (list, tuple, None.__class__), 'length', 2 ),
	'wspace': ( (int, float), None ),
	'hspace': ( (int, float), None ),

	'tick_majorlabel': ( bool, None ),
	'tick_labelsize': ( (int, float, None.__class__), None ),
	'tick_labelformat': ( str, None ),
	'margins': ( (int, float), None ),

	'show_kdeplots': ( (int, None.__class__), None ),
	'kdeplots_level': ( (float, int), 'range', [0, np.inf] ),
	'show_kdeplots_of_by': ( bool, None ),

	'external_fig_and_ax': (( None.__class__ , tuple, list), None),
}

@utils._input_function_validation(_input_val_dict)
def plot_plairplot(
		df:pd.DataFrame, 
		columns:list = ['all'],
		by:str = None,
		
		colors_reference:list = ['black', '#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2', '#9f4800', '#f14cc1', '#a3a3a3', '#ffc400', '#00d7ff'],
		dict_colors_of_variable_by:dict = None,
		zorder:list = None,
		markers:list = None,

		fontsize:float = 10.,
		kargs_labels:dict = {},

		figsize:tuple = (6, 6),
		wspace:float = 0.12,
		hspace:float = 0.12,
		s:int = 10,

		tick_majorlabel:bool = True,
		tick_labelsize:float = None,
		tick_labelformat:str = '{x:.4g}',
		margins:float = 0.08,

		show_kdeplots:int = None,
		kdeplots_level:int = 3,
		show_kdeplots_of_by:bool = False,
		kargs_kdeplots:dict = {},

		external_fig_and_ax = None,

		**kwargs_scatter

		) -> tuple[Figure, Axes]:

	
	'''
	Create a pairplot-style scatter plot matrix with optional grouping and KDE contours.

	This function plots scatter plots for all pairs of columns in the provided DataFrame. It supports grouping data by a categorical variable (`by`), customizable colors, markers, and z-order. Optional KDE contour plots can be overlaid on scatter plots to visualize density.

	Parameters
	----------
	df : pandas.DataFrame
		Input dataset containing columns to be plotted.

	columns : list of str, default ['all']
		List of columns to include in the pairplot. If ['all'], uses all DataFrame columns.

	by : str or None, optional
		Column name for grouping the data. If specified, plots points grouped by categories in this column.

	colors_reference : list of str, optional
		List of colors to cycle through when assigning colors to groups (used if `dict_colors_of_variable_by` is None).

	dict_colors_of_variable_by : dict or None, optional
		Dictionary mapping categories from `by` column to colors. If provided, overrides `colors_reference`.

	zorder : list or None, optional
		List specifying plotting order of groups in `by`. Groups later in the list are plotted on top.

	markers : list or None, optional
		List of matplotlib marker styles for each group in `by`. If fewer markers than groups are provided, defaults will be used.

	fontsize : float, default 10.0
		Font size for axis labels.

	kargs_labels : dict, optional
		Additional keyword arguments passed to label text objects.

	figsize : tuple, default (6, 6)
		Figure size in inches.

	wspace : float, default 0.12
		Width space between subplots.

	hspace : float, default 0.12
		Height space between subplots.

	s : int, default 10
		Marker size for scatter plots.

	tick_majorlabel : bool, default True
		Whether to show major tick labels.

	tick_labelsize : float or None, optional
		Font size for tick labels. If None, uses matplotlib default.

	tick_labelformat : str, default '{x:.4g}'
		Format string for tick labels.

	margins : float, default 0.08
		Fractional margin added around axis limits.

	show_kdeplots : int or None, optional
		If set, overlays KDE contour plots with this z-order.

	kdeplots_level : int, default 3
		Number of contour levels in KDE plots.

	show_kdeplots_of_by : bool, default False
		If True, draws KDE contours separately for each group in `by`.

	kargs_kdeplots : dict, optional
		Additional keyword arguments for seaborn KDE plot.
	
	external_fig_and_ax : `None` or `tuple(Figure, Axes)`
		If provided, uses the given Matplotlib `Figure` and `Axes` for plotting.

	**kwargs_scatter : dict
		Additional keyword arguments passed to scatter plot calls.

	Returns
	-------
	fig : matplotlib.figure.Figure
		The created figure object.

	ax : numpy.ndarray of matplotlib.axes.Axes
		Array of axes objects forming the scatter matrix.

	Example
	-------
	```python
	fig, ax = plot_plairplot(df, columns=['height', 'weight', 'age'], by='gender', s=20, show_kdeplots=2)
	```
	'''


	##########################################################
	########### 0 - Define initial configurations: ###########
	##########################################################

	df = df.copy()

	# validate external_fig_and_ax
	if external_fig_and_ax:
		fig, ax = external_fig_and_ax
		assert ( isinstance(fig, Figure) ), 'index 0 of "external_fig_and_ax" are not a matplotlib.figure.Figure type'
		assert ( isinstance(ax, Axes) ), 'index 1 of "external_fig _and_ax" are not a matplotlib.axes._axes.Axes type'
	
	if (columns == ['all']):
		columns = list(df.columns)

	if (tick_labelsize is None):
		tick_labelsize = matplotlib.rcParams['font.size']

	kargs_labels['fontsize'] = fontsize

	if by:
		column_by = df[by].copy()
		unique_by = column_by.unique()
		# make sure that zorder_list is in "unique_by"
		if zorder:
			check = all([(cat in unique_by) for cat in zorder])
			assert check, 'Some "zorder" categories are not in "by" unique values'
	
	# make sure that "markers" has the same length of "unique_by"
	if by:
		if markers:
			markers = markers + [matplotlib.rcParams["scatter.marker"]]*(len(unique_by)-len(markers)) if len(markers)<len(unique_by) else markers
		else:
			markers = [matplotlib.rcParams["scatter.marker"]]*len(unique_by)
		markers.reverse()
	else:
		markers = [matplotlib.rcParams["scatter.marker"]]


	# Only work with numeric columns
	print(f'\n    String type columns:\n')
	numeric_columns = []
	for col in columns:
		if not(df[col].dtype == object):
			numeric_columns.append(col)
		else:
			print(col,'     ',df[col].dtype)
	columns = numeric_columns
	print('columns = ', list(columns))
	print('\n')

	# Define the colors for each unique values "unique_by"
	# If len(unique_by) > len(colors_reference), the colors os "colors_reference" will repeat
	if by:

		if dict_colors_of_variable_by:
			# validate dict_colors_of_variable_by
			check = len(dict_colors_of_variable_by.keys()) == len(unique_by)
			assert check, 'len(dict_colors_of_variable_by.keys()) != len(unique_by)'
			for cat in unique_by:
				check = cat in list(dict_colors_of_variable_by.keys())
				assert check, 'dict_colors_of_variable_by does not have all the categories of "by"'
			colors = dict_colors_of_variable_by
		else:
			colors_sequence = []
			n = len(unique_by)//len(colors_reference)
			r = len(unique_by)%len(colors_reference)
			colors_sequence = colors_reference*n + colors_reference[0:r]
			colors = dict(zip(unique_by,colors_sequence))

	else:
		colors = colors_reference[0]

	# Create Matplotlib fig and axis
	if external_fig_and_ax:
		fig, ax = external_fig_and_ax
	else:
		fig, ax = plt.subplots(ncols=len(columns)-1,
							nrows=len(columns)-1,
							figsize=figsize)
	
	################################################################
	########### 1 - set a piece of code that will repeat ###########
	################################################################

	def graph_definitions():
		xlim = (df[col].min(), df[col].max())
		ylim = (df[row].min(), df[row].max())

		if not(np.isnan(xlim[0]) or np.isnan(xlim[1])):
			ampl_x = (xlim[1] - xlim[0])*margins
			ax[i,j].set_xlim([ xlim[0]-ampl_x, xlim[1]+ampl_x ])
		if not(np.isnan(ylim[0]) or np.isnan(ylim[1])):
			ampl_y = (ylim[1] - ylim[0])*margins
			ax[i,j].set_ylim([ ylim[0]-ampl_y, ylim[1]+ampl_y ])

		ax[i,j].xaxis.set_major_locator(matplotlib.ticker.FixedLocator(xlim))
		ax[i,j].yaxis.set_major_locator(matplotlib.ticker.FixedLocator(ylim))

		if tick_majorlabel == True:
			ax[i,j].tick_params(axis = 'both', which='major', bottom=True, left=True, length=6)
			ax[i,j].tick_params(axis = 'both', labelsize=tick_labelsize)
			ax[i,j].xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter(tick_labelformat))
		else:
			ax[i,j].tick_params(axis = 'both', which='major', labelbottom=False, labelleft=False)

		# X and Y labels
		# if the graph is in the last row
		if (i==(len(columns)-2)):
			xlabels.append(col)
			ax[i,j].tick_params(axis='x', which='both', rotation=90)
		else:
			ax[i,j].tick_params(which='both', bottom=False, labelbottom=False)

		# if the graph is in the first column
		if (j==0):
			ylabels.append(row)
		else:
			ax[i,j].tick_params(which='both', left=False, labelleft=False)
	
	###########################################
	########### 2 - Plot the graphs ###########
	###########################################
	if by:
		if zorder:
			order_of_plot = list(zorder)
			order_of_plot += list( set(unique_by) - set(order_of_plot) ) 
			order_of_plot.reverse()
		else:
			order_of_plot = unique_by

	i, j = (-1, -1)
	xlabels = []
	ylabels = []

	for row in columns: #i
		for col in columns: #j
			if (row==col):
				j = 0
				break
			# Plot:
			if by:
				for count, group in enumerate(order_of_plot):
					df_filtered = df.loc[ column_by==group, [row, col] ]
					ax[i,j].scatter(
						x = df_filtered[col],
						y = df_filtered[row],
						color = colors[group],
						marker = markers[count],
						s = s,
						**kwargs_scatter
						)
					
			else:
				df_filtered = df.dropna(subset=[row, col])
				ax[i,j].scatter(
					x = df_filtered[col],
					y = df_filtered[row],
					color = colors,
					marker = markers[0],
					s = s,
					**kwargs_scatter
					)
				
			graph_definitions()
			j+=1
		i+=1

	########################################
	########## 3 - Plot kde plots ##########
	########################################
	if show_kdeplots:
		i, j = (-1, -1)

		for row in columns: #i
			for col in columns: #j
				if (row==col):
					j = 0
					break
				# Plot contour plots:
				if (by is not None) and (show_kdeplots_of_by):
					for count, group in enumerate(order_of_plot):
						df_filtered = df.loc[ column_by==group, [row, col] ]
						sns.kdeplot(df_filtered, x=col, y=row,
							levels = kdeplots_level,
							color = colors[group],
							ax=ax[i,j],
							**kargs_kdeplots
							)
						ax[i,j].collections[-1].set_zorder(show_kdeplots)
					ax[i,j].set_xlabel(None)
					ax[i,j].set_ylabel(None)
					
				else:
					df_filtered = df.dropna(subset=[row, col])
					sns.kdeplot(df_filtered, x=col, y=row,
							levels = kdeplots_level,
							ax=ax[i,j],
							**kargs_kdeplots
							)
					ax[i,j].collections[-1].set_zorder(show_kdeplots)
					ax[i,j].set_xlabel(None)
					ax[i,j].set_ylabel(None)
					
				j+=1
			i+=1

	###########################################
	########## 4 - Final adjustments ##########
	###########################################

	#Remover eixos não usados
	aux = 0
	for row in range(len(columns)-1): #i
		for col in range(len(columns)-1): #j
			if col>row:
				ax[row,col].remove()

	plt.subplots_adjust(wspace=wspace, hspace=hspace)

	_add_aling_and_adjust_labels_manually(ax, fig, xlabels, ylabels, kargs_labels=kargs_labels)

	# Put a legend manually
	if by:
		legend_paches = []
		for k, v in colors.items():
			legend_paches.append( Patch( color=v, label=k) )
		xmax = ax[-1][len(columns)-2].get_position(fig.transFigure).x1
		ymax = ax[0][0].get_position(fig.transFigure).y1
		
		fig.legend(handles=legend_paches, title=by+' legend:', loc='upper right', bbox_to_anchor=(xmax, ymax), edgecolor='black')
	
	return fig, ax