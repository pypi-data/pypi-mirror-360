import numpy as np
import textwrap
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from ._plot_text import _plot_text
from ._plot_bboxes import _plot_bboxes

from .._input_function_validation import _input_function_validation


def _check_if_obj_is_large(
	fig:object,

	obj_list:list,
	ref_list:list,

	dimension:str, # w=width or h=height
	threshold:float = 0.8,

	_plot_ref = False,
	_plot_obj = False,

	) -> bool :
	
	# Force to draw the fig
	fig.canvas.draw()
	renderer = fig.canvas.get_renderer()

	# get_window_extent() -> return the labels bounding box (bbox)
	bboxes_obj = [obj.get_window_extent(renderer) for obj in obj_list] 
	bboxes_ref = [ref.get_window_extent(renderer) for ref in ref_list] 
	
	if _plot_obj==True: _plot_bboxes(bboxes_obj, fig)
	if _plot_ref==True: _plot_bboxes(bboxes_ref, fig)
	

	if bboxes_obj and bboxes_ref:
		if dimension=='w':
			total_obj_dim = sum(obj.width for obj in bboxes_obj)
			total_ref_dim = sum(b.width for b in bboxes_ref)
		elif dimension=='h':
			total_obj_dim = sum(obj.height for obj in bboxes_obj)
			total_ref_dim = sum(ref.height for ref in bboxes_ref)
		
		if total_obj_dim > total_ref_dim*threshold:
			return True
		else: 
			return False

def _check_if_obj_overlaps_ref(
	fig:object,
    obj_list:list,
    ref_list:list,
	
	_plot_obj:bool = False,
	_plot_ref:bool = False,

    ) -> bool:

    # Force to draw the fig
	fig.canvas.draw()
	renderer = fig.canvas.get_renderer()

	# get_window_extent() -> return the labels bounding box (bbox)
	bboxes_obj = [obj.get_window_extent(renderer) for obj in obj_list]
	bboxes_ref = [ref.get_window_extent(renderer) for ref in ref_list] 
	
	if _plot_obj==True: _plot_bboxes(bboxes_obj, fig)
	if _plot_ref==True: _plot_bboxes(bboxes_ref, fig)

	for obj in bboxes_obj:
		for ref in bboxes_ref:
			if obj.overlaps(ref):
				return True
			else:
				continue
	
	return False






_input_val_dict = {
	'fig' : ( Figure, None ),
	'obj_list' : ( list, None ),
	'ref_list' : ( list, None ),
	'dimension' : ( str, 'pattern', ['w', 'h'] ),
	'steps' : ( list, None ),
	
	'threshold' : ( (float, int), 'range', [0, np.inf]),
	'rotate_max' : ( (float, int), 'range', [0, np.inf]),
	'rotate_rate' : ( (float, int), 'range', [0, np.inf]),
	
	'fontsize_max' : ( (float, int), 'range', [0, np.inf]),
	'fontsize_rate' : ( (float, int), 'range', [0, np.inf]),
	
	'abbreviate_list' : ( (list, tuple), None),
	'tick_ax' : ( (None.__class__, Axes), None),
	
	'move_rate' : ( (list, tuple), 'length', 2),

	'wrap_rate' : ( (int), 'range', [0, np.inf]),
	'wrap_maxlines' : ( (int), 'range', [0, np.inf]),
	
	'_plot_ref' : ( bool, None),
	'_plot_obj' : ( bool, None),
	
	
}

