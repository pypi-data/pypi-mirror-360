from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import scipy

from ..utils.plot import _adjust_obj_to_ref

def _add_tick(ax, axis, pos, label):
	
	ticks = list(ax.get_xticks()) if axis=='x' else list(ax.get_yticks())

	obj_labels = ax.get_xticklabels() if axis=='x' else ax.get_yticklabels()
	labels = [tick.get_text() for tick in obj_labels]

	# Add the new "pos" and "label"
	ticks.append(pos)
	labels.append(label)
	# Update
	ax.set_xticks(ticks)
	ax.set_xticklabels(labels)


def _check_if_label_outside(label, ax, fig):
	"""
	Check if a label is outside the axis limits.

	Returns:
	- "x"  → if the label exceeds horizontally (out of X limits)
	- "y"  → if the label exceeds vertically (out of Y limits)
	- None → if the label is fully inside the axis
	"""
	fig.canvas.draw()
	renderer = fig.canvas.get_renderer()

	bbox_label = label.get_window_extent(renderer)
	bbox_ax = ax.get_window_extent()

	# when the label does not appear in the figure, its bboxes are x0,x1 = (0,1) and y0,y1 = (0,1):
	check_x = bbox_label.x0==0 and bbox_label.x1==1
	check_y = bbox_label.y0==0 and bbox_label.y1==1
	if check_x and check_y:
		return None

	# Check if exceeds X
	if bbox_label.x0 < bbox_ax.x0 or bbox_label.x1 > bbox_ax.x1:
		return 'x'
	# Check if exceeds only Y_max
	if bbox_label.y1 > bbox_ax.y1:
		return 'y'
	# If its ok:
	return None











_input_val_dict = {
	'df': (pd.DataFrame, None),
	'variable': (str, None),
	'mode': (str, 'pattern', ['bar', 'hist']),
	'by': ((str, None.__class__), None),
	'by_mode': (str, 'pattern', ['stacked', 'grouped', 'subploted']),

	'alpha': ((float, int), 'range', [0, 1]),
	'colors_reference': ((list, tuple), None),
	'figsize': ((list, tuple), 'length', 2),
	'fontsize': ((None.__class__, int, float), None),
	'labels': ((str, None.__class__), 'pattern', [None, 'top', 'center']),
	'labels_format': ( (str, None.__class__) , None),
	'labels_padding': ( (list, tuple), 'length', 2),
	'labels_threshold': ( (float, int), 'range', [0, np.inf]),
	'norm': (bool, None),

	'bar_width': ((int, float), 'range', [0,1]),

	'hist_bins': (int, 'range', [0, np.inf]),
	'hist_ticklabels_format': (str, None),
	'hist_grouped_offset': ((list,tuple), 'length', 2),
	'hist_x_log_scale': (bool, None),
	'hist_average_line': (bool, None),
	'hist_average_line_kargs': (dict, None),
	
	'external_fig_and_ax': (( None.__class__ , tuple, list), None),
	'dict_colors_of_variable_by': ((None.__class__ , dict), None),
	'verbose': (bool, None)
	}

