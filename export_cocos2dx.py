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

import os
from collections import OrderedDict
from math import inf

import bpy
import bpy_extras.io_utils
from mathutils import Matrix


def triangulate_mesh(mesh):
    import bmesh
    temp_mesh = bmesh.new()
    temp_mesh.from_mesh(mesh)
    bmesh.ops.triangulate(temp_mesh, faces=temp_mesh.faces)
    temp_mesh.to_mesh(mesh)
    temp_mesh.free()


class Table:
    """A list wrapper, which adds an items_per_line attribute for pretty-printing.
    """
    def __init__(self, items, num_items_per_line=1):
        self.items = list(items)
        self.items_per_line = num_items_per_line

    def append(self, item):
        self.items.append(item)

    def extend(self, items):
        self.items.extend(items)


class Inline:
    """A wrapper to output lists in a single line.
    """
    def __init__(self, value):
        self.value = value


class JsonWriter:
    """Serializes value in JSON format to fw.

    This is a straight forward implementation of a basic JSON encoder. This encoder is used rather than Python's
    standard json package because it allows to hook in custom formatting of tables.
    """
    def __init__(self):
        self.int_format = '{}'
        self.float_format = '{}'
        self.fw = None
        self.inline = False

    def write(self, value, fw):
        self.fw = fw
        self._encode(value, 0)
        self.fw('\n')

    def _encode_list(self, lst, indent, items_per_line=1):
        if not lst:
            self.fw('[]')
            return
        indent += 1
        nl = '\n' + '    ' * indent
        sep = ''
        self.fw('[')
        for idx in range(len(lst)):
            self.fw(sep)
            sep = ', '
            if not self.inline and idx % items_per_line == 0:
                self.fw(nl)
            self._encode(lst[idx], indent)
        if not self.inline:
            indent -= 1
            nl = '\n' + '    ' * indent
            self.fw(nl)
        self.fw(']')

    def _encode_dict(self, dct, indent):
        if not dct:
            self.fw('{}')
            return
        indent += 1
        nl = '\n' + '    ' * indent
        sep = ''
        self.fw('{' + nl)
        for key, val in dct.items():
            self.fw(sep)
            if not sep:
                sep = ',' + nl
            self.fw('"{}": '.format(key))
            self._encode(val, indent)
        indent -= 1
        nl = '\n' + '    ' * indent
        self.fw(nl + '}')

    def _encode(self, o, indent):
        if isinstance(o, str):
            self.fw('"{}"'.format(o))
        elif o is None:
            self.fw('null')
        elif o is True:
            self.fw('true')
        elif o is False:
            self.fw('false')
        elif isinstance(o, int):
            self.fw(self.int_format.format(o))
        elif isinstance(o, float):
            self.fw(self.float_format.format(o))
        elif isinstance(o, (list, tuple)):
            self._encode_list(o, indent)
        elif isinstance(o, dict):
            self._encode_dict(o, indent)
        elif isinstance(o, Table):
            int_format = self.int_format
            float_format = self.float_format
            self.int_format = '{:5}'
            self.float_format = '{:12.7f}'
            self._encode_list(o.items, indent, o.items_per_line)
            self.int_format = int_format
            self.float_format = float_format
        elif isinstance(o, Inline):
            inline = self.inline
            self.inline = True
            self._encode(o.value, indent)
            self.inline = inline
        else:
            self._encode_dict(o.to_json_dict(), indent)


