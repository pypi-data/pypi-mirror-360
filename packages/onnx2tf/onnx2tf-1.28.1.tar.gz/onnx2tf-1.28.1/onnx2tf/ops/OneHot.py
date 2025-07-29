import random
random.seed(0)
import numpy as np
np.random.seed(0)
import tensorflow as tf
import onnx_graphsurgeon as gs
from onnx2tf.utils.common_functions import (
    get_constant_or_variable,
    print_node_info,
    inverted_operation_enable_disable,
    make_tf_node_info,
    get_replacement_parameter,
    pre_process_transpose,
    post_process_transpose,
)
from onnx2tf.utils.enums import NUMPY_DTYPES_TO_TF_DTYPES


def process_neg_indices(depth, indices):
    indices_dtype = NUMPY_DTYPES_TO_TF_DTYPES[indices.dtype] \
        if isinstance(indices.dtype, np.dtype) else indices.dtype
    depth_dtype = NUMPY_DTYPES_TO_TF_DTYPES[depth.dtype] \
        if isinstance(depth.dtype, np.dtype) else depth.dtype
    indices = tf.math.floormod(tf.add(tf.cast(indices, depth_dtype), depth), depth)
    return tf.cast(indices, indices_dtype)


@print_node_info
@inverted_operation_enable_disable
@get_replacement_parameter
def make_node(
    *,
    graph_node: gs.Node,
    tf_layers_dict: dict,
    **kwargs: dict,
):
    """OneHot

    Parameters
    ----------
    graph_node: gs.Node
        graph_surgeon Node

    tf_layers_dict: dict
        optype, shape, dtype, tensorflow graph
    """
    indices_cast_map = {
        tf.uint16: tf.int32,
        tf.uint32: tf.int64,
        tf.uint64: tf.int64,
        tf.int8: tf.int32,
        tf.int16: tf.int32,
        # ONNX spec state that all non-integer type will be casted to int64 before use
        tf.float16: tf.int64,
        tf.float32: tf.int64,
        tf.float64: tf.int64,
    }
    depth_supported_type = [tf.int32]
    depth_cast_map = {
        tf.uint8: tf.int32,
        tf.uint16: tf.int32,
        tf.uint32: tf.int32,
        tf.uint64: tf.int32,
        tf.int8: tf.int32,
        tf.int16: tf.int32,
        tf.int64: tf.int32,
        # ONNX spec state that all non-integer type will be casted to int64 before use
        # but TF only support int32 for depth so will cast to int32
        tf.float16: tf.int32,
        tf.float32: tf.int32,
        tf.float64: tf.int32,
    }

    before_op_output_shape_trans_1 = \
        tf_layers_dict.get(graph_node.inputs[0].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans_2 = \
        tf_layers_dict.get(graph_node.inputs[1].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans_3 = \
        tf_layers_dict.get(graph_node.inputs[2].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans = \
        before_op_output_shape_trans_1 \
        and before_op_output_shape_trans_2 \
        and before_op_output_shape_trans_3

    graph_node_input_1 = get_constant_or_variable(
        graph_node.inputs[0],
        before_op_output_shape_trans,
    )
    graph_node_input_2 = get_constant_or_variable(
        graph_node.inputs[1],
        before_op_output_shape_trans,
    )
    graph_node_input_3 = get_constant_or_variable(
        graph_node.inputs[2],
        before_op_output_shape_trans,
    )
    graph_node_output: gs.Variable = graph_node.outputs[0]
    shape = graph_node_output.shape
    dtype = graph_node_output.dtype

    # Preserving Graph Structure (Dict)
    tf_layers_dict[graph_node_output.name] = {
        'optype': graph_node.op,
        'shape': shape,
        'dtype': dtype,
    }

    # Generation of TF OP
    indices = tf_layers_dict[graph_node_input_1.name]['tf_node'] \
        if isinstance(graph_node_input_1, gs.Variable) else graph_node_input_1
    depth = tf_layers_dict[graph_node_input_2.name]['tf_node'] \
        if isinstance(graph_node_input_2, gs.Variable) else graph_node_input_2
    values = tf_layers_dict[graph_node_input_3.name]['tf_node'] \
        if isinstance(graph_node_input_3, gs.Variable) else graph_node_input_3

    # Pre-process transpose
    indices = pre_process_transpose(
        value_before_transpose=indices,
        param_target='inputs',
        param_name=graph_node.inputs[0].name,
        **kwargs,
    )
    depth = pre_process_transpose(
        value_before_transpose=depth,
        param_target='inputs',
        param_name=graph_node.inputs[1].name,
        **kwargs,
    )
    values = pre_process_transpose(
        value_before_transpose=values,
        param_target='inputs',
        param_name=graph_node.inputs[2].name,
        **kwargs,
    )

    axis = graph_node.attrs.get('axis', -1)
    axis = axis if axis >= 0 else axis + len(indices.shape) + axis + 1

    # process tf.one_hot unsupported datatype for indices
    indices_dtype = NUMPY_DTYPES_TO_TF_DTYPES[indices.dtype] \
        if isinstance(indices.dtype, np.dtype) else indices.dtype
    indices = tf.cast(indices, indices_cast_map[indices_dtype]) \
        if indices_dtype in indices_cast_map else indices

    # process tf.one_hot unsupported datatype for depth
    depth_dtype = NUMPY_DTYPES_TO_TF_DTYPES[depth.dtype] \
        if isinstance(depth.dtype, np.dtype) else depth.dtype
    depth = tf.cast(depth, depth_cast_map[depth_dtype]) \
        if depth_dtype in depth_cast_map else depth

    depth = tf.squeeze(depth) if len(depth.shape) == 1 else depth

    # process negative indices
    indices = process_neg_indices(depth, indices)

    off_value = values[0]
    on_value = values[1]

    tf_layers_dict[graph_node_output.name]['tf_node'] = \
        tf.one_hot(
            indices=indices,
            depth=depth,
            on_value=on_value,
            off_value=off_value,
            axis=axis,
            dtype=on_value.dtype,
            name=graph_node.name,
        )

    # Post-process transpose
    tf_layers_dict[graph_node_output.name]['tf_node'] = post_process_transpose(
        value_before_transpose=tf_layers_dict[graph_node_output.name]['tf_node'],
        param_target='outputs',
        param_name=graph_node.outputs[0].name,
        **kwargs,
    )

    # Generation of Debug Info
    tf_layers_dict[graph_node_output.name]['tf_node_info'] = \
        make_tf_node_info(
            node_info={
                'tf_op_type': tf.one_hot,
                'tf_inputs': {
                    'indices': indices,
                    'depth': depth,
                    'on_value': on_value,
                    'off_value': off_value,
                    'axis': axis,
                    'dtype': on_value.dtype,
                },
                'tf_outputs': {
                    'output': tf_layers_dict[graph_node_output.name]['tf_node'],
                },
            }
        )
