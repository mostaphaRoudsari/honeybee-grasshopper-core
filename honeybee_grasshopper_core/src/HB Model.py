# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Honeybee Model, which can be sent for simulation.
-

    Args:
        rooms_: A list of honeybee Rooms to be added to the Model. Note that at
            least one Room is necessary to make a simulate-able energy model.
        faces_: A list of honeybee Faces to be added to the Model. Note that
            faces without a parent Room are not allowed for energy models.
        shades_: A list of honeybee Shades to be added to the Model.
        apertures_: A list of honeybee Apertures to be added to the Model. Note
            that apertures without a parent Face are not allowed for energy models.
        doors_: A list of honeybee Doors to be added to the Model. Note
            that doors without a parent Face are not allowed for energy models.
        _north_: An number between 0 and 360 to set the clockwise north
            direction in degrees. This can also be a vector to set the North.
            Default is 0.
        _run: Set to "True" to run the component and create the Model.
    
    Returns:
        report: Reports, errors, warnings, etc.
        model: A Honeybee Model object possessing all of the input geometry
            objects.
"""

ghenv.Component.Name = "HB Model"
ghenv.Component.NickName = 'Model'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set a default name
    name = _name_ if _name_ is not None else 'unnamed'
    
    # create the model
    model = Model(name, rooms_, faces_, shades_, apertures_, doors_)
    
    # set the north if it is not defaulted
    if _north_ is not None:
        try:
            model.north_vector = to_vector2d(_north_)
        except AttributeError:  # north angle instead of vector
            model.north_angle = _north_