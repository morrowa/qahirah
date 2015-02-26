"""A Python 3 wrapper for the Cairo graphics library <http://cairographics.org/>
using ctypes. This is modelled on Pycairo, but differs from that in
some important ways. It also operates at a higher level than the underlying
Cairo API where this makes sense. For example, it defines a “Vector”
class for representing a 2D point, with operations on the Vector as a
whole, rather than having to operate on individual x- and y-coordinates.
Also, get/set API calls are collapsed into read/write Python properties
where this makes sense; for example, instead of Context.get_line_width()
and Context.set_line_width() calls, there is a Context.line_width property
that may be read and written.
"""
#+
# Copyright 2015 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import math
from numbers import \
    Number
import ctypes as ct

cairo = ct.cdll.LoadLibrary("libcairo.so.2")
ft = ct.cdll.LoadLibrary("libfreetype.so.6")
try :
    fc = ct.cdll.LoadLibrary("libfontconfig.so.1")
except OSError as fail :
    if True : # if fail.errno == 2 : # ENOENT
      # no point checking, because it is None! (Bug?)
        fc = None
    else :
        raise
    #end if
#end try

class CAIRO :
    "useful definitions adapted from cairo.h. You will need to use the constants," \
    " but apart from that, see the more Pythonic wrappers defined outside this" \
    " class in preference to accessing low-level structures directly."

    # General ctypes gotcha: when passing addresses of ctypes-constructed objects
    # to routine calls, do not construct the objects directly in the call. Otherwise
    # the refcount goes to 0 before the routine is actually entered, and the object
    # can get prematurely disposed. Always store the object reference into a local
    # variable, and pass the value of the variable instead.

    status_t = ct.c_uint

    # cairo_status_t codes
    STATUS_SUCCESS = 0

    STATUS_NO_MEMORY = 1
    STATUS_INVALID_RESTORE = 2
    STATUS_INVALID_POP_GROUP = 3
    STATUS_NO_CURRENT_POINT = 4
    STATUS_INVALID_MATRIX = 5
    STATUS_INVALID_STATUS = 6
    STATUS_NULL_POINTER = 7
    STATUS_INVALID_STRING = 8
    STATUS_INVALID_PATH_DATA = 9
    STATUS_READ_ERROR = 10
    STATUS_WRITE_ERROR = 11
    STATUS_SURFACE_FINISHED = 12
    STATUS_SURFACE_TYPE_MISMATCH = 13
    STATUS_PATTERN_TYPE_MISMATCH = 14
    STATUS_INVALID_CONTENT = 15
    STATUS_INVALID_FORMAT = 16
    STATUS_INVALID_VISUAL = 17
    STATUS_FILE_NOT_FOUND = 18
    STATUS_INVALID_DASH = 19
    STATUS_INVALID_DSC_COMMENT = 20
    STATUS_INVALID_INDEX = 21
    STATUS_CLIP_NOT_REPRESENTABLE = 22
    STATUS_TEMP_FILE_ERROR = 23
    STATUS_INVALID_STRIDE = 24
    STATUS_FONT_TYPE_MISMATCH = 25
    STATUS_USER_FONT_IMMUTABLE = 26
    STATUS_USER_FONT_ERROR = 27
    STATUS_NEGATIVE_COUNT = 28
    STATUS_INVALID_CLUSTERS = 29
    STATUS_INVALID_SLANT = 30
    STATUS_INVALID_WEIGHT = 31
    STATUS_INVALID_SIZE = 32
    STATUS_USER_FONT_NOT_IMPLEMENTED = 33
    STATUS_DEVICE_TYPE_MISMATCH = 34
    STATUS_DEVICE_ERROR = 35
    STATUS_INVALID_MESH_CONSTRUCTION = 36
    STATUS_DEVICE_FINISHED = 37

    STATUS_LAST_STATUS = 38

    # cairo_format_t codes
    FORMAT_INVALID = -1
    FORMAT_ARGB32 = 0
    FORMAT_RGB24 = 1
    FORMAT_A8 = 2
    FORMAT_A1 = 3
    FORMAT_RGB16_565 = 4
    FORMAT_RGB30 = 5

    # cairo_content_t codes
    CONTENT_COLOR =  0x1000
    CONTENT_ALPHA = 0x2000
    CONTENT_COLOR_ALPHA = 0x3000

    # cairo_extend_t codes
    EXTEND_NONE = 0
    EXTEND_REPEAT = 1
    EXTEND_REFLECT = 2
    EXTEND_PAD = 3

    # cairo_filter_t codes
    FILTER_FAST = 0
    FILTER_GOOD = 1
    FILTER_BEST = 2
    FILTER_NEAREST = 3
    FILTER_BILINEAR = 4
    FILTER_GAUSSIAN = 5

    # cairo_operator_t codes
    OPERATOR_CLEAR = 0

    OPERATOR_SOURCE = 1
    OPERATOR_OVER = 2
    OPERATOR_IN = 3
    OPERATOR_OUT = 4
    OPERATOR_ATOP = 5

    OPERATOR_DEST = 6
    OPERATOR_DEST_OVER = 7
    OPERATOR_DEST_IN = 8
    OPERATOR_DEST_OUT = 9
    OPERATOR_DEST_ATOP = 10

    OPERATOR_XOR = 11
    OPERATOR_ADD = 12
    OPERATOR_SATURATE = 13

    OPERATOR_MULTIPLY = 14
    OPERATOR_SCREEN = 15
    OPERATOR_OVERLAY = 16
    OPERATOR_DARKEN = 17
    OPERATOR_LIGHTEN = 18
    OPERATOR_COLOR_DODGE = 19
    OPERATOR_COLOR_BURN = 20
    OPERATOR_HARD_LIGHT = 21
    OPERATOR_SOFT_LIGHT = 22
    OPERATOR_DIFFERENCE = 23
    OPERATOR_EXCLUSION = 24
    OPERATOR_HSL_HUE = 25
    OPERATOR_HSL_SATURATION = 26
    OPERATOR_HSL_COLOR = 27
    OPERATOR_HSL_LUMINOSITY = 28

    class matrix_t(ct.Structure) :
        _fields_ = \
            [
                ("xx", ct.c_double),
                ("yx", ct.c_double),
                ("xy", ct.c_double),
                ("yy", ct.c_double),
                ("x0", ct.c_double),
                ("y0", ct.c_double),
            ]
    #end matrix_t

    # cairo_antialias_t codes
    ANTIALIAS_DEFAULT = 0
    # method
    ANTIALIAS_NONE = 1
    ANTIALIAS_GRAY = 2
    ANTIALIAS_SUBPIXEL = 3
    # hints
    ANTIALIAS_FAST = 4
    ANTIALIAS_GOOD = 5
    ANTIALIAS_BEST = 6

    # cairo_subpixel_order_t codes
    SUBPIXEL_ORDER_DEFAULT = 0
    SUBPIXEL_ORDER_RGB = 1
    SUBPIXEL_ORDER_BGR = 2
    SUBPIXEL_ORDER_VRGB = 3
    SUBPIXEL_ORDER_VBGR = 4

    # cairo_hint_style_t codes
    HINT_STYLE_DEFAULT = 0
    HINT_STYLE_NONE = 1
    HINT_STYLE_SLIGHT = 2
    HINT_STYLE_MEDIUM = 3
    HINT_STYLE_FULL = 4

    # cairo_hint_metrics_t codes
    HINT_METRICS_DEFAULT = 0
    HINT_METRICS_OFF = 1
    HINT_METRICS_ON = 2

    # cairo_fill_rule_t codes
    FILL_RULE_WINDING = 0
    FILL_RULE_EVEN_ODD = 1

    # cairo_line_cap_t codes
    LINE_CAP_BUTT = 0
    LINE_CAP_ROUND = 1
    LINE_CAP_SQUARE = 2

    # cairo_line_join_t codes
    LINE_JOIN_MITER = 0
    LINE_JOIN_ROUND = 1
    LINE_JOIN_BEVEL = 2

    # cairo_path_data_type_t codes
    PATH_MOVE_TO = 0
    PATH_LINE_TO = 1
    PATH_CURVE_TO = 2
    PATH_CLOSE_PATH = 3
    path_data_type_t = ct.c_uint

    class path_data_t(ct.Union) :

        class header_t(ct.Structure) :
            "followed by header_t.length point_t structs."
            _fields_ = \
                [
                    ("type", ct.c_uint), # path_data_type_t
                    ("length", ct.c_int), # number of following points
                ]
        #end header_t
        header_ptr_t = ct.POINTER(header_t)

        class point_t(ct.Structure) :
            _fields_ = \
                [
                    ("x", ct.c_double),
                    ("y", ct.c_double),
                ]
        #end point_t
        point_ptr_t = ct.POINTER(point_t)

        _fields_ = \
            [
                ("header", header_t),
                ("point" , point_t),
            ]

    #end path_data_t
    path_data_t_ptr = ct.POINTER(path_data_t)

    class path_t(ct.Structure) :
        pass
    path_t._fields_ = \
        [
            ("status", status_t),
            ("data", ct.c_void_p), # path_data_t_ptr
            ("num_data", ct.c_int), # number of elements in data
        ]
    #end path_t
    path_ptr_t = ct.POINTER(path_t)

    class rectangle_t(ct.Structure) :
        _fields_ = \
            [
                ("x", ct.c_double),
                ("y", ct.c_double),
                ("width", ct.c_double),
                ("height", ct.c_double),
            ]
    #end rectangle_t
    rectangle_ptr_t = ct.POINTER(rectangle_t)

    class rectangle_list_t(ct.Structure) :
        pass
    rectangle_list_t._fields_ = \
        [
            ("status", status_t),
            ("rectangles", rectangle_ptr_t),
            ("num_rectangles", ct.c_int),
        ]
    #end rectangle_list_t
    rectangle_list_ptr_t = ct.POINTER(rectangle_list_t)

    class glyph_t(ct.Structure) :
        _fields_ = \
            [
                ("index", ct.c_ulong), # glyph index
                ("x", ct.c_double), # position relative to origin
                ("y", ct.c_double),
            ]
    #end glyph_t

    # cairo_font_type_t codes
    FONT_TYPE_TOY = 0
    FONT_TYPE_FT = 1
    FONT_TYPE_WIN32 = 2
    FONT_TYPE_QUARTZ = 3
    FONT_TYPE_USER = 4

    destroy_func_t = ct.CFUNCTYPE(None, ct.c_void_p)

