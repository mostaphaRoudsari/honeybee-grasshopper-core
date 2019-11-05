# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Quickly preview any Honeybee geometry object within the Rhino scene.
_
Sub-faces and assigned shades will not be included in the output, allowing for
a faster preview of large lists of objects but without the ability to check the
assignment of child objects.
-

    Args:
        _hb_obj: A Honeybee Room, Face, Shade, Aperture, or Door to be previewed
            in the Rhino scene.
    
    Returns:
        geo: The Rhino version of the Honeybee geometry object, which will be
            visible in the Rhino scene.
"""

ghenv.Component.Name = "HB Vizualize Quick"
ghenv.Component.NickName = 'VizQuick'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the core honeybee dependencies
    from ladybug_rhino.fromgeometry import from_face3d
    from ladybug_rhino.fromgeometry import from_polyface3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    geo = []
    
    # loop through all objects and add them
    for hb_obj in _hb_obj:
        try:  # Face, Shade, Aperture, or Door
            geo.append(from_face3d(hb_obj.geometry))
        except AttributeError:  # Room
            geo.append(from_polyface3d(hb_obj.geometry))