
from typing import List
from typing import Tuple

# Data types
from .fcscore import XYZ
from .fcscore import GEOM_Object
from .fcscore import GEOM_Field
from .fcscore import TColStd_HSequenceOfTransient

# Enumerations
from .fcscore import GEOMAlgo_State
from .fcscore import ExplodeType
from .fcscore import ComparisonCondition
from .fcscore import TopAbs_ShapeEnum
from .fcscore import ShapeKind
from .fcscore import SICheckLevel

# Operations
from .fcscore import Geometry3DPrimitives
from .fcscore import GeometryBasicOperations
from .fcscore import GeometryBlockOperations
from .fcscore import GeometryBooleanOperations
from .fcscore import GeometryCurveOperations
from .fcscore import GeometryHealingOperations
from .fcscore import GeometryFieldOperations
from .fcscore import GeometryGroupOperations
from .fcscore import GeometryInsertOperations
from .fcscore import GeometryLocalOperations
from .fcscore import GeometryMeasureOperations
from .fcscore import GeometryShapeOperations
from .fcscore import GeometryTransformOperations

# Extensions 
from .fcscore import ExtGeometryShapeOperations
from .fcscore import ExtGeometryMeasureOperations
from .fcscore import ExtGeometryBooleanOperations
from .fcscore import ExtGeometry3DPrimitives
from .fcscore import ExtGeometryHealingOperations

# IO Handling
from .fcscore import ExportOperations
from .fcscore import ImportOperations

# System  
import os
import sys
import time

