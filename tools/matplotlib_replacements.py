# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This is the place to store the replacements/adjustments made to the matplotlib code
 NOTE - if using this file, it has to be imported by midvatten.py
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
import six
import matplotlib as mpl

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg as NavigationToolbar

from matplotlib import pyplot as plt
from matplotlib import rcsetup
from cycler import cycler
from midvatten_utils import returnunicode as ru
from qgis.PyQt.QtCore import QCoreApplication, Qt, pyqtSignal, QObject
import types


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
    params_to_add = {'axes.midv_line_cycle': [cycler('linestyle', ['-', '--', '-.', ':']), rcsetup.validate_cycler],
                     'axes.midv_marker_cycle': [cycler('marker', ['o', '+', 's', 'x']), rcsetup.validate_cycler],
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

