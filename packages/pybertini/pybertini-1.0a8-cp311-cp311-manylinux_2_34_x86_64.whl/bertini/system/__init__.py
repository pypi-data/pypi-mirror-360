# coding : utf-8
#
# This file is part of Bertini 2.
# 
# python/bertini/system/__init__.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# python/bertini/system/__init__.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with python/bertini/system/__init__.py.  If not, see <http://www.gnu.org/licenses/>.
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
Provides utilities for working with systems of functions -- polynomials are intended, although you can work with functions involving things like trig functions, arbitrary powers, etc.

Making a new `System` is the starting point you want, probably some of these things:

::

	sys = bertini.system.System()
	sys.add_function(...)
	sys.add_variable_group(...)
	
	x = sys.dehomogenize_point(z)

"""

import bertini._pybertini.system

from bertini._pybertini.system import * # brings the type System
from bertini._pybertini.system import start_system

__all__ = dir(bertini._pybertini.system)
__all__.extend(['start_system'])
