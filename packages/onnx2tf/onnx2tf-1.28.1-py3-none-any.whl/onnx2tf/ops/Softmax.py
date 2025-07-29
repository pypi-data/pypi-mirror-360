import sys
import copy
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
    convert_axis,
    print_node_info,
    inverted_operation_enable_disable,
    make_tf_node_info,
    get_replacement_parameter,
    pre_process_transpose,
    post_process_transpose,
    dummy_tf_inference,
    get_tf_model_inputs,
    onnx_tf_tensor_validation,
    transpose_with_flexing_deterrence,
)
from typing import Any, Dict


def custom_tf_nn_softmax(logits, axis, name):
    '''
        Customer Tensorflow Softmax Op
            official softmax op limits Dim(input) <= 5, otherwise throw an inference exception error

        Arguments:
            [1] logits: tf.Tensor, tf.float32, input logits with arbitrary shape
            [2] axis:   constant,  int,        axis index
            [3] name:   constant,  string,     softmax op name

        Returns:
            [1] logits: tf.Tensor, tf.float32, output logits with Sum(output[..., axis, ...]) == 1.0
    '''
    before_shape = logits.shape
    if len(before_shape) > 5:
        head = before_shape[:axis]
        tail = before_shape[axis:][1:]

        after_shape = []
        after_shape += ([] if len(head) == 0 else [tf.math.reduce_prod(head)])
        after_shape += [before_shape[axis]]
        after_shape += ([] if len(tail) == 0 else [tf.math.reduce_prod(tail)])

        output = \
            tf.nn.softmax(tf.reshape(logits, shape=after_shape), int(len(head) > 0), name)
        output = tf.reshape(output, shape=before_shape)
    else:
        output = tf.nn.softmax(logits, axis, name)
    return output


