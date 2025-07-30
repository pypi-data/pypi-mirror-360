# This file is part of Bertini 2.
# 
# python/bertini/endgame/__init__.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# python/bertini/endgame/__init__.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with python/bertini/endgame/__init__.py.  If not, see <http://www.gnu.org/licenses/>.
# 
#  Copyright(C) 2018-2025 by Bertini2 Development Team
# 
#  See <http://www.gnu.org/licenses/> for a copy of the license, 
#  as well as COPYING.  Bertini2 is provided with permitted 
#  additional terms in the b2/licenses/ directory.

#  individual authors of this file include:
# 
#  silviana amethyst
#  UWEC
#  Spring 2018
# 

"""
Endgame-specific things -- endgames, configs
***********************************************

Endgames allow the computation of singular endpoints.  

Flavors
=========

There are two basic flavors of endgame implemented:

1. Power Series, commonly written PS or PSEG
2. Cauchy

Both estimate the cycle number and use it to compute a root at a time which is never tracked to.  PSEG uses Hermite interpolation and extrapolation, and Cauchy uses loops around the target time coupled with the `Cauchy integral formula <https://en.wikipedia.org/wiki/Cauchy%27s_integral_formula>`_.  Both continue until two successive approximations of the root match to a given tolerance (:py:attr:`bertini.endgame.config.Endgame.final_tolerance`).

The implementations of the endgames go with a particular tracker, hence there are six provided endgame types.  Choose the one that goes with your selected tracker type.  Adaptive Multiple Precision is a good choice.


Implementation reference
=========================

AMP Endgames
-------------

* :class:`~bertini.endgame.AMPCauchyEG`
* :class:`~bertini.endgame.AMPPSEG`

Fixed Double Precision Endgames
---------------------------------

* :class:`~bertini.endgame.FixedDoublePSEG`
* :class:`~bertini.endgame.FixedDoublePSEG`

Fixed Multiple Precision  Endgames
-------------------------------------

* :class:`~bertini.endgame.FixedMultiplePSEG`
* :class:`~bertini.endgame.FixedMultiplePSEG`

"""

import bertini._pybertini.endgame

from bertini._pybertini.endgame import *

__all__ = ['AMPCauchyEG',
 'AMPPSEG',
 'FixedDoubleCauchyEG',
 'FixedDoublePSEG',
 'FixedMultipleCauchyEG',
 'FixedMultiplePSEG',
 '__doc__',
 '__loader__',
 '__name__',
 '__package__',
 '__spec__',
 'config',
 'observers']
