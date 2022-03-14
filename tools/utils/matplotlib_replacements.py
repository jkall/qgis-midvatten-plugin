# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the place to store the replacements/adjustments made to the matplotlib code
 NOTE - if using this file, it has to be imported by midvatten_plugin.py
                             -------------------
        begin                : 2011-10-18
        copyright            : (C) 2011 by joskal
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import matplotlib as mpl
import six

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg as NavigationToolbar

from matplotlib import cbook, cm, colors as mcolors, markers, image as mimage
from matplotlib.backends.qt_compat import QtGui
from matplotlib.backends.qt_editor import _formlayout
from matplotlib.dates import DateConverter, num2date


from matplotlib import pyplot as plt
from matplotlib import rcsetup
from qgis.PyQt.QtCore import QCoreApplication, Qt, pyqtSignal, QObject
import types

from midvatten.tools.utils.common_utils import returnunicode as ru
import midvatten.definitions.midvatten_defs as defs


def replace_matplotlib_style_core_update_nested_dict():
        def update_nested_dict(main_dict, new_dict):
            """
            FUNCTION REPLACED BY MIDVATTEN

            REPLACEMENT PURPOSE:
            * Replaces the memory stored style completely instead of just updating the changed key-value pairs.

            """
            # update named styles specified by user
            #print("Uses replacement for update_nested_dict")
            for name, rc_dict in six.iteritems(new_dict):
                main_dict[name] = rc_dict
                #if name in main_dict:
                #    main_dict[name] = rc_dict
                #else:
                #    main_dict[name] = rc_dict
            return main_dict
        mpl.style.core.update_nested_dict = update_nested_dict

def replace_matplotlib_backends_backend_qt5agg_NavigationToolbar2QT_functions():
    """
    REPLACES matplotlib.backends.backend_qt5agg.NavigationToolbar2QT functions:
     'edit_parameters', 'configure_subplots', 'save_figure'

    PURPOSE: Using those buttons now applies the matplotlib style stored in NavigationToolbar2QT self.midv_use_style.

    :return:
    """

    def apply_func(old_func):
        def use_style_context(self, *args, **kwargs):
            old_f = getattr(self, old_func)
            if hasattr(self, 'midv_use_style'):
                mpl.style.reload_library()
                with plt.style.context(self.midv_use_style):
                    old_f(*args, **kwargs)
            else:
                old_f(*args, **kwargs)

        return use_style_context
    for old_func in ['edit_parameters', 'configure_subplots', 'save_figure']:
        new_name = '_midv_old_{}'.format(old_func)
        setattr(NavigationToolbar, new_name, getattr(NavigationToolbar, old_func))
        setattr(NavigationToolbar, old_func, apply_func(new_name))

    _funcs = ['edit_parameters', 'configure_subplots', 'save_figure']
    for old_func in _funcs:
        new_name = '_midv_old_{}'.format(old_func)
        if hasattr(NavigationToolbar, new_name):
            continue
        else:
            setattr(NavigationToolbar, new_name, getattr(NavigationToolbar, old_func))
            setattr(NavigationToolbar, old_func, apply_func(new_name))


def add_to_rc_defaultParams():
    """
    Adds parameters to rcParams

    :return:
    """
    params_to_add = {'axes.midv_line_cycle': [defs.midv_line_cycle(), rcsetup.validate_cycler],
                     'axes.midv_marker_cycle': [defs.midv_marker_cycle(), rcsetup.validate_cycler],
                     'legend.midv_ncol': [1, rcsetup.validate_int]}

    rcsetup.defaultParams.update(params_to_add)
    mpl.RcParams.validate = dict((key, converter) for key, (default, converter) in
                    six.iteritems(rcsetup.defaultParams))
    mpl.rcParamsDefault.update({k: v[0] for k, v in params_to_add.items()})
    mpl.rcdefaults()


def perform_all_replacements():
    add_to_rc_defaultParams()
    replace_matplotlib_style_core_update_nested_dict()
    replace_matplotlib_backends_backend_qt5agg_NavigationToolbar2QT_functions()
    mpl.backends.qt_editor.figureoptions.figure_edit = figure_edit



def replace_matplotlib_backends_backend_qt5agg_NavigationToolbar2QT_set_message_xylimits(mpltoolbar):
    def set_message(self, s):
        ax = self.canvas.figure.get_axes()[0]
        xlim = (round(ax.get_xlim()[0], 3), round(ax.get_xlim()[1], 3))
        ylim = (round(ax.get_ylim()[0], 3), round(ax.get_ylim()[1], 3))
        msg = ru(QCoreApplication.translate(
            'replace_matplotlib_backends_backend_qt5agg_NavigationToolbar2QT_set_message_xylimits',
            'xlim %s ylim %s')) % (str(xlim), str(ylim))

        if not s:
            s = msg
        else:
            s = ', '.join([s, msg])

        self.message.emit(s)
        if self.coordinates:
            self.locLabel.setText(s)

    mpltoolbar.set_message = types.MethodType(set_message, mpltoolbar)
    mpltoolbar.locLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)