def plot_dist(
		df, variable, mode,
		by = None,
		by_mode = 'stacked', # segmentation mode
		
		alpha = 0.5,
		colors_reference = ['b','g','r','c','m','y','k'],
		figsize = None,
		fontsize = None,
		labels = None,
		labels_format = None,
		labels_padding = [0, 0],
		labels_threshold = 0.85,
		norm = False,

		bar_width = 0.8,
		
		hist_bins = 10,
		hist_ticklabels_format = '.2f',
		hist_grouped_offset = [None, None], # (x, y)
		hist_x_log_scale = False,#
		hist_average_line = False,#
		hist_average_line_kargs = {'linewidth':1, 'alpha':0.25, 'edgecolor':'black', 'color':'black'},

		external_fig_and_ax = None,
		dict_colors_of_variable_by = None,
		verbose = False,

		**bar_kargs
	
		) -> tuple[Figure, Axes]:
	'''
    Plot the distribution of a variable using bar plots or histograms, with support for category segmentation,
    normalization, and extensive customization options.

    This function is useful for visually exploring the frequency distribution of a variable, optionally segmented
    by a categorical column (`by`). It supports different layout modes such as stacked bars, grouped bars, or
    separated subplots.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing the data to be plotted.

    variable : str
        Name of the column to be plotted.

    mode : {'bar', 'hist'}
        Plotting mode:
        - 'bar' : for categorical variables (bar chart),
        - 'hist': for numeric variables (histogram).

    by : str or None, optional
        Name of the grouping column for segmentation (used to separate or color the distributions).

    by_mode : {'stacked', 'grouped', 'subploted'}, default='stacked'
        Layout style when grouping is applied:
        - 'stacked'   : stacked bars.
        - 'grouped'   : side-by-side grouped bars.
        - 'subploted' : one subplot per category.

    alpha : float, optional
        Transparency level of the bars (from 0 to 1).

    colors_reference : list or tuple, optional
        List of colors to assign to `by` categories (used if `dict_colors_of_variable_by` is not provided).

    figsize : list or tuple of length 2, optional
        Size of the figure in inches: `[width, height]`.

    fontsize : int or float, optional
        Global font size for the plot.

    labels : {None, 'top', 'center'}, optional
        If not None, adds value labels to the bars:
        - 'top'    : place above the bars.
        - 'center' : place inside the bars.

    labels_format : str, optional
        Format string for bar labels (e.g., '.0f', '.1%', etc.).

    labels_padding : list or tuple of length 2, default=[0, 0]
        Offset for labels in points: `[x_offset, y_offset]`.

    labels_threshold : float, optional
        Minimum proportion of overlap allowed for the label to remain visible.

    norm : bool, optional
        If True, normalize bar heights so they sum to 1. Useful for comparing distributions.

    bar_width : float, optional
        Width of the bars in `'bar'` mode (between 0 and 1).

    hist_bins : int, optional
        Number of bins for the histogram.

    hist_ticklabels_format : str, optional
        Format string for x-axis tick labels in histogram mode.

    hist_grouped_offset : list or tuple of 2 elements, optional
        Offset for each group in grouped histogram mode: `[x_offset, y_offset]`.

    hist_x_log_scale : bool, optional
        If True, applies log10 scale to the x-axis before plotting.

    hist_average_line : bool, optional
        If True, adds a smoothed KDE (kernel density estimate) curve over the histogram.

    hist_average_line_kargs : dict, optional
        Additional keyword arguments for the KDE curve (passed to `stackplot()`).

    external_fig_and_ax : None or tuple (Figure, Axes), optional
        If provided, uses the given Matplotlib `Figure` and `Axes` for plotting.

    dict_colors_of_variable_by : dict or None, optional
        Custom color mapping for each category in the `by` column.

    verbose : bool, optional
        If True, prints the min and max values of the `variable`.

    **bar_kargs : keyword arguments
        Additional arguments passed directly to `ax.bar()`.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created Matplotlib Figure object.

    ax : matplotlib.axes.Axes or numpy.ndarray of Axes
        The created Axes object(s). May be an array if `by_mode='subploted'`.

    Examples
    --------
	```python
	df = pd.DataFrame({'Category': ['A', 'B', 'A', 'C', 'B'], 'Value': [10, 20, 30, 40, 50]})
    plot_dist(df, variable='Category', mode='bar')
	```
	```python
	plot_dist(df, variable='Value', mode='hist', hist_bins=5)
	```
	```python
	plot_dist(df, variable='Category', mode='bar', by='Value', by_mode='grouped')
	```
	'''
	
	# validate external_fig_and_ax
	if external_fig_and_ax:
		fig, ax = external_fig_and_ax
		assert ( type(fig) == type(plt.figure()) ), 'index 0 of "external_fig_and_ax" are not a matplotlib.figure.Figure type'
		assert ( type(ax) == type(plt.axes()) ), 'index 1 of "external_fig _and_ax" are not a matplotlib.axes._axes.Axes type'

	#change the global font size
	if fontsize:
		original_fontsize = plt.rcParams['font.size']
		plt.rcParams['font.size'] = fontsize

	# Filter DataFrame "df"
	if by:
		if variable==by:
			df = df[[variable]].copy()
			by = by+'2'
			df[by] = df[variable]
		else:
			df = df[[variable, by]].copy()
	else:
		df = df[[variable]].copy()
	
	df.dropna(subset=[variable], inplace=True)
	x_range = [df[variable].min(), df[variable].max()]

	# Validate values for "hist" mode
	if mode=='hist':
		try:
			df[variable] = df[variable].astype(float)
		except ValueError:
			raise ValueError('The "variable" values are nor numeric for "hist" mode')

	# define unique values of "by". the ".value_counts()" method sort the unique values
	if by:
		by_valuecounts = df[by].value_counts()
		unique_by = list( by_valuecounts.index )

	# Define the list colors of categories of "by"
	colors = {}
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
		colors['all'] = colors_reference[0]


	# Create Matplotlib fig and axis
	if external_fig_and_ax:
		fig, ax = external_fig_and_ax
	else:
		if (by) and (by_mode=='subploted'):
			nrows = len(unique_by)
			figsize = [6.4, 2.*nrows] if figsize is None else figsize
			fig, ax = plt.subplots(ncols=1, nrows=nrows, figsize=figsize, sharex=True, sharey=True)
		else:
			figsize = [6.4, 4.8] if figsize is None else figsize
			fig, ax = plt.subplots(figsize=figsize)
	
	
	# 0 - "bar_coord" will store all the plot parameters.
	# "kargs" are kargs (ax.bar optional args) used for all plots.
	# "all" indicates the specific values without "by" segmentation. "x" is not specific, but is a mandatory argument
	bar_kargs = bar_kargs if bar_kargs else {'linewidth': .7, 'edgecolor': 'black'}
	bar_coord = {
		'kargs':{
			'tick_label': [],
			'width': [],
			'alpha': alpha,
			'align': [],
		},
		'all': {
			'x': [],
			'bottom': [],
			'height': [],
		}
	}


	# 1 - 1st: Define the general parameters (without "by")
	#     2nd: Define the "x_coordinates", "bottoms" and "height" of the bars for each "by_mode"
	if mode == 'bar':
		variable_valuecounts = df[variable].value_counts()
		unique_variable = list( variable_valuecounts.index )

		bar_coord['all']['x'] = np.arange(len(unique_variable))
		bar_coord['all']['bottom'] = [0]*len(unique_variable)
		bar_coord['all']['height'] = variable_valuecounts.values.tolist()

		bar_coord['kargs']['tick_label'] = unique_variable
		bar_coord['kargs']['width'] = bar_width
		bar_coord['kargs']['align'] = 'center'

		if by:
			if by_mode=='stacked':
				# Calculate specific parameters for the categories of "by" (bottom and height)
				next_bottom = [0]*len(unique_variable)
				for group in unique_by:
					bar_coord[group] = {}
					valuecounts_filtered = df.loc[ df[by]==group, variable ].value_counts()
					actual_height = [ valuecounts_filtered[x] if (x in valuecounts_filtered.index) else 0 for x in unique_variable]
					
					bar_coord[group]['x'] = bar_coord['all']['x']
					bar_coord[group]['bottom'] = next_bottom
					bar_coord[group]['height'] = actual_height
					next_bottom = np.add(next_bottom, actual_height)

			elif by_mode=='grouped':
				b = len(unique_by)
				sub_bar_width = bar_width/b
				cte = (bar_width*(1-b))/(2*b)
				###### EQUATION PROOF: ######
				# bar_width = w | sub_bar_width = sw
				# position of each sub-bar = f(x)
				# f(x) = j - w/2 + sw*i + sw/2 , for j = [0, 1, 2, ...] -> unique_variable index
				#                                    i = [0, 1, 2, ...] -> unique_by index
				# f(x) = j + sw*i + w*(1-b)/2b
				# f(x) = j + sw*i + cte
				for n_group, group in enumerate(unique_by):
					bar_coord[group] = {}
					# Apply the Equation for x sub-bars possitions
					bar_coord[group]['x'] = [ j + sub_bar_width*n_group + cte for j in bar_coord['all']['x'] ]
					# Calculate the "heigth"
					valuecounts_filtered = df.loc[ df[by]==group, variable ].value_counts()
					actual_height = [ valuecounts_filtered[x] if (x in valuecounts_filtered.index) else 0 for x in unique_variable]
					bar_coord[group]['height'] = actual_height

					bar_coord[group]['bottom'] = bar_coord['all']['bottom']
				# Change graphic kargs
				bar_coord['kargs']['width'] = sub_bar_width

			elif by_mode=='subploted':
				for group in unique_by:
					bar_coord[group] = {}
					bar_coord[group]['x'] = bar_coord['all']['x']
					bar_coord[group]['bottom'] = bar_coord['all']['bottom']
					# Calculate the height of each unique_variable
					valuecounts_filtered = df.loc[ df[by]==group, variable ].value_counts()
					actual_height = [ valuecounts_filtered[x] if (x in valuecounts_filtered.index) else 0 for x in unique_variable]
					bar_coord[group]['height'] = actual_height
					

	elif mode =='hist':

		if (hist_x_log_scale==False):
			hist_width = (x_range[1]-x_range[0])/hist_bins
		else:
			x_range = [ math.log10(x_range[0]), math.log10(x_range[1])]
			hist_width = (x_range[1]-x_range[0])/hist_bins
			df[variable] = np.log10(df[variable])
			# Converte tudo para log de forma que tudo que foi feito consiga ser aplicado
			# No final, mudar as configurações de relativar à estética do eixo
			
		bar_coord['all']['x'] = np.arange( x_range[0], x_range[1], hist_width ).tolist()
		bar_coord['all']['bottom'] = [0]*hist_bins
		
		# Calculate the frequencies/height
		bar_coord['all']['height'] = []
		for x_min in bar_coord['all']['x']:
			x_max = x_min + hist_width
			condition = np.all([df[variable]>=x_min, df[variable]<x_max], axis=0)
			bar_coord['all']['height'].append(np.sum(condition))
		# Add the rows where df[variable]>=x_max
		bar_coord['all']['height'][-1] += np.sum(df[variable]>=x_max)

		
		bar_coord['kargs']['width'] = hist_width
		bar_coord['kargs']['align'] = 'edge'

		if (hist_x_log_scale==False):
			bar_coord['kargs']['tick_label'] = [ ('{:'+hist_ticklabels_format+'}').format(i) for i in bar_coord['all']['x'] ]
		else:
			bar_coord['kargs']['tick_label'] = [ ('{:'+hist_ticklabels_format+'}').format(10**i) for i in bar_coord['all']['x'] ]

		if by:
			if by_mode=='stacked':
				# Calculate specific parameters for the categories of "by" (bottom and height)
				next_bottom = [0]*hist_bins
				for group in unique_by:
					df_filtered = df.loc[df[by]==group, [variable]]
					bar_coord[group] = {}

					# Calculate the frequencies/height
					actual_height = []
					for x_min in bar_coord['all']['x']:
						x_max = x_min + hist_width
						condition = np.all([df_filtered[variable]>=x_min, df_filtered[variable]<x_max], axis=0)
						actual_height.append(np.sum(condition))
					# Add the rows where df[variable]>=x_max
					actual_height[-1] += np.sum(df_filtered[variable]>=x_max)
					
					bar_coord[group]['x'] = bar_coord['all']['x']
					bar_coord[group]['bottom'] = next_bottom
					bar_coord[group]['height'] = actual_height
					next_bottom = np.add(next_bottom, actual_height)
			
			elif by_mode=='grouped':
				
				offset = hist_grouped_offset
				if all([offset[0] is None, offset[1] is None]):
					offset[0] = 0
					offset[1] = 0.9*max(bar_coord['all']['height'])
				
				for n_group, group in enumerate(unique_by):
					df_filtered = df.loc[df[by]==group, [variable]]
					bar_coord[group] = {}

					# Calculate the height of each unique_variable
					bar_coord[group]['height'] = []
					for x_min in bar_coord['all']['x']:
						x_max = x_min + hist_width
						condition = np.all([df_filtered[variable]>=x_min, df_filtered[variable]<x_max], axis=0)
						bar_coord[group]['height'].append(np.sum(condition))
					# Add the rows where df[variable]>=x_max
					bar_coord[group]['height'][-1] += np.sum(df_filtered[variable]>=x_max)

					#Define "x", "bottom" and "height" with offset
					bar_coord[group]['x'] 		= np.add( bar_coord['all']['x'], offset[0]*n_group)
					bar_coord[group]['bottom'] 	= np.add( bar_coord['all']['bottom'], offset[1]*n_group)
					# bar_coord[group]['height'] 	= np.add( bar_coord[group]['height'], offset[1]*n_group)


			
			elif by_mode=='subploted':
				for group in unique_by:
					df_filtered = df.loc[df[by]==group, [variable]]
					bar_coord[group] = {}
					
					# Calculate the height of each unique_variable
					bar_coord[group]['height'] = []
					for x_min in bar_coord['all']['x']:
						x_max = x_min + hist_width
						condition = np.all([df_filtered[variable]>=x_min, df_filtered[variable]<x_max], axis=0)
						bar_coord[group]['height'].append(np.sum(condition))
					# Add the rows where df[variable]>=x_max
					bar_coord[group]['height'][-1] += np.sum(df_filtered[variable]>=x_max)

					bar_coord[group]['x'] 		= bar_coord['all']['x']
					bar_coord[group]['bottom'] 	= bar_coord['all']['bottom']


	# 2 - Recalculate the bottoms and height if norm=True
	if norm==True:
		if by:
			for group in unique_by:
				bar_coord[group]['bottom'] = list(map(float, bar_coord[group]['bottom']))
				bar_coord[group]['height'] = list(map(float, bar_coord[group]['height']))
				aux_number_of_bars = hist_bins if mode=='hist' else len(unique_variable)
				for bin in range(aux_number_of_bars):
					denominator = bar_coord['all']['height'][bin]
					if denominator!=0:
						bar_coord[group]['bottom'][bin] = round( bar_coord[group]['bottom'][bin]/denominator, 6 )
						bar_coord[group]['height'][bin] = round( bar_coord[group]['height'][bin]/denominator, 6 )
					else:
						bar_coord[group]['bottom'][bin] = 0.
						bar_coord[group]['height'][bin] = 0.
			bar_coord['all']['height'] = [1]*len(unique_variable) if mode=='bar' else [1]*hist_bins
		else:
			print('"plot_dist" function: normalization not performed - "by_mode" is None')
	
	
	# 3 - Plot the graphics
	bars_obj = []
	if by:
		#by_mode="grouped": plot the graph in REVERSE ORDER so that the bars in group 0 are in front
		range_unique_by = enumerate(unique_by) if by_mode!='grouped' else reversed(list( enumerate(unique_by) ))
		for n_group, group in range_unique_by:
			graph = ax[n_group] if by_mode=='subploted' else ax
			aux_bars = graph.bar(x = bar_coord[group]['x'],
								height = bar_coord[group]['height'],
								bottom = bar_coord[group]['bottom'],
								color = colors[group],
								label = group,
								**bar_coord['kargs'],
								**bar_kargs
								)
			
			bars_obj = ( bars_obj + [list(aux_bars)] ) if by_mode!='grouped' else ( [list(aux_bars)] + bars_obj)
	else:
		aux_bars = ax.bar(x = bar_coord['all']['x'],
						height = bar_coord['all']['height'],
						bottom = bar_coord['all']['bottom'],
						color = colors['all'],
						label = 'all',
						**bar_coord['kargs'],
						**bar_kargs
						)
		bars_obj += [list(aux_bars)]

	# 3.1 - Add the last tick for mode="hist"
	if mode=='hist':
		if (hist_x_log_scale==False):
			one_tick_label = ('{:'+hist_ticklabels_format+'}').format(x_range[1])
		else:
			one_tick_label = ('{:'+hist_ticklabels_format+'}').format(10**x_range[1])

		_add_tick(
			ax[-1] if (by_mode=='subploted' and by) else ax, 
			'x', 
			x_range[1],
			one_tick_label)
	
	
	

	# 4 - Graphic adjustments and labels
	if labels_format is None:
		labels_format = '.0%' if norm==True else '.0f'

	subplots = ax if (by_mode=='subploted' and by) else [ax]
	last_graph = ax[-1] if (by_mode=='subploted' and by) else ax
	
	for n_axis_obj, axis_obj in enumerate(subplots):
		
		axis_obj.margins(0.1)
		axis_obj.set(ylabel='Frequency')
		axis_obj.legend()


		# 4.1 - Histogram average lines
		if (hist_average_line==True):
			# if (hist_x_log_scale == False):
			# Using gaussian_kde
			density = scipy.stats.gaussian_kde(df[variable].astype(np.float64))
			xlim = axis_obj.get_xlim()
			x = np.linspace(xlim[0], xlim[1], 1000)
			axis_obj.stackplot(x, density(x)*sum(bar_coord['all']['height'])*hist_width,
									# color='black',
									# alpha = 0.4,
									# linewidth = 0,
									**hist_average_line_kargs)
			axis_obj.set_xlim(xlim)


		# 4.2 - Bar labels
		if labels:
			if by:
				if by_mode=='stacked':

					if labels=='top':
						for x, height in zip(bar_coord['all']['x'], bar_coord['all']['height']):
							
							xy = (x, height) if mode=='bar' else ( x+hist_width/2, height )

							axis_obj.annotate(('{:'+labels_format+'}').format(height),
												xy = xy,
												xytext = np.add([0, 8], labels_padding),
												textcoords = "offset points",
												ha = 'center', va = 'center',
												rotation = 0)

					elif labels=='center':

						previous_y = [0]*len(unique_variable) if mode == 'bar' else [0]*hist_bins

						for group in unique_by:
							for x, height, p_y in zip(bar_coord[group]['x'], bar_coord[group]['height'], previous_y):
								
								y = p_y + height/2
								xy = (x, y) if mode=='bar' else ( x+hist_width/2, y )
								
								axis_obj.annotate(('{:'+labels_format+'}').format(height),
												xy=xy,
												xytext=np.add([0, 0], labels_padding),
												textcoords="offset points",
												ha='center', va='center',
												rotation=0)
							
							previous_y = np.add( previous_y, bar_coord[group]['height'])
						
				elif by_mode=='grouped':
					for n_group, group in enumerate(unique_by):
						for x, height in zip(bar_coord[group]['x'], bar_coord[group]['height']):
							
							y = height/2 if labels=='center' else height
							xytext = [0, 0] if labels=='center' else [0, 8]
							xy = (x, y) if mode=='bar' else ( x+hist_width/2, y+offset[1]*n_group )

							axis_obj.annotate(('{:'+labels_format+'}').format(height),
										xy=xy,
										xytext=np.add( xytext, labels_padding),
										textcoords="offset points",
										ha='center', va='center',
										rotation=0)
						
				elif by_mode=='subploted':
					group = unique_by[n_axis_obj]
					for x, height in zip(bar_coord[group]['x'], bar_coord[group]['height']):

						y = height/2 if labels=='center' else height
						xytext = [0, 0] if labels=='center' else [0, 8]
						xy = (x, y) if mode=='bar' else ( x+hist_width/2, y )

						axis_obj.annotate(('{:'+labels_format+'}').format(height),
									xy=xy,
									xytext = np.add( xytext, labels_padding),
									textcoords="offset points",
									ha='center', va='center',
									rotation=0)

			else:
				for x, height in zip(bar_coord['all']['x'], bar_coord['all']['height']):
					
					y = height/2 if labels=='center' else height
					xytext = [0, 0] if labels=='center' else [0, 8]
					xy = (x, y) if mode=='bar' else ( x+hist_width/2, y )
					
					axis_obj.annotate(('{:'+labels_format+'}').format(height),
										xy=xy,
										xytext=np.add( xytext, labels_padding),
										textcoords="offset points",
										ha='center', va='center',
										rotation=0)
			

			# 4.3 - Adjust annotations (axis_obj.texts) labels
			bars_obj_to_adjustment = np.ravel(bars_obj) if (by_mode=='grouped') else bars_obj[n_axis_obj]
			_adjust_obj_to_ref(
				fig, 
				list(axis_obj.texts),
				list(bars_obj_to_adjustment),
				'w',
				steps= ['try_rotate', 'decrease_fontsize']*3,
				threshold = labels_threshold,
				rotate_rate = 45
				)
				


			# 4.4 - Increase axis limits if labels are outside the axis
			axis_obj.margins(0.1)

			for bar_label in axis_obj.texts:
				for t in range(50):
					check = _check_if_label_outside(label = bar_label, ax = axis_obj, fig = fig)
					if check is None:
						break
					elif check == 'x':
						axis_obj.margins( x=0.05*(1+t) )
					elif check == 'y':
						axis_obj.margins( y=0.05*(1+t) )
			
			# 4.5 - Remove labels in a small space or move them up
			# OBS: Order to put the labels = 1° group -> 2° bars
			for n_bar, bar_label in enumerate(axis_obj.texts):
				
				if bar_label.get_text()=='0':
					bar_label.set_text('')
					continue
				
				if mode=='hist':
					n_group = n_bar//hist_bins + n_axis_obj # plus "n_axis_obj" for the case of "subplots"
					label_count = n_bar%hist_bins
				elif mode =='bar':
					n_group = n_bar//len(unique_variable) + n_axis_obj # plus "n_axis_obj" for the case of "subplots"
					label_count = n_bar%len(unique_variable)
					
				bar_obj_to_adjustment = bars_obj[n_group][label_count]
				move_rate_y = bar_coord[ unique_by[n_group] ][ 'height' ][ label_count ] if by else bar_coord[ 'all' ][ 'height' ][ label_count ]
				
				if (labels=='center'):
					# move up labels in a small space
					if (norm==False) and (by_mode!='stacked'):
						_adjust_obj_to_ref(
							fig,
							[bar_label],
							[bar_obj_to_adjustment],
							'h',
							steps=['move_until_no_overlaps'],
							move_rate = [ 0, 0.015*axis_obj.get_ylim()[1] ]
						)
					else:
						# remove labels in a small space
						_adjust_obj_to_ref(
						fig,
						[bar_label],
						[bar_obj_to_adjustment],
						'h',
						steps=['remove_label'],
						threshold = labels_threshold
						)
					
	
	
	# 5 - Adjust tick labels
	bars_obj_to_adjustment = bars_obj[0]
	_adjust_obj_to_ref(
		fig, 
		last_graph.get_xticklabels(),
		bars_obj_to_adjustment,
		'w',
		steps= ['try_rotate', 'decrease_fontsize']*3 + ['try_rotate', 'reset_fontsize', 'abbreviate_or_remove_tick_labels'],
		rotate_rate = 45,
		threshold = labels_threshold,
		tick_ax = last_graph
		)


	# 6 - Final adjustments

	last_graph.set(xlabel=variable)
	
	if verbose==True:
		print('min =', x_range[0])
		print('max =', x_range[1])

	#return fontsize to the original size
	if fontsize:
		plt.rcParams['font.size'] = original_fontsize

	plt.show()

	return fig, ax