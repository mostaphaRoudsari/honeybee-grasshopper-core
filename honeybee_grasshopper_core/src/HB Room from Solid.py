# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Honeybee Rooms from solids (closed Rhino polysurfaces).
_
Note that each Room is mapped to a single zone in EnergyPlus/OpenStudio and
should always be a closed volume to ensure correct volumetric calculations and
avoid light leaks in Radiance simulations.
-

    Args:
        _geo: A list of closed Rhino polysurfaces (aka.breps) to be converted
            into honeybee Rooms. This list can also include closed meshes that
            represent the rooms.
        _name_: Text to set the base name for the Room, which will also be incorporated
            into unique Room identifier. If the name is not provided, a random name
            will be assigned.
        _mod_set_: Text for the modifier set of the Rooms, which is used to
            assign all default radiance modifiers needed to create a radiance
            model. Text should refer to a ModifierSet within the library) such
            as that output from the "HB List Modifier Sets" component. This
            can also be a custom ModifierSet object. If nothing is input here,
            the Room will have a generic construction set that is not sensitive to
            the Room's climate or building energy code.
        _constr_set_: Text for the construction set of the Rooms, which is used
            to assign all default energy constructions needed to create an energy
            model. Text should refer to a ConstructionSet within the library such
            as that output from the "HB List Construction Sets" component. This
            can also be a custom ConstructionSet object. If nothing is input here,
            the Rooms will have a generic construction set that is not sensitive to
            the Rooms's climate or building energy code.
        _program_: Text for the program of the Rooms (to be looked up in the ProgramType
            library) such as that output from the "HB List Programs" component.
            This can also be a custom ProgramType object. If no program is input
            here, the Rooms will have a generic office program. Note that ProgramTypes
            effectively map to OpenStudio space types upon export to OpenStudio.
        conditioned_: Boolean to note whether the Rooms have heating and cooling
            systems.
        _roof_angle_: Cutting angle for roof from Z axis in degrees. Default: 30.
    
    Returns:
        report: Reports, errors, warnings, etc.
        rooms: Honeybee rooms. These can be used directly in energy and radiance
            simulations.
"""

ghenv.Component.Name = "HB Room from Solid"
ghenv.Component.NickName = 'RoomSolid'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.facetype import get_type_from_normal
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.togeometry import to_polyface3d
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        document_counter, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.programtypes import program_type_by_identifier, office_program
    from honeybee_energy.lib.constructionsets import construction_set_by_identifier
except ImportError as e:
    if len(_program_) != 0:
        raise ValueError('_program_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif len(_constr_set_) != 0:
        raise ValueError('_constr_set_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif len(conditioned_) != 0:
        raise ValueError('conditioned_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier
except ImportError as e:
    if len(_mod_set_) != 0:
        raise ValueError('_mod_set_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))

import uuid


if all_required_inputs(ghenv.Component):
    # set the default roof angle
    roof_angle = _roof_angle_ if _roof_angle_ is not None else 30

    rooms = []  # list of rooms that will be returned
    for i, geo in enumerate(_geo):
        # get the name for the Room
        if len(_name_) == 0:  # make a default Room name
            name = "Room_{}_{}".format(document_counter('room_count'), str(uuid.uuid4())[:8])
        else:
            display_name = '{}_{}'.format(longest_list(_name_, i), i + 1)
            name = clean_and_id_string(display_name)

        # create the Room
        room = Room.from_polyface3d(name, to_polyface3d(geo), roof_angle, ground_depth=tolerance)
        if len(_name_) != 0:
            room.display_name = display_name

        # check that the Room geometry is closed.
        if not room.check_solid(tolerance, angle_tolerance, False):
            give_warning(ghenv.Component, 'Input _geo is not a closed volume.\n'
                         'Room volume must be closed to access most honeybee features.\n'
                         'Preview the output Room to see the holes in your model.')

        # try to assign the modifier set
        if len(_mod_set_) != 0:
            mod_set = longest_list(_mod_set_, i)
            if isinstance(mod_set, str):
                mod_set = modifier_set_by_identifier(mod_set)
            room.properties.radiance.modifier_set = mod_set

        # try to assign the construction set
        if len(_constr_set_) != 0:
            constr_set = longest_list(_constr_set_, i)
            if isinstance(constr_set, str):
                constr_set = construction_set_by_identifier(constr_set)
            room.properties.energy.construction_set = constr_set

        # try to assign the program
        if len(_program_) != 0:
            program = longest_list(_program_, i)
            if isinstance(program, str):
                program = program_type_by_identifier(program)
            room.properties.energy.program_type = program
        else:  # generic office program by default
            try:
                room.properties.energy.program_type = office_program
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed

        # try to assign an ideal air system
        if len(conditioned_) == 0 or longest_list(conditioned_, i):
            try:
                room.properties.energy.add_default_ideal_air()
            except (NameError, AttributeError):
                pass  # honeybee-energy is not installed

        rooms.append(room)