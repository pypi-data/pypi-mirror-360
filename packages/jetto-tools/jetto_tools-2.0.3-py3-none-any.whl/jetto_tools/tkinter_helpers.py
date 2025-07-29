import logging
import os
from functools import wraps
from datetime import datetime, timedelta
import time
from collections import OrderedDict
import glob

logger = logging.getLogger('jetto_tools.tkinter_helpers')
logger.setLevel(logging.INFO)
try:
    import tkinter as tk
    from tkinter.font import Font
    from tkinter import ttk
except ImportError:
    logger.warning("Python module 'tkinter' not found. Submodule 'tkinter_helpers' needs it")
    raise

from IPython import embed

def fixed_map(style, option):
    """ Returns the style map for 'option'

    Fix for setting text colour for Tkinter 8.6.9
    From: https://core.tcl.tk/tk/info/509cafafae

    Returns the style map for 'option' with any styles starting with
    ('!disabled', '!selected', ...) filtered out.
    From https://bugs.python.org/issue36468

    style.map() returns an empty list for missing options, so this
    should be future-safe.
    """

    return [elm for elm in style.map('Treeview', query_opt=option) if
      elm[:2] != ('!disabled', '!selected')]

class throttle(object):
    """ Decorator to prevent function being called too often

    Decorator that prevents a function from being called more than once every
    time period.
    To create a function that cannot be called more than once a minute:
        @throttle(minutes=1)
        def my_fun():
            pass
    from https://gist.github.com/ChrisTM/5834503
    """
    def __init__(self, microseconds=0, milliseconds=0, seconds=0, minutes=0, hours=0):
        self.throttle_period = timedelta(
            microseconds=microseconds, milliseconds=milliseconds, seconds=seconds, minutes=minutes, hours=hours
        )
        self.time_of_last_call = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return fn(*args, **kwargs)

        return wrapper

def _get_non_root_parent(tree, field, verbosity=0):
    """ Get the last non-root parent of a field in a `ttk.Treeview`

    Traverses a field of the `ttk.Treeview` until the last
    non root (non '') parent is reached.

    Args:
        tree: ttk.Treeview instance to traverse
        field: Fieldname to find parent from

    Kwargs:
        verbosity: Debug level. Default 0

    Returns:
        String containing the last non-root parent
    """
    parent = tree.parent(field)
    if verbosity >= 1:
        print(f'parent of "{field}" is "{parent}"')
    if parent != '':
        potential_parent = _get_non_root_parent(tree, parent)
        if verbosity >= 1:
            print(f'"{parent}" has potential_parent "{potential_parent}"')
        if parent == potential_parent:
            if verbosity >= 1:
                print(f'no use going deeper, "{potential_parent}"')
            return potential_parent
    else:
        if verbosity >= 1:
            print(f'This seems to be root, returning field iself: "{field}"')
        return field

def _find_recursive_tree(tree, field, results=None, item=''):
    """ find a field in a `ttk.Treeview`

    Recursively traverses the tree (depth-first) until the specified
    field is found.

    Args:
        tree: ttk.Treeview instance to traverse
        field: Fieldname to find in tree

    Kwargs:
        results: Dict with the result; used to pass results between calls
        item: Item to start traversing from

    Returns:
        results: Dict with the result.
                 Keys the name of the field, values the value of the field
    """
    if results is None:
        results = OrderedDict()
    children = tree.get_children(item)
    #index = [item]
    for child in children:
        text = tree.item(child, 'text')
        if text == field:
            value = tree.item(child)['values'][0]
            results[value] = child
        _find_recursive_tree(tree, field, results=results, item=child) # Use the function for all the children, their children, and so on..
    return results