class Exporter:
    def __init__(self, context, source_filepath, dest_filepath, path_mode):
        self.context = context

        self.dest_filepath = dest_filepath

        # Texture images etc. can use paths relative to the source file. These paths have to be resolved.
        self._source_directory = os.path.dirname(source_filepath)
        self._dest_directory = os.path.dirname(dest_filepath)
        self._path_mode = path_mode
        self._copy_set = set()  # A set of images which need to be copied. TODO

        self._use_cycles = context.scene.render.engine == 'CYCLES'
        self._exported_materials_to_id_map = {}

        self.version = '0.7'
        self.id = ''
        self.meshes = []
        self.materials = []
        self.nodes = []

    def to_json_dict(self):
        dct = OrderedDict()
        dct['version'] = self.version
        dct['id'] = self.id
        dct['meshes'] = self.meshes
        dct['materials'] = self.materials
        dct['nodes'] = self.nodes
        return dct

    def get_material_id(self, material, textures):
        """Creates a material ID.
        """
        # Keep a mapping from material/texture tuples to the id in the exported file.
        key = tuple([material] + textures)
        mat_id = self._exported_materials_to_id_map.get(key)
        if mat_id is None:
            name = ''
            for mt in key:
                if mt:
                    name = mt.name
                    break
            if not name:
                name = 'mat'
            mat_id = name
            counter = 0
            while mat_id in self._exported_materials_to_id_map.values():
                counter += 1
                mat_id = '{}.{}'.format(name, counter)
            self._exported_materials_to_id_map[key] = mat_id

            if self._use_cycles:
                self._register_cycles_renderer_material(material, mat_id)
            else:
                self._register_internal_renderer_material(material, mat_id)
        return mat_id

    def _make_texture_desc(self, texture, name):
        """Creates a texture description.
        """
        if not texture.image:
            return None
        texture_desc = OrderedDict()
        texture_desc['id'] = name
        texture_desc['filename'] = bpy_extras.io_utils.path_reference(
            texture.image.filepath, self._source_directory, self._dest_directory, self._path_mode, "", self._copy_set,
            texture.image.library)

        texture_desc['type'] = 'DIFFUSE'
        if texture.extension == 'REPEAT':
            texture_desc['wrapModeV'] = 'REPEAT'
            texture_desc['wrapModeU'] = 'REPEAT'
        elif texture.extension == 'CLIP':
            texture_desc['wrapModeU'] = 'CLAMP'
            texture_desc['wrapModeV'] = 'CLAMP'
        else:  # texture.extension == 'EXTEND'
            texture_desc['wrapModeU'] = 'UNKNOWN'
            texture_desc['wrapModeV'] = 'UNKNOWN'
        return texture_desc

    def _register_cycles_renderer_material(self, material, mat_id):
        mat_desc = OrderedDict()
        mat_desc['id'] = mat_id
        mat_desc['ambient'] = Inline((1.0, 1.0, 1.0))  # TODO
        mat_desc['diffuse'] = Inline(material.diffuse_color[:])
        mat_desc['emissive'] = Inline(material.diffuse_color[:])  # In Blender the emitted color is the diffuse color.
        mat_desc['opacity'] = material.alpha
        mat_desc['specular'] = Inline(material.specular_color[:])
        mat_desc['shininess'] = 2.0  # TODO
        mat_desc['textures'] = []
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    texture_desc = self._make_texture_desc(node, node.name)
                    if texture_desc:
                        mat_desc['textures'].append(texture_desc)
        else:
            # TODO: When Cycles renderer is chosen, can a material without nodes have a texture?
            pass
        if not mat_desc['textures']:
            mat_desc.popitem('textures')
        self.materials.append(mat_desc)

    def _register_internal_renderer_material(self, material, mat_id):
        mat_desc = OrderedDict()
        mat_desc['id'] = mat_id
        mat_desc['ambient'] = Inline((1.0, 1.0, 1.0))  # TODO
        mat_desc['diffuse'] = Inline(material.diffuse_color[:])
        mat_desc['emissive'] = Inline(material.diffuse_color[:])  # In Blender the emitted color is the diffuse color.
        mat_desc['opacity'] = material.alpha
        mat_desc['specular'] = Inline(material.specular_color[:])
        mat_desc['shininess'] = 2.0  # TODO
        mat_desc['textures'] = []
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEXTURE':
                    texture_desc = self._make_texture_desc(node.texture, node.texture.name)
                    if texture_desc:
                        mat_desc['textures'].append(texture_desc)
        else:
            for tex in material.texture_slots:
                if tex and tex.texture and tex.texture.type == 'IMAGE':
                    texture_desc = self._make_texture_desc(tex.texture, tex.texture.name)
                    if texture_desc:
                        mat_desc['textures'].append(texture_desc)
        if not mat_desc['textures']:
            mat_desc.popitem('textures')
        self.materials.append(mat_desc)

    def run(self, context,
            *,
            global_matrix=None,
            use_selection,
            export_normals,
            export_uv_maps,
            export_animations_only=False,
            use_mesh_modifiers,
            use_mesh_modifiers_render):
        """Exports a scene in the Cocos2d-x format.

        :param global_matrix: The matrix applied to the transform of the nodes. Useful for rotating the coordinate frame
            and applying a global scale.
        """

        # Life is much easier if there is always a global matrix. Fall back to the identity matrix.
        if global_matrix is None:
            global_matrix = Matrix()

        scene = context.scene

        # Enter object mode.
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        # Depending on the user settings, either all objects or only the selected objects
        # will be exported.
        if use_selection:
            objects_to_export = context.selected_objects
        else:
            objects_to_export = scene.objects

        export_model = True
        if export_model:
            for obj_idx, obj in enumerate(objects_to_export):
                try:
                    mesh = obj.to_mesh(scene, use_mesh_modifiers, calc_tessface=False,
                                       settings='RENDER' if use_mesh_modifiers_render else 'PREVIEW')
                except RuntimeError:
                    mesh = None
                if mesh is None:
                    continue

                triangulate_mesh(mesh)
                if export_normals:
                    mesh.calc_normals_split()

                # The position is always included in the per-vertex attributes.
                per_vertex_attribute_desc = [OrderedDict([('attribute', 'VERTEX_ATTRIB_POSITION'),
                                                          ('size', 3),
                                                          ('type', "GL_FLOAT")
                                                          ])]
                # Add the normal vectors to the per-vertex attributes.
                if export_normals:
                    per_vertex_attribute_desc.append(
                            OrderedDict([("attribute", 'VERTEX_ATTRIB_NORMAL'),
                                         ('size', 3),
                                         ('type', 'GL_FLOAT')
                                         ]))
                # Add the texture coordinates to the per-vertex attributes.
                num_uv_layers = 0
                if export_uv_maps:
                    # Limit the number of UV maps to 8.
                    num_uv_layers = min(8, len(mesh.uv_layers), len(mesh.uv_textures))
                    for idx in range(num_uv_layers):
                        attribute_name = 'VERTEX_ATTRIB_TEX_COORD{}'.format(idx if idx else "")
                        per_vertex_attribute_desc.append(
                                OrderedDict([('attribute', attribute_name),
                                             ('size', 2),
                                             ('type', 'GL_FLOAT')
                                             ]))

                # Polygons with different (material, textures)-combinations belong to
                # different parts of the mesh. Assign all polygons with the same (material, textures)-tuple
                # to one set. We do this through a dict, where the (material, textures)-tuple is
                # used as key.
                materials = mesh.materials
                if not materials:
                    materials = [None]
                part_to_polygons_map = OrderedDict()
                for poly in mesh.polygons:
                    local_textures = [uv.data[poly.index].image for uv in mesh.uv_textures[:num_uv_layers]]
                    material_id = self.get_material_id(materials[poly.material_index], local_textures)
                    if material_id not in part_to_polygons_map:
                        part_to_polygons_map[material_id] = []
                    part_to_polygons_map[material_id].append(poly)

                # A mapping from vertex attributes to an integer index. Used to uniquify vertex data.
                vertex_attributes_to_index_map = {}
                num_unique_vertices = 0
                vertex_attributes = []
                local_parts = []
                local_parts_ref = []
                for part_idx, (material_id, polygons) in enumerate(part_to_polygons_map.items()):
                    # The ID of this mesh part.
                    mesh_part_id = '{}_part{}'.format(obj.name, part_idx + 1)
                    # A list of vertex indices which make up a polygon.
                    polygon_vertex_indices = []
                    aabb_min = [inf, inf, inf]
                    aabb_max = [-inf, -inf, -inf]
                    for poly in polygons:
                        for vertex_idx, loop in zip(poly.vertices, poly.loop_indices):
                            # Collect all vertex attributes (position, normal vector, uv-coordinates...) in an array.
                            local_vertex_attributes = list(mesh.vertices[vertex_idx].co)
                            if export_normals:
                                local_vertex_attributes.extend(mesh.vertices[vertex_idx].normal)
                            for uv_idx in range(num_uv_layers):
                                uv_coord = mesh.uv_layers[uv_idx].data[loop].uv
                                local_vertex_attributes.extend([uv_coord[0], 1 - uv_coord[1]])
                            # Avoid storing duplicated vertex attributes.
                            vertex_key = tuple(local_vertex_attributes)
                            unique_idx = vertex_attributes_to_index_map.get(vertex_key)
                            if unique_idx is None:
                                unique_idx = vertex_attributes_to_index_map[vertex_key] = num_unique_vertices
                                num_unique_vertices += 1
                                vertex_attributes.extend(local_vertex_attributes)
                                # Update the bounding box.
                                for coord in range(3):
                                    aabb_min[coord] = min(aabb_min[coord], local_vertex_attributes[coord])
                                    aabb_max[coord] = max(aabb_max[coord], local_vertex_attributes[coord])

                            polygon_vertex_indices.append(unique_idx)

                    local_parts.append(OrderedDict([('id', mesh_part_id),
                                                    ('type', 'TRIANGLES'),
                                                    ('indices', Table(polygon_vertex_indices, 3)),
                                                    ('aabb', Table(aabb_min + aabb_max, 3))
                                                    ]))
                    local_parts_ref.append(OrderedDict([('meshpartid', mesh_part_id),
                                                        ('materialid', material_id),
                                                        ('uvMapping', Inline([[0]]))  # TODO
                                                        ]))

                # Apply the global matrix to the object's transform matrix (which could flip the coordinate system
                # or scale the instance, for example).
                transform = global_matrix * obj.matrix_world

                vertex_attributes = Table(vertex_attributes)
                vertex_attributes.items_per_line = sum([pva['size'] for pva in per_vertex_attribute_desc])
                self.meshes.append(OrderedDict([('attributes', per_vertex_attribute_desc),
                                                ('vertices', vertex_attributes),
                                                ('parts', local_parts)
                                                ]))
                self.nodes.append(OrderedDict([('id', obj.name),
                                               ('skeleton', False),
                                               ('transform', Table([col for row in transform.transposed()
                                                                    for col in row], 4)),
                                               ('parts', local_parts_ref)
                                               ]))
                # Delete the recently created mesh.
                bpy.data.meshes.remove(mesh)

        # Finally write the file.
        with open(self.dest_filepath, 'wt') as out_file:
            writer = JsonWriter()
            writer.write(self, out_file.write)

        # Copy all textures which have been collected in the copy-set.
        bpy_extras.io_utils.path_reference_copy(self._copy_set)

