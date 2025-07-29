"""Model templates for Fesslix.

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


##################################################
# Model templates                                #
##################################################

def generate_reliability_R_S_example():
    """Defines a simple R-S model for reliability analysis."""
    res = {}
    ## ==============================================
    ## Generate input model
    ## ==============================================
    config_rv_R = { 'name':'R', 'type':'logn', 'mu':5., 'sd':1. }
    config_rv_S = { 'name':'S', 'type':'normal', 'mu':1., 'sd':2. }
    res['rv_set'] = flx.rv_set( {'name':'rv_set'}, [ config_rv_R, config_rv_S ] )
    res['sampler'] = flx.sampler(['rv_set'])
    ## ==============================================
    ## Generate output model
    ## ==============================================
    res['model'] = [ "rbrv(rv_set::R)-rbrv(rv_set::S)" ]
    ## ==============================================
    ## return model
    ## ==============================================
    return res