#end CAIRO

#+
# Routine arg/result types
#-

cairo.cairo_version_string.restype = ct.c_char_p
cairo.cairo_status_to_string.restype = ct.c_char_p

cairo.cairo_status.argtypes = (ct.c_void_p,)
cairo.cairo_create.argtypes = (ct.c_void_p,)
cairo.cairo_create.restype = ct.c_void_p
cairo.cairo_destroy.restype = ct.c_void_p
cairo.cairo_save.argtypes = (ct.c_void_p,)
cairo.cairo_restore.argtypes = (ct.c_void_p,)
cairo.cairo_get_target.restype = ct.c_void_p
cairo.cairo_get_target.argtypes = (ct.c_void_p,)
cairo.cairo_push_group.argtypes = (ct.c_void_p,)
cairo.cairo_push_group_with_content.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_pop_group.restype = ct.c_void_p
cairo.cairo_pop_group.argtypes = (ct.c_void_p,)
cairo.cairo_pop_group_to_source.argtypes = (ct.c_void_p,)
cairo.cairo_get_group_target.restype = ct.c_void_p
cairo.cairo_get_group_target.argtypes = (ct.c_void_p,)

cairo.cairo_copy_path.argtypes = (ct.c_void_p,)
cairo.cairo_copy_path.restype = ct.c_void_p
cairo.cairo_copy_path_flat.argtypes = (ct.c_void_p,)
cairo.cairo_copy_path_flat.restype = ct.c_void_p
cairo.cairo_append_path.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_has_current_point.argtypes = (ct.c_void_p,)
cairo.cairo_get_current_point.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_new_path.argtypes = (ct.c_void_p,)
cairo.cairo_new_sub_path.argtypes = (ct.c_void_p,)
cairo.cairo_close_path.argtypes = (ct.c_void_p,)
cairo.cairo_arc.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_arc_negative.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_curve_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_line_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_move_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_rectangle.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_glyph_path.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int)
cairo.cairo_text_path.argtypes = (ct.c_void_p, ct.c_char_p)
cairo.cairo_rel_curve_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_rel_line_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_rel_move_to.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_path_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)

cairo.cairo_translate.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_scale.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_rotate.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_transform.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_set_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_identity_matrix.argtypes = (ct.c_void_p,)
cairo.cairo_user_to_device.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_user_to_device_distance.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_device_to_user.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_device_to_user_distance.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)

cairo.cairo_image_surface_create.restype = ct.c_void_p
cairo.cairo_get_source.argtypes = (ct.c_void_p,)
cairo.cairo_get_source.restype = ct.c_void_p
cairo.cairo_set_source_rgb.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_set_source_rgba.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_set_source.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_get_antialias.argtypes = (ct.c_void_p,)
cairo.cairo_set_dash.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int, ct.c_double)
cairo.cairo_get_dash_count.argtypes = (ct.c_void_p,)
cairo.cairo_get_dash.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_set_antialias.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_set_fill_rule.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_fill_rule.argtypes = (ct.c_void_p,)
cairo.cairo_set_line_cap.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_line_cap.argtypes = (ct.c_void_p,)
cairo.cairo_set_line_join.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_line_join.argtypes = (ct.c_void_p,)
cairo.cairo_get_line_width.argtypes = (ct.c_void_p,)
cairo.cairo_get_line_width.restype = ct.c_double
cairo.cairo_set_line_width.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_get_miter_limit.restype = ct.c_double
cairo.cairo_set_miter_limit.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_get_operator.argtypes = (ct.c_void_p,)
cairo.cairo_set_operator.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_get_tolerance.restype = ct.c_double
cairo.cairo_set_tolerance.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_clip.argtypes = (ct.c_void_p,)
cairo.cairo_clip_preserve.argtypes = (ct.c_void_p,)
cairo.cairo_clip_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_in_clip.restype = ct.c_bool
cairo.cairo_in_clip.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_copy_clip_rectangle_list.restype = CAIRO.rectangle_list_ptr_t
cairo.cairo_copy_clip_rectangle_list.argtypes = (ct.c_void_p,)
cairo.cairo_rectangle_list_destroy.argtypes = (CAIRO.rectangle_list_ptr_t,)
cairo.cairo_reset_clip.argtypes = (ct.c_void_p,)
cairo.cairo_fill.argtypes = (ct.c_void_p,)
cairo.cairo_fill_preserve.argtypes = (ct.c_void_p,)
cairo.cairo_fill_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_in_fill.restype = ct.c_bool
cairo.cairo_in_fill.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_mask.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_mask_surface.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_double, ct.c_double)
cairo.cairo_paint.argtypes = (ct.c_void_p,)
cairo.cairo_paint_with_alpha.argtypes = (ct.c_void_p, ct.c_double)
cairo.cairo_stroke.argtypes = (ct.c_void_p,)
cairo.cairo_stroke_preserve.argtypes = (ct.c_void_p,)
cairo.cairo_stroke_extents.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_in_stroke.restype = ct.c_bool
cairo.cairo_in_stroke.argtypes = (ct.c_void_p, ct.c_double, ct.c_double)

cairo.cairo_path_destroy.argtypes = (ct.c_void_p,)

cairo.cairo_surface_reference.restype = ct.c_void_p
cairo.cairo_surface_reference.argtypes = (ct.c_void_p,)
cairo.cairo_surface_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_surface_flush.argtypes = (ct.c_void_p,)
cairo.cairo_surface_write_to_png.argtypes = (ct.c_void_p, ct.c_char_p)
cairo.cairo_image_surface_create.restype = ct.c_void_p
cairo.cairo_image_surface_get_format.argtypes = (ct.c_void_p,)
cairo.cairo_image_surface_get_width.argtypes = (ct.c_void_p,)
cairo.cairo_image_surface_get_height.argtypes = (ct.c_void_p,)
cairo.cairo_image_surface_get_stride.argtypes = (ct.c_void_p,)