class NavigationToolbarWithSignal(NavigationToolbar, QObject):
    edit_parameters_used = pyqtSignal()

    def __init__(self, *args, **kwargs):
        NavigationToolbar.__init__(self, *args, **kwargs)

    def edit_parameters(self, *args, **kwargs):
        super(NavigationToolbarWithSignal, self).edit_parameters(*args, **kwargs)
        self.edit_parameters_used.emit()


LINESTYLES = {'-': 'Solid',
              '--': 'Dashed',
              '-.': 'DashDot',
              ':': 'Dotted',
              'None': 'None',
              }

DRAWSTYLES = {
    'default': 'Default',
    'steps-pre': 'Steps (Pre)', 'steps': 'Steps (Pre)',
    'steps-mid': 'Steps (Mid)',
    'steps-post': 'Steps (Post)'}

MARKERS = markers.MarkerStyle.markers

def figure_edit(axes, parent=None):
    """Edit matplotlib figure options"""
    sep = (None, None)  # separator

    # Get / General
    def convert_limits(lim, converter):
        """Convert axis limits for correct input editors."""
        if isinstance(converter, DateConverter):
            return map(num2date, lim)
        # Cast to builtin floats as they have nicer reprs.
        return map(float, lim)

    xconverter = axes.xaxis.converter
    xmin, xmax = convert_limits(axes.get_xlim(), xconverter)
    yconverter = axes.yaxis.converter
    ymin, ymax = convert_limits(axes.get_ylim(), yconverter)
    general = [('Title', axes.get_title()),
               sep,
               (None, "<b>X-Axis</b>"),
               ('Left', xmin), ('Right', xmax),
               ('Label', axes.get_xlabel()),
               ('Scale', [axes.get_xscale(),
                          'linear', 'log', 'symlog', 'logit']),
               sep,
               (None, "<b>Y-Axis</b>"),
               ('Bottom', ymin), ('Top', ymax),
               ('Label', axes.get_ylabel()),
               ('Scale', [axes.get_yscale(),
                          'linear', 'log', 'symlog', 'logit']),
               sep,
               ('(Re-)Generate automatic legend', False),
               ]

    # Save the unit data
    xunits = axes.xaxis.get_units()
    yunits = axes.yaxis.get_units()

    # Get / Curves
    labeled_lines = []
    for line in axes.get_lines():
        label = line.get_label()
        if label == '_nolegend_':
            continue
        labeled_lines.append((label, line))
    curves = []

    def prepare_data(d, init):
        """
        Prepare entry for FormLayout.

        *d* is a mapping of shorthands to style names (a single style may
        have multiple shorthands, in particular the shorthands `None`,
        `"None"`, `"none"` and `""` are synonyms); *init* is one shorthand
        of the initial style.

        This function returns an list suitable for initializing a
        FormLayout combobox, namely `[initial_name, (shorthand,
        style_name), (shorthand, style_name), ...]`.
        """
        if init not in d:
            d = {**d, init: str(init)}
        # Drop duplicate shorthands from dict (by overwriting them during
        # the dict comprehension).
        name2short = {name: short for short, name in d.items()}
        # Convert back to {shorthand: name}.
        short2name = {short: name for name, short in name2short.items()}
        # Find the kept shorthand for the style specified by init.
        canonical_init = name2short[d[init]]
        # Sort by representation and prepend the initial value.
        return ([canonical_init] +
                sorted(short2name.items(),
                       key=lambda short_and_name: short_and_name[1]))

    for label, line in labeled_lines:
        color = mcolors.to_hex(
            mcolors.to_rgba(line.get_color(), line.get_alpha()),
            keep_alpha=True)
        ec = mcolors.to_hex(
            mcolors.to_rgba(line.get_markeredgecolor(), line.get_alpha()),
            keep_alpha=True)
        fc = mcolors.to_hex(
            mcolors.to_rgba(line.get_markerfacecolor(), line.get_alpha()),
            keep_alpha=True)
        curvedata = [
            ('Label', label),
            sep,
            (None, '<b>Line</b>'),
            ('Line style', prepare_data(LINESTYLES, line.get_linestyle())),
            ('Draw style', prepare_data(DRAWSTYLES, line.get_drawstyle())),
            ('Width', line.get_linewidth()),
            ('Color (RGBA)', color),
            sep,
            (None, '<b>Marker</b>'),
            ('Style', prepare_data(MARKERS, line.get_marker())),
            ('Size', line.get_markersize()),
            ('Face color (RGBA)', fc),
            ('Edge color (RGBA)', ec)]
        curves.append([curvedata, label, ""])
    # Is there a curve displayed?
    has_curve = bool(curves)

    # Get ScalarMappables.
    labeled_mappables = []
    for mappable in [*axes.images, *axes.collections]:
        label = mappable.get_label()
        if label == '_nolegend_' or mappable.get_array() is None:
            continue
        labeled_mappables.append((label, mappable))
    mappables = []
    cmaps = [(cmap, name) for name, cmap in sorted(cm._cmap_registry.items())]
    for label, mappable in labeled_mappables:
        cmap = mappable.get_cmap()
        if cmap not in cm._cmap_registry.values():
            cmaps = [(cmap, cmap.name), *cmaps]
        low, high = mappable.get_clim()
        mappabledata = [
            ('Label', label),
            ('Colormap', [cmap.name] + cmaps),
            ('Min. value', low),
            ('Max. value', high),
        ]
        if hasattr(mappable, "get_interpolation"):  # Images.
            interpolations = [
                (name, name) for name in sorted(mimage.interpolations_names)]
            mappabledata.append((
                'Interpolation',
                [mappable.get_interpolation(), *interpolations]))
        mappables.append([mappabledata, label, ""])
    # Is there a scalarmappable displayed?
    has_sm = bool(mappables)

    datalist = [(general, "Axes", "")]
    if curves:
        datalist.append((curves, "Curves", ""))
    if mappables:
        datalist.append((mappables, "Images, etc.", ""))

    def apply_callback(data):
        """A callback to apply changes."""
        orig_xlim = axes.get_xlim()
        orig_ylim = axes.get_ylim()

        general = data.pop(0)
        curves = data.pop(0) if has_curve else []
        mappables = data.pop(0) if has_sm else []
        if data:
            raise ValueError("Unexpected field")

        # Set / General
        (title, xmin, xmax, xlabel, xscale, ymin, ymax, ylabel, yscale,
         generate_legend) = general

        if axes.get_xscale() != xscale:
            axes.set_xscale(xscale)
        if axes.get_yscale() != yscale:
            axes.set_yscale(yscale)

        axes.set_title(title)
        axes.set_xlim(xmin, xmax)
        axes.set_xlabel(xlabel)
        axes.set_ylim(ymin, ymax)
        axes.set_ylabel(ylabel)

        # Restore the unit data
        axes.xaxis.converter = xconverter
        axes.yaxis.converter = yconverter
        axes.xaxis.set_units(xunits)
        axes.yaxis.set_units(yunits)
        axes.xaxis._update_axisinfo()
        axes.yaxis._update_axisinfo()

        # Set / Curves
        for index, curve in enumerate(curves):
            line = labeled_lines[index][1]
            (label, linestyle, drawstyle, linewidth, color, marker, markersize,
             markerfacecolor, markeredgecolor) = curve
            line.set_label(label)
            line.set_linestyle(linestyle)
            line.set_drawstyle(drawstyle)
            line.set_linewidth(linewidth)
            rgba = mcolors.to_rgba(color)
            line.set_alpha(None)
            line.set_color(rgba)
            if marker != 'none':
                line.set_marker(marker)
                line.set_markersize(markersize)
                line.set_markerfacecolor(markerfacecolor)
                line.set_markeredgecolor(markeredgecolor)

        # Set ScalarMappables.
        for index, mappable_settings in enumerate(mappables):
            mappable = labeled_mappables[index][1]
            if len(mappable_settings) == 5:
                label, cmap, low, high, interpolation = mappable_settings
                mappable.set_interpolation(interpolation)
            elif len(mappable_settings) == 4:
                label, cmap, low, high = mappable_settings
            mappable.set_label(label)
            mappable.set_cmap(cm.get_cmap(cmap))
            mappable.set_clim(*sorted([low, high]))

        # re-generate legend, if checkbox is checked
        if generate_legend:
            draggable = None
            ncol = 1
            if axes.legend_ is not None:
                old_legend = axes.get_legend()
                draggable = old_legend._draggable is not None
                ncol = old_legend._ncol
            new_legend = axes.legend(ncol=ncol)
            if new_legend:
                new_legend.set_draggable(draggable)

        # Redraw
        figure = axes.get_figure()
        figure.canvas.draw()
        if not (axes.get_xlim() == orig_xlim and axes.get_ylim() == orig_ylim):
            figure.canvas.toolbar.push_current()

    _formlayout.fedit(
        datalist, title="Figure options", parent=parent,
        icon=QtGui.QIcon(
            str(cbook._get_data_path('images', 'qt4_editor_options.svg'))),
        apply=apply_callback)

