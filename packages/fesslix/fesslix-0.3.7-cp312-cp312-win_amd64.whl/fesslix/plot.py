"""Plotting module for Fesslix.

"""

# Fesslix - Stochastic Analysis
# Copyright (C) 2010-2025 Wolfgang Betz
#
# Fesslix is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fesslix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fesslix.  If not, see <http://www.gnu.org/licenses/>. 

import fesslix as flx
import fesslix.tools as flx_tools

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

##################################################
# Constants                                      #
##################################################

color_seq = [ 'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan' ]

color_era_1 = (0.35,0.58,0.36)
color_era_2 = (0.36,0.45,0.33)
color_era_3 = (0.35,0.31,0.27)
color_era_grey_1 = '#939598'
color_era_grey_2 = '#636466'
color_era_grey_3 = '#3B3B3C'
color_tumblue = "#0065BD"
color_tumgreen = "#A2AD00"
color_tumorange = "#E37222"
color_tumlightblue = "#98C6EA"
color_tumdarkblue = "#005293"
color_seq_era = [ color_era_1, color_era_2, color_era_3, color_era_grey_1, color_era_grey_2, color_era_grey_3 ]
color_seq_tum = [ color_tumblue, color_tumgreen, color_tumorange, color_tumlightblue, color_tumdarkblue ]

def gen_cmap_gr():
    c = [ "darkgreen", "lawngreen", "yellow", "orange", "red", "darkred"]
    v = [0,.2,.5,0.8,.9,1.]
    l = list(zip(v,c))
    cmap=mpl.colors.LinearSegmentedColormap.from_list('rg',l, N=256)
    return cmap

cmap_gr = gen_cmap_gr()


##################################################
# Defaults                                       #
##################################################

def_ed = {} ## default era_dict

def_ed['x_low']            = None
def_ed['x_up']             = None
def_ed['q_low']            = None
def_ed['q_up']             = None
def_ed['q_bounds']         = 1e-3
def_ed['x_disc_N']         = int(1e3)
def_ed['x_disc_shift']     = False
def_ed['x_disc_on_log']    = False
def_ed['scattermtx_max_n'] = int(5e3)    # TODO docu, needed?
def_ed['color_seq']        = color_seq   # TODO docu, needed?
def_ed['cmap']             = cmap_gr     # TODO docu, needed?
def_ed['cid']              = None        # TODO docu, needed?
def_ed['cbar_useLog']      = False       # TODO docu, needed?
def_ed['cbar_label']       = None        # TODO docu, needed?
def_ed['xlabel']           = None        # TODO docu, needed?
def_ed['ylabel']           = None        # TODO docu, needed?
def_ed['violin_invert_y']  = False       # TODO docu, needed?
def_ed['label']            = None
def_ed['show_legend']      = True        # TODO docu, needed?
def_ed['xticks_strformat'] = None        # TODO docu, needed?
def_ed['yticks_strformat'] = None        # TODO docu, needed?
def_ed['xticks_nbins']     = None        # TODO docu, needed?
def_ed['yticks_nbins']     = None        # TODO docu, needed?
def_ed['xticklabelsrotation'] = 0.       # TODO docu, needed?
def_ed['figsize']          = None        # TODO docu, needed?


##################################################
# internal Functions                             #
##################################################

def _assign_color(param_dict,era_dict):
    if 'color' in param_dict:
        return
    if 'c' in param_dict:
        return
    if era_dict['cid'] is not None:
        if isinstance(era_dict['cid'], int):
            if era_dict['color_seq'] is not None:
                param_dict['color'] = era_dict['color_seq'][era_dict['cid']]
        else:
            param_dict['color'] = era_dict['cid']

def _complete_era_dict(era_dict):
    """
    For all properties missing in era_dict, the default values are added.

    Returns
    -------
    A copy of era_dict with the added properties.
    """
    ## make sure that the dictionary has not already been completed
    if 'is_complete' in era_dict:
        if era_dict['is_complete']:
            return era_dict
    ## fill up the dictionary
    ed = era_dict.copy()
    for key, val in def_ed.items():
        if key not in ed:
            ed[key] = val
    ## process q_low and q_up
    if ed['q_low'] is None:
        ed['q_low'] = ed['q_bounds']
    if ed['q_up'] is None:
        ed['q_up'] = 1.-ed['q_bounds']
    ## classify ed as completed.
    ed['is_complete'] = True
    return ed



##################################################
# plotting of distributions                      #
##################################################

##================================================
# helping function
##================================================

def _draw_distribution(ax, rv, mode, config_dict={}, param_dict={}, reverse_axis=False):
    """
    Draws the PDF/CDF/SF of rv on ax.

    Parameters
    ----------
    ax : axes
        The axes object to draw onto.
    rv : rv_base
        The random variable of which to draw the PDF.
    config_dict : dictionary
        A dictionary for plotting properties related to this module.
    param_dict : dictionary
        A dictionary for plotting properties related to matplotlib.
    reverse_axis : bool
        the horizontal and vertical axes of the plot are switched

    Returns
    -------
    the object returned by ax.plot(...)
    """
    ## get a full list of all module-related plotting properties
    ed = _complete_era_dict(config_dict)
    ## make sure that the bounds on the x-axis are defined
    flx_tools.detect_bounds_x(rv, ed, q_low=ed['q_low'], q_up=ed['q_up'])
    ## obtain values for the x-axis
    x = flx_tools.discretize_x( x_low=ed['x_low'], x_up=ed['x_up'], x_disc_N=ed['x_disc_N'], x_disc_shift=ed['x_disc_shift'], x_disc_on_log=ed['x_disc_on_log'] )
    ## evaluate values for the y-axis
    if mode=='pdf':
        y = rv.pdf_array(x)
    elif mode=='cdf':
        y = rv.cdf_array(x)
    elif mode=='sf':
        y = rv.sf_array(x)
    ## Colors
    param_dict_ = param_dict.copy()
    _assign_color(param_dict_,ed)
    ## Label
    if ed["label"] is None:
        lbl = rv.get_descr()
        if lbl=="":
            lbl = rv.get_name()
    else:
        lbl = ed["label"]
    ## draw the PDF
    if reverse_axis:
        out = ax.plot(y, x, label=lbl, **param_dict_)
    else:
        out = ax.plot(x, y, label=lbl, **param_dict_)
    return out


##================================================
# plot PDF
##================================================

def draw_pdf(ax, rv, config_dict={}, param_dict={}, reverse_axis=False):
    return _draw_distribution(ax, rv, 'pdf', config_dict, param_dict, reverse_axis)


##================================================
# plot CDF
##================================================

def draw_cdf(ax, rv, config_dict={}, param_dict={}, reverse_axis=False):
    return _draw_distribution(ax, rv, 'cdf', config_dict, param_dict, reverse_axis)

##================================================
# plot SF
##================================================

def draw_sf(ax, rv, config_dict={}, param_dict={}, reverse_axis=False):
    return _draw_distribution(ax, rv, 'sf', config_dict, param_dict, reverse_axis)