class GeometryBuilder(object):
    """
    All geometry operations shall be accessed by the GeometryBuilder wrapper class.
    """

    UseOri = 1
    AutoCorrect = 2

    def __init__(self):
        """
        Initializes all operators. 
        """
        # Instantiate geometry operators
        self.geometry_primitives = Geometry3DPrimitives()
        self.basic_operations = GeometryBasicOperations()
        self.block_operations = GeometryBlockOperations()
        self.boolean_operations = GeometryBooleanOperations()
        self.curve_operations = GeometryCurveOperations()
        self.field_operations = GeometryFieldOperations()
        self.group_operations = GeometryGroupOperations()
        self.insert_operations = GeometryInsertOperations()
        self.healing_operations = GeometryHealingOperations()
        self.local_operations = GeometryLocalOperations()
        self.measure_operations = GeometryMeasureOperations()
        self.shape_operations = GeometryShapeOperations()
        self.transform_operations = GeometryTransformOperations()

        # Instantiate extension operators
        self.ext_shape_operations = ExtGeometryShapeOperations(self.shape_operations)
        self.ext_measure_operations = ExtGeometryMeasureOperations(self.measure_operations)
        self.ext_boolean_operations = ExtGeometryBooleanOperations(self.boolean_operations)
        self.ext_geometry_primitives = ExtGeometry3DPrimitives(self.geometry_primitives)
        self.ext_healing_operations = ExtGeometryHealingOperations(self.healing_operations)

        # Instantiate generic operators
        self.export_operations = ExportOperations()
        self.import_operations = ImportOperations()

    """
    Methods for Input/Output Operations
        - These methods should be separated.
    """
    def import_step(self, complete_path: str, get_assembly_info=False) -> GEOM_Object:
        return self.import_operations.import_step(complete_path, get_assembly_info)

    def import_step_by_hierarchy(self, complete_path: str) -> Tuple[List[str], List[str], List[GEOM_Object], List[bool]]:
        """
        Returns a nested mapped list of shapes: 
        [[list of names],[list of hierarchical location], [list of shapes], [list of true flags if part only]]
        """
        return self.import_operations.import_step_by_hierarchy(complete_path)

    def export_step(self, model: GEOM_Object, exp_file: str, units = "mm") -> None:
        # ToDo: Add unit control, currently exports in 'mm' in Backend
        self.export_operations.export_step(model, exp_file)

    def export_stl(self, model: GEOM_Object, exp_file: str, tesselation_size: float=0.0, is_binary=False) -> None:
        """
        If tesselation size is non-positive it will estimate it on its own (recommended for general purpose).
        If you want to modify your mesh size, it is recommended to first query the default stl size and then
        reduce/increase the tesselation size accordingly.
        """
        self.export_operations.export_stl(model, exp_file, tesselation_size, is_binary)

    def get_default_stl_size(self, model: GEOM_Object) -> float:
        return self.export_operations.get_default_stl_size(model)

    def get_refined_stl_size(self, model: GEOM_Object) -> float:
        return self.export_operations.get_refined_stl_size(model)

    def get_t2g_file_last_export(self) -> str:
        return self.export_operations.get_t2g_file_path()

    def get_stl_file_last_export(self) -> str:
        return self.export_operations.get_stl_file_path()

    """
    Methods for Primitives Operations
    """
    def make_box_dx_dy_dz(self, the_dx: float, the_dy: float, the_dz: float) -> GEOM_Object:
        return self.geometry_primitives.make_box_dx_dy_dz(the_dx, the_dy, the_dz)

    def make_box_two_pnt(self,  the_pnt1: GEOM_Object, the_pnt2: GEOM_Object) -> GEOM_Object:
        return self.geometry_primitives.make_box_two_pnt( the_pnt1, the_pnt2)

    def make_face_h_w(self,  the_h: float, the_w: float, the_orientation: int) -> GEOM_Object:
        return self.geometry_primitives.make_face_h_w( the_h, the_w, the_orientation)

    def make_face_obj_h_w(self,  the_obj: GEOM_Object, the_h: float, the_w: float) -> GEOM_Object:
        return self.geometry_primitives.make_face_obj_h_w( the_obj, the_h, the_w)

    def make_disk_three_pnt(self,  the_pnt1: GEOM_Object, the_pnt2: GEOM_Object, the_pnt3: GEOM_Object) -> GEOM_Object:
        return self.geometry_primitives.make_disk_three_pnt( the_pnt1, the_pnt2, the_pnt3)

    def make_disk_pnt_vec_r(self,  the_pnt1: GEOM_Object, the_vec: GEOM_Object, the_r: float) -> GEOM_Object:
        return self.geometry_primitives.make_disk_pnt_vec_r( the_pnt1, the_vec, the_r)

    def make_disk_r(self,  the_r: float, the_orientation: int) -> GEOM_Object:
        return self.geometry_primitives.make_disk_r( the_r, the_orientation)

    def make_cylinder_r_h(self,  the_r: float, the_h: float) -> GEOM_Object:
        return self.geometry_primitives.make_cylinder_r_h( the_r, the_h)

    def make_cylinder_pnt_vec_r_h(self,  the_pnt: GEOM_Object, the_vec: GEOM_Object, the_r: float, the_h: float) -> GEOM_Object:
        return self.geometry_primitives.make_cylinder_pnt_vec_r_h( the_pnt, the_vec, the_r, the_h)

    def make_cylinder_r_h_a(self,  the_r: float, the_h: float, the_a: float) -> GEOM_Object:
        return self.geometry_primitives.make_cylinder_r_h_a( the_r, the_h, the_a)

    def make_cylinder_pnt_vec_r_h_a(self,  the_pnt: GEOM_Object, the_vec: GEOM_Object, the_r: float, the_h: float, the_a: float) -> GEOM_Object:
        return self.geometry_primitives.make_cylinder_pnt_vec_r_h_a( the_pnt, the_vec, the_r, the_h, the_a)

    def make_cone_r1_r2_h(self,  the_r1: float, the_r2: float, the_h: float) -> GEOM_Object:
        return self.geometry_primitives.make_cone_r1_r2_h( the_r1, the_r2, the_h)

    def make_cone_pnt_vec_r1_r2_h(self,  the_pnt: GEOM_Object, the_vec: GEOM_Object, the_r1: float, the_r2: float, the_h: float) -> GEOM_Object:
        return self.geometry_primitives.make_cone_pnt_vec_r1_r2_h( the_pnt, the_vec, the_r1, the_r2, the_h)

    def make_sphere_r(self,  the_r: float) -> GEOM_Object:
        return self.geometry_primitives.make_sphere_r( the_r)

    def make_sphere_pnt_r(self,  the_pnt: GEOM_Object, the_r: float) -> GEOM_Object:
        return self.geometry_primitives.make_sphere_pnt_r( the_pnt, the_r)

    def make_torus_r_r(self,  the_r_major: float, the_r_minor: float) -> GEOM_Object:
        return self.geometry_primitives.make_torus_r_r( the_r_major, the_r_minor)

    def make_torus_pnt_vec_r_r(self,  the_pnt: GEOM_Object, the_vec: GEOM_Object, the_r_major: float, the_r_minor: float) -> GEOM_Object:
        return self.geometry_primitives.make_torus_pnt_vec_r_r( the_pnt, the_vec, the_r_major, the_r_minor)

    def make_prism_vec_h(self,  the_base: GEOM_Object, the_vec: GEOM_Object, the_h: float, the_scale_factor = -1.0) -> GEOM_Object:
        return self.geometry_primitives.make_prism_vec_h( the_base, the_vec, the_h, the_scale_factor)

    def make_prism_vec_h2_ways(self,  the_base: GEOM_Object, the_vec: GEOM_Object, the_h: float) -> GEOM_Object:
        return self.geometry_primitives.make_prism_vec_h2_ways( the_base, the_vec, the_h)

    def make_prism_two_pnt(self,  the_base: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object, the_scale_factor = -1.0) -> GEOM_Object:
        return self.geometry_primitives.make_prism_two_pnt( the_base, the_point1, the_point2, the_scale_factor)

    def make_prism_two_pnt2_ways(self,  the_base: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object) -> GEOM_Object:
        return self.geometry_primitives.make_prism_two_pnt2_ways( the_base, the_point1, the_point2)

    def make_prism_dx_dy_dz(self,  the_base: GEOM_Object, the_d_x: float, the_d_y: float, the_d_z: float, the_scale_factor = -1.0) -> GEOM_Object:
        return self.geometry_primitives.make_prism_dx_dy_dz( the_base, the_d_x, the_d_y, the_d_z, the_scale_factor)

    def make_prism_dx_dy_dz_2ways(self,  the_base: GEOM_Object, the_d_x: float, the_d_y: float, the_d_z: float) -> GEOM_Object:
        return self.geometry_primitives.make_prism_dx_dy_dz_2ways( the_base, the_d_x, the_d_y, the_d_z)

    def make_draft_prism(self,  the_init_shape: GEOM_Object, the_base: GEOM_Object, the_height: float, the_angle: float, the_fuse: bool, invert = False) -> GEOM_Object:
        return self.geometry_primitives.make_draft_prism( the_init_shape, the_base, the_height, the_angle, the_fuse, invert)

    def make_pipe(self,  the_base: GEOM_Object, the_path: GEOM_Object, is_generate_groups: bool) -> TColStd_HSequenceOfTransient:
        return self.geometry_primitives.make_pipe( the_base, the_path, is_generate_groups)

    def make_revolution_axis_angle(self,  the_base: GEOM_Object, the_axis: GEOM_Object, the_angle: float) -> GEOM_Object:
        return self.geometry_primitives.make_revolution_axis_angle( the_base, the_axis, the_angle)

    def make_revolution_axis_angle2_ways(self,  the_base: GEOM_Object, the_axis: GEOM_Object, the_angle: float) -> GEOM_Object:
        return self.geometry_primitives.make_revolution_axis_angle2_ways( the_base, the_axis, the_angle)

    def make_filling(self,  the_contours: list, the_method: int, the_min_deg = 2, the_max_deg = 5, the_tol2_d = 0.0001, the_tol3_d = 0.0001, the_nb_iter = 0, is_approx = False) -> GEOM_Object:
        return self.geometry_primitives.make_filling( the_contours, the_min_deg, the_max_deg, the_tol2_d, the_tol3_d, the_nb_iter, the_method, is_approx)

    def make_thru_sections(self,  the_seq_sections: TColStd_HSequenceOfTransient, the_mode_solid: bool, the_preci: float, the_ruled: bool) -> GEOM_Object:
        return self.geometry_primitives.make_thru_sections( the_seq_sections, the_mode_solid, the_preci, the_ruled)

    def make_pipe_with_different_sections(self,  the_bases: TColStd_HSequenceOfTransient, the_locations: TColStd_HSequenceOfTransient, the_path: GEOM_Object, the_with_contact: bool, the_with_corrections: bool, is_by_steps: bool, is_generate_groups: bool) -> TColStd_HSequenceOfTransient:
        return self.geometry_primitives.make_pipe_with_different_sections( the_bases, the_locations, the_path, the_with_contact, the_with_corrections, is_by_steps, is_generate_groups)

    def make_pipe_with_shell_sections(self,  the_bases: TColStd_HSequenceOfTransient, the_sub_bases: TColStd_HSequenceOfTransient, the_locations: TColStd_HSequenceOfTransient, the_path: GEOM_Object, the_with_contact: bool, the_with_corrections: bool, is_generate_groups: bool) -> TColStd_HSequenceOfTransient:
        return self.geometry_primitives.make_pipe_with_shell_sections( the_bases, the_sub_bases, the_locations, the_path, the_with_contact, the_with_corrections, is_generate_groups)

    def make_pipe_shells_without_path(self,  the_bases: TColStd_HSequenceOfTransient, the_locations: TColStd_HSequenceOfTransient, is_generate_groups: bool) -> TColStd_HSequenceOfTransient:
        return self.geometry_primitives.make_pipe_shells_without_path( the_bases, the_locations, is_generate_groups)

    def make_pipe_bi_normal_along_vector(self,  the_base: GEOM_Object, the_path: GEOM_Object, the_vec: GEOM_Object, is_generate_groups: bool) -> List[GEOM_Object]:
        return self.ext_geometry_primitives.make_pipe_bi_normal_along_vector( the_base, the_path, the_vec, is_generate_groups)

    def make_thickening(self,  the_object: GEOM_Object, the_offset: float, the_faces_ids: list, is_copy: bool, the_inside = False) -> GEOM_Object:
        return self.geometry_primitives.make_thickening( the_object, the_faces_ids, the_offset, is_copy, the_inside)

    def restore_path(self,  the_shape: GEOM_Object, the_base1: GEOM_Object, the_base2: GEOM_Object) -> GEOM_Object:
        return self.geometry_primitives.restore_path( the_shape, the_base1, the_base2)

    """
    Methods for BasicOperations
    """
    def make_vertex_xyz(self, x: float, y: float, z: float) -> GEOM_Object:
        return self.basic_operations.make_point_xyz(x, y, z)

    def make_vertex_with_reference(self, the_reference: GEOM_Object, the_x: float, the_y: float, the_z: float) -> GEOM_Object:
        return self.basic_operations.make_point_with_reference(the_reference, the_x, the_y, the_z)

    def make_vertex_on_curve(self, the_curve: GEOM_Object, the_parameter: float, take_orientation_into_account: bool) -> GEOM_Object:
        return self.basic_operations.make_point_on_curve(the_curve, the_parameter, take_orientation_into_account)

    def make_vertex_on_curve_by_length(self, the_curve: GEOM_Object, the_start_point: GEOM_Object, the_length: float) -> GEOM_Object:
        return self.basic_operations.make_point_on_curve_by_length(the_curve, the_start_point, the_length)

    def make_vertex_on_curve_by_coord(self, the_curve: GEOM_Object, the_x_param: float, the_y_param: float, the_z_param: float) -> GEOM_Object:
        return self.basic_operations.make_point_on_curve_by_coord(the_curve, the_x_param, the_y_param, the_z_param)

    def make_vertex_on_lines_intersection(self, the_line1: GEOM_Object, the_line2: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_point_on_lines_intersection(the_line1, the_line2)

    def make_vertex_on_surface(self, the_surface: GEOM_Object, the_u_parameter: float, the_v_parameter: float) -> GEOM_Object:
        return self.basic_operations.make_point_on_surface(the_surface, the_u_parameter, the_v_parameter)

    def make_vertex_on_surface_by_coord(self, the_surface: GEOM_Object, the_x_param: float, the_y_param: float, the_z_param: float) -> GEOM_Object:
        return self.basic_operations.make_point_on_surface_by_coord(the_surface, the_x_param, the_y_param, the_z_param)

    def make_vertex_on_face(self, the_face: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_point_on_face(the_face)

    def make_vector(self, the_d_x: float, the_d_y: float, the_d_z: float) -> GEOM_Object:
        return self.basic_operations.make_vector(the_d_x, the_d_y, the_d_z)

    def make_vector_two_pnt(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_vector_two_pnt(the_pnt1, the_pnt2)

    def make_tangent_on_curve(self, the_curve: GEOM_Object, the_parameter: float) -> GEOM_Object:
        return self.basic_operations.make_tangent_on_curve(the_curve, the_parameter)

    def make_line_two_pnt(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_line_two_pnt(the_pnt1, the_pnt2)

    def make_line_two_faces(self, the_face1: GEOM_Object, the_face2: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_line_two_faces(the_face1, the_face2)

    def make_line(self, the_pnt: GEOM_Object, the_dir: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_line(the_pnt, the_dir)

    def make_plane_three_points(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object, the_pnt3: GEOM_Object, the_size: float) -> GEOM_Object:
        return self.basic_operations.make_plane_three_points(the_pnt1, the_pnt2, the_pnt3, the_size)

    def make_plane_point_vector(self, the_pnt: GEOM_Object, the_vec: GEOM_Object, the_size: float) -> GEOM_Object:
        return self.basic_operations.make_plane_point_vector(the_pnt, the_vec, the_size)

    def make_plane_face(self, the_face: GEOM_Object, the_size: float) -> GEOM_Object:
        return self.basic_operations.make_plane_face(the_face, the_size)

    def make_plane_two_vectors(self, the_vec1: GEOM_Object, the_vec2: GEOM_Object, the_size: float) -> GEOM_Object:
        return self.basic_operations.make_plane_two_vectors(the_vec1, the_vec2, the_size)

    def make_plane_lcs(self, the_face: GEOM_Object, the_size: float, the_orientation: int) -> GEOM_Object:
        return self.basic_operations.make_plane_lcs(the_face, the_size, the_orientation)

    def make_marker(self, the_o_x: float, the_o_y: float, the_o_z: float, the_x_d_x: float, the_x_d_y: float, the_x_d_z: float, the_y_d_x: float, the_y_d_y: float, the_y_d_z: float) -> GEOM_Object:
        return self.basic_operations.make_marker(the_o_x, the_o_y, the_o_z, the_x_d_x, the_x_d_y, the_x_d_z, the_y_d_x, the_y_d_y, the_y_d_z)

    def make_marker_from_shape(self, the_shape: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_marker_from_shape(the_shape)

    def make_marker_point_two_vectors(self, the_origin: GEOM_Object, the_x_vec: GEOM_Object, the_y_vec: GEOM_Object) -> GEOM_Object:
        return self.basic_operations.make_marker_point_two_vectors(the_origin, the_x_vec, the_y_vec)

    def make_tangent_plane_on_face(self, the_face: GEOM_Object, the_param_u: float, the_param_v: float, the_size: float) -> GEOM_Object:
        return self.basic_operations.make_tangent_plane_on_face(the_face, the_param_u, the_param_v, the_size)

    def get_last_vertex(self, the_shape: GEOM_Object) -> GEOM_Object:
        nb_vert = self.shape_operations.number_of_sub_shapes(the_shape, TopAbs_ShapeEnum.VERTEX)
        return self.measure_operations.get_vertex_by_index(the_shape,nb_vert-1,True)

    def get_first_vertex(self, the_shape: GEOM_Object) -> GEOM_Object:
        return self.measure_operations.get_vertex_by_index(the_shape,0,True)

    """
    Methods for BlockOperations
    """
    def make_quad(self, the_edge1: GEOM_Object, the_edge2: GEOM_Object, the_edge3: GEOM_Object, the_edge4: GEOM_Object) -> GEOM_Object:
        return self.block_operations.make_quad(the_edge1, the_edge2, the_edge3, the_edge4)

    def make_quad2_edges(self, the_edge1: GEOM_Object, the_edge2: GEOM_Object) -> GEOM_Object:
        return self.block_operations.make_quad2_edges(the_edge1, the_edge2)

    def make_quad4_vertices(self, the_point1: GEOM_Object, the_point2: GEOM_Object, the_point3: GEOM_Object, the_point4: GEOM_Object) -> GEOM_Object:
        return self.block_operations.make_quad4_vertices(the_point1, the_point2, the_point3, the_point4)

    def make_hexa(self, the_face1: GEOM_Object, the_face2: GEOM_Object, the_face3: GEOM_Object, the_face4: GEOM_Object, the_face5: GEOM_Object, the_face6: GEOM_Object) -> GEOM_Object:
        return self.block_operations.make_hexa(the_face1, the_face2, the_face3, the_face4, the_face5, the_face6)

    def make_hexa2_faces(self, the_face1: GEOM_Object, the_face2: GEOM_Object) -> GEOM_Object:
        return self.block_operations.make_hexa2_faces(the_face1, the_face2)

    def make_block_compound(self, the_compound: GEOM_Object) -> GEOM_Object:
        return self.block_operations.make_block_compound(the_compound)

    def get_point(self, the_shape: GEOM_Object, the_x: float, the_y: float, the_z: float, the_epsilon: float) -> GEOM_Object:
        return self.block_operations.get_point(the_shape, the_x, the_y, the_z, the_epsilon)

    def get_vertex_near_point(self, the_shape: GEOM_Object, the_point: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_vertex_near_point(the_shape, the_point)

    def get_edge(self, the_shape: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_edge(the_shape, the_point1, the_point2)

    def get_edge_near_point(self, the_block: GEOM_Object, the_point: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_edge_near_point(the_block, the_point)

    def get_face_by_points(self, the_shape: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object, the_point3: GEOM_Object, the_point4: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_face_by_points(the_shape, the_point1, the_point2, the_point3, the_point4)

    def get_face_by_edges(self, the_shape: GEOM_Object, the_edge1: GEOM_Object, the_edge2: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_face_by_edges(the_shape, the_edge1, the_edge2)

    def get_opposite_face(self, the_block: GEOM_Object, the_face: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_opposite_face(the_block, the_face)

    def get_face_near_point(self, the_block: GEOM_Object, the_point: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_face_near_point(the_block, the_point)

    def get_face_by_normale(self, the_block: GEOM_Object, the_vector: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_face_by_normale(the_block, the_vector)

    def get_shapes_near_point(self, the_shape: GEOM_Object, the_point: GEOM_Object, the_shape_type: int, the_tolerance = 1e-7) -> GEOM_Object:
        return self.block_operations.get_shapes_near_point(the_shape, the_point, the_shape_type, the_tolerance)

    def is_compound_of_blocks(self, the_compound: GEOM_Object, the_min_nb_faces: int, the_max_nb_faces: int, the_nb_blocks: int) -> bool:
        return self.block_operations.is_compound_of_blocks(the_compound, the_min_nb_faces, the_max_nb_faces, the_nb_blocks)

    def check_compound_of_blocks(self, the_compound: GEOM_Object, the_tolerance_c1: float, the_errors: list) -> bool:
        return self.block_operations.check_compound_of_blocks(the_compound, the_tolerance_c1, the_errors)

    def print_b_c_errors(self, the_compound: GEOM_Object, the_errors: list) -> str:
        return self.block_operations.print_b_c_errors(the_compound, the_errors)

    def get_non_blocks(self, the_shape: GEOM_Object, the_tolerance_c1: float, the_non_quads: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_non_blocks(the_shape, the_tolerance_c1, the_non_quads)

    def remove_extra_edges(self, the_shape: GEOM_Object, the_optimum_num_faces=6) -> GEOM_Object:
        return self.block_operations.remove_extra_edges(the_shape, the_optimum_num_faces)

    def union_faces(self, the_shape: GEOM_Object) -> GEOM_Object:
        return self.block_operations.union_faces(the_shape)

    def check_and_improve(self, the_compound: GEOM_Object) -> GEOM_Object:
        return self.block_operations.check_and_improve(the_compound)

    def explode_compound_of_blocks(self, the_compound: GEOM_Object, the_min_nb_faces: int, the_max_nb_faces: int) -> TColStd_HSequenceOfTransient:
        return self.block_operations.explode_compound_of_blocks(the_compound, the_min_nb_faces, the_max_nb_faces)

    def get_block_near_point(self, the_compound: GEOM_Object, the_point: GEOM_Object) -> GEOM_Object:
        return self.block_operations.get_block_near_point(the_compound, the_point)

    def get_block_by_parts(self, the_compound: GEOM_Object, the_parts: TColStd_HSequenceOfTransient) -> GEOM_Object:
        return self.block_operations.get_block_by_parts(the_compound, the_parts)

    def get_blocks_by_parts(self, the_compound: GEOM_Object, the_parts: TColStd_HSequenceOfTransient) -> TColStd_HSequenceOfTransient:
        return self.block_operations.get_blocks_by_parts(the_compound, the_parts)

    def make_multi_transformation1_d(self, the_block: GEOM_Object, the_dir_face1: int, the_dir_face2: int, the_nb_times: int) -> GEOM_Object:
        return self.block_operations.make_multi_transformation1_d(the_block, the_dir_face1, the_dir_face2, the_nb_times)

    def make_multi_transformation2_d(self, the_block: GEOM_Object, the_dir_face1_u: int, the_dir_face2_u: int, the_nb_times_u: int, the_dir_face1_v: int, the_dir_face2_v: int, the_nb_times_v: int) -> GEOM_Object:
        return self.block_operations.make_multi_transformation2_d(the_block, the_dir_face1_u, the_dir_face2_u, the_nb_times_u, the_dir_face1_v, the_dir_face2_v, the_nb_times_v)

    def propagate(self, the_shape: GEOM_Object) -> TColStd_HSequenceOfTransient:
        return self.block_operations.propagate(the_shape)

    """
    Methods for Boolean Operations
    """
    def make_boolean(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, the_op: int, is_check_self_inte: bool=False) -> GEOM_Object:
        """Boolean operation between any two shapes

        Args:
            the_shape1 (GEOM_Object): first shape
            the_shape2 (GEOM_Object): second shape
            the_op (int): 
                1 - Common
                2 - Cut
                3 - Fuse
                4 - Section
            is_check_self_inte (bool): check for self intersection?

        Returns:
            GEOM_Object: Boolean result
        """
        return self.boolean_operations.make_boolean(the_shape1, the_shape2, the_op, is_check_self_inte)

    def make_section(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, is_check_self_intersection=False) -> GEOM_Object:
        return self.boolean_operations.make_boolean(the_shape1, the_shape2, 4, is_check_self_intersection)

    def make_fuse(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, is_check_self_inte: bool, is_rm_extra_edges: bool) -> GEOM_Object:
        return self.boolean_operations.make_fuse(the_shape1, the_shape2, is_check_self_inte, is_rm_extra_edges)

    def make_fuse_list(self, the_shapes: TColStd_HSequenceOfTransient, is_check_self_inte: bool, is_rm_extra_edges: bool) -> GEOM_Object:
        return self.boolean_operations.make_fuse_list(the_shapes, is_check_self_inte, is_rm_extra_edges)

    def make_common_list(self, the_shapes: TColStd_HSequenceOfTransient, is_check_self_inte: bool) -> GEOM_Object:
        return self.boolean_operations.make_common_list(the_shapes, is_check_self_inte)

    def make_cut_list(self, the_main_shape: GEOM_Object, the_shapes: TColStd_HSequenceOfTransient, is_check_self_inte: bool) -> GEOM_Object:
        return self.boolean_operations.make_cut_list(the_main_shape, the_shapes, is_check_self_inte)

    def make_half_partition(self, the_shape: GEOM_Object, the_plane: GEOM_Object) -> GEOM_Object:
        return self.boolean_operations.make_half_partition(the_shape, the_plane)

    """
    Methods for Boolean Extension Operations
    """
    def make_partition(self, 
                       the_shapes: list, 
                       the_tools = [], 
                       the_keep_inside = [], 
                       the_remove_inside = [], 
                       the_limit = -1, 
                       the_remove_webs = 0, 
                       the_materials = [], 
                       the_keep_nonlimit_shapes = 0, 
                       the_perform_self_intersections = False, 
                       is_check_self_inte = False) -> GEOM_Object:
        return self.ext_boolean_operations.make_partition(the_shapes, the_tools, the_keep_inside, the_remove_inside, the_limit, the_remove_webs, the_materials, the_keep_nonlimit_shapes, the_perform_self_intersections, is_check_self_inte)


    """
    Methods for CurveOperations
    """
    def make_circle_three_points(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object, the_pnt3: GEOM_Object) -> GEOM_Object:
        return self.curve_operations.make_circle_three_pnt(the_pnt1, the_pnt2, the_pnt3)

    def make_circle_center_two_points(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object, the_pnt3: GEOM_Object) -> GEOM_Object:
        return self.curve_operations.make_circle_center2_pnt(the_pnt1, the_pnt2, the_pnt3)

    def make_circle_pnt_vec_r(self, the_pnt: GEOM_Object, the_vec: GEOM_Object, the_r: float) -> GEOM_Object:
        return self.curve_operations.make_circle_pnt_vec_r(the_pnt, the_vec, the_r)

    def make_ellipse(self, the_pnt: GEOM_Object, the_vec: GEOM_Object, the_r_major: float, the_r_minor: float, the_vec_maj: GEOM_Object) -> GEOM_Object:
        return self.curve_operations.make_ellipse(the_pnt, the_vec, the_r_major, the_r_minor, the_vec_maj)

    def make_arc(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object, the_pnt3: GEOM_Object) -> GEOM_Object:
        return self.curve_operations.make_arc(the_pnt1, the_pnt2, the_pnt3)

    def make_arc_center(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object, the_pnt3: GEOM_Object, the_sense: bool) -> GEOM_Object:
        return self.curve_operations.make_arc_center(the_pnt1, the_pnt2, the_pnt3, the_sense)

    def make_arc_of_ellipse(self, the_pnt1: GEOM_Object, the_pnt2: GEOM_Object, the_pnt3: GEOM_Object) -> GEOM_Object:
        return self.curve_operations.make_arc_of_ellipse(the_pnt1, the_pnt2, the_pnt3)

    def make_polyline(self, the_points: list, is_closed = False) -> GEOM_Object:
        return self.curve_operations.make_polyline(the_points, False)

    def make_spline_bezier(self, the_points: list, is_closed = False) -> GEOM_Object:
        return self.curve_operations.make_spline_bezier(the_points, is_closed)

    def make_spline_interpolation(self, the_points: list, is_closed = False, do_reordering = False) -> GEOM_Object:
        return self.curve_operations.make_spline_interpolation(the_points, is_closed, do_reordering)

    def make_spline_interpol_with_tangents(self, the_points: list, the_first_vec: GEOM_Object, the_last_vec: GEOM_Object) -> GEOM_Object:
        return self.curve_operations.make_spline_interpol_with_tangents(the_points, the_first_vec, the_last_vec)

    def make_3d_sketcher(self, the_coordinates: list) -> GEOM_Object:
        return self.curve_operations.make3_d_sketcher(the_coordinates)

    def make_isoline(self, the_face: GEOM_Object, is_u_iso: bool, the_parameter: float) -> GEOM_Object:
        return self.curve_operations.make_isoline(the_face, is_u_iso, the_parameter)

    def make_polyline_2d(self, the_coords: list, the_names: list, the_types:list, the_closeds: list, the_working_plane:list) -> GEOM_Object:
        return self.curve_operations.make_polyline2_d(the_coords, the_names, the_types, the_closeds, the_working_plane)

    def make_polyline_2d_on_plane(self, the_coords: list, the_names: list, the_types: list, the_closeds: list, the_working_plane: GEOM_Object) -> GEOM_Object:
        return self.curve_operations.make_polyline2_d_on_plane(the_coords, the_names, the_types, the_closeds, the_working_plane)

    """
    Methods for HealingOperations
    """
    def shape_process(self, the_object: GEOM_Object, the_operations: list, the_params: list, the_values: list) -> GEOM_Object:
        return self.healing_operations.shape_process(the_object, the_operations, the_params, the_values)

    def get_shape_process_parameters(self, the_operations: list, the_params: list, the_values: list) -> None:
        return self.healing_operations.get_shape_process_parameters(the_operations, the_params, the_values)

    def get_operator_parameters(self, the_operation: str, the_params: list, the_values: list) -> bool:
        return self.healing_operations.get_operator_parameters(the_operation, the_params, the_values)

    #def get_parameters(self, the_operation: str, the_params: list) -> list:
    #    return self.healing_operations.get_parameters(the_operation, the_params)

    def suppress_faces(self, the_object: GEOM_Object, the_faces: list) -> GEOM_Object:
        return self.healing_operations.suppress_faces(the_object, the_faces)

    def close_contour(self, the_object: GEOM_Object, the_wires: list, is_common_vertex: bool) -> GEOM_Object:
        return self.healing_operations.close_contour(the_object, the_wires, is_common_vertex)

    def remove_int_wires(self, the_object: GEOM_Object, the_wires: list) -> GEOM_Object:
        return self.healing_operations.remove_int_wires(the_object, the_wires)

    def fill_holes(self, the_object: GEOM_Object) -> GEOM_Object:
        """
        Original method required to pass in indices of wires, this method currently
        will just by defaul fill in all holes it finds.
        """
        return self.ext_healing_operations.fill_holes(the_object)

    def sew(self, the_object: list, the_tolerance: float, is_allow_non_manifold=False) -> GEOM_Object:
        return self.healing_operations.sew(the_object, the_tolerance, is_allow_non_manifold)

    def remove_internal_faces(self, the_solids: List[GEOM_Object]) -> GEOM_Object:
        return self.healing_operations.remove_internal_faces(the_solids)

    def divide_edge(self, the_object: GEOM_Object, the_index: int, the_value: float, is_by_parameter: bool) -> GEOM_Object:
        return self.healing_operations.divide_edge(the_object, the_index, the_value, is_by_parameter)

    def divide_edge_by_point(self, the_object: GEOM_Object, the_index: int, the_point: list) -> GEOM_Object:
        return self.healing_operations.divide_edge_by_point(the_object, the_index, the_point)

    def fuse_collinear_edges_within_wire(self, the_wire: GEOM_Object, the_vertices: list) -> GEOM_Object:
        return self.healing_operations.fuse_collinear_edges_within_wire(the_wire, the_vertices)

    def get_free_boundary(self, the_object: GEOM_Object) -> Tuple[List[GEOM_Object],List[GEOM_Object]]:
        """
        Returns a list of wires were 'holes' are located. 
        The first member of the tuple is the list of open wires,
        the second one is a the list of closed wires.

        If the calculation was unsuccessful OR there are no open and closed wires, then an empty tuple is returned.
        """
        return self.ext_healing_operations.get_free_boundary(the_object)

    def change_orientation(self, the_object: GEOM_Object) -> GEOM_Object:
        return self.healing_operations.change_orientation(the_object)

    def change_orientation_copy(self, the_object: GEOM_Object) -> GEOM_Object:
        return self.healing_operations.change_orientation_copy(the_object)

    def limit_tolerance(self, the_object: GEOM_Object, the_tolerance: float, shape_type: TopAbs_ShapeEnum) -> GEOM_Object:
        return self.healing_operations.limit_tolerance(the_object, the_tolerance, shape_type)

    """
    Methods for InsertOperations
    """
    def make_copy(self, the_original: GEOM_Object) -> GEOM_Object:
        return self.insert_operations.make_copy(the_original)

    def import_file(self, the_file_name: str, the_format_type: str) -> TColStd_HSequenceOfTransient:
        return self.insert_operations.import_file(the_file_name, the_format_type)

    def read_value(self, the_file_name: str, the_format_type: str, the_parameter_name: str) -> str:
        return self.insert_operations.read_value(the_file_name, the_format_type, the_parameter_name)

    def export_file(self, the_original: GEOM_Object, the_file_name: str, the_format_type: str) -> None:
        return self.insert_operations.export(the_original, the_file_name, the_format_type)

    def restore_shape(self, the_stream: str) -> GEOM_Object:
        return self.insert_operations.restore_shape(the_stream)

    def load_texture(self, the_texture_file: str) -> int:
        return self.insert_operations.load_texture(the_texture_file)

    def add_texture(self, the_width: int, the_height: int, the_texture: list) -> int:
        return self.insert_operations.add_texture(the_width, the_height, the_texture)

    def get_texture(self, the_texture_id: int, the_width: int, the_height: int) -> list:
        return self.insert_operations.get_texture(the_texture_id, the_width, the_height)

    def get_all_textures(self) -> list:
        return self.insert_operations.get_all_textures()

    def transfer_data(self, the_object_from: GEOM_Object, the_object_to: GEOM_Object, the_find_method: int, the_result: list) -> bool:
        return self.insert_operations.transfer_data(the_object_from, the_object_to, the_find_method, the_result)


    """
    Methods for FieldOperations
    """
    def create_field(self, the_shape: GEOM_Object, the_name: str, the_type: int, the_dimension: int, the_component_names: list) -> GEOM_Field:
        return self.field_operations.create_field(the_shape, the_name, the_type, the_dimension, the_component_names)

    def count_fields(self, shape: GEOM_Object) -> int:
        return self.field_operations.count_fields(shape)

    def get_fields(self, shape: GEOM_Object) -> TColStd_HSequenceOfTransient:
        return self.field_operations.get_fields(shape)

    def get_field(self, shape: GEOM_Object, name: str) -> GEOM_Field:
        return self.field_operations.get_field(shape, name)

    """
    Methods for GroupOperations
    """
    def create_group(self, the_main_shape: GEOM_Object, the_shape_type: TopAbs_ShapeEnum) -> GEOM_Object:
        return self.group_operations.create_group(the_main_shape, the_shape_type)

    def add_object(self, the_group: GEOM_Object, the_sub_shape_i_d: int) -> None:
        return self.group_operations.add_object(the_group, the_sub_shape_i_d)

    def remove_object(self, the_group: GEOM_Object, the_sub_shape_i_d: int) -> None:
        return self.group_operations.remove_object(the_group, the_sub_shape_i_d)

    def union_list(self, the_group: GEOM_Object, the_sub_shapes: TColStd_HSequenceOfTransient) -> None:
        return self.group_operations.union_list(the_group, the_sub_shapes)

    def difference_list(self, the_group: GEOM_Object, the_sub_shapes: TColStd_HSequenceOfTransient) -> None:
        return self.group_operations.difference_list(the_group, the_sub_shapes)

    def union_ids(self, the_group: GEOM_Object, the_sub_shapes: list) -> None:
        return self.group_operations.union_i_ds(the_group, the_sub_shapes)

    def difference_ids(self, the_group: GEOM_Object, the_sub_shapes: list) -> None:
        return self.group_operations.difference_i_ds(the_group, the_sub_shapes)

    def union_groups(self, the_group1: GEOM_Object, the_group2: GEOM_Object) -> GEOM_Object:
        return self.group_operations.union_groups(the_group1, the_group2)

    def intersect_groups(self, the_group1: GEOM_Object, the_group2: GEOM_Object) -> GEOM_Object:
        return self.group_operations.intersect_groups(the_group1, the_group2)

    def cut_groups(self, the_group1: GEOM_Object, the_group2: GEOM_Object) -> GEOM_Object:
        return self.group_operations.cut_groups(the_group1, the_group2)

    def union_list_of_groups(self, the_g_list: TColStd_HSequenceOfTransient) -> GEOM_Object:
        return self.group_operations.union_list_of_groups(the_g_list)

    def intersect_list_of_groups(self, the_g_list: TColStd_HSequenceOfTransient) -> GEOM_Object:
        return self.group_operations.intersect_list_of_groups(the_g_list)

    def cut_list_of_groups(self, the_g_list1: TColStd_HSequenceOfTransient, the_g_list2: TColStd_HSequenceOfTransient) -> GEOM_Object:
        return self.group_operations.cut_list_of_groups(the_g_list1, the_g_list2)

    def get_type(self, the_group: GEOM_Object) -> TopAbs_ShapeEnum:
        return self.group_operations.get_type(the_group)

    def get_main_shape(self, the_group: GEOM_Object) -> GEOM_Object:
        return self.group_operations.get_main_shape(the_group)

    def get_objects(self, the_group: GEOM_Object) -> list:
        return self.group_operations.get_objects(the_group)

    """
    Methods for LocalOperations
    """
    def make_fillet_all(self, the_shape: GEOM_Object, the_r: float) -> GEOM_Object:
        return self.local_operations.make_fillet_all(the_shape, the_r)

    def make_fillet_edges(self, the_shape: GEOM_Object, the_r: float, the_edges: list) -> GEOM_Object:
        return self.local_operations.make_fillet_edges(the_shape, the_r, the_edges)

    def make_fillet_edges_r1_r2(self, the_shape: GEOM_Object, the_r1: float, the_r2: float, the_edges: list) -> GEOM_Object:
        return self.local_operations.make_fillet_edges_r1_r2(the_shape, the_r1, the_r2, the_edges)

    def make_fillet_faces(self, the_shape: GEOM_Object, the_r: float, the_faces: list) -> GEOM_Object:
        return self.local_operations.make_fillet_faces(the_shape, the_r, the_faces)

    def make_fillet_faces_r1_r2(self, the_shape: GEOM_Object, the_r1: float, the_r2: float, the_faces: list) -> GEOM_Object:
        return self.local_operations.make_fillet_faces_r1_r2(the_shape, the_r1, the_r2, the_faces)

    def make_fillet_2d(self, the_shape: GEOM_Object, the_r: float, the_vertices: list) -> GEOM_Object:
        return self.local_operations.make_fillet2_d(the_shape, the_r, the_vertices)

    def make_fillet_1d(self, the_shape: GEOM_Object, the_r: float, the_vertices: list, do_ignore_secant_vertices = True) -> GEOM_Object:
        return self.local_operations.make_fillet1_d(the_shape, the_r, the_vertices, do_ignore_secant_vertices)

    def make_chamfer_all(self, the_shape: GEOM_Object, the_d: float) -> GEOM_Object:
        return self.local_operations.make_chamfer_all(the_shape, the_d)

    def make_chamfer_edge(self, the_shape: GEOM_Object, the_d1: float, the_d2: float, the_face1: int, the_face2: int) -> GEOM_Object:
        return self.local_operations.make_chamfer_edge(the_shape, the_d1, the_d2, the_face1, the_face2)

    def make_chamfer_edge_a_d(self, the_shape: GEOM_Object, the_d: float, the_angle: float, the_face1: int, the_face2: int) -> GEOM_Object:
        return self.local_operations.make_chamfer_edge_a_d(the_shape, the_d, the_angle, the_face1, the_face2)

    def make_chamfer_faces(self, the_shape: GEOM_Object, the_d1: float, the_d2: float, the_faces: list) -> GEOM_Object:
        return self.local_operations.make_chamfer_faces(the_shape, the_d1, the_d2, the_faces)

    def make_chamfer_faces_a_d(self, the_shape: GEOM_Object, the_d: float, the_angle: float, the_faces: list) -> GEOM_Object:
        return self.local_operations.make_chamfer_faces_a_d(the_shape, the_d, the_angle, the_faces)

    def make_chamfer_edges(self, the_shape: GEOM_Object, the_d1: float, the_d2: float, the_edges: list) -> GEOM_Object:
        return self.local_operations.make_chamfer_edges(the_shape, the_d1, the_d2, the_edges)

    def make_chamfer_edges_a_d(self, the_shape: GEOM_Object, the_d: float, the_angle: float, the_edges: list) -> GEOM_Object:
        return self.local_operations.make_chamfer_edges_a_d(the_shape, the_d, the_angle, the_edges)

    def make_archimede(self, the_shape: GEOM_Object, the_weight: float, the_water_density: float, the_meshing_deflection: float) -> GEOM_Object:
        return self.local_operations.make_archimede(the_shape, the_weight, the_water_density, the_meshing_deflection)

    def get_sub_shape_index(self, the_shape: GEOM_Object, the_sub_shape: GEOM_Object) -> int:
        return self.local_operations.get_sub_shape_index(the_shape, the_sub_shape)

    """
    Methods for MeasureOperations
    """
    #def kind_of_shape(self, the_shape: GEOM_Object, the_integers: list, the_floats: list) -> ShapeKind:
    #    return self.measure_operations.kind_of_shape(the_shape, the_integers, the_floats)

    #def get_position(self, the_shape: GEOM_Object, ox: float, oy: float, oz: float, zx: float, zy: float, zz: float, xx: float, xy: float, xz: float) -> None:
    #    return self.measure_operations.get_position(the_shape, ox, oy, oz, zx, zy, zz, xx, xy, xz)

    def get_centre_of_mass(self, the_shape: GEOM_Object) -> GEOM_Object:
        return self.measure_operations.get_centre_of_mass(the_shape)

    def get_vertex_by_index(self, the_shape: GEOM_Object, the_index: int, the_use_ori: bool) -> GEOM_Object:
        return self.measure_operations.get_vertex_by_index(the_shape, the_index, the_use_ori)

    def get_normal(self, the_face: GEOM_Object) -> GEOM_Object:
        return self.measure_operations.get_normal(the_face)

    def get_normal_ref_point(self, the_face: GEOM_Object, the_optional_point: GEOM_Object) -> GEOM_Object:
        return self.measure_operations.get_normal_ref_point(the_face, the_optional_point)

    ## Get vector coordinates
    #  @return [x, y, z]
    #
    #  @ref tui_measurement_tools_page "Example"
    def vector_coordinates(self,Vector: GEOM_Object) -> GEOM_Object:
        """
        Get vector coordinates

        Returns:
            [x, y, z]
        """

        p1=self.get_first_vertex(Vector)
        p2=self.get_last_vertex(Vector)

        X1=self.point_coordinates(p1)
        X2=self.point_coordinates(p2)

        return (X2[0]-X1[0],X2[1]-X1[1],X2[2]-X1[2])


    ## Compute cross product
    #  @return vector w=u^v
    def cross_product(self, Vector1: GEOM_Object, Vector2: GEOM_Object) -> GEOM_Object:
        """
        Compute cross product

        Returns: vector w=u^v
        """
        u=self.vector_coordinates(Vector1)
        v=self.vector_coordinates(Vector2)
        w=self.make_vector(u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])

        return w

    ## Compute cross product
    #  @return dot product  p=u.v
    def dot_product(self, Vector1: GEOM_Object, Vector2: GEOM_Object) -> float:
        """
        Compute cross product

        Returns: dot product  p=u.v
        """
        u=self.vector_coordinates(Vector1)
        v=self.vector_coordinates(Vector2)
        p=u[0]*v[0]+u[1]*v[1]+u[2]*v[2]

        return p

    #def get_basic_properties(self, the_shape: GEOM_Object, the_tolerance: float, the_length: float, the_surf_area: float, the_volume: float) -> None:
    #    return self.measure_operations.get_basic_properties(the_shape, the_tolerance, the_length, the_surf_area, the_volume)

    #def get_inertia(self, the_shape: GEOM_Object, i11: float, i12: float, i13: float, i21: float, i22: float, i23: float, i31: float, i32: float, i33: float, ix: float, iy: float, iz: float) -> None:
    #    return self.measure_operations.get_inertia(the_shape, i11, i12, i13, i21, i22, i23, i31, i32, i33, ix, iy, iz)

    #def get_bounding_box(self, the_shape: GEOM_Object, precise: bool, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float) -> None:
    #    return self.measure_operations.get_bounding_box(the_shape, precise, xmin, xmax, ymin, ymax, zmin, zmax)

    def get_bounding_box_shape(self, the_shape: GEOM_Object, precise=False) -> GEOM_Object:
        return self.measure_operations.get_bounding_box_shape(the_shape, precise)

    def get_tolerance(self, the_shape: GEOM_Object, face_min: float, face_max: float, edge_min: float, edge_max: float, vert_min: float, vert_max: float) -> None:
        return self.measure_operations.get_tolerance(the_shape, face_min, face_max, edge_min, edge_max, vert_min, vert_max)

    def check_shape(self, the_shape: GEOM_Object, the_is_check_geom: bool, the_errors: list) -> bool:
        return self.measure_operations.check_shape(the_shape, the_is_check_geom, the_errors)

    def print_shape_errors(self, the_shape: GEOM_Object, the_errors: list) -> str:
        return self.measure_operations.print_shape_errors(the_shape, the_errors)

    def check_self_intersections(self, the_shape: GEOM_Object, the_check_level: SICheckLevel, the_intersections: list) -> bool:
        return self.measure_operations.check_self_intersections(the_shape, the_check_level, the_intersections)

    def check_self_intersections_fast(self, the_shape: GEOM_Object, deflection: float, tolerance: float, the_intersections: list) -> bool:
        return self.measure_operations.check_self_intersections_fast(the_shape, deflection, tolerance, the_intersections)

    def check_bop_arguments(self, the_shape: GEOM_Object) -> bool:
        return self.measure_operations.check_b_o_p_arguments(the_shape)

    #def fast_intersect(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, tolerance = 0.0, deflection = 1e-6, the_intersections1: list, the_intersections2: list) -> bool:
    #    return self.measure_operations.fast_intersect(the_shape1, the_shape2, tolerance, deflection, the_intersections1, the_intersections2)

    def is_good_for_solid(self, the_shape: GEOM_Object) -> str:
        return self.measure_operations.is_good_for_solid(the_shape)

    def what_is(self, the_shape: GEOM_Object) -> str:
        return self.measure_operations.what_is(the_shape)

    def are_coords_inside(self, the_shape: GEOM_Object, coords: list, tolerance: float) -> list:
        return self.measure_operations.are_coords_inside(the_shape, coords, tolerance)

    #def get_min_distance(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    #    return self.measure_operations.get_min_distance(the_shape1, the_shape2, x1, y1, z1, x2, y2, z2)

    #def closest_points(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, the_floats: list) -> int:
    #    return self.measure_operations.closest_points(the_shape1, the_shape2, the_floats)

    #def point_coordinates(self, the_shape: GEOM_Object) -> None:
    #    return self.measure_operations.point_coordinates(the_shape)

    def get_angle(self, the_line1: GEOM_Object, the_line2: GEOM_Object) -> float:
        return self.measure_operations.get_angle(the_line1, the_line2)

    def get_angle_btw_vectors(self, the_vec1: GEOM_Object, the_vec2: GEOM_Object) -> float:
        return self.measure_operations.get_angle_btw_vectors(the_vec1, the_vec2)

    def curve_curvature_by_param(self, the_curve: GEOM_Object, the_param: float) -> float:
        return self.measure_operations.curve_curvature_by_param(the_curve, the_param)

    def curve_curvature_by_point(self, the_curve: GEOM_Object, the_point: GEOM_Object) -> float:
        return self.measure_operations.curve_curvature_by_point(the_curve, the_point)

    def get_curve_location_by_parameter(self, the_curve: GEOM_Object, parameter: float) -> XYZ:
        return self.measure_operations.get_curve_location_by_parameter(the_curve, parameter)

    def max_surface_curvature_by_param(self, the_surf: GEOM_Object, the_u_param: float, the_v_param: float) -> float:
        return self.measure_operations.max_surface_curvature_by_param(the_surf, the_u_param, the_v_param)

    def max_surface_curvature_by_point(self, the_surf: GEOM_Object, the_point: GEOM_Object) -> float:
        return self.measure_operations.max_surface_curvature_by_point(the_surf, the_point)

    def min_surface_curvature_by_param(self, the_surf: GEOM_Object, the_u_param: float, the_v_param: float) -> float:
        return self.measure_operations.min_surface_curvature_by_param(the_surf, the_u_param, the_v_param)

    def min_surface_curvature_by_point(self, the_surf: GEOM_Object, the_point: GEOM_Object) -> float:
        return self.measure_operations.min_surface_curvature_by_point(the_surf, the_point)

    """
    EXTENSION Methods for MeasureOperations
    """

    def get_basic_properties(self, the_shape: GEOM_Object, the_tolerance = 1e-6) -> list:
        return self.ext_measure_operations.get_basic_properties(the_shape, the_tolerance)

    def kind_of_shape(self, the_shape: GEOM_Object) -> list:
        return self.ext_measure_operations.kind_of_shape(the_shape)

    def closest_points(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object) -> list:
        return self.ext_measure_operations.closest_points(the_shape1, the_shape2)

    def get_min_distance_components(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object) -> list:
        a_tuple = self.ext_measure_operations.get_min_distance(the_shape1, the_shape2)
        a_result = [a_tuple[0], a_tuple[4] - a_tuple[1], a_tuple[5] - a_tuple[2], a_tuple[6] - a_tuple[3]]
        return a_result

    def get_min_distance(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object) -> float:
        return self.ext_measure_operations.get_min_distance(the_shape1, the_shape2)[0]

    def point_coordinates(self, the_point: GEOM_Object) -> list: 
        return self.ext_measure_operations.point_coordinates(the_point)

    def fast_intersect(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, tolerance = 0.0, deflection = 1e-3) -> list:
        res =  self.ext_measure_operations.fast_intersect(the_shape1, the_shape2, tolerance, deflection)
        return res

    def get_inertia(self, the_shape: GEOM_Object) -> list:
        return self.ext_measure_operations.get_inertia(the_shape)

    def get_position(self, the_shape: GEOM_Object) -> list:
        return self.ext_measure_operations.get_position(the_shape)

    def bounding_box(self, the_shape: GEOM_Object, precise = False) -> list:
        return self.ext_measure_operations.bounding_box(the_shape, precise)

    def oriented_bounding_box(self, the_shape: GEOM_Object) -> list:
        """
        Return list structure:
            [ X_extension, Y_extension, Z_extension, bounding box shape ]
        """
        return self.ext_measure_operations.oriented_bounding_box(the_shape, False)

    """
    Methods for ShapeOperations
    """
    def make_edge(self, the_point1: GEOM_Object, the_point2: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.make_edge(the_point1, the_point2)

    def make_edge_on_curve_by_length(self, the_curve: GEOM_Object, the_length: float, the_start_point: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.make_edge_on_curve_by_length(the_curve, the_length, the_start_point)

    def make_edge_wire(self, the_wire: GEOM_Object, the_linear_tolerance: float, the_angular_tolerance: float) -> GEOM_Object:
        return self.shape_operations.make_edge_wire(the_wire, the_linear_tolerance, the_angular_tolerance)

    def make_wire(self, the_edges_and_wires: list, the_tolerance = 1e-7) -> GEOM_Object:
        return self.shape_operations.make_wire(the_edges_and_wires, the_tolerance)

    def make_face(self, the_wire: GEOM_Object, is_planar_wanted: bool) -> GEOM_Object:
        return self.shape_operations.make_face(the_wire, is_planar_wanted)

    def make_face_wires(self, the_wires: list, is_planar_wanted = True) -> GEOM_Object:
        return self.shape_operations.make_face_wires(the_wires, is_planar_wanted)

    def make_face_from_surface(self, the_face: GEOM_Object, the_wire: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.make_face_from_surface(the_face, the_wire)

    def make_face_with_constraints(self, the_constraints: list) -> GEOM_Object:
        return self.shape_operations.make_face_with_constraints(the_constraints)

    def make_shell(self, the_shapes: list) -> GEOM_Object:
        return self.shape_operations.make_shell(the_shapes)

    def make_solid_shells(self, the_shells: list) -> GEOM_Object:
        return self.shape_operations.make_solid_shells(the_shells)

    def make_compound(self, the_shapes: list) -> GEOM_Object:
        return self.shape_operations.make_compound(the_shapes)

    def make_solid_from_connected_faces(self, the_faces_or_shells: list, is_intersect: bool) -> GEOM_Object:
        return self.shape_operations.make_solid_from_connected_faces(the_faces_or_shells, is_intersect)

    def make_glue_faces(self, the_shapes: list, the_tolerance: float, do_keep_non_solids = True) -> GEOM_Object:
        return self.shape_operations.make_glue_faces(the_shapes, the_tolerance, do_keep_non_solids)

    def make_glue_faces_by_list(self, the_shapes: list, the_tolerance: float, the_faces: list, do_keep_non_solids: bool, do_glue_all_edges: bool) -> GEOM_Object:
        return self.shape_operations.make_glue_faces_by_list(the_shapes, the_tolerance, the_faces, do_keep_non_solids, do_glue_all_edges)

    def make_glue_edges(self, the_shapes: list, the_tolerance: float) -> GEOM_Object:
        return self.shape_operations.make_glue_edges(the_shapes, the_tolerance)

    def get_glue_shapes(self, the_shapes: list, the_tolerance: float, the_type: TopAbs_ShapeEnum) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_glue_shapes(the_shapes, the_tolerance, the_type)

    def make_glue_edges_by_list(self, the_shapes: list, the_tolerance: float, the_edges: list) -> GEOM_Object:
        return self.shape_operations.make_glue_edges_by_list(the_shapes, the_tolerance, the_edges)

    def get_existing_sub_objects_groups(self, the_shape: GEOM_Object, the_groups_only: bool) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_existing_sub_objects_groups(the_shape, the_groups_only)

    def get_existing_sub_objects(self, the_shape: GEOM_Object, the_types: int) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_existing_sub_objects(the_shape, the_types)

    def make_explode(self, the_shape: GEOM_Object, the_shape_type: TopAbs_ShapeEnum, is_sorted: bool, explode_type: ExplodeType) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.make_explode(the_shape, the_shape_type.value, is_sorted, explode_type)

    def extract_shapes_original(self, the_shape: GEOM_Object, the_shape_type: TopAbs_ShapeEnum, is_sorted: bool) -> TColStd_HSequenceOfTransient:
        return self.make_explode(the_shape, the_shape_type, is_sorted, ExplodeType.EXPLODE_NEW_EXCLUDE_MAIN) 

    def sub_shape_all_ids(self, the_shape: GEOM_Object, the_shape_type: int, is_sorted: bool, explode_type: ExplodeType) -> list:
        return self.shape_operations.sub_shape_all_i_ds(the_shape, the_shape_type, is_sorted, explode_type)

    def get_sub_shape(self, the_main_shape: GEOM_Object, the_i_d: int) -> GEOM_Object:
        return self.shape_operations.get_sub_shape(the_main_shape, the_i_d)

    def make_sub_shapes(self, the_main_shape: GEOM_Object, the_indices: list) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.make_sub_shapes(the_main_shape, the_indices)

    def get_sub_shape_index(self, the_main_shape: GEOM_Object, the_sub_shape: GEOM_Object) -> int:
        return self.shape_operations.get_sub_shape_index(the_main_shape, the_sub_shape)

    #def get_sub_shapes_indices(self, the_main_shape: GEOM_Object, the_sub_shapes: list) -> list:
    #    return self.shape_operations.get_sub_shapes_indices(the_main_shape, the_sub_shapes)

    def get_topology_index(self, the_main_shape: GEOM_Object, the_sub_shape: GEOM_Object) -> int:
        return self.shape_operations.get_topology_index(the_main_shape, the_sub_shape)

    def get_shape_type_string(self, the_shape: GEOM_Object) -> str:
        return self.shape_operations.get_shape_type_string(the_shape)

    def is_sub_shape_belongs_to(self, the_sub_object: GEOM_Object, the_object: GEOM_Object, the_sub_object_index = 0, the_object_index = 0) -> bool:
        return self.shape_operations.is_sub_shape_belongs_to(the_sub_object, the_sub_object_index, the_object, the_object_index)

    def number_of_sub_shapes(self, the_shape: GEOM_Object, the_shape_type: int) -> int:
        return self.shape_operations.number_of_sub_shapes(the_shape, the_shape_type)

    def reverse_shape(self, the_shapes: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.reverse_shape(the_shapes)

    def get_free_faces_ids(self, the_shape: GEOM_Object) -> list:
        return self.shape_operations.get_free_faces_i_ds(the_shape)

    def get_shared_shapes(self, the_shape1: GEOM_Object, the_shape2: GEOM_Object, the_shape_type: int) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shared_shapes(the_shape1, the_shape2, the_shape_type)

    def get_multi_shared_shapes(self, the_shapes: list, the_shape_type: int, the_multi_share=True) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_multi_shared_shapes(the_shapes, the_shape_type, the_multi_share)

    def get_shapes_on_plane(self, the_shape: GEOM_Object, the_shape_type: int, the_ax1: GEOM_Object, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_plane(the_shape, the_shape_type, the_ax1, the_state)

    def get_shapes_on_plane_with_location(self, the_shape: GEOM_Object, the_shape_type: int, the_ax1: GEOM_Object, the_pnt: GEOM_Object, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_plane_with_location(the_shape, the_shape_type, the_ax1, the_pnt, the_state)

    def get_shapes_on_cylinder(self, the_shape: GEOM_Object, the_shape_type: int, the_axis: GEOM_Object, the_radius: float, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_cylinder(the_shape, the_shape_type, the_axis, the_radius, the_state)

    def get_shapes_on_cylinder_with_location(self, the_shape: GEOM_Object, the_shape_type: int, the_axis: GEOM_Object, the_pnt: GEOM_Object, the_radius: float, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_cylinder_with_location(the_shape, the_shape_type, the_axis, the_pnt, the_radius, the_state)

    def get_shapes_on_sphere(self, the_shape: GEOM_Object, the_shape_type: int, the_center: GEOM_Object, the_radius: float, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_sphere(the_shape, the_shape_type, the_center, the_radius, the_state)

    def get_shapes_on_plane_ids(self, the_shape: GEOM_Object, the_shape_type: int, the_ax1: GEOM_Object, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_plane_i_ds(the_shape, the_shape_type, the_ax1, the_state)

    def get_shapes_on_plane_with_location_ids(self, the_shape: GEOM_Object, the_shape_type: int, the_ax1: GEOM_Object, the_pnt: GEOM_Object, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_plane_with_location_i_ds(the_shape, the_shape_type, the_ax1, the_pnt, the_state)

    def get_shapes_on_cylinder_ids(self, the_shape: GEOM_Object, the_shape_type: int, the_axis: GEOM_Object, the_radius: float, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_cylinder_i_ds(the_shape, the_shape_type, the_axis, the_radius, the_state)

    def get_shapes_on_cylinder_with_location_ids(self, the_shape: GEOM_Object, the_shape_type: int, the_axis: GEOM_Object, the_pnt: GEOM_Object, the_radius: float, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_cylinder_with_location_i_ds(the_shape, the_shape_type, the_axis, the_pnt, the_radius, the_state)

    def get_shapes_on_sphere_ids(self, the_shape: GEOM_Object, the_shape_type: int, the_center: GEOM_Object, the_radius: float, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_sphere_i_ds(the_shape, the_shape_type, the_center, the_radius, the_state)

    def get_shapes_on_quadrangle(self, the_shape: GEOM_Object, the_shape_type: int, the_top_left_point: GEOM_Object, the_top_right_point: GEOM_Object, the_bottom_left_point: GEOM_Object, the_bottom_right_point: GEOM_Object, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_quadrangle(the_shape, the_shape_type, the_top_left_point, the_top_right_point, the_bottom_left_point, the_bottom_right_point, the_state)

    def get_shapes_on_quadrangle_ids(self, the_shape: GEOM_Object, the_shape_type: int, the_top_left_point: GEOM_Object, the_top_right_point: GEOM_Object, the_bottom_left_point: GEOM_Object, the_bottom_right_point: GEOM_Object, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_quadrangle_i_ds(the_shape, the_shape_type, the_top_left_point, the_top_right_point, the_bottom_left_point, the_bottom_right_point, the_state)

    def get_shapes_on_cylinder_old(self, the_shape: GEOM_Object, the_shape_type: int, the_axis: GEOM_Object, the_radius: float) -> GEOM_Object:
        return self.shape_operations.get_shapes_on_cylinder_old(the_shape, the_shape_type, the_axis, the_radius)

    def get_shapes_on_sphere_old(self, the_shape: GEOM_Object, the_shape_type: int, the_center: GEOM_Object, the_radius: float) -> GEOM_Object:
        return self.shape_operations.get_shapes_on_sphere_old(the_shape, the_shape_type, the_center, the_radius)

    def get_in_place(self, the_shape_where: GEOM_Object, the_shape_what: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.get_in_place(the_shape_where, the_shape_what)

    def get_in_place_old(self, the_shape_where: GEOM_Object, the_shape_what: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.get_in_place_old(the_shape_where, the_shape_what)

    def get_in_place_by_history(self, the_shape_where: GEOM_Object, the_shape_what: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.get_in_place_by_history(the_shape_where, the_shape_what)

    def get_in_place_map(self, the_shape_where: GEOM_Object, the_shape_what: GEOM_Object, the_res_vec: list) -> None:
        return self.shape_operations.get_in_place_map(the_shape_where, the_shape_what, the_res_vec)

    def get_same(self, the_shape_where: GEOM_Object, the_shape_what: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.get_same(the_shape_where, the_shape_what)

    def get_same_ids(self, the_shape_where: GEOM_Object, the_shape_what: GEOM_Object) -> list:
        return self.shape_operations.get_same_i_ds(the_shape_where, the_shape_what)

    def get_shapes_on_box_ids(self, the_box: GEOM_Object, the_shape: GEOM_Object, the_shape_type: int, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_box_i_ds(the_box, the_shape, the_shape_type, the_state)

    def get_shapes_on_box(self, the_box: GEOM_Object, the_shape: GEOM_Object, the_shape_type: int, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_box(the_box, the_shape, the_shape_type, the_state)

    def get_shapes_on_shape_ids(self, the_check_shape: GEOM_Object, the_shape: GEOM_Object, the_shape_type: int, the_state: GEOMAlgo_State) -> list:
        return self.shape_operations.get_shapes_on_shape_i_ds(the_check_shape, the_shape, the_shape_type, the_state)

    def get_shapes_on_shape(self, the_check_shape: GEOM_Object, the_shape: GEOM_Object, the_shape_type: int, the_state: GEOMAlgo_State) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_shapes_on_shape(the_check_shape, the_shape, the_shape_type, the_state)

    def get_shapes_on_shape_as_compound(self, the_check_shape: GEOM_Object, the_shape: GEOM_Object, the_shape_type: int, the_state: GEOMAlgo_State) -> GEOM_Object:
        return self.shape_operations.get_shapes_on_shape_as_compound(the_check_shape, the_shape, the_shape_type, the_state)

    def extend_edge(self, the_edge: GEOM_Object, the_min: float, the_max: float) -> GEOM_Object:
        return self.shape_operations.extend_edge(the_edge, the_min, the_max)

    def extend_face(self, the_face: GEOM_Object, the_u_min: float, the_u_max: float, the_v_min: float, the_v_max: float) -> GEOM_Object:
        return self.shape_operations.extend_face(the_face, the_u_min, the_u_max, the_v_min, the_v_max)

    def make_surface_from_face(self, the_face: GEOM_Object) -> GEOM_Object:
        return self.shape_operations.make_surface_from_face(the_face)

    def get_sub_shape_edge_sorted(self, the_shape: GEOM_Object, the_start_point: GEOM_Object) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_sub_shape_edge_sorted(the_shape, the_start_point)

    def get_sub_shapes_with_tolerance(self, the_shape: GEOM_Object, the_shape_type: int, the_condition: ComparisonCondition, the_tolerance: float) -> TColStd_HSequenceOfTransient:
        return self.shape_operations.get_sub_shapes_with_tolerance(the_shape, the_shape_type, the_condition, the_tolerance)

    #def make_extraction(self, the_shape: GEOM_Object, the_sub_shape_ids: list, the_stats: list) -> GEOM_Object:
    #    return self.field_operations.make_extraction(the_shape, the_sub_shape_i_ds, the_stats)

    """
    EXTENSION Methods for ShapeOperations
    """
    def extract_shapes(self, the_shape: GEOM_Object, the_shape_type: TopAbs_ShapeEnum, is_sorted = False) -> list:
        return self.ext_shape_operations.extract_shapes(the_shape, the_shape_type, is_sorted)

    def extract_shapes_sorted_centres(self, the_shape: GEOM_Object, the_shape_type: TopAbs_ShapeEnum) -> list:
        return self.ext_shape_operations.extract_shapes(the_shape, the_shape_type, True)

    def get_sub_shapes_indices(self, the_main_shape: GEOM_Object, the_sub_shapes: list) -> list:
        return self.ext_shape_operations.get_sub_shapes_indices(the_main_shape, the_sub_shapes)

    def get_visible_and_hidden_edges(self, main_shape: GEOM_Object, camera_position = [0,0,0], camera_direction = [0,0,1], should_include_hidden = True) -> list:
        """
        Expected input for camera position and direction is a list with three doubles:
            e.g. camera_position = [0, 0, 10] and camera_direction = [0, 0, -1]
        """
        return self.ext_shape_operations.get_visible_and_hidden_edges(main_shape, camera_position, camera_direction, should_include_hidden)

    """
    Methods for TransformOperations
    """
    def translate_two_points(self, the_object: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.translate_two_points(the_object, the_point1, the_point2)

    def translate_two_points_copy(self, the_object: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.translate_two_points_copy(the_object, the_point1, the_point2)

    def translate_dx_dy_dz(self, the_object: GEOM_Object, the_x: float, the_y: float, the_z: float) -> GEOM_Object:
        return self.transform_operations.translate_d_x_d_y_d_z(the_object, the_x, the_y, the_z)

    def translate_dx_dy_dz_copy(self, the_object: GEOM_Object, the_x: float, the_y: float, the_z: float) -> GEOM_Object:
        return self.transform_operations.translate_d_x_d_y_d_z_copy(the_object, the_x, the_y, the_z)

    def translate_vector(self, the_object: GEOM_Object, the_vector: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.translate_vector(the_object, the_vector)

    def translate_vector_copy(self, the_object: GEOM_Object, the_vector: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.translate_vector_copy(the_object, the_vector)

    def translate_vector_distance(self, the_object: GEOM_Object, the_vector: GEOM_Object, the_distance: float, the_copy: bool) -> GEOM_Object:
        return self.transform_operations.translate_vector_distance(the_object, the_vector, the_distance, the_copy)

    def translate_1d(self, the_object: GEOM_Object, the_vector: GEOM_Object, the_step: float, the_nb_times: int) -> GEOM_Object:
        return self.transform_operations.translate1_d(the_object, the_vector, the_step, the_nb_times)

    def translate_2d(self, the_object: GEOM_Object, the_vector: GEOM_Object, the_step1: float, the_nb_times1: int, the_vector2: GEOM_Object, the_step2: float, the_nb_times2: int) -> GEOM_Object:
        return self.transform_operations.translate2_d(the_object, the_vector, the_step1, the_nb_times1, the_vector2, the_step2, the_nb_times2)

    def mirror_plane(self, the_object: GEOM_Object, the_plane: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.mirror_plane(the_object, the_plane)

    def mirror_plane_copy(self, the_object: GEOM_Object, the_plane: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.mirror_plane_copy(the_object, the_plane)

    def mirror_axis(self, the_object: GEOM_Object, the_axis: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.mirror_axis(the_object, the_axis)

    def mirror_axis_copy(self, the_object: GEOM_Object, the_axis: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.mirror_axis_copy(the_object, the_axis)

    def mirror_point(self, the_object: GEOM_Object, the_point: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.mirror_point(the_object, the_point)

    def mirror_point_copy(self, the_object: GEOM_Object, the_point: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.mirror_point_copy(the_object, the_point)

    def offset_shape(self, the_object: GEOM_Object, the_offset: float, the_join_by_pipes: bool) -> GEOM_Object:
        return self.transform_operations.offset_shape(the_object, the_offset, the_join_by_pipes)

    def offset_shape_copy(self, the_object: GEOM_Object, the_offset: float, the_join_by_pipes: bool) -> GEOM_Object:
        return self.transform_operations.offset_shape_copy(the_object, the_offset, the_join_by_pipes)

    def project_shape_copy(self, the_source: GEOM_Object, the_target: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.project_shape_copy(the_source, the_target)

    def project_point_on_wire(self, the_point: GEOM_Object, the_wire: GEOM_Object, the_point_on_edge: GEOM_Object, the_edge_in_wire_index: int) -> float:
        return self.transform_operations.project_point_on_wire(the_point, the_wire, the_point_on_edge, the_edge_in_wire_index)

    def scale_shape(self, the_object: GEOM_Object, the_point: GEOM_Object, the_factor: float) -> GEOM_Object:
        return self.transform_operations.scale_shape(the_object, the_point, the_factor)

    def scale_shape_copy(self, the_object: GEOM_Object, the_point: GEOM_Object, the_factor: float) -> GEOM_Object:
        return self.transform_operations.scale_shape_copy(the_object, the_point, the_factor)

    def scale_shape_along_axes(self, the_object: GEOM_Object, the_point: GEOM_Object, the_factor_x: float, the_factor_y: float, the_factor_z: float, do_copy: bool) -> GEOM_Object:
        return self.transform_operations.scale_shape_along_axes(the_object, the_point, the_factor_x, the_factor_y, the_factor_z, do_copy)

    def position_shape(self, the_object: GEOM_Object, the_start_l_c_s: GEOM_Object, the_end_l_c_s: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.position_shape(the_object, the_start_l_c_s, the_end_l_c_s)

    def position_shape_copy(self, the_object: GEOM_Object, the_start_l_c_s: GEOM_Object, the_end_l_c_s: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.position_shape_copy(the_object, the_start_l_c_s, the_end_l_c_s)

    def position_along_path(self, the_object: GEOM_Object, the_path: GEOM_Object, the_distance: float, the_copy: bool, the_reverse: bool) -> GEOM_Object:
        return self.transform_operations.position_along_path(the_object, the_path, the_distance, the_copy, the_reverse)

    def rotate(self, the_object: GEOM_Object, the_axis: GEOM_Object, the_angle: float) -> GEOM_Object:
        return self.transform_operations.rotate(the_object, the_axis, the_angle)

    def rotate_copy(self, the_object: GEOM_Object, the_axis: GEOM_Object, the_angle: float) -> GEOM_Object:
        return self.transform_operations.rotate_copy(the_object, the_axis, the_angle)

    def rotate_1d(self, the_object: GEOM_Object, the_axis: GEOM_Object, the_nb_times: int) -> GEOM_Object:
        return self.transform_operations.rotate1_d(the_object, the_axis, the_nb_times)

    def rotate_1d_steps(self, the_object: GEOM_Object, the_axis: GEOM_Object, the_angle_step: float, the_nb_steps: int) -> GEOM_Object:
        return self.transform_operations.rotate1_d_steps(the_object, the_axis, the_angle_step, the_nb_steps)

    def rotate_2d(self, the_object: GEOM_Object, the_axis: GEOM_Object, the_nb_objects: int, the_radial_step: float, the_nb_steps: int) -> GEOM_Object:
        return self.transform_operations.rotate2_d(the_object, the_axis, the_nb_objects, the_radial_step, the_nb_steps)

    def rotate_2d_steps(self, the_object: GEOM_Object, the_axis: GEOM_Object, the_angle: float, the_nb_times1: int, the_step: float, the_nb_times2: int) -> GEOM_Object:
        return self.transform_operations.rotate2_d_steps(the_object, the_axis, the_angle, the_nb_times1, the_step, the_nb_times2)

    def rotate_three_points(self, the_object: GEOM_Object, the_cent_point: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.rotate_three_points(the_object, the_cent_point, the_point1, the_point2)

    def rotate_three_points_copy(self, the_object: GEOM_Object, the_cent_point: GEOM_Object, the_point1: GEOM_Object, the_point2: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.rotate_three_points_copy(the_object, the_cent_point, the_point1, the_point2)

    def transform_like_other_copy(self, the_object: GEOM_Object, the_sample: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.transform_like_other_copy(the_object, the_sample)

    def make_projection_on_cylinder(self, the_object: GEOM_Object, the_radius: float, the_start_angle: float, the_angle_length: float, the_angle_rotation: float) -> GEOM_Object:
        return self.transform_operations.make_projection_on_cylinder(the_object, the_radius, the_start_angle, the_angle_length, the_angle_rotation)

    def deep_copy(self, the_object: GEOM_Object) -> GEOM_Object:
        return self.transform_operations.deep_copy(the_object)