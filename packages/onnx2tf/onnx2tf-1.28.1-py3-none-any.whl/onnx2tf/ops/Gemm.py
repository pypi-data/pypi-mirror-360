import random
random.seed(0)
import numpy as np
np.random.seed(0)
import tensorflow as tf
import tf_keras
import onnx_graphsurgeon as gs
from onnx2tf.utils.common_functions import (
    replace_parameter,
    get_constant_or_variable,
    print_node_info,
    inverted_operation_enable_disable,
    make_tf_node_info,
    get_replacement_parameter,
    pre_process_transpose,
    post_process_transpose,
)
from onnx2tf.utils.enums import (
    NUMPY_DTYPES_TO_TF_DTYPES,
)


@print_node_info
@inverted_operation_enable_disable
@get_replacement_parameter
def make_node(
    *,
    graph_node: gs.Node,
    tf_layers_dict: dict,
    **kwargs: dict,
):
    """Gemm

    Parameters
    ----------
    graph_node: gs.Node
        graph_surgeon Node

    tf_layers_dict: dict
        optype, shape, dtype, tensorflow graph
    """
    before_op_output_shape_trans_1 = \
        tf_layers_dict.get(graph_node.inputs[0].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans_2 = \
        tf_layers_dict.get(graph_node.inputs[1].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans = \
        before_op_output_shape_trans_1 \
        and before_op_output_shape_trans_2

    graph_node_input_1 = get_constant_or_variable(
        graph_node.inputs[0],
        before_op_output_shape_trans,
    )
    graph_node_input_2 = get_constant_or_variable(
        graph_node.inputs[1],
        before_op_output_shape_trans,
    )
    if len(graph_node.inputs) > 2:
        graph_node_input_3 = get_constant_or_variable(
            graph_node.inputs[2],
            before_op_output_shape_trans,
            is_bias=True \
                if graph_node.inputs[2].shape is not None \
                    and len(graph_node.inputs[2].shape) == 1 else False,
        )
    else:
        graph_node_input_3 = 0
    graph_node_output: gs.Variable = graph_node.outputs[0]

    x = tf_layers_dict[graph_node_input_1.name]['tf_node'] \
        if isinstance(graph_node_input_1, gs.Variable) else graph_node_input_1
    y = tf_layers_dict[graph_node_input_2.name]['tf_node'] \
        if isinstance(graph_node_input_2, gs.Variable) else graph_node_input_2
    z = tf_layers_dict[graph_node_input_3.name]['tf_node'] \
        if isinstance(graph_node_input_3, gs.Variable) else graph_node_input_3

    # Pre-process transpose
    x = pre_process_transpose(
        value_before_transpose=x,
        param_target='inputs',
        param_name=graph_node.inputs[0].name,
        **kwargs,
    )
    y = pre_process_transpose(
        value_before_transpose=y,
        param_target='inputs',
        param_name=graph_node.inputs[1].name,
        **kwargs,
    )
    if len(graph_node.inputs) > 2:
        z = pre_process_transpose(
            value_before_transpose=z,
            param_target='inputs',
            param_name=graph_node.inputs[2].name,
            **kwargs,
        )

    input_tensor_x_dtype = NUMPY_DTYPES_TO_TF_DTYPES[x.dtype] \
        if isinstance(x.dtype, np.dtype) else x.dtype
    x = tf_keras.layers.Flatten()(x)

    # The Flatten API changes data type from tf.float64 to tf.float32
    # so we need the following line to get the original type back
    x = tf.cast(x, input_tensor_x_dtype) \
        if input_tensor_x_dtype is tf.float64 else x

    shape = graph_node_output.shape
    dtype = graph_node_output.dtype

    transA = bool(graph_node.attrs.get('transA', 0))
    transB = bool(graph_node.attrs.get('transB', 0))
    alpha = graph_node.attrs.get('alpha', 1.0)
    beta = graph_node.attrs.get('beta', 1.0)

    optimization_for_gpu_delegate: bool = \
        kwargs['optimization_for_gpu_delegate']

    # Preserving Graph Structure (Dict)
    tf_layers_dict[graph_node_output.name] = {
        'optype': graph_node.op,
        'shape': shape,
        'dtype': dtype,
    }

    # Param replacement
    x = replace_parameter(
        value_before_replacement=x,
        param_target='inputs',
        param_name=graph_node.inputs[0].name,
        **kwargs,
    )
    y = replace_parameter(
        value_before_replacement=y,
        param_target='inputs',
        param_name=graph_node.inputs[1].name,
        **kwargs,
    )
    if len(graph_node.inputs) > 2:
        z = replace_parameter(
            value_before_replacement=z,
            param_target='inputs',
            param_name=graph_node.inputs[2].name,
            **kwargs,
        )
    alpha = replace_parameter(
        value_before_replacement=alpha,
        param_target='attributes',
        param_name='alpha',
        **kwargs,
    )
    beta = replace_parameter(
        value_before_replacement=beta,
        param_target='attributes',
        param_name='beta',
        **kwargs,
    )
    transA = replace_parameter(
        value_before_replacement=transA,
        param_target='attributes',
        param_name='transA',
        **kwargs,
    )
    transB = replace_parameter(
        value_before_replacement=transB,
        param_target='attributes',
        param_name='transB',
        **kwargs,
    )

    # Generation of TF OP
    x = x \
        if not isinstance(x, np.ndarray) \
            else tf.convert_to_tensor(x)
    y = y \
        if not isinstance(y, np.ndarray) \
            else tf.convert_to_tensor(y)
    if z is not None:
        z = z \
            if not isinstance(z, np.ndarray) \
                else tf.convert_to_tensor(z)
    if transA == True:
        x = tf.transpose(x)
    if transB == True:
        y = tf.transpose(y)

    # We cast to either input or attribute data type to preserve precision
    if input_tensor_x_dtype in [tf.float64]:
        # cast to input data type
        alpha = tf.cast(alpha, input_tensor_x_dtype)
        beta = tf.cast(beta, input_tensor_x_dtype)
        tf_layers_dict[graph_node_output.name]['tf_node'] = \
            alpha * tf.matmul(x, y) + beta * z

    else:
        # cast to attribute data type
        x = tf.cast(x, tf.float32)
        y = tf.cast(y, tf.float32)
        z = tf.cast(z, tf.float32)
        if not optimization_for_gpu_delegate:
            if z is not None:
                result = tf.convert_to_tensor(alpha) * tf.matmul(x, y) + tf.convert_to_tensor(beta) * z
            else:
                result = tf.convert_to_tensor(alpha) * tf.matmul(x, y) + tf.convert_to_tensor(beta)

        else:
            result = tf.convert_to_tensor(alpha) * tf.matmul(x, y) - (tf.convert_to_tensor(beta) * z) * tf.convert_to_tensor(-1.0, dtype=z.dtype)

        if result.dtype != input_tensor_x_dtype:
            tf_layers_dict[graph_node_output.name]['tf_node'] = \
                tf.cast(result, input_tensor_x_dtype)
        else:
            tf_layers_dict[graph_node_output.name]['tf_node'] = result

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
                'tf_op_type': tf.matmul,
                'tf_inputs': {
                    'x': x,
                    'y': y,
                    'z': z,
                    'alpha': alpha,
                    'beta': beta,
                },
                'tf_outputs': {
                    'output': tf_layers_dict[graph_node_output.name]['tf_node'],
                },
            }
        )