class SearchableComboBox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This is a bit wonky, have to call tkinter primitives directly:
        # Taken from https://stackoverflow.com/questions/53848622/how-to-bind-keypress-event-for-combobox-drop-out-menu-in-tkinter-python-3-7
        pd = self.tk.call('ttk::combobox::PopdownWindow', self) #get popdownWindow reference
        lb = self.lb = pd + '.f.l' #get popdown listbox

        self._bind(('bind', lb), '<FocusIn>', self._set_focus, '+') # Bind when listbox opens
        self._bind(('bind', lb), '<FocusIn>', self._bind_search_to_box, '+') # Bind when listbox opens
        self._bind(('bind', lb), '<FocusOut>', self._unbind_search_from_box, '+')# Bind when listbox closes
        self._set_dropdown_font()

        self.configure(font=self._get_dropdown_font())

        self.buffer = []
        self.wait_time = 500 # ms
        self.short_wait_time = 200 # ms
        self.last_after = None

    def _set_dropdown_font(self, font=None):
        """ Set font of dropdown menu

        Defaults to monospaced font
        """
        # Hacky hacky, seems setting "TkFixedFont" does not work on all platforms
        if font is None:
            font = Font(font='TkFixedFont')
        elif isinstance(font, str):
            font = Font(font=font)
        font_spec = '"{!s}" {!s}'.format(font['family'], font['size'])
        self.tk.call(self.lb, 'configure', '-font', font_spec)

    def _get_dropdown_font(self):
        font_spec = self.tk.call(self.lb, 'configure', '-font')[-1]
        font = Font(font=font_spec)
        return font

    def set_combo_width_to_values(self):
        values = self['values']
        if len(values) == 0:
            # No values defined yet, skipping
            return
        font = self._get_dropdown_font()
        long = max(values, key=len)
        width = max(0,font.measure(long.strip() + '0') - self.winfo_width()) # Width in pixels
        self.config(width=len(long) + 1) #width in characters

    def _bind_search_to_box(self, event):
        self.bind_all('<KeyPress>', self._press_key, '+')

    def _unbind_search_from_box(self, event):
        self.unbind_all('<KeyPress>')

    def _press_key(self, event):
        # If an alphanumerical character is pressed, append it to buffer
        self.buffer.append(event.char)
        if event.char.isalnum():
            if len(self.buffer) >= 2 and all(char == event.char for char in self.buffer):
                # Double tap, do not wait very long for next keypress
                # Do not do the normal routine
                if self.last_after is not None:
                    self.after_cancel(self.last_after)
                # Immediately jump one character for each char buffer and clear it
                for char in self.buffer:
                    search_string = char.upper()
                    self._set_focus_by_search_string(search_string)
                    del self.buffer[0]
                self.last_after = self.after(self.short_wait_time, self._key_event, event)
            else:
                # Cancel the last triggered event to trigger _key_event after last key
                # is not pressed for a while
                if self.last_after is not None:
                    self.after_cancel(self.last_after)
                # Trigger key event after a while
                self.last_after = self.after(self.wait_time, self._key_event, event)

    def _set_focus(self, event):
        current = self.get()
        self._set_focus_by_search_string(current)

    def _set_focus_by_search_string(self, search_string):
        values = self['values']
        cur_idx = self.current() # Current selected index
        target = None
        if cur_idx >= 0:
            # Try to select next one
            for ii, candidate in enumerate(values[cur_idx+1:], cur_idx+1):
                if candidate.upper().startswith(search_string):
                    target = (ii, candidate)
                    break

        if target is None:
            # If there is no next one, search before current selection
            for ii, candidate in enumerate(values):
                if candidate.upper().startswith(search_string):
                    target = (ii, candidate)
                    break

        if target is not None:
            # https://www.tcl.tk/man/tcl/TkCmd/listbox.htm
            # Clear the Listbox selection; the highlighted element
            self.tk.call(self.lb, 'selection', 'clear', 0, len(values))
            # Scroll Listbox until candidate is visible
            self.tk.call(self.lb, 'see', target[0])
            # Highlight candidate in Listbox
            self.tk.call(self.lb, 'selection', 'set', target[0])
            self.tk.call(self.lb, 'activate', target[0])
            # Select candidate in Entry
            self.current(target[0])

    def _key_event(self, event):
        #print('Buffer', self.buffer)
        #print('Selected', self.tk.call(self.lb, 'curselection'))
        # Search case insensitive
        search_string = ''.join([char.upper() for char in self.buffer])
        self._set_focus_by_search_string(search_string)
        # Clear buffer
        del self.buffer[:]
        self.last_after = None


class _tkBaseVar():
    """ Dummy Tk string
    """
    def __init__(self, *args, headless=False, **kwargs):
        self._variable = None
        self.name = kwargs.pop('name', None)
        self.value = kwargs.pop('value', None)
        self.master = None

    def get(self):
        if self._variable is not None:
            val = self._variable.get()
        else:
            val = self.value
        return val

    def set(self, value):
        if self._variable is not None:
            self._variable.set(value)
        else:
            self.value = value

class _tkDoubleVar(_tkBaseVar):
    """ Dummy Tk double
    """
    def __init__(self, *args, **kwargs):
        headless = kwargs.pop('headless', None)
        super().__init__(*args, headless=headless, **kwargs)
        if not headless:
            self._variable = tk.DoubleVar(**kwargs)

class _tkStringVar(_tkBaseVar):
    """ Dummy Tk string
    """

    def __init__(self, *args, **kwargs):
        headless = kwargs.pop('headless', None)
        super().__init__(*args, headless=headless, **kwargs)
        if not headless:
            self._variable = tk.StringVar(**kwargs)

def next_path(path_pattern, search_path=None):
    """ Finds the next free path in an sequentially named list of files

    Adapted from https://stackoverflow.com/a/47087513/3613853
    e.g. path_pattern = 'file-%s.txt':

    file-1.txt
    file-2.txt
    file-3.txt

    Runs in log(n) time where n is the number of existing files in sequence
    """
    i = 1
    if search_path is not None:
        path_pattern = os.path.join(search_path, path_pattern)

    # First do an exponential search
    while any(os.path.exists(path) for path in glob.glob(path_pattern % i)):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if any(os.path.exists(path) for path in glob.glob(path_pattern % c)) else (a, c)

    return path_pattern % b