@print_node_info
@inverted_operation_enable_disable
@get_replacement_parameter
def make_node(
    *,
    graph_node: gs.Node,
    tf_layers_dict: dict,
    **kwargs: dict,
):
    """Softmax

    Parameters
    ----------
    graph_node: gs.Node
        graph_surgeon Node

    tf_layers_dict: dict
        optype, shape, dtype, tensorflow graph
    """
    before_op_output_shape_trans_1 = \
        tf_layers_dict.get(graph_node.inputs[0].name, {}).get('before_op_output_shape_trans', True)
    before_op_output_shape_trans = \
        before_op_output_shape_trans_1

    graph_node_input = get_constant_or_variable(
        graph_node.inputs[0],
        before_op_output_shape_trans,
    )
    graph_node_output: gs.Variable = graph_node.outputs[0]
    shape = graph_node_output.shape
    dtype = graph_node_output.dtype

    input_tensor = tf_layers_dict[graph_node_input.name]['tf_node'] \
        if isinstance(graph_node_input, gs.Variable) else graph_node_input
    tensor_rank = len(input_tensor.shape)

    axis = graph_node.attrs.get('axis', tensor_rank - 1)
    pre_convert_axis = axis
    axis = (axis + tensor_rank) % tensor_rank
    axis = convert_axis(
        axis=axis,
        tensor_rank=tensor_rank,
        before_op_output_shape_trans=before_op_output_shape_trans,
    )

    # Preserving Graph Structure (Dict)
    tf_layers_dict[graph_node_output.name] = {
        'optype': graph_node.op,
        'shape': shape,
        'dtype': dtype,
        'nhwc': tf_layers_dict[graph_node_input.name]['nhwc'] \
            if isinstance(graph_node_input, gs.Variable) \
                and 'nhwc' in tf_layers_dict[graph_node_input.name].keys() else False,
        'nwc_nhwc_ndhwc_keep': tf_layers_dict[graph_node_input.name]['nwc_nhwc_ndhwc_keep'] \
            if isinstance(graph_node_input, gs.Variable) \
                and 'nwc_nhwc_ndhwc_keep' in tf_layers_dict[graph_node_input.name].keys() else False,
    }

    onnx_tensor_infos_for_validation: Dict[str:np.ndarray] = kwargs['onnx_tensor_infos_for_validation']
    test_data_nhwc: np.ndarray = kwargs['test_data_nhwc']
    custom_input_op_name_np_data_path: str = kwargs['custom_input_op_name_np_data_path']
    disable_strict_mode: bool = kwargs['disable_strict_mode']
    onnx_tensor_infos = None
    validation_data = None

    # If all axes are of different sizes and the axis sizes specified in axis are the same
    # in onnx and Tensorflow, skip the accuracy check.
    acc_check_pass_flg = False
    if graph_node.inputs[0].shape is not None \
        and input_tensor.shape is not None:
        onnx_input_shapes = list(graph_node.inputs[0].shape)
        tf_input_shapes = list(input_tensor.shape)
        if onnx_input_shapes is not None \
            and tf_input_shapes is not None \
            and len(onnx_input_shapes) >= 1 \
            and len(tf_input_shapes) >= 1 \
            and len(onnx_input_shapes) == len(set(onnx_input_shapes)) \
            and not isinstance(onnx_input_shapes[pre_convert_axis], str) \
            and tf_input_shapes[axis] is not None \
            and onnx_input_shapes[pre_convert_axis] == tf_input_shapes[axis]:
            acc_check_pass_flg = True

    if onnx_tensor_infos_for_validation is not None \
        and onnx_tensor_infos_for_validation.get(graph_node_output.name, None) is not None \
        and not acc_check_pass_flg:
        # Get the output tensor of one previous OP of TensorFlow only once
        if not disable_strict_mode:
            tf_model_inputs = get_tf_model_inputs(tf_layers_dict=tf_layers_dict)
            val_model = None
            if not isinstance(input_tensor, np.ndarray):
                val_model = tf_keras.Model(
                    inputs=tf_model_inputs,
                    outputs=[
                        input_tensor,
                    ],
                )
            else:
                pass

        # TF dummy inference
        #   Get the output tensor of the previous layer of MatMul
        #   If input.1 and input.2 are both layers, tf_pre_tensor_infos is 2 cases
        #   If one of input.1 or input.2 is np.ndarray, tf_pre_tensor_infos is 1 case
        tf_pre_tensor_infos = {}
        if not disable_strict_mode:
            try:
                tf_pre_tensor_infos: Dict[Any] = \
                    dummy_tf_inference(
                        model=val_model,
                        inputs=tf_model_inputs,
                        test_data_nhwc=test_data_nhwc,
                        custom_input_op_name_np_data_path=custom_input_op_name_np_data_path,
                    )
            except:
                pass

        # Get np.ndarray for validation
        if not disable_strict_mode:
            if len(tf_pre_tensor_infos) == 1:
                if not isinstance(input_tensor, np.ndarray):
                    validation_data = list(tf_pre_tensor_infos.values())[0]
                else:
                    validation_data = copy.deepcopy(input_tensor)

            # Get ONNX inference results
            onnx_tensor_infos = None
            if onnx_tensor_infos_for_validation is not None \
                and onnx_tensor_infos_for_validation.get(graph_node_output.name, None) is not None:
                onnx_tensor_infos = {
                    graph_node_output.name:
                    onnx_tensor_infos_for_validation[graph_node_output.name]
                }
                del onnx_tensor_infos_for_validation

    # Param replacement
    input_tensor = replace_parameter(
        value_before_replacement=input_tensor,
        param_target='inputs',
        param_name=graph_node.inputs[0].name,
        **kwargs,
    )
    axis = replace_parameter(
        value_before_replacement=axis,
        param_target='attributes',
        param_name='axis',
        **kwargs,
    )

    # Pre-process transpose
    before_trans_shape = input_tensor.shape
    input_tensor = pre_process_transpose(
        value_before_transpose=input_tensor,
        param_target='inputs',
        param_name=graph_node.inputs[0].name,
        **kwargs,
    )
    after_trans_shape = input_tensor.shape
    if 'nhwc' in tf_layers_dict[graph_node_output.name].keys() \
        and tf_layers_dict[graph_node_output.name]['nhwc'] == True \
        and before_trans_shape != after_trans_shape:
        tf_layers_dict[graph_node_output.name].pop('nhwc')

    # It seems that TensorFlow only behaves incorrectly when processing
    # Reducemax() -> Subtract() -> Softmax() in that order.
    # Work around a bug in TensorFlow's model optimizer.
    # https://github.com/PINTO0309/onnx2tf/issues/182
    try:
        if graph_node.i().op == 'Sub':
            sub_op: gs.Node = graph_node.i()
            if sub_op.i(tensor_idx=0).op == 'ReduceMax' \
                or sub_op.i(tensor_idx=1).op == 'ReduceMax':
                input_tensor = \
                    tf.math.subtract(
                        x=tf.math.add(
                            x=input_tensor,
                            y=tf.constant(1e-7, dtype=input_tensor.dtype)
                        ),
                        y=tf.constant(1e-7, dtype=input_tensor.dtype)
                    )
    except Exception as ex:
        pass

    # Detect conversion errors in axis and identify the axis
    # with the smallest possible error and replace it.
    min_abs_err = sys.maxsize
    min_abs_err_axis: int = axis

    if not disable_strict_mode and not acc_check_pass_flg:
        if onnx_tensor_infos is not None and validation_data is not None:
            check_axes = reversed([idx for idx in range(tensor_rank)])
            # Search for the axis with the smallest error
            for check_axis in check_axes:
                # Build TF dummy model
                input = tf_keras.Input(
                    shape=validation_data.shape[1:],
                    batch_size=validation_data.shape[0] \
                        if isinstance(validation_data.shape[0], int) else None,
                    name='dummy_input',
                    dtype=validation_data.dtype,
                )
                val_model = tf_keras.Model(
                    inputs=[
                        input,
                    ],
                    outputs=[
                        custom_tf_nn_softmax(
                            logits=input,
                            axis=check_axis,
                            name=graph_node.name,
                        )
                    ],
                )
                # TF dummy inference
                tf_tensor_infos: Dict[Any] = \
                    dummy_tf_inference(
                        model=val_model,
                        inputs=[
                            input,
                        ],
                        verification_datas=[
                            validation_data,
                        ],
                    )
                del input
                del val_model

                # Validation
                onnx_tf_output_pairs = {
                    (oi[0], ti[0]): (oi[1], ti[1]) \
                        for oi, ti in zip(onnx_tensor_infos.items(), tf_tensor_infos.items())
                }
                """
                check_results: Dict[str, List[np.ndarray, int, float|int]]
                    {
                        onnx_output_name: [
                            onnx_tensor,
                            matched_flg, <--- 0: Unmatched, 1: Matched, 2: Skipped (Deleted or Shape Unmatched)
                            max_abs_err,
                        ]
                    }
                """
                check_results = onnx_tf_tensor_validation(
                    output_pairs=onnx_tf_output_pairs,
                    rtol=0.0,
                    atol=0.0,
                )
                result_err = sum([val[2] for val in check_results.values()])
                if result_err < min_abs_err:
                    min_abs_err = result_err
                    min_abs_err_axis = check_axis
                    if min_abs_err < 1e-3:
                        break

    # Suppress automatic Traspose extrapolation behavior by Softmax in TensorFlow
    flex_deterrent_perm_rev = []
    if min_abs_err_axis != tensor_rank - 1:
        # 0,1,3,4,5,6,2
        flex_deterrent_perm = [
            idx for idx in range(tensor_rank) if idx != min_abs_err_axis
        ] + [min_abs_err_axis]
        # 0,1,3,4,5,6,2 -> 0,1,6,2,3,4,5
        flex_deterrent_perm_rev = [
            idx if idx != min_abs_err_axis else tensor_rank - 1
            for idx in range(min_abs_err_axis + 1)
        ] + [idx for idx in range(min_abs_err_axis, tensor_rank - 1)]
        transpose_output_shape = np.asarray(
            input_tensor.shape)[flex_deterrent_perm]
        input_tensor = transpose_with_flexing_deterrence(
            input_tensor=input_tensor,
            perm=flex_deterrent_perm,
            output_shape=transpose_output_shape \
                if None not in transpose_output_shape else None,
            **kwargs,
        )

    # Generation of TF OP
    tf_layers_dict[graph_node_output.name]['tf_node'] = \
        custom_tf_nn_softmax(
            logits=input_tensor,
            axis=min_abs_err_axis if not flex_deterrent_perm_rev else tensor_rank - 1,
            name=graph_node.name,
        )

    # Inversion of suppression of automatic Traspose extrapolation behavior by Softmax in TensorFlow
    if flex_deterrent_perm_rev:
        tf_layers_dict[graph_node_output.name]['tf_node'] = \
            transpose_with_flexing_deterrence(
                input_tensor=tf_layers_dict[graph_node_output.name]['tf_node'],
                perm=flex_deterrent_perm_rev,
                output_shape=after_trans_shape \
                    if None not in after_trans_shape else None,
                **kwargs,
            )

    # Post-process transpose
    before_trans_shape = tf_layers_dict[
        graph_node_output.name]['tf_node'].shape
    tf_layers_dict[graph_node_output.name]['tf_node'] = post_process_transpose(
        value_before_transpose=tf_layers_dict[graph_node_output.name]
        ['tf_node'],
        param_target='outputs',
        param_name=graph_node.outputs[0].name,
        **kwargs,
    )
    after_trans_shape = tf_layers_dict[graph_node_output.name]['tf_node'].shape
    if 'nhwc' in tf_layers_dict[graph_node_output.name].keys() \
        and tf_layers_dict[graph_node_output.name]['nhwc'] == True \
        and before_trans_shape != after_trans_shape:
        tf_layers_dict[graph_node_output.name].pop('nhwc')

    # Generation of Debug Info
    tf_layers_dict[graph_node_output.name]['tf_node_info'] = \
        make_tf_node_info(
            node_info={
                'tf_op_type': tf.nn.softmax,
                'tf_inputs': {
                    'logits': input_tensor,
                    'axis': axis,
                },
                'tf_outputs': {
                    'output': tf_layers_dict[graph_node_output.name]['tf_node'],
                },
            }
        )