cairo.cairo_pattern_status.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_reference.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_reference.restype = ct.c_void_p
cairo.cairo_pattern_add_color_stop_rgb.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_add_color_stop_rgba.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_get_color_stop_count.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_get_color_stop_rgba.argtypes = (ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_create_rgb.argtypes = (ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_create_rgb.restype = ct.c_void_p
cairo.cairo_pattern_create_rgba.argtypes = (ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_create_rgba.restype = ct.c_void_p
cairo.cairo_pattern_get_rgba.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_create_for_surface.restype = ct.c_void_p
cairo.cairo_pattern_create_for_surface.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_create_linear.argtypes = (ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_create_linear.restype = ct.c_void_p
cairo.cairo_pattern_get_linear_points.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_create_radial.argtypes = (ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
cairo.cairo_pattern_get_radial_circles.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_get_extend.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_set_extend.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_pattern_get_filter.argtypes = (ct.c_void_p,)
cairo.cairo_pattern_set_filter.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_pattern_get_surface.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_get_matrix.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_pattern_set_matrix.argtypes = (ct.c_void_p, ct.c_void_p)

cairo.cairo_font_options_status.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_create.restype = ct.c_void_p
cairo.cairo_font_options_destroy.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_copy.restype = ct.c_void_p
cairo.cairo_font_options_copy.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_merge.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_font_options_equal.argtypes = (ct.c_void_p, ct.c_void_p)
cairo.cairo_font_options_equal.restype = ct.c_bool
cairo.cairo_font_options_get_antialias.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_antialias.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_font_options_get_subpixel_order.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_subpixel_order.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_font_options_get_hint_style.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_hint_style.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_font_options_get_hint_metrics.argtypes = (ct.c_void_p,)
cairo.cairo_font_options_set_hint_metrics.argtypes = (ct.c_void_p, ct.c_int)

cairo.cairo_font_face_status.argtypes = (ct.c_void_p,)
cairo.cairo_font_face_get_type.argtypes = (ct.c_void_p,)
cairo.cairo_ft_font_face_create_for_ft_face.argtypes = (ct.c_void_p, ct.c_int)
cairo.cairo_ft_font_face_create_for_ft_face.restype = ct.c_void_p
cairo.cairo_ft_font_face_create_for_pattern.argtypes = (ct.c_void_p,)
cairo.cairo_ft_font_face_create_for_pattern.restype = ct.c_void_p
cairo.cairo_font_face_set_user_data.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p)
cairo.cairo_ft_font_options_substitute.argtypes = (ct.c_void_p, ct.c_void_p)

if fc != None :
    fc.FcInit.restype = ct.c_bool
    fc.FcNameParse.argtypes = (ct.c_char_p,)
    fc.FcNameParse.restype = ct.c_void_p
    fc.FcConfigSubstitute.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_int)
    fc.FcConfigSubstitute.restype = ct.c_bool
    fc.FcDefaultSubstitute.argtypes = (ct.c_void_p,)
    fc.FcDefaultSubstitute.restype = None
    fc.FcPatternDestroy.argtypes = (ct.c_void_p,)
    fc.FcPatternDestroy.restype = None

    class _FC :
        # minimal Fontconfig interface, just sufficient for my needs.

        FcMatchPattern = 0
        FcResultMatch = 0

    #end _FC

    class _FcPatternManager :
        # context manager which collects a list of FcPattern objects requiring disposal.

        def __init__(self) :
            self.to_dispose = []
        #end __init__

        def __enter__(self) :
            return \
                self
        #end __enter__

        def collect(self, pattern) :
            "collects another FcPattern reference to be disposed."
            # c_void_p function results are peculiar: they return integers
            # for non-null values, but None for null.
            if pattern != None :
                self.to_dispose.append(pattern)
            #end if
            return \
                pattern
        #end collect

        def __exit__(self, exception_type, exception_value, traceback) :
            for pattern in self.to_dispose :
                fc.FcPatternDestroy(pattern)
            #end for
        #end __exit__

    #end _FcPatternManager

#end if

ft_lib = None
ft_destroy_key = ct.c_int() # dummy address

def _ensure_ft() :
    # ensures FreeType is usable, raising suitable exceptions if not.
    global ft_lib
    if ft_lib == None :
        lib = ct.c_void_p()
        status = ft.FT_Init_FreeType(ct.byref(lib))
        if status != 0 :
            raise RuntimeError("Error %d initializing FreeType" % status)
        #end if
        ft_lib = lib.value
    #end if
#end _ensure_ft

fc_inited = False

def _ensure_fc() :
    # ensures Fontconfig is usable, raising suitable exceptions if not.
    global fc_inited
    if not fc_inited :
        if fc == None :
            raise NotImplementedError("Fontconfig not available")
        #end if
        if not fc.FcInit() :
            raise RuntimeError("failed to initialize Fontconfig.")
        #end if
        fc_inited = True
    #end if
#end _ensure_fc

#+
# Higher-level stuff begins here
#-

def version() :
    "returns the Cairo version as a single integer."
    return \
        cairo.cairo_version()
#end version

def version_tuple() :
    "returns the Cairo version as a triple of integers."
    vers = cairo.cairo_version()
    return \
        (vers // 10000, vers // 100 % 100, vers % 100)
#end version_tuple

def version_string() :
    "returns the Cairo version string."
    return \
        cairo.cairo_version_string().decode("utf-8")
#end version_string

def status_to_string(status) :
    "returns the message for a given Cairo status code."
    return \
        cairo.cairo_status_to_string(status).decode("utf-8")
#end status_to_string

def debug_reset_static_data() :
    cairo.cairo_debug_reset_static_data()
#end debug_reset_static_data

def check(status) :
    if status != 0 :
        raise CairoError(status)
    #end if
#end check

class CairoError(Exception) :
    "just to identify a Cairo-specific error exception."

    def __init__(self, code) :
        self.args = ("Cairo error %d -- %s" % (code, status_to_string(code)),)
    #end __init__

#end CairoError

deg = 180 / math.pi
  # All angles are in radians. You can use the standard Python functions math.degrees
  # and math.radians to convert back and forth, or multiply and divide by this deg
  # factor: divide by deg to convert degrees to radians, and multiply by deg to convert
  # the other way, e.g.
  #
  #     math.sin(45 / deg)
  #     math.atan(1) * deg

class Vector :
    "something missing from Cairo itself, a representation of a 2D point."

    def __init__(self, x, y) :
        self.x = x
        self.y = y
    #end __init__

    def to_tuple(self) :
        return \
            (self.x, self.y)
    #end to_tuple

    def __repr__(self) :
        return \
            "Vector(%.3f, %.3f)" % (self.x, self.y)
    #end __repr__

    def __getitem__(self, i) :
        "being able to access elements by index allows a Vector to be cast to a tuple or list."
        return \
            (self.x, self.y)[i]
    #end __getitem__

    def __add__(v1, v2) :
        return \
            (
                lambda : NotImplemented,
                lambda : Vector(v1.x + v2.x, v1.y + v2.y)
            )[isinstance(v2, Vector)]()
    #end __add__

    def __neg__(self) :
        "reflect across origin."
        return Vector \
          (
            x = - self.x,
            y = - self.y
          )
    #end __neg__

    def __sub__(v1, v2) :
        return \
            (
                lambda : NotImplemented,
                lambda : Vector(v1.x - v2.x, v1.y - v2.y)
            )[isinstance(v2, Vector)]()
    #end __sub__

    def __mul__(v, f) :
        if isinstance(f, Vector) :
            result = Vector(v.x * f.x, v.y * f.y)
        elif isinstance(f, Number) :
            result = Vector(v.x * f, v.y * f)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __mul__
    __rmul__ = __mul__

    def __truediv__(v, f) :
        if isinstance(f, Vector) :
            result = Vector(v.x / f.x, v.y / f.y)
        elif isinstance(f, Number) :
            result = Vector(v.x / f, v.y / f)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __truediv__

    @staticmethod
    def unit(angle) :
        "returns the unit vector with the specified direction."
        return \
            Vector(math.cos(angle), math.sin(angle))
    #end unit

    def rotate(self, angle) :
        "returns the Vector rotated by the specified angle."
        cos = math.cos(angle)
        sin = math.sin(angle)
        return \
            Vector(self.x * cos - self.y * sin, self.x * sin + self.y * cos)
    #end rotate

    def __abs__(self) :
        "use abs() to get the length of a Vector."
        return \
            math.hypot(self.x, self.y)
    #end __abs__

    def angle(self) :
        "returns the Vector’s rotation angle."
        return \
            math.atan2(self.y, self.x)
    #end angle

    @staticmethod
    def from_polar(length, angle) :
        "constructs a Vector from a length and a direction."
        return \
            Vector(length * math.cos(angle), length * math.sin(angle))
    #end from_polar

#end Vector

class Matrix :
    "representation of a 3-by-2 affine homogeneous matrix."

    def __init__(self, xx, yx, xy, yy, x0, y0) :
        self.xx = xx
        self.yx = yx
        self.xy = xy
        self.yy = yy
        self.x0 = x0
        self.y0 = y0
        # self.u = 0
        # self.v = 0
        # self.w = 1
    #end __init__

    @staticmethod
    def from_cairo(m) :
        return \
            Matrix(m.xx, m.yx, m.xy, m.yy, m.x0, m.y0)
    #end from_cairo

    def to_cairo(m) :
        return \
            CAIRO.matrix_t(m.xx, m.yx, m.xy, m.yy, m.x0, m.y0)
    #end to_cairo

    @staticmethod
    def identity() :
        "returns an identity matrix."
        return Matrix(1, 0, 0, 1, 0, 0)
    #end identity

    def __mul__(m1, m2) :
        "returns concatenation with another Matrix."
        return Matrix \
          (
            xx = m1.xx * m2.xx + m1.xy * m2.yx,
            yx = m1.yx * m2.xx + m1.yy * m2.yx,
            xy = m1.xx * m2.xy + m1.xy * m2.yy,
            yy = m1.yx * m2.xy + m1.yy * m2.yy,
            x0 = m1.xx * m2.x0 + m1.xy * m2.y0 + m1.x0,
            y0 = m1.yx * m2.x0 + m1.yy * m2.y0 + m1.y0,
          )
    #end __mul__

    @staticmethod
    def translation(delta) :
        "returns a Matrix that translates by the specified delta Vector."
        return Matrix(1, 0, 0, 1, delta.x, delta.y)
    #end translation

    @staticmethod
    def scaling(factor) :
        "returns a matrix that scales by the specified scalar or Vector factors."
        if isinstance(factor, Number) :
            result = Matrix(factor, 0, 0, factor, 0, 0)
        elif isinstance(factor, Vector) :
            result = Matrix(factor.x, 0, 0, factor.y, 0, 0)
        else :
            raise TypeError("factor must be a number or a Vector")
        #end if
        return \
            result
    #end scaling

    @staticmethod
    def rotation(angle) :
        "returns a Matrix that rotates about the origin by the specified" \
        " angle in radians."
        cos = math.cos(angle)
        sin = math.sin(angle)
        return Matrix(cos, -sin, sin, cos, 0, 0)
    #end rotation

    def det(self) :
        "matrix determinant."
        return \
            (self.xx * self.yy - self.xy * self.yx)
    #end det

    def adj(self) :
        "matrix adjoint."
        return Matrix \
          (
            xx = self.yy,
            yx = - self.yx,
            xy = - self.xy,
            yy = self.xx,
            x0 = self.xy * self.y0 - self.yy * self.x0,
            y0 = self.yx * self.x0 - self.xx * self.y0,
          )
    #end adj

    def inv(self) :
        "matrix inverse computed using minors" \
        " <http://mathworld.wolfram.com/MatrixInverse.html>."
        adj = self.adj()
        det = self.det()
        return Matrix \
          (
            xx = adj.xx / det,
            yx = adj.yx / det,
            xy = adj.xy / det,
            yy = adj.yy / det,
            x0 = adj.x0 / det,
            y0 = adj.y0 / det,
          )
    #end inv

    def map(self, pt) :
        "maps a Vector through the Matrix."
        return Vector \
          (
            x = pt.x * self.xx + pt.y * self.xy + self.x0,
            y = pt.x * self.yx + pt.y * self.yy + self.y0
          )
    #end map

    def mapdelta(self, pt) :
        "maps a Vector through the Matrix, ignoring the translation part."
        return Vector \
          (
            x = pt.x * self.xx + pt.y * self.xy,
            y = pt.x * self.yx + pt.y * self.yy
          )
    #end mapdelta

    def mapiter(self, pts) :
        "maps an iterable of Vectors through the Matrix."
        pts = iter(pts)
        while True : # until pts raises StopIteration
            yield self.map(pts.next())
        #end while
    #end mapiter

    def mapdeltaiter(self, pts) :
        "maps an iterable of Vectors through the Matrix, ignoring the" \
        " translation part."
        pts = iter(pts)
        while True : # until pts raises StopIteration
            yield self.mapdelta(pts.next())
        #end while
    #end mapdeltaiter

    def __repr__(self) :
        return \
            (
                "Matrix(%f, %f, %f, %f, %f, %f)"
            %
                (
                    self.xx, self.yx,
                    self.xy, self.yy,
                    self.x0, self.y0,
                )
            )
    #end __repr__

#end Matrix

def interp(fract, p1, p2) :
    "returns the point along p1 to p2 at relative position fract."
    return (p2 - p1) * fract + p1
#end interp

def distribute(nrdivs, p1 = 0.0, p2 = 1.0, endincl = False) :
    "returns a sequence of nrdivs values evenly distributed over" \
    " [p1, p2) (if not endincl) or nrdivs + 1 values over [p1, p2] (if endincl)."
    interval = p2 - p1
    return tuple \
      (
        interval * (i / nrdivs) + p1
            for i in range(0, nrdivs + int(endincl))
      )
#end distribute

class Rect :
    "an axis-aligned rectangle. The constructor takes the left and top coordinates," \
    " and the width and height. Or use from_corners to construct one from two Vectors" \
    " representing opposite corners."

    def __init__(self, left, top, width, height) :
        self.left = left
        self.top = top
        self.width = width
        self.height = height
    #end __init__

    @staticmethod
    def from_corners(pt1, pt2) :
        min_x = min(pt1.x, pt2.x)
        max_x = max(pt1.x, pt2.x)
        min_y = min(pt1.y, pt2.y)
        max_y = max(pt1.y, pt2.y)
        return \
            Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    #end from_corners

    @staticmethod
    def from_cairo(r) :
        "converts a CAIRO.rectangle_t to a Rect."
        return \
            Rect(r.x, r.y, r.width, r.height)
    #end from_cairo

    @property
    def bottom(self) :
        return \
            self.top + self.height
    #end bottom

    @property
    def right(self) :
        return \
            self.left + self.width
    #end right

    @property
    def topleft(self) :
        "the top-left corner point."
        return \
            Vector(self.left, self.top)
    #end topleft

    @property
    def botright(self) :
        "the bottom-right corner point."
        return \
            Vector(self.left + self.width, self.top + self.height)
    #end botright

    @property
    def dimensions(self) :
        "the dimensions of the Rect as a Vector."
        return \
            Vector(self.width, self.height)
    #end dimensions

    @property
    def middle(self) :
        "the midpoint as a Vector."
        return \
            Vector(self.left + self.width / 2, self.top + self.height / 2)
    #end middle

    def __round__(self) :
        "returns the Rect with all coordinates rounded to integers."
        return \
            Rect(round(self.left), round(self.top), round(self.width), round(self.height))
    #end __round__

    def __add__(self, v) :
        "add a Rect to a Vector to return the Rect offset by the Vector."
        if isinstance(v, Vector) :
            result = Rect(self.left + v.x, self.top + v.y, self.width, self.height)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __add__

    def __sub__(self, v) :
        "subtract a Vector from a Rect to return the Rect offset in the" \
        " opposite direction to the Vector."
        if isinstance(v, Vector) :
            result = Rect(self.left - v.x, self.top - v.y, self.width, self.height)
        else :
            result = NotImplemented
        #end if
        return \
            result
    #end __sub__

    def __eq__(r1, r2) :
        "equality of two rectangles."
        return \
            (
                r1.left == r2.left
            and
                r1.top == r2.top
            and
                r1.width == r2.width
            and
                r1.height == r2.height
            )
    #end __eq__

    def __repr__(self) :
        return "Rect(%f, %f, %f, %f)" % (self.left, self.top, self.width, self.height)
    #end __repr__

    def position(self, relpt, halign = None, valign = None) :
        "returns a copy of this Rect repositioned relative to Vector relpt, horizontally" \
        " according to halign and vertically according to valign (if not None" \
        " in each case). halign = 0 means the left edge is on the point, while" \
        " halign = 1 means the right edge is on the point. Similarly valign = 0" \
        " means the top edge is on the point, while valign = 1 means the bottom" \
        " edge is on the point. Intermediate values correspond to intermediate" \
        " linearly-interpolated positions."
        left = self.left
        top = self.top
        if halign != None :
            left = relpt.x - interp(halign, 0, self.width)
        #end if
        if valign != None :
            top = relpt.y - interp(valign, 0, self.height)
        #end if
        return Rect(left = left, top = top, width = self.width, height = self.height)
    #end position

    def align(self, within, halign = None, valign = None) :
        "returns a copy of this Rect repositioned relative to within, which is" \
        " another Rect, horizontally according to halign and vertically according" \
        " to valign (if not None in each case). halign = 0 means the left edges" \
        " coincide, while halign = 1 means the right edges coincide. Similarly" \
        " valign = 0 means the top edges coincide, while valign = 1 means the" \
        " bottom edges coincide. Intermediate values correspond to intermediate" \
        " linearly-interpolated positions."
        left = self.left
        top = self.top
        if halign != None :
            left = interp(halign, within.left, within.left + within.width - self.width)
        #end if
        if valign != None :
            top = interp(valign, within.top, within.top + within.height - self.height)
        #end if
        return Rect(left = left, top = top, width = self.width, height = self.height)
    #end align

    def transform_to(self, dst) :
        "returns a Matrix which maps this Rect into dst Rect."
        return \
            (
                Matrix.translation(dst.topleft)
            *
                Matrix.scaling(dst.dimensions / self.dimensions)
            *
                Matrix.translation(- self.topleft)
            )
    #end transform_to

#end Rect

class Glyph :
    "specifies a glyph index and position relative to the origin."

    def __init__(self, index, pos) :
        if not isinstance(pos, Vector) :
            raise TypeError("pos is not a Vector")
        #end if
        self.index = index
        self.pos = pos
    #end __init__

#end Glyph

class Context :
    "a Cairo drawing context. Instantiate with a Surface object."
    # <http://cairographics.org/manual/cairo-cairo-t.html>

    def _check(self) :
        # check for error from last operation on this Context.
        check(cairo.cairo_status(self._cairobj))
    #end _check

    def __init__(self, surface) :
        self._cairobj = cairo.cairo_create(surface._cairobj)
        self._check()
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def save(self) :
        cairo.cairo_save(self._cairobj)
    #end save

    def restore(self) :
        cairo.cairo_restore(self._cairobj)
        self._check()
    #end restore

    @property
    def target(self) :
        "a copy of the current target Surface. Will not return the same" \
        " wrapper object each time, but Surface objects can be compared for equality," \
        " which means they reference the same underlying Cairo surface_t object."
        return \
            Surface(cairo.cairo_surface_reference(cairo.cairo_get_target(self._cairobj)))
    #end target

    def push_group(self) :
        cairo.cairo_push_group(self._cairobj)
    #end push_group

    def push_group_with_content(self, content) :
        "content is a CAIRO.CONTENT_xxx value."
        cairo.cairo_push_group_with_content(self._cairobj, content)
    #end push_group_with_content

    def pop_group(self) :
        return \
            Pattern(cairo.cairo_pop_group(self._cairobj))
    #end pop_group

    def pop_group_to_source(self) :
        cairo.cairo_pop_group_to_source(self._cairobj)
    #end pop_group_to_source

    @property
    def group_target(self) :
        return \
            Surface(cairo.cairo_get_group_target(self._cairobj))
    #end group_target

    @property
    def source(self) :
        "a copy of the current source Pattern. Will not return the same" \
        " wrapper object each time, but Pattern objects can be compared for equality," \
        " which means they reference the same underlying Cairo pattern_t object."
        return \
            Pattern(cairo.cairo_pattern_reference(cairo.cairo_get_source(self._cairobj)))
    #end source

    @source.setter
    def source(self, source) :
        if not isinstance(source, Pattern) :
            raise TypeError("source is not a Pattern")
        #end if
        cairo.cairo_set_source(self._cairobj, source._cairobj)
        self._check()
    #end source

    def set_source_rgb(self, r, g, b) :
        cairo.cairo_set_source_rgb(self._cairobj, r, g, b)
        self._check()
    #end set_source_rgb

    def set_source_rgba(self, r, g, b, a) :
        cairo.cairo_set_source_rgba(self._cairobj, r, g, b, a)
        self._check()
    #end set_source_rgba

    @property
    def antialias(self) :
        "the current antialias mode."
        return \
            cairo.cairo_get_antialias(self._cairobj)
    #end antialias

    @antialias.setter
    def antialias(self, antialias) :
        cairo.cairo_set_antialias(self._cairobj, antialias)
    #end antialias

    @property
    def dash(self) :
        "the current line dash setting, as a tuple of two items: the first is a tuple" \
        " of reals specifying alternating on- and off-lengths, the second is a real" \
        " specifying the starting offset."
        segs = (cairo.cairo_get_dash_count(self._cairobj) * ct.c_double)()
        offset = ct.c_double()
        cairo.cairo_get_dash(self._cairobj, ct.byref(segs), ct.byref(offset))
        return \
            (tuple(i for i in segs), offset.value)
    #end dash

    @dash.setter
    def dash(self, dashes) :
        segs, offset = dashes
        nrsegs = len(segs)
        csegs = (nrsegs * ct.c_double)()
        for i in range(nrsegs) :
            csegs[i] = segs[i]
        #end for
        cairo.cairo_set_dash(self._cairobj, ct.byref(csegs), nrsegs, offset)
    #end dash

    @property
    def fill_rule(self) :
        return \
            cairo.cairo_get_fill_rule(self._cairobj)
    #end fill_rule

    @fill_rule.setter
    def fill_rule(self, fill_rule) :
        cairo.cairo_set_fill_rule(self._cairobj, fill_rule)
    #end fill_rule

    @property
    def line_cap(self) :
        return \
            cairo.cairo_get_line_cap(self._cairobj)
    #end line_cap

    @line_cap.setter
    def line_cap(self, line_cap) :
        cairo.cairo_set_line_cap(self._cairobj, line_cap)
    #end line_cap

    @property
    def line_join(self) :
        return \
            cairo.cairo_get_line_join(self._cairobj)
    #end line_join

    @line_join.setter
    def line_join(self, line_join) :
        cairo.cairo_set_line_join(self._cairobj, line_join)
    #end line_join

    @property
    def line_width(self) :
        "the current stroke line width."
        return \
            cairo.cairo_get_line_width(self._cairobj)
    #end line_width

    @line_width.setter
    def line_width(self, width) :
        cairo.cairo_set_line_width(self._cairobj, width)
    #end line_width

    @property
    def miter_limit(self) :
        return \
            cairo.cairo_get_miter_limit(self._cairobj)
    #end miter_limit

    @miter_limit.setter
    def miter_limit(self, width) :
        cairo.cairo_set_miter_limit(self._cairobj, width)
    #end miter_limit

    @property
    def operator(self) :
        "the current drawing operator."
        return \
            cairo.cairo_get_operator(self._cairobj)
    #end operator

    @operator.setter
    def operator(self, op) :
        "sets a new drawing operator."
        cairo.cairo_set_operator(self._cairobj, int(op))
        self._check()
    #end operator

    @property
    def tolerance(self) :
        return \
            cairo.cairo_get_tolerance(self._cairobj)
    #end tolerance

    @tolerance.setter
    def tolerance(self, width) :
        cairo.cairo_set_tolerance(self._cairobj, width)
    #end tolerance

    def clip(self) :
        cairo.cairo_clip(self._cairobj)
    #end clip

    def clip_preserve(self) :
        cairo.cairo_clip_preserve(self._cairobj)
    #end clip_preserve

    @property
    def clip_extents(self) :
        "returns a Rect bounding the current clip."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_clip_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end clip_extents

    def in_clip(self, pt) :
        "is the given Vector pt within the current clip."
        return \
            cairo.cairo_in_clip(self._cairobj, pt.x, pt.y)
    #end in_clip

    @property
    def clip_rectangle_list(self) :
        "returns a copy of the current clip region as a list of Rects."
        rects = cairo.cairo_copy_clip_rectangle_list(self._cairobj)
        check(rects.contents.status)
        result = list(Rect.from_cairo(rects.contents.rectangles[i]) for i in range(rects.contents.num_rectangles))
        cairo.cairo_rectangle_list_destroy(rects)
        return \
            result
    #end clip_rectangle_list

    def reset_clip(self) :
        cairo.cairo_reset_clip(self._cairobj)
    #end reset_clip

    def fill(self) :
        cairo.cairo_fill(self._cairobj)
    #end fill

    def fill_preserve(self) :
        cairo.cairo_fill_preserve(self._cairobj)
    #end fill_preserve

    @property
    def fill_extents(self) :
        "returns a Rect bounding the current path if filled."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_fill_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end fill_extents

    def in_fill(self, pt) :
        "is the given Vector pt within the current path if filled."
        return \
            cairo.cairo_in_fill(self._cairobj, pt.x, pt.y)
    #end in_fill

    def mask(self, pattern) :
        if not isinstance(pattern, Pattern) :
            raise TypeError("pattern is not a Pattern")
        #end if
        cairo.cairo_mask(self._cairobj, pattern._cairobj)
    #end mask

    def mask_surface(self, surface, origin) :
        if not isinstance(surface, Surface) :
            raise TypeError("surface is not a Surface")
        #end if
        cairo.cairo_mask_surface(self._cairobj, surface._cairobj, origin.x, origin.y)
    #end mask_surface

    def paint(self) :
        cairo.cairo_paint(self._cairobj)
    #end paint

    def paint_with_alpha(self, alpha) :
        cairo.cairo_paint_with_alpha(self._cairobj, alpha)
    #end paint_with_alpha

    def stroke(self) :
        cairo.cairo_stroke(self._cairobj)
    #end stroke

    def stroke_preserve(self) :
        cairo.cairo_stroke_preserve(self._cairobj)
    #end stroke_preserve

    @property
    def stroke_extents(self) :
        "returns a Rect bounding the current path if stroked."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_stroke_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end stroke_extents

    def in_stroke(self, pt) :
        "is the given Vector pt within the current path if stroked."
        return \
            cairo.cairo_in_stroke(self._cairobj, pt.x, pt.y)
    #end in_stroke

    # TODO: copy/show page, user_data

    # paths <http://cairographics.org/manual/cairo-Paths.html>

    def copy_path(self) :
        return \
            Path(cairo.cairo_copy_path(self._cairobj))
    #end copy_path

    def copy_path_flat(self) :
        return \
            Path(cairo.cairo_copy_path_flat(self._cairobj))
    #end copy_path_flat

    def append_path(self, path) :
        if not isinstance(source, Path) :
            raise TypeError("path is not a Path")
        #end if
        cairo.cairo_append_path(self._cairobj, path._cairobj)
        self._check()
    #end append_path

    @property
    def has_current_point(self) :
        return \
            bool(cairo.cairo_has_current_point(self._cairobj))
    #end has_current_point

    @property
    def current_point(self) :
        if self.has_current_point :
            x = ct.c_double()
            y = ct.c_double()
            cairo.cairo_get_current_point(self._cairobj, ct.byref(x), ct.byref(y))
            result = Vector(x.value, y.value)
        else :
            result = None
        #end if
        return \
            result
    #end current_point

    def new_path(self) :
        cairo.cairo_new_path(self._cairobj)
    #end new_path

    def new_sub_path(self) :
        cairo.cairo_new_sub_path(self._cairobj)
    #end new_sub_path

    def close_path(self) :
        cairo.cairo_close_path(self._cairobj)
    #end close_path

    def arc(self, centre, radius, angle1, angle2) :
        cairo.cairo_arc(self._cairobj, centre.x, centre.y, radius, angle1, angle2)
    #end arc

    def arc_xy(self, xc, yc, radius, angle1, angle2) :
        cairo.cairo_arc(self._cairobj, xc, yc, radius, angle1, angle2)
    #end arc

    def arc_negative_xy(self, xc, yc, radius, angle1, angle2) :
        cairo.cairo_arc_negative(self._cairobj, xc, yc, radius, angle1, angle2)
    #end arc_negative_xy

    def curve_to(self, p1, p2, p3) :
        cairo.cairo_curve_to(self._cairobj, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
    #end curve_to

    def curve_to_xy(self, x1, y1, x2, y2, x3, y3) :
        cairo.cairo_curve_to(self._cairobj, x1, y1, x2, y2, x3, y3)
    #end curve_to_xy

    def line_to(self, p) :
        cairo.cairo_line_to(self._cairobj, p.x, p.y)
    #end line_to

    def line_to_xy(self, x, y) :
        cairo.cairo_line_to(self._cairobj, x, y)
    #end line_to_xy

    def move_to(self, p) :
        cairo.cairo_move_to(self._cairobj, p.x, p.y)
    #end move_to

    def move_to_xy(self, x, y) :
        cairo.cairo_move_to(self._cairobj, x, y)
    #end move_to_xy

    def rectangle(self, rect) :
        cairo.cairo_rectangle(self._cairobj, rect.left, rect.top, rect.width, rect.height)
    #end rectangle

    def glyph_path(self, glyphs) :
        "glyphs is a sequence of Glyph objects."
        nr_glyphs = len(glyphs)
        buf = (nr_glyphs * CAIRO.glyph_t)()
        for i in range(nr_glyphs) :
            src = glyphs[i]
            buf[i] = CAIRO.glyph_t(src.index, src.pos.x, src.pos.y)
        #end for
        cairo.cairo_glyph_path(self._cairobj, ct.byref(buf), nr_glyphs)
    #end glyph_path

    def text_path(self, text) :
        cairo.cairo_text_path(self._cairobj, text.encode("utf-8"))
    #end text_path

    def rel_curve_to(self, p1, p2, p3) :
        cairo.cairo_rel_curve_to(self._cairobj, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
    #end rel_curve_to

    def rel_curve_to_xy(self, x1, y1, x2, y2, x3, y3) :
        cairo.cairo_rel_curve_to(self._cairobj, x1, y1, x2, y2, x3, y3)
    #end rel_curve_to_xy

    def rel_line_to(self, p) :
        cairo.cairo_rel_line_to(self._cairobj, p.x, p.y)
    #end rel_line_to

    def rel_line_to_xy(self, x, y) :
        cairo.cairo_rel_line_to(self._cairobj, x, y)
    #end rel_line_to_xy

    def rel_move_to(self, p) :
        cairo.cairo_rel_move_to(self._cairobj, p.x, p.y)
    #end rel_move_to

    def rel_move_to_xy(self, x, y) :
        cairo.cairo_rel_move_to(self._cairobj, x, y)
    #end rel_move_to_xy

    @property
    def path_extents(self) :
        "returns a Rect bounding the current path."
        x1 = ct.c_double()
        x2 = ct.c_double()
        y1 = ct.c_double()
        y2 = ct.c_double()
        cairo.cairo_path_extents(self._cairobj, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2))
        return \
            Rect(x1.value, y1.value, x2.value - x1.value, y2.value - y1.value)
    #end path_extents

    # TODO: Regions <http://cairographics.org/manual/cairo-Regions.html>

    # Transformations <http://cairographics.org/manual/cairo-Transformations.html>

    def translate(self, t) :
        "applies a translation by the Vector t to the current coordinate system."
        cairo.cairo_translate(self._cairobj, t.x, t.y)
    #end translate

    def scale(self, s) :
        "applies a scaling by the Vector s to the current coordinate system."
        cairo.cairo_scale(self._cairobj, s.x, s.y)
    #end scale

    def rotate(self, angle) :
        "applies a rotation by the specified angle to the current coordinate system."
        cairo.cairo_rotate(self._cairobj, angle)
    #end rotate

    def transform(self, m) :
        m = m.to_cairo()
        cairo.cairo_transform(self._cairobj, ct.byref(m))
    #end transform

    @property
    def matrix(self) :
        "the current transformation matrix."
        result = CAIRO.matrix_t()
        cairo.cairo_get_matrix(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end matrix

    @matrix.setter
    def matrix(self, m) :
        m = m.to_cairo()
        cairo.cairo_set_matrix(self._cairobj, ct.byref(m))
        self._check()
    #end matrix

    def identity_matrix(self) :
        cairo.cairo_identity_matrix(self._cairobj)
    #end identity_matrix

    # TODO: user to/from device

    # TODO: Text <http://cairographics.org/manual/cairo-text.html>

#end Context

class Surface :
    "base class for Cairo surfaces. Do not instantiate directly."

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        check(cairo.cairo_surface_status(_cairobj))
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_surface_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def __eq__(self, other) :
        "do the two Surface objects refer to the same surface. Needed because" \
        " methods like Context.target and Pattern.surface cannot return the same" \
        " Surface object each time."
        return \
            self._cairobj == other._cairobj
    #end __eq__

    # TODO: create_similar, device, font_options etc
    # <http://cairographics.org/manual/cairo-cairo-surface-t.html>

    def flush(self) :
        cairo.cairo_surface_flush(self._cairobj)
    #end flush

    def write_to_png(self, filename) :
        check(cairo.cairo_surface_write_to_png(self._cairobj, filename.encode("utf-8")))
    #end write_to_png

    # TODO: user data

#end Surface

class ImageSurface(Surface) :
    "A Cairo image surface. Instantiate with a suitable CAIRO.FORMAT_xxx code" \
    " and desired integer dimensions."

    def __init__(self, format, width, height) :
        super().__init__(cairo.cairo_image_surface_create(int(format), int(width), int(height)))
    #end __init__

    @staticmethod
    def format_stride_for_width(format, width) :
        return \
            cairo.cairo_format_stride_for_width(int(format), int(width))
    #end format_stride_for_width

    # TODO: create_for_data, get_data

    @property
    def format(self) :
        return \
            cairo.cairo_image_surface_get_format(self._cairobj)
    #end format

    @property
    def width(self) :
        return \
            cairo.cairo_image_surface_get_width(self._cairobj)
    #end width

    @property
    def height(self) :
        return \
            cairo.cairo_image_surface_get_height(self._cairobj)
    #end height

    @property
    def stride(self) :
        return \
            cairo.cairo_image_surface_get_stride(self._cairobj)
    #end stride

#end ImageSurface

# TODO: PDF Surfaces, PNG Surfaces, PostScript Surfaces,
# Recording Surfaces, SVG Surfaces, Script Surfaces

class Pattern :
    "a Cairo Pattern object. Do not instantiate directly; use one of the create methods."
    # <http://cairographics.org/manual/cairo-cairo-pattern-t.html>

    def _check(self) :
        # check for error from last operation on this Pattern.
        check(cairo.cairo_pattern_status(self._cairobj))
    #end _check

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        self._check()
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_pattern_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def __eq__(self, other) :
        "do the two Pattern objects refer to the same Pattern. Needed because" \
        " Context.source cannot return the same Pattern object each time."
        return \
            self._cairobj == other._cairobj
    #end __eq__

    def add_color_stop_rgb(self, offset, r, g, b) :
        "adds an opaque colour stop. This must be a gradient Pattern."
        cairo.cairo_pattern_add_color_stop_rgb(self._cairobj, offset, r, g, b)
        self._check()
    #end add_color_stop_rgb

    def add_color_stop_rgba(self, offset, r, g, b, a) :
        "adds a colour stop. This must be a gradient Pattern."
        cairo.cairo_pattern_add_color_stop_rgba(self._cairobj, offset, r, g, b, a)
        self._check()
    #end add_color_stop_rgba

    @property
    def color_stops_rgba(self) :
        "a tuple of the currently-defined (offset, r, g, b, a) colour stops. This must" \
        " be a gradient Pattern."
        count = ct.c_int()
        check(cairo.cairo_pattern_get_color_stop_count(self._cairobj, ct.byref(count)))
        count = count.value
        result = []
        offset = ct.c_double()
        r = ct.c_double()
        g = ct.c_double()
        b = ct.c_double()
        a = ct.c_double()
        for i in range(count) :
            check(cairo.cairo_pattern_get_color_stop_rgba(self._cairobj, i, ct.byref(offset), ct.byref(r), ct.byref(g), ct.byref(b), ct.byref(a)))
            result.append((offset.value, r.value, g.value, b.value, a.value))
        #end for
        return \
            tuple(result)
    #end color_stops_rgba

    @staticmethod
    def create_rgb(r, g, b) :
        "creates a Pattern that paints the destination with the specified opaque (r, g, b) colour."
        return \
            Pattern(cairo.cairo_pattern_create_rgb(r, g, b))
    #end create_rgb

    @staticmethod
    def create_rgba(r, g, b, a) :
        "creates a Pattern that paints the destination with the specified (r, g, b, a) colour."
        return \
            Pattern(cairo.cairo_pattern_create_rgba(r, g, b, a))
    #end create_rgb

    @property
    def rgba(self) :
        "assumes the Pattern is a solid-colour pattern, returns its (r, g, b, a) colour."
        r = ct.c_double()
        g = ct.c_double()
        b = ct.c_double()
        a = ct.c_double()
        check(cairo.cairo_pattern_get_rgba(self._cairobj, ct.byref(r), ct.byref(g), ct.byref(g), ct.byref(a)))
        return \
            (r.value, g.value, b.value, a.value)
    #end rgba

    @staticmethod
    def create_for_surface(surface) :
        if not isinstance(surface, Surface) :
            raise TypeError("surface is not a Surface")
        #end if
        return \
            Pattern(cairo.cairo_pattern_create_for_surface(surface._cairobj))
    #end create_for_surface

    @property
    def surface(self) :
        "assuming there is a Surface for which this Pattern was created, returns the Surface."
        surf = ct.c_void_p()
        check(cairo.cairo_pattern_get_surface(self._cairobj, ct.byref(surf)))
        return \
            Surface(cairo.cairo_surface_reference(surf.value))
    #end surface

    @staticmethod
    def create_linear(p0, p1) :
        "creates a linear gradient Pattern that varies between the specified Vector" \
        " points in pattern space."
        return \
            Pattern(cairo.cairo_pattern_create_linear(p0.x, p0.y, p1.x, p1.y))
    #end create_linear

    @property
    def linear_p0(self) :
        "the first Vector point for a linear gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_linear_points(self._cairobj, ct.byref(x), ct.byref(y), None, None))
        return \
            Vector(x.value, y.value)
    #end linear_p0

    @property
    def linear_p1(self) :
        "the second Vector point for a linear gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_linear_points(self._cairobj, None, None, ct.byref(x), ct.byref(y)))
        return \
            Vector(x.value, y.value)
    #end linear_p1

    @staticmethod
    def create_radial(c0, r0, c1, r1) :
        "creates a radial gradient Pattern varying between the circle centred at Vector c0," \
        " radius r0 and the one centred at Vector c1, radius r1."
        return \
            Pattern(cairo.cairo_pattern_create_radial(c0.x, c0.y, r0, c1.x, c1.y, r1))
    #end create_radial

    @property
    def radial_c0(self) :
        "the centre of the start circle for a radial gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, ct.byref(x), ct.byref(y), None, None, None, None))
        return \
            Vector(x.value, y.value)
    #end radial_c0

    @property
    def radial_r0(self) :
        "the radius of the start circle for a radial gradient Pattern."
        r = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, None, None, ct.byref(r), None, None, None))
        return \
            r.value
    #end radial_r0

    @property
    def radial_c1(self) :
        "the centre of the end circle for a radial gradient Pattern."
        x = ct.c_double()
        y = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, None, None, None, ct.byref(x), ct.byref(y), None))
        return \
            Vector(x.value, y.value)
    #end radial_c1

    @property
    def radial_r1(self) :
        "the radius of the end circle for a radial gradient Pattern."
        r = ct.c_double()
        check(cairo.cairo_pattern_get_radial_circles(self._cairobj, None, None, None, None, None, ct.byref(r)))
        return \
            r.value
    #end radial_r1

    # TODO: mesh patterns

    @property
    def extend(self) :
        return \
            cairo.cairo_pattern_get_extend(self._cairobj)
    #end extend

    @extend.setter
    def extend(self, ext) :
        cairo.cairo_pattern_set_extend(self._cairobj, ext)
    #end extend

    @property
    def filter(self) :
        return \
            cairo.cairo_pattern_get_filter(self._cairobj)
    #end filter

    @filter.setter
    def filter(self, filt) :
        cairo.cairo_pattern_set_filter(self._cairobj, filt)
    #end filter

    @property
    def matrix(self) :
        result = CAIRO.matrix_t()
        cairo.cairo_pattern_get_matrix(self._cairobj, ct.byref(result))
        return \
            Matrix.from_cairo(result)
    #end matrix

    @matrix.setter
    def matrix(self, m) :
        m = m.to_cairo()
        cairo.cairo_pattern_set_matrix(self._cairobj, ct.byref(m))
    #end matrix

    # TODO: Raster Sources <http://cairographics.org/manual/cairo-Raster-Sources.html>

    # TODO: user data

#end Pattern

class Path :
    "a Cairo Path object. Do not instantiate directly."

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        check(ct.cast(self._cairobj, CAIRO.path_ptr_t).contents.status)
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_path_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    class Element :
        "base class for Path elements. Do not instantiate directly."

        def __init__(self, typ) :
            self.typ = typ
        #end __init__

        def draw(self, g) :
            raise NotImplementedError("subclass forgot to override")
        #end draw

    #end Element

    class MoveTo(Element) :
        "represents a move_to the specified Vector position."

        def __init__(self, p) :
            super().__init__(CAIRO.PATH_MOVE_TO)
            self.p = p
        #end __init__

        def draw(self, g) :
            "draws the element into the Context g."
            g.move_to(self.p)
        #end draw

        def __repr__(self) :
            return \
                "MoveTo(%s)" % self.p
        #end __repr__

    #end MoveTo

    class LineTo(Element) :
        "represents a line_to the specified Vector position."

        def __init__(self, p) :
            super().__init__(CAIRO.PATH_LINE_TO)
            self.p = p
        #end __init__

        def draw(self, g) :
            "draws the element into the Context g."
            g.line_to(self.p)
        #end draw

        def __repr__(self) :
            return \
                "LineTo(%s)" % self.p
        #end __repr__

    #end LineTo

    class CurveTo(Element) :
        "represents a curve_to via the specified three Vector positions."

        def __init__(self, p1, p2, p3) :
            super().__init__(CAIRO.PATH_CURVE_TO)
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
        #end __init__

        def draw(self, g) :
            "draws the element into the Context g."
            g.curve_to(self.p1, self.p2, self.p3)
        #end draw

        def __repr__(self) :
            return \
                "CurveTo(%s, %s, %s)" % (self.p1, self.p2, self.p3)
        #end __repr__

    #end CurveTo

    class Close(Element) :
        "represents a closing of the current path."

        def __init__(self) :
            super().__init__(CAIRO.PATH_CLOSE_PATH)
        #end __init__

        def draw(self, g) :
            "draws the element into the Context g."
            g.close_path()
        #end draw

        def __repr__(self) :
            return \
                "Close()"
        #end __repr__

    #end Close

    element_types = \
        { # number of control points and Element subclass for each path element type
            CAIRO.PATH_MOVE_TO : {"nr" : 1, "type" : MoveTo},
            CAIRO.PATH_LINE_TO : {"nr" : 1, "type" : LineTo},
            CAIRO.PATH_CURVE_TO : {"nr" : 3, "type" : CurveTo},
            CAIRO.PATH_CLOSE_PATH : {"nr" : 0, "type" : Close},
        }

    @property
    def elements(self) :
        "yields the elements of the path in turn, as a sequence of" \
        " Path.MoveTo, Path.LineTo, Path.CurveTo and Path.Close objects" \
        " as appropriate."
        data = ct.cast(self._cairobj, CAIRO.path_ptr_t).contents.data
        nrelts = ct.cast(self._cairobj, CAIRO.path_ptr_t).contents.num_data
        i = 0
        while True :
            if i == nrelts :
                break
            i += 1
            header = ct.cast(data, CAIRO.path_data_t.header_ptr_t).contents
            assert header.length == self.element_types[header.type]["nr"] + 1, "expecting %d control points for path elt type %d, got %d" % (self.element_types[header.type]["nr"] + 1, header.type, header.length)
            data += ct.sizeof(CAIRO.path_data_t)
            points = []
            for j in range(header.length - 1) :
                assert i < nrelts, "buffer overrun"
                i += 1
                point = ct.cast(data, CAIRO.path_data_t.point_ptr_t).contents
                points.append(Vector(point.x, point.y))
                data += ct.sizeof(CAIRO.path_data_t)
            #end for
            yield self.element_types[header.type]["type"](*points)
        #end for
    #end elements

#end Path

class FontOptions :
    "Cairo font options. Instantiate with no arguments to create a new font_options_t object."
    # <http://cairographics.org/manual/cairo-cairo-font-options-t.html>

    def _check(self) :
        # check for error from last operation on this FontOptions.
        check(cairo.cairo_font_options_status(self._cairobj))
    #end _check

    def __init__(self, existing = None) :
        if existing == None :
            self._cairobj = cairo.cairo_font_options_create()
        else :
            self._cairobj = existing
        #end if
        self._check()
    #end __init__

    def __del__(self) :
        if self._cairobj != None :
            cairo.cairo_font_options_destroy(self._cairobj)
            self._cairobj = None
        #end if
    #end __del__

    def copy(self) :
        "returns a copy of this FontOptions in a new object."
        return \
            FontOptions(cairo.cairo_font_options_copy(self._cairobj))
    #end copy

    def merge(self, other) :
        "merges non-default options from another FontOptions object."
        if not isinstance(other, FontOptions) :
            raise TypeError("can only merge with another FontOptions object")
        #end if
        cairo.cairo_font_options_merge(self._cairobj, other._cairobj)
        self._check()
    #end merge

    def __eq__(self, other) :
        "equality of settings in two FontOptions objects."
        if not isinstance(other, FontOptions) :
            raise TypeError("can only compare equality with another FontOptions object")
        #end if
        return \
            cairo.cairo_font_options_equal(self._cairobj, other._cairobj)
    #end __eq__

    @property
    def antialias(self) :
        "antialias mode for this FontOptions."
        return \
            cairo.cairo_font_options_get_antialias(self._cairobj)
    #end antialias

    @antialias.setter
    def antialias(self, anti) :
        cairo.cairo_font_options_set_antialias(self._cairobj, anti)
    #end antialias

    @property
    def subpixel_order(self) :
        "subpixel order for this FontOptions."
        return \
            cairo.cairo_font_options_get_subpixel_order(self._cairobj)
    #end subpixel_order

    @subpixel_order.setter
    def subpixel_order(self, sub) :
        cairo.cairo_font_options_set_subpixel_order(self._cairobj, sub)
    #end subpixel_order

    @property
    def hint_style(self) :
        "hint style for this FontOptions."
        return \
            cairo.cairo_font_options_get_hint_style(self._cairobj)
    #end hint_style

    @hint_style.setter
    def hint_style(self, hint) :
        cairo.cairo_font_options_set_hint_style(self._cairobj, hint)
    #end hint_style

    @property
    def hint_metrics(self) :
        "hint metrics for this FontOptions."
        return \
            cairo.cairo_font_options_get_hint_metrics(self._cairobj)
    #end hint_metrics

    @hint_metrics.setter
    def hint_metrics(self, hint) :
        cairo.cairo_font_options_set_hint_metrics(self._cairobj, hint)
    #end hint_metrics

    def __repr__(self) :
        return \
            (
                "FontOptions({%s})"
            %
                ", ".join
                  (
                    "%s = %d" % (name, getattr(self, name))
                    for name in ("antialias", "subpixel_order", "hint_style", "hint_metrics")
                  )
            )
    #end __repr__

#end FontOptions

class FontFace :
    "a general Cairo font object. Do not instantiate directly; use the create methods."
    # <http://cairographics.org/manual/cairo-cairo-font-face-t.html>

    def _check(self) :
        # check for error from last operation on this FontFace.
        check(cairo.cairo_font_face_status(self._cairobj))
    #end _check

    def __init__(self, _cairobj) :
        self._cairobj = _cairobj
        self._check()
    #end __init__

    @property
    def type(self) :
        "the type of font underlying this FontFace."
        return \
            cairo.cairo_font_face_get_type(self._cairobj)
    #end type

    @staticmethod
    def create_for_file(filename, face_index = 0, load_flags = 0) :
        "uses FreeType to load a font from the specified filename, and returns" \
        " a new FontFace for it."
        _ensure_ft()
        ft_face = ct.c_void_p()
        status = ft.FT_New_Face(ct.c_void_p(ft_lib), filename.encode("utf-8"), face_index, ct.byref(ft_face))
        if status != 0 :
            raise RuntimeError("Error %d loading FreeType font" % status)
        #end if
        try :
            cairo_face = cairo.cairo_ft_font_face_create_for_ft_face(ft_face.value, load_flags)
            result = FontFace(cairo_face)
            check(cairo.cairo_font_face_set_user_data
              (
                cairo_face,
                ct.byref(ft_destroy_key),
                ft_face.value,
                ft.FT_Done_Face
              ))
            ft_face = None # so I don't free it yet
        finally :
            if ft_face != None :
                ft.FT_Done_Face(ft_face)
            #end if
        #end try
        return \
            result
    #end create_for_file

    @staticmethod
    def create_for_pattern(pattern, options = None) :
        "uses Fontconfig to find a font matching the specified pattern string," \
        " uses FreeType to load the font, and returns a new FontFace for it." \
        " options, if present, must be a FontOptions object."
        _ensure_ft()
        _ensure_fc()
        if options != None and not isinstance(options, FontOptions) :
            raise TypeError("options must be a FontOptions")
        #end if
        with _FcPatternManager() as patterns :
            search_pattern = patterns.collect(fc.FcNameParse(pattern.encode("utf-8")))
            if search_pattern == None :
                raise RuntimeError("cannot parse FontConfig name pattern")
            #end if
            if not fc.FcConfigSubstitute(None, search_pattern, _FC.FcMatchPattern) :
                raise RuntimeError("cannot substitute Fontconfig configuration")
            #end if
            if options != None :
                cairo_ft_font_options_substitute(search_pattern, options._cairobj)
            #end if
            fc.FcDefaultSubstitute(search_pattern)
            match_result = ct.c_int()
            found_pattern = patterns.collect(fc.FcFontMatch(None, search_pattern, ct.byref(match_result)))
            if found_pattern == None or match_result.value != _FC.FcResultMatch :
                raise RuntimeError("Fontconfig cannot match font name")
            #end if
            cairo_face = cairo.cairo_ft_font_face_create_for_pattern(found_pattern)
        #end with
        return \
            FontFace(cairo_face)
    #end create_for_pattern

    # TODO: synthesize, user data

#end FontFace

# TODO: scaled_font_face_t, user fonts
