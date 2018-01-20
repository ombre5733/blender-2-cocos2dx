#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# ====---------------------------------------------------------------------====
#     This is a Blender addon for exporting a scene to Cocos2d-x in
#     its JSON file format (c3t).
#     Created by Manuel Freiberger.
# ====---------------------------------------------------------------------====


bl_info = {
    "name": "Cocos2d-x exporter",
    "author": "Manuel Freiberger",
    "version": (0, 2, 0),
    "blender": (2, 78, 0),
    "location": "File > Export",
    "description": "Exports objects to Cocos2d-x",
    "category": "Import-Export"}


import os

import bpy
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        )
from bpy_extras.io_utils import (
        axis_conversion,
        ExportHelper,
        orientation_helper_factory,
        path_reference_mode,
        )

from . import addon_updater_ops
from . import export_cocos2dx


# Create a factory which defines properties for the forward axis and the up axis.
IOCocos2dxOrientationHelper = orientation_helper_factory('IOCocos2dxOrientationHelper', axis_forward='-Z', axis_up='Y')


class ExportCocos2dx(bpy.types.Operator, ExportHelper, IOCocos2dxOrientationHelper):
    """Export to a Cocos2d-x text file"""

    bl_idname = 'export_scene.cocos2dx'
    bl_label = 'Export Cocos2d-x'
    bl_options = {'PRESET'}

    filename_ext = '.c3t'
    filter_glob = StringProperty(
            default='*.c3t',
            options={'HIDDEN'},
            )

    # context group
    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    # data group
    export_normals = BoolProperty(
            name="Export Normals",
            description="Export one normal per face per per vertex, to represent flat faces and sharp edges",
            default=True,
            )

    export_uv_maps = BoolProperty(
            name="Export UVs",
            description="Exports the UV coordinates and the assigned textures",
            default=True,
            )

    # object group
    use_mesh_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Apply modifiers",
            default=True,
            )

    use_mesh_modifiers_render = BoolProperty(
            name="Use Modifiers Render Settings",
            description="Use render settings when applying modifiers to mesh objects",
            default=False,
            )

    global_scale = FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            description="Scaling factor applied to all exported objects",
            default=1.0
            )

    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from mathutils import Matrix

        keywords = self.as_keywords(ignore=('axis_forward',  # from IOCocos2dxOrientationHelper
                                            'axis_up',  # from IOCocos2dxOrientationHelper
                                            'check_existing',  # from ExportHelper
                                            'filepath',  # from ExportHelper
                                            'filter_glob',
                                            'global_scale',
                                            'path_mode'
                                            ))

        # Create a matrix which incorporates the global scale and the rotation to match Cocos2d-x's coordinate frame.
        global_matrix = (Matrix.Scale(self.global_scale, 4)
                         * axis_conversion(to_forward=self.axis_forward,
                                           to_up=self.axis_up).to_4x4())
        keywords['global_matrix'] = global_matrix

        exporter = export_cocos2dx.Exporter(context=context, source_filepath=bpy.data.filepath,
                                            dest_filepath=self.filepath, path_mode=self.path_mode)
        exporter.run(context, **keywords)
        return {'FINISHED'}


class Cocos2dxExporterPreferences(bpy.types.AddonPreferences):
    bl_idname = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

    # addon updater preferences

    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
        )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    def draw(self, context):
        # updater draw function
        addon_updater_ops.update_settings_ui(self, context)


def menu_func_export(self, context):
    self.layout.operator(ExportCocos2dx.bl_idname, text='Cocos2d-x (.c3t)')


def register():
    addon_updater_ops.register(bl_info)
    bpy.utils.register_class(Cocos2dxExporterPreferences)
    bpy.utils.register_class(ExportCocos2dx)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(ExportCocos2dx)
    bpy.utils.register_class(Cocos2dxExporterPreferences)
    addon_updater_ops.unregister()


if __name__ == '__main__':
    register()