@_input_function_validation(_input_val_dict)
def _adjust_obj_to_ref(
		fig:object,
		obj_list:list,
		ref_list:list,
		dimension:str, # w=width or h=height
		steps:list,

		threshold:float = 0.8,
		rotate_max:float = 90,
		rotate_rate:float = 5,

		fontsize_max:float = 7,
		fontsize_rate:float = 0.9,

		abbreviate_list:list = ['letters'],
		tick_ax:Axes = None,

		move_rate:tuple = (None, None),

		wrap_rate = 2,
		wrap_maxlines = 3,

		_plot_ref:bool = False,
		_plot_obj:bool = False,

		) -> None:
	"""
	Adjust the visual layout of matplotlib text-like objects to fit within a reference area.

	This utility attempts to avoid overlaps or excessive dimensions by applying a series of
	predefined correction steps (`steps`). It is commonly used to fix overlapping labels
	or text elements in matplotlib plots.

	Parameters:
	----------
	fig : matplotlib.figure.Figure
		The figure object where the elements belong. It is used to compute bounding boxes.

	obj_list : list
		List of matplotlib objects to adjust (e.g., tick labels, titles, manually added texts).
		Each object must support `.get_window_extent()` and other adjustment methods (e.g. rotation, font size, etc.).

	ref_list : list
		List of reference objects used to determine the allowed space for `obj_list`. It can receive ".get_window_extent()" method. Ex.: `[ax]`

	dimension : str
		Target dimension to consider for overflow detection. `'w'` for width or `'h'` for height.

	steps : list of str
		Sequence of correction strategies to apply. Options include:
			- 'try_rotate': Rotate text incrementally. Has "get_rotation()" and "set_rotation()" methods;
			- 'decrease_fontsize': Scale down font size. Has "get_fontsize()" and "set_fontsize()" methods;
			- 'reset_fontsize': Restore original font size. Has "set_fontsize()" method;
			- 'remove_label': Remove all labels/texts. Has "set_text()" method;
			- 'abbreviate_or_remove_tick_labels': Replace tick labels with abbreviated symbols. Is a "ax.get_xticklabels()" or "ax.get_yticklabels()" matplotlib object. works only if the ticklabels obey the common position for their respective axes. (x, 0) for the x_axis and (0, y) for the y_axis;
			- 'abbreviate_or_remove': Replace text content with abbreviations or remove them. Has ".get_text()", "set_text()" and ".get_position()" method;
			- 'move_until_no_overlaps': Move objects until no overlap is detected. Has ".set_position()" method;
			- 'wrap_until_fit': Wrap long text into multiple lines. Has ".get_text()" and ".set_text()" methods.
		
		Examples:
	```
	Ex: 
	list(text_list) = [Text(), Text(), Text(), ...]
	list(ax.texts), ax.get_xticklabels()
	```

	threshold : float, default=0.8
		Maximum allowed fraction of occupied space relative to `ref_list` before applying adjustments.


	Returns:
	-------
	None
		The function modifies `obj_list` elements in-place to fit within the reference space.

	Examples
	--------
	```python
	fig, ax = plt.subplots()
	bars = ax.bar(['Very very long label A', 'Extremely long label B'], [3, 5])
	fig.canvas.draw()

	ticklabels = ax.get_xticklabels()
	ref_bboxes = [bar.get_window_extent(fig.canvas.get_renderer()) for bar in bars]
	```

	```python
	# Example 1: Try to rotate or shrink tick labels to fit within the bars
	_adjust_obj_to_ref(fig, ticklabels, ref_bboxes, dimension='w',
			steps=['try_rotate', 'decrease_fontsize'], threshold=0.9)
	```
	```python
	# Example 2: If nothing works, abbreviate or remove labels
	_adjust_obj_to_ref(fig, ticklabels, ref_bboxes, dimension='w',
			steps=['abbreviate_or_remove_tick_labels'], abbreviate_list=['A', 'B'], tick_ax=ax)
	```
	```python
	# Example 3: Wrap text titles or annotations that are too wide
	texts = [ax.text(0.5, 0.95, 'Some excessively long title string', ha='center', transform=ax.transAxes)]
	_adjust_obj_to_ref(fig, texts, [ax], dimension='w',
			steps=['wrap_until_fit'], wrap_rate=3, wrap_maxlines=3)
	```
	"""

	# Validade Steps
	adjust_modes = [ 
		'try_rotate', 
		'decrease_fontsize',
		'reset_fontsize',
		'remove_label',
		'abbreviate_or_remove_tick_labels', 
		'abbreviate_or_remove',
		'move_until_no_overlaps',
		'wrap_until_fit'
		]
	for step in steps:
		assert step in adjust_modes, f'"{step}" value in "steps" is outside of range "{adjust_modes}"'


	kargs_check_if_obj_is_large = {'fig':fig, 'obj_list':obj_list, 'ref_list':ref_list,
								'dimension':dimension, 'threshold':threshold,
								'_plot_ref':_plot_ref, '_plot_obj':_plot_obj}

	kargs_check_if_obj_overlaps_ref = {'fig':fig, 'obj_list':obj_list, 'ref_list':ref_list,
										'_plot_ref':_plot_ref, '_plot_obj':_plot_obj}

	# Check if the sum of the objects dimensions is really large
	
	if not(_check_if_obj_is_large(**kargs_check_if_obj_is_large)) and not('move_until_no_overlaps' in steps): return
	

	if 'try_rotate' in steps:
		original_rotation = [ obj_list[i].get_rotation() for i in range(len(obj_list)) ]
	if 'reset_fontsize' in steps:
		original_fontsize = [ obj_list[i].get_fontsize() for i in range(len(obj_list)) ]

	for step in steps:

		if step=='try_rotate':
			trials = rotate_max//rotate_rate
			for _ in range(trials):
				for obj in obj_list:
					obj.set_rotation( obj.get_rotation() + rotate_rate )
				if not(_check_if_obj_is_large(**kargs_check_if_obj_is_large)): return

			if _check_if_obj_is_large(**kargs_check_if_obj_is_large):
				for n_obj, obj in enumerate(obj_list):
					obj.set_rotation( original_rotation[n_obj] )
		
		elif step=='decrease_fontsize':
			current_size = np.array( [obj_list[i].get_fontsize() for i in range(len(obj_list))] )
			if all(current_size < fontsize_max):
				print(f'"_adjust_obj_to_ref" function: scale down not performed - font size below allowed "{fontsize_max}"')
				continue
			for obj in obj_list:
				obj.set_fontsize( obj.get_fontsize() * fontsize_rate)
			if not(_check_if_obj_is_large(**kargs_check_if_obj_is_large)): return
		
		elif step=='reset_fontsize':
			for n_obj, obj in enumerate(obj_list):
				obj.set_fontsize( original_fontsize[n_obj] )
		
		elif step=='remove_label':
			for obj in obj_list:
				obj.set_text( '' )

		elif step=='abbreviate_or_remove':
			labels = [text.get_text() for text in obj_list]
			if abbreviate_list==['letters']:
				# generate abbreviations (letters) for the labels
				symbols = [chr(i) for i in range(ord('A'), ord('Z')+1)]
				abbreviations = ( symbols * ( len(labels)//len(symbols) + 1 ) )[:len(labels)]
			else:
				abbreviations = ( abbreviate_list * ( len(labels)//len(abbreviate_list) + 1 ) )[:len(labels)]
			legend = dict(zip(labels, abbreviations))

			for text in obj_list:
				text.set_text( legend[text.get_text()] )
			if _check_if_obj_is_large(**kargs_check_if_obj_is_large):
				for text in obj_list:
					text.set_text( '' )
					return
			
			# Put a legend with abreviations
			textlegend = f'legend:\n\n'
			for k,v in legend.items():
				textlegend += f'{v} = {k}\n'
			fig_text, _ = _plot_text(textlegend, _fontsize=10)
			return

		elif step=='abbreviate_or_remove_tick_labels':
			assert tick_ax is not None, 'The step "abbreviate_or_remove_tick_labels" needs a value for "tick_ax" (matplotlib.axes._axes.Axes)'

			labels = [label.get_text() for label in obj_list]
			if abbreviate_list==['letters']:
				# generate abbreviations (letters) for the labels
				symbols = [chr(i) for i in range(ord('A'), ord('Z')+1)]
				abbreviations = ( symbols * ( len(labels)//len(symbols) + 1 ) )[:len(labels)]
			else:
				abbreviations = ( abbreviate_list * ( len(labels)//len(abbreviate_list) + 1 ) )[:len(labels)]
			legend = dict(zip(labels, abbreviations))
			
			positions = [label.get_position() for label in obj_list]
			
			check_if_x_is_zero = all([pos[0]==0 for pos in positions]) 
			check_if_y_is_zero = all([pos[1]==0 for pos in positions])

			if check_if_x_is_zero and not(check_if_y_is_zero):
				y_positions = [pos[1] for pos in positions]
				tick_ax.set_yticks(y_positions)
				tick_ax.set_yticklabels(legend.values())
				if _check_if_obj_is_large(**kargs_check_if_obj_is_large):
					tick_ax.set_yticklabels([])
					return
			elif check_if_y_is_zero and not(check_if_x_is_zero):
				x_positions = [pos[0] for pos in positions]
				tick_ax.set_xticks(x_positions)
				tick_ax.set_xticklabels(legend.values())
				if _check_if_obj_is_large(**kargs_check_if_obj_is_large):
					tick_ax.set_xticklabels([])
					return
			else:
				print(f'"_adjust_obj_to_ref" function: abbreviate_or_remove_tick_labels step not performed - It was not possible to estimate whether the labels are on the x or y axis with the positions "{positions}"')
				continue

			# Put a legend with abreviations
			text = f'legend:\n\n'
			for k,v in legend.items():
				text += f'{v} = {k}\n'
			fig_text, _ = _plot_text(text, _fontsize=10)
			return
		
		elif step=='move_until_no_overlaps':
			
			check = (move_rate[0] is not None) and (move_rate[1] is not None)
			assert check, '"move_rate" needs a value for (x, y)'
			
			for _ in range(10):
				if _check_if_obj_overlaps_ref(**kargs_check_if_obj_overlaps_ref):
					for obj in obj_list:
						obj.set_position( np.add(obj.get_position(), move_rate) )
				else:
					return
		
		elif step=='wrap_until_fit':
			max_labels_width = max([len(text.get_text()) for text in obj_list])
			textwidth = max_labels_width
			original_text = [obj.get_text() for obj in obj_list]
			for _ in range(50):
				textwidth -= wrap_rate
				if textwidth<=0: return
				for obj, text in zip(obj_list, original_text):
					wrapped = textwrap.wrap(text, width=textwidth, max_lines=wrap_maxlines, placeholder='')
					obj.set_text('\n'.join(wrapped))
				
				if not( _check_if_obj_is_large(**kargs_check_if_obj_is_large) ): return

					


