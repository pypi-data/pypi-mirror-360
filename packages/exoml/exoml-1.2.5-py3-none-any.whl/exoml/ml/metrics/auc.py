import abc
import tensorflow as tf
import numpy as np
import tensorflow.keras.backend as K

#from keras import backend
#from keras.utils import metrics_utils
#from keras.utils.generic_utils import to_list
#from keras_core import Metric
#from keras_core.src.utils import tf_utils
#from tf_keras.src.metrics import base_metric


#from tf_keras.src.metrics import base_metric
from keras.src import backend
from keras.src.utils import tf_utils
from keras.metrics import Metric
#from keras.src.utils import metrics_utils
#from keras.src.utils.generic_utils import to_list
#from keras.src.metrics import base_metric
# from keras.src import backend

# Replacement functions for metrics_utils
from enum import Enum

NEG_INF = -1e10

def assert_thresholds_range(thresholds):
    if thresholds is not None:
        invalid_thresholds = [
            t for t in thresholds if t is None or t < 0 or t > 1
        ]
        if invalid_thresholds:
            raise ValueError(
                "Threshold values must be in [0, 1]. "
                f"Received: {invalid_thresholds}"
            )

def parse_init_thresholds(thresholds, default_threshold=0.5):
    if thresholds is not None:
        assert_thresholds_range(to_list(thresholds))
    thresholds = to_list(
        default_threshold if thresholds is None else thresholds
    )
    return thresholds

def to_list(x):
    """Normalizes a list/tensor into a list.

    If a tensor is passed, we return
    a list of size 1 containing the tensor.

    Args:
        x: target object to be normalized.

    Returns:
        A list.
    """
    if isinstance(x, list):
        return x
    return [x]

def is_evenly_distributed_thresholds(thresholds):
    """Check if the thresholds list is evenly distributed.

    We could leverage evenly distributed thresholds to use less memory when
    calculate metrcis like AUC where each individual threshold need to be
    evaluated.

    Args:
      thresholds: A python list or tuple, or 1D numpy array whose value is
        ranged in [0, 1].

    Returns:
      boolean, whether the values in the inputs are evenly distributed.
    """
    # Check the list value and see if it is evenly distributed.
    num_thresholds = len(thresholds)
    if num_thresholds < 3:
        return False
    even_thresholds = np.arange(num_thresholds, dtype=np.float32) / (
        num_thresholds - 1
    )
    return np.allclose(thresholds, even_thresholds, atol=backend.epsilon())

class ConfusionMatrix(Enum):
    TRUE_POSITIVES = "tp"
    FALSE_POSITIVES = "fp"
    TRUE_NEGATIVES = "tn"
    FALSE_NEGATIVES = "fn"

def _assert_splits_match(nested_splits_lists):
    """Checks that the given splits lists are identical.

    Performs static tests to ensure that the given splits lists are identical,
    and returns a list of control dependency op tensors that check that they are
    fully identical.

    Args:
      nested_splits_lists: A list of nested_splits_lists, where each split_list
        is a list of `splits` tensors from a `RaggedTensor`, ordered from
        outermost ragged dimension to innermost ragged dimension.

    Returns:
      A list of control dependency op tensors.
    Raises:
      ValueError: If the splits are not identical.
    """
    error_msg = (
        "Inputs must have identical ragged splits. "
        f"Input received: {nested_splits_lists}"
    )
    for splits_list in nested_splits_lists:
        if len(splits_list) != len(nested_splits_lists[0]):
            raise ValueError(error_msg)
    return [
        tf.debugging.assert_equal(s1, s2, message=error_msg)
        for splits_list in nested_splits_lists[1:]
        for (s1, s2) in zip(nested_splits_lists[0], splits_list)
    ]

def ragged_assert_compatible_and_get_flat_values(values, mask=None):
    """If ragged, it checks the compatibility and then returns the flat_values.

       Note: If two tensors are dense, it does not check their compatibility.
       Note: Although two ragged tensors with different ragged ranks could have
             identical overall rank and dimension sizes and hence be compatible,
             we do not support those cases.
    Args:
       values: A list of potentially ragged tensor of the same ragged_rank.
       mask: A potentially ragged tensor of the same ragged_rank as elements in
         Values.

    Returns:
       A tuple in which the first element is the list of tensors and the second
       is the mask tensor. ([Values], mask). Mask and the element in Values
       are equal to the flat_values of the input arguments (if they were
       ragged).
    """
    if isinstance(values, list):
        is_all_ragged = all(isinstance(rt, tf.RaggedTensor) for rt in values)
        is_any_ragged = any(isinstance(rt, tf.RaggedTensor) for rt in values)
    else:
        is_all_ragged = isinstance(values, tf.RaggedTensor)
        is_any_ragged = is_all_ragged
    if is_all_ragged and ((mask is None) or isinstance(mask, tf.RaggedTensor)):
        to_be_stripped = False
        if not isinstance(values, list):
            values = [values]
            to_be_stripped = True

        # NOTE: we leave the flat_values compatibility to
        # tf.TensorShape `assert_is_compatible_with` check if both dynamic
        # dimensions are equal and then use the flat_values.
        nested_row_split_list = [rt.nested_row_splits for rt in values]
        assertion_list = _assert_splits_match(nested_row_split_list)

        # if both are ragged sample_weights also should be ragged with same
        # dims.
        if isinstance(mask, tf.RaggedTensor):
            assertion_list_for_mask = _assert_splits_match(
                [nested_row_split_list[0], mask.nested_row_splits]
            )
            with tf.control_dependencies(assertion_list_for_mask):
                mask = tf.expand_dims(mask.flat_values, -1)

        # values has at least 1 element.
        flat_values = []
        for value in values:
            with tf.control_dependencies(assertion_list):
                flat_values.append(tf.expand_dims(value.flat_values, -1))

        values = flat_values[0] if to_be_stripped else flat_values

    elif is_any_ragged:
        raise TypeError(
            "Some of the inputs are not tf.RaggedTensor. "
            f"Input received: {values}"
        )
    # values are empty or value are not ragged and mask is ragged.
    elif isinstance(mask, tf.RaggedTensor):
        raise TypeError(
            "Ragged mask is not allowed with non-ragged inputs. "
            f"Input received: {values}, mask received: {mask}"
        )

    return values, mask

def remove_squeezable_dimensions(
    labels, predictions, expected_rank_diff=0, name=None
):
    """Squeeze last dim if ranks differ from expected by exactly 1.

    In the common case where we expect shapes to match, `expected_rank_diff`
    defaults to 0, and we squeeze the last dimension of the larger rank if they
    differ by 1.

    But, for example, if `labels` contains class IDs and `predictions` contains
    1 probability per class, we expect `predictions` to have 1 more dimension
    than `labels`, so `expected_rank_diff` would be 1. In this case, we'd
    squeeze `labels` if `rank(predictions) - rank(labels) == 0`, and
    `predictions` if `rank(predictions) - rank(labels) == 2`.

    This will use static shape if available. Otherwise, it will add graph
    operations, which could result in a performance hit.

    Args:
      labels: Label values, a `Tensor` whose dimensions match `predictions`.
      predictions: Predicted values, a `Tensor` of arbitrary dimensions.
      expected_rank_diff: Expected result of `rank(predictions) - rank(labels)`.
      name: Name of the op.

    Returns:
      Tuple of `labels` and `predictions`, possibly with last dim squeezed.
    """
    with backend.name_scope(name or "remove_squeezable_dimensions"):
        predictions = tf_utils.ensure_tensor(predictions)
        labels = tf_utils.ensure_tensor(labels)
        predictions_shape = predictions.shape
        predictions_rank = predictions_shape.ndims
        labels_shape = labels.shape
        labels_rank = labels_shape.ndims
        if (labels_rank is not None) and (predictions_rank is not None):
            # Use static rank.
            rank_diff = predictions_rank - labels_rank
            if rank_diff == expected_rank_diff + 1 and predictions_shape.dims[
                -1
            ].is_compatible_with(1):
                predictions = tf.squeeze(predictions, [-1])
            elif rank_diff == expected_rank_diff - 1 and labels_shape.dims[
                -1
            ].is_compatible_with(1):
                labels = tf.squeeze(labels, [-1])
            return labels, predictions

        # Use dynamic rank.
        rank_diff = tf.rank(predictions) - tf.rank(labels)
        if (predictions_rank is None) or (
            predictions_shape.dims[-1].is_compatible_with(1)
        ):
            predictions = tf.cond(
                tf.equal(expected_rank_diff + 1, rank_diff),
                lambda: tf.squeeze(predictions, [-1]),
                lambda: predictions,
            )
        if (labels_rank is None) or (
            labels_shape.dims[-1].is_compatible_with(1)
        ):
            labels = tf.cond(
                tf.equal(expected_rank_diff - 1, rank_diff),
                lambda: tf.squeeze(labels, [-1]),
                lambda: labels,
            )
        return labels, predictions

def squeeze_or_expand_dimensions(y_pred, y_true=None, sample_weight=None):
    """Squeeze or expand last dimension if needed.

    1. Squeezes last dim of `y_pred` or `y_true` if their rank differs by 1
    (using `remove_squeezable_dimensions`).
    2. Squeezes or expands last dim of `sample_weight` if its rank differs by 1
    from the new rank of `y_pred`.
    If `sample_weight` is scalar, it is kept scalar.

    This will use static shape if available. Otherwise, it will add graph
    operations, which could result in a performance hit.

    Args:
      y_pred: Predicted values, a `Tensor` of arbitrary dimensions.
      y_true: Optional label `Tensor` whose dimensions match `y_pred`.
      sample_weight: Optional weight scalar or `Tensor` whose dimensions match
        `y_pred`.

    Returns:
      Tuple of `y_pred`, `y_true` and `sample_weight`. Each of them possibly has
      the last dimension squeezed,
      `sample_weight` could be extended by one dimension.
      If `sample_weight` is None, (y_pred, y_true) is returned.
    """
    y_pred_shape = y_pred.shape
    y_pred_rank = y_pred_shape.ndims
    if y_true is not None:

        # If sparse matrix is provided as `y_true`, the last dimension in
        # `y_pred` may be > 1. Eg: y_true = [0, 1, 2] (shape=(3,)), y_pred =
        # [[.9, .05, .05], [.5, .89, .6], [.05, .01, .94]] (shape=(3, 3)) In
        # this case, we should not try to remove squeezable dimension.
        y_true_shape = y_true.shape
        y_true_rank = y_true_shape.ndims
        if (y_true_rank is not None) and (y_pred_rank is not None):
            # Use static rank for `y_true` and `y_pred`.
            if (y_pred_rank - y_true_rank != 1) or y_pred_shape[-1] == 1:
                y_true, y_pred = remove_squeezable_dimensions(y_true, y_pred)
        else:
            # Use dynamic rank.
            rank_diff = tf.rank(y_pred) - tf.rank(y_true)
            squeeze_dims = lambda: remove_squeezable_dimensions(y_true, y_pred)
            is_last_dim_1 = tf.equal(1, tf.shape(y_pred)[-1])
            maybe_squeeze_dims = lambda: tf.cond(
                is_last_dim_1, squeeze_dims, lambda: (y_true, y_pred)
            )
            y_true, y_pred = tf.cond(
                tf.equal(1, rank_diff), maybe_squeeze_dims, squeeze_dims
            )

    if sample_weight is None:
        return y_pred, y_true

    weights_shape = sample_weight.shape
    weights_rank = weights_shape.ndims
    if weights_rank == 0:  # If weights is scalar, do nothing.
        return y_pred, y_true, sample_weight

    if (y_pred_rank is not None) and (weights_rank is not None):
        # Use static rank.
        if weights_rank - y_pred_rank == 1:
            sample_weight = tf.squeeze(sample_weight, [-1])
        elif y_pred_rank - weights_rank == 1:
            sample_weight = tf.expand_dims(sample_weight, [-1])
        return y_pred, y_true, sample_weight

    # Use dynamic rank.
    weights_rank_tensor = tf.rank(sample_weight)
    rank_diff = weights_rank_tensor - tf.rank(y_pred)
    maybe_squeeze_weights = lambda: tf.squeeze(sample_weight, [-1])

    def _maybe_expand_weights():
        expand_weights = lambda: tf.expand_dims(sample_weight, [-1])
        return tf.cond(
            tf.equal(rank_diff, -1), expand_weights, lambda: sample_weight
        )

    def _maybe_adjust_weights():
        return tf.cond(
            tf.equal(rank_diff, 1), maybe_squeeze_weights, _maybe_expand_weights
        )

    # squeeze or expand last dim of `sample_weight` if its rank differs by 1
    # from the new rank of `y_pred`.
    sample_weight = tf.cond(
        tf.equal(weights_rank_tensor, 0),
        lambda: sample_weight,
        _maybe_adjust_weights,
    )
    return y_pred, y_true, sample_weight

def _filter_top_k(x, k):
    """Filters top-k values in the last dim of x and set the rest to NEG_INF.

    Used for computing top-k prediction values in dense labels (which has the
    same shape as predictions) for recall and precision top-k metrics.

    Args:
      x: tensor with any dimensions.
      k: the number of values to keep.

    Returns:
      tensor with same shape and dtype as x.
    """
    _, top_k_idx = tf.math.top_k(x, k, sorted=False)
    top_k_mask = tf.reduce_sum(
        tf.one_hot(top_k_idx, tf.shape(x)[-1], axis=-1), axis=-2
    )
    return x * top_k_mask + NEG_INF * (1 - top_k_mask)

def _update_confusion_matrix_variables_optimized(
    variables_to_update,
    y_true,
    y_pred,
    thresholds,
    multi_label=False,
    sample_weights=None,
    label_weights=None,
    thresholds_with_epsilon=False,
):
    """Update confusion matrix variables with memory efficient alternative.

    Note that the thresholds need to be evenly distributed within the list, eg,
    the diff between consecutive elements are the same.

    To compute TP/FP/TN/FN, we are measuring a binary classifier
      C(t) = (predictions >= t)
    at each threshold 't'. So we have
      TP(t) = sum( C(t) * true_labels )
      FP(t) = sum( C(t) * false_labels )

    But, computing C(t) requires computation for each t. To make it fast,
    observe that C(t) is a cumulative integral, and so if we have
      thresholds = [t_0, ..., t_{n-1}];  t_0 < ... < t_{n-1}
    where n = num_thresholds, and if we can compute the bucket function
      B(i) = Sum( (predictions == t), t_i <= t < t{i+1} )
    then we get
      C(t_i) = sum( B(j), j >= i )
    which is the reversed cumulative sum in tf.cumsum().

    We can compute B(i) efficiently by taking advantage of the fact that
    our thresholds are evenly distributed, in that
      width = 1.0 / (num_thresholds - 1)
      thresholds = [0.0, 1*width, 2*width, 3*width, ..., 1.0]
    Given a prediction value p, we can map it to its bucket by
      bucket_index(p) = floor( p * (num_thresholds - 1) )
    so we can use tf.math.unsorted_segment_sum() to update the buckets in one
    pass.

    Consider following example:
    y_true = [0, 0, 1, 1]
    y_pred = [0.1, 0.5, 0.3, 0.9]
    thresholds = [0.0, 0.5, 1.0]
    num_buckets = 2   # [0.0, 1.0], (1.0, 2.0]
    bucket_index(y_pred) = tf.math.floor(y_pred * num_buckets)
                         = tf.math.floor([0.2, 1.0, 0.6, 1.8])
                         = [0, 0, 0, 1]
    # The meaning of this bucket is that if any of the label is true,
    # then 1 will be added to the corresponding bucket with the index.
    # Eg, if the label for 0.2 is true, then 1 will be added to bucket 0. If the
    # label for 1.8 is true, then 1 will be added to bucket 1.
    #
    # Note the second item "1.0" is floored to 0, since the value need to be
    # strictly larger than the bucket lower bound.
    # In the implementation, we use tf.math.ceil() - 1 to achieve this.
    tp_bucket_value = tf.math.unsorted_segment_sum(true_labels, bucket_indices,
                                                   num_segments=num_thresholds)
                    = [1, 1, 0]
    # For [1, 1, 0] here, it means there is 1 true value contributed by bucket
    # 0, and 1 value contributed by bucket 1. When we aggregate them to
    # together, the result become [a + b + c, b + c, c], since large thresholds
    # will always contribute to the value for smaller thresholds.
    true_positive = tf.math.cumsum(tp_bucket_value, reverse=True)
                  = [2, 1, 0]

    This implementation exhibits a run time and space complexity of O(T + N),
    where T is the number of thresholds and N is the size of predictions.
    Metrics that rely on standard implementation instead exhibit a complexity of
    O(T * N).

    Args:
      variables_to_update: Dictionary with 'tp', 'fn', 'tn', 'fp' as valid keys
        and corresponding variables to update as values.
      y_true: A floating point `Tensor` whose shape matches `y_pred`. Will be
        cast to `bool`.
      y_pred: A floating point `Tensor` of arbitrary shape and whose values are
        in the range `[0, 1]`.
      thresholds: A sorted floating point `Tensor` with value in `[0, 1]`.
        It need to be evenly distributed (the diff between each element need to
        be the same).
      multi_label: Optional boolean indicating whether multidimensional
        prediction/labels should be treated as multilabel responses, or
        flattened into a single label. When True, the valus of
        `variables_to_update` must have a second dimension equal to the number
        of labels in y_true and y_pred, and those tensors must not be
        RaggedTensors.
      sample_weights: Optional `Tensor` whose rank is either 0, or the same rank
        as `y_true`, and must be broadcastable to `y_true` (i.e., all dimensions
        must be either `1`, or the same as the corresponding `y_true`
        dimension).
      label_weights: Optional tensor of non-negative weights for multilabel
        data. The weights are applied when calculating TP, FP, FN, and TN
        without explicit multilabel handling (i.e. when the data is to be
        flattened).
      thresholds_with_epsilon: Optional boolean indicating whether the leading
        and tailing thresholds has any epsilon added for floating point
        imprecisions.  It will change how we handle the leading and tailing
        bucket.

    Returns:
      Update op.
    """
    num_thresholds = thresholds.shape.as_list()[0]

    if sample_weights is None:
        sample_weights = 1.0
    else:
        sample_weights = tf.__internal__.ops.broadcast_weights(
            tf.cast(sample_weights, dtype=y_pred.dtype), y_pred
        )
        if not multi_label:
            sample_weights = tf.reshape(sample_weights, [-1])
    if label_weights is None:
        label_weights = 1.0
    else:
        label_weights = tf.expand_dims(label_weights, 0)
        label_weights = tf.__internal__.ops.broadcast_weights(
            label_weights, y_pred
        )
        if not multi_label:
            label_weights = tf.reshape(label_weights, [-1])
    weights = tf.cast(tf.multiply(sample_weights, label_weights), y_true.dtype)

    # We shouldn't need this, but in case there are predict value that is out of
    # the range of [0.0, 1.0]
    y_pred = tf.clip_by_value(y_pred, clip_value_min=0.0, clip_value_max=1.0)

    y_true = tf.cast(tf.cast(y_true, tf.bool), y_true.dtype)
    if not multi_label:
        y_true = tf.reshape(y_true, [-1])
        y_pred = tf.reshape(y_pred, [-1])

    true_labels = tf.multiply(y_true, weights)
    false_labels = tf.multiply((1.0 - y_true), weights)

    # Compute the bucket indices for each prediction value.
    # Since the predict value has to be strictly greater than the thresholds,
    # eg, buckets like [0, 0.5], (0.5, 1], and 0.5 belongs to first bucket.
    # We have to use math.ceil(val) - 1 for the bucket.
    bucket_indices = tf.math.ceil(y_pred * (num_thresholds - 1)) - 1

    if thresholds_with_epsilon:
        # In this case, the first bucket should actually take into account since
        # the any prediction between [0.0, 1.0] should be larger than the first
        # threshold. We change the bucket value from -1 to 0.
        bucket_indices = tf.nn.relu(bucket_indices)

    bucket_indices = tf.cast(bucket_indices, tf.int32)

    if multi_label:
        # We need to run bucket segment sum for each of the label class. In the
        # multi_label case, the rank of the label is 2. We first transpose it so
        # that the label dim becomes the first and we can parallel run though
        # them.
        true_labels = tf.transpose(true_labels)
        false_labels = tf.transpose(false_labels)
        bucket_indices = tf.transpose(bucket_indices)

        def gather_bucket(label_and_bucket_index):
            label, bucket_index = (
                label_and_bucket_index[0],
                label_and_bucket_index[1],
            )
            return tf.math.unsorted_segment_sum(
                data=label,
                segment_ids=bucket_index,
                num_segments=num_thresholds,
            )

        tp_bucket_v = tf.vectorized_map(
            gather_bucket, (true_labels, bucket_indices), warn=False
        )
        fp_bucket_v = tf.vectorized_map(
            gather_bucket, (false_labels, bucket_indices), warn=False
        )
        tp = tf.transpose(tf.cumsum(tp_bucket_v, reverse=True, axis=1))
        fp = tf.transpose(tf.cumsum(fp_bucket_v, reverse=True, axis=1))
    else:
        tp_bucket_v = tf.math.unsorted_segment_sum(
            data=true_labels,
            segment_ids=bucket_indices,
            num_segments=num_thresholds,
        )
        fp_bucket_v = tf.math.unsorted_segment_sum(
            data=false_labels,
            segment_ids=bucket_indices,
            num_segments=num_thresholds,
        )
        tp = tf.cumsum(tp_bucket_v, reverse=True)
        fp = tf.cumsum(fp_bucket_v, reverse=True)

    # fn = sum(true_labels) - tp
    # tn = sum(false_labels) - fp
    if (
        ConfusionMatrix.TRUE_NEGATIVES in variables_to_update
        or ConfusionMatrix.FALSE_NEGATIVES in variables_to_update
    ):
        if multi_label:
            total_true_labels = tf.reduce_sum(true_labels, axis=1)
            total_false_labels = tf.reduce_sum(false_labels, axis=1)
        else:
            total_true_labels = tf.reduce_sum(true_labels)
            total_false_labels = tf.reduce_sum(false_labels)

    update_ops = []
    if ConfusionMatrix.TRUE_POSITIVES in variables_to_update:
        variable = variables_to_update[ConfusionMatrix.TRUE_POSITIVES]
        update_ops.append(variable.assign_add(tp))
    if ConfusionMatrix.FALSE_POSITIVES in variables_to_update:
        variable = variables_to_update[ConfusionMatrix.FALSE_POSITIVES]
        update_ops.append(variable.assign_add(fp))
    if ConfusionMatrix.TRUE_NEGATIVES in variables_to_update:
        variable = variables_to_update[ConfusionMatrix.TRUE_NEGATIVES]
        tn = total_false_labels - fp
        update_ops.append(variable.assign_add(tn))
    if ConfusionMatrix.FALSE_NEGATIVES in variables_to_update:
        variable = variables_to_update[ConfusionMatrix.FALSE_NEGATIVES]
        fn = total_true_labels - tp
        update_ops.append(variable.assign_add(fn))
    return tf.group(update_ops)

def update_confusion_matrix_variables(
    variables_to_update,
    y_true,
    y_pred,
    thresholds,
    top_k=None,
    class_id=None,
    sample_weight=None,
    multi_label=False,
    label_weights=None,
    thresholds_distributed_evenly=False,
):
    """Returns op to update the given confusion matrix variables.

    For every pair of values in y_true and y_pred:

    true_positive: y_true == True and y_pred > thresholds
    false_negatives: y_true == True and y_pred <= thresholds
    true_negatives: y_true == False and y_pred <= thresholds
    false_positive: y_true == False and y_pred > thresholds

    The results will be weighted and added together. When multiple thresholds
    are provided, we will repeat the same for every threshold.

    For estimation of these metrics over a stream of data, the function creates
    an `update_op` operation that updates the given variables.

    If `sample_weight` is `None`, weights default to 1.
    Use weights of 0 to mask values.

    Args:
      variables_to_update: Dictionary with 'tp', 'fn', 'tn', 'fp' as valid keys
        and corresponding variables to update as values.
      y_true: A `Tensor` whose shape matches `y_pred`. Will be cast to `bool`.
      y_pred: A floating point `Tensor` of arbitrary shape and whose values are
        in the range `[0, 1]`.
      thresholds: A float value, float tensor, python list, or tuple of float
        thresholds in `[0, 1]`, or NEG_INF (used when top_k is set).
      top_k: Optional int, indicates that the positive labels should be limited
        to the top k predictions.
      class_id: Optional int, limits the prediction and labels to the class
        specified by this argument.
      sample_weight: Optional `Tensor` whose rank is either 0, or the same rank
        as `y_true`, and must be broadcastable to `y_true` (i.e., all dimensions
        must be either `1`, or the same as the corresponding `y_true`
        dimension).
      multi_label: Optional boolean indicating whether multidimensional
        prediction/labels should be treated as multilabel responses, or
        flattened into a single label. When True, the valus of
        `variables_to_update` must have a second dimension equal to the number
        of labels in y_true and y_pred, and those tensors must not be
        RaggedTensors.
      label_weights: (optional) tensor of non-negative weights for multilabel
        data. The weights are applied when calculating TP, FP, FN, and TN
        without explicit multilabel handling (i.e. when the data is to be
        flattened).
      thresholds_distributed_evenly: Boolean, whether the thresholds are evenly
        distributed within the list. An optimized method will be used if this is
        the case. See _update_confusion_matrix_variables_optimized() for more
        details.

    Returns:
      Update op.

    Raises:
      ValueError: If `y_pred` and `y_true` have mismatched shapes, or if
        `sample_weight` is not `None` and its shape doesn't match `y_pred`, or
        if `variables_to_update` contains invalid keys.
    """
    if multi_label and label_weights is not None:
        raise ValueError(
            "`label_weights` for multilabel data should be handled "
            "outside of `update_confusion_matrix_variables` when "
            "`multi_label` is True."
        )
    if variables_to_update is None:
        return
    if not any(
        key for key in variables_to_update if key in list(ConfusionMatrix)
    ):
        raise ValueError(
            "Please provide at least one valid confusion matrix "
            "variable to update. Valid variable key options are: "
            f'"{list(ConfusionMatrix)}". '
            f'Received: "{variables_to_update.keys()}"'
        )

    variable_dtype = list(variables_to_update.values())[0].dtype

    y_true = tf.cast(y_true, dtype=variable_dtype)
    y_pred = tf.cast(y_pred, dtype=variable_dtype)

    if thresholds_distributed_evenly:
        # Check whether the thresholds has any leading or tailing epsilon added
        # for floating point imprecision. The leading and tailing threshold will
        # be handled bit differently as the corner case.  At this point,
        # thresholds should be a list/array with more than 2 items, and ranged
        # between [0, 1]. See is_evenly_distributed_thresholds() for more
        # details.
        thresholds_with_epsilon = thresholds[0] < 0.0 or thresholds[-1] > 1.0

    thresholds = tf.convert_to_tensor(thresholds, dtype=variable_dtype)
    num_thresholds = thresholds.shape.as_list()[0]

    if multi_label:
        one_thresh = tf.equal(
            tf.cast(1, dtype=tf.int32),
            tf.rank(thresholds),
            name="one_set_of_thresholds_cond",
        )
    else:
        [y_pred, y_true], _ = ragged_assert_compatible_and_get_flat_values(
            [y_pred, y_true], sample_weight
        )
        one_thresh = tf.cast(True, dtype=tf.bool)

    invalid_keys = [
        key for key in variables_to_update if key not in list(ConfusionMatrix)
    ]
    if invalid_keys:
        raise ValueError(
            f'Invalid keys: "{invalid_keys}". '
            f'Valid variable key options are: "{list(ConfusionMatrix)}"'
        )

    if sample_weight is None:
        y_pred, y_true = squeeze_or_expand_dimensions(
            y_pred, y_true
        )
    else:
        sample_weight = tf.cast(sample_weight, dtype=variable_dtype)
        (
            y_pred,
            y_true,
            sample_weight,
        ) = squeeze_or_expand_dimensions(
            y_pred, y_true, sample_weight=sample_weight
        )
    y_pred.shape.assert_is_compatible_with(y_true.shape)

    if top_k is not None:
        y_pred = _filter_top_k(y_pred, top_k)
    if class_id is not None:
        # Preserve dimension to match with sample_weight
        y_true = y_true[..., class_id, None]
        y_pred = y_pred[..., class_id, None]

    if thresholds_distributed_evenly:
        return _update_confusion_matrix_variables_optimized(
            variables_to_update,
            y_true,
            y_pred,
            thresholds,
            multi_label=multi_label,
            sample_weights=sample_weight,
            label_weights=label_weights,
            thresholds_with_epsilon=thresholds_with_epsilon,
        )

    pred_shape = tf.shape(y_pred)
    num_predictions = pred_shape[0]
    if y_pred.shape.ndims == 1:
        num_labels = 1
    else:
        num_labels = tf.math.reduce_prod(pred_shape[1:], axis=0)
    thresh_label_tile = tf.where(
        one_thresh, num_labels, tf.ones([], dtype=tf.int32)
    )

    # Reshape predictions and labels, adding a dim for thresholding.
    if multi_label:
        predictions_extra_dim = tf.expand_dims(y_pred, 0)
        labels_extra_dim = tf.expand_dims(tf.cast(y_true, dtype=tf.bool), 0)
    else:
        # Flatten predictions and labels when not multilabel.
        predictions_extra_dim = tf.reshape(y_pred, [1, -1])
        labels_extra_dim = tf.reshape(tf.cast(y_true, dtype=tf.bool), [1, -1])

    # Tile the thresholds for every prediction.
    if multi_label:
        thresh_pretile_shape = [num_thresholds, 1, -1]
        thresh_tiles = [1, num_predictions, thresh_label_tile]
        data_tiles = [num_thresholds, 1, 1]
    else:
        thresh_pretile_shape = [num_thresholds, -1]
        thresh_tiles = [1, num_predictions * num_labels]
        data_tiles = [num_thresholds, 1]

    thresh_tiled = tf.tile(
        tf.reshape(thresholds, thresh_pretile_shape), tf.stack(thresh_tiles)
    )

    # Tile the predictions for every threshold.
    preds_tiled = tf.tile(predictions_extra_dim, data_tiles)

    # Compare predictions and threshold.
    pred_is_pos = tf.greater(preds_tiled, thresh_tiled)

    # Tile labels by number of thresholds
    label_is_pos = tf.tile(labels_extra_dim, data_tiles)

    if sample_weight is not None:
        sample_weight = tf.__internal__.ops.broadcast_weights(
            tf.cast(sample_weight, dtype=variable_dtype), y_pred
        )
        weights_tiled = tf.tile(
            tf.reshape(sample_weight, thresh_tiles), data_tiles
        )
    else:
        weights_tiled = None

    if label_weights is not None and not multi_label:
        label_weights = tf.expand_dims(label_weights, 0)
        label_weights = tf.__internal__.ops.broadcast_weights(
            label_weights, y_pred
        )
        label_weights_tiled = tf.tile(
            tf.reshape(label_weights, thresh_tiles), data_tiles
        )
        if weights_tiled is None:
            weights_tiled = label_weights_tiled
        else:
            weights_tiled = tf.multiply(weights_tiled, label_weights_tiled)

    update_ops = []

    def weighted_assign_add(label, pred, weights, var):
        label_and_pred = tf.cast(tf.logical_and(label, pred), dtype=var.dtype)
        if weights is not None:
            label_and_pred *= tf.cast(weights, dtype=var.dtype)
        return var.assign_add(tf.reduce_sum(label_and_pred, 1))

    loop_vars = {
        ConfusionMatrix.TRUE_POSITIVES: (label_is_pos, pred_is_pos),
    }
    update_tn = ConfusionMatrix.TRUE_NEGATIVES in variables_to_update
    update_fp = ConfusionMatrix.FALSE_POSITIVES in variables_to_update
    update_fn = ConfusionMatrix.FALSE_NEGATIVES in variables_to_update

    if update_fn or update_tn:
        pred_is_neg = tf.logical_not(pred_is_pos)
        loop_vars[ConfusionMatrix.FALSE_NEGATIVES] = (label_is_pos, pred_is_neg)

    if update_fp or update_tn:
        label_is_neg = tf.logical_not(label_is_pos)
        loop_vars[ConfusionMatrix.FALSE_POSITIVES] = (label_is_neg, pred_is_pos)
        if update_tn:
            loop_vars[ConfusionMatrix.TRUE_NEGATIVES] = (
                label_is_neg,
                pred_is_neg,
            )

    for matrix_cond, (label, pred) in loop_vars.items():

        if matrix_cond in variables_to_update:
            update_ops.append(
                weighted_assign_add(
                    label, pred, weights_tiled, variables_to_update[matrix_cond]
                )
            )

    return tf.group(update_ops)

def inject_mesh(init_method):
    """Inject DTensor mesh information to an object.

    This is useful for keras object like `Metric` and `Optimizer` which need
    DTensor mesh to create the weights, but doesn't want to change the current
    public API interface.

    This is for temporary usage and eventually the mesh/layout information will
    be public arguments in the `__init__` method.

    Sample usage:
    ```python
    class Accuracy(tf.keras.metrics.Metric):

      @inject_mesh
      def __init__(self, name='accuracy', dtype=None):
         super().__init__(**kwargs)

      acc = Accuracy(mesh=mesh)
      assert acc._mesh == mesh
    ```

    Args:
      init_method: the `__init__` method of the Keras class to annotate.

    Returns:
      the annotated __init__ method.
    """

    def _wrap_function(instance, *args, **kwargs):
        mesh = kwargs.pop("mesh", None)
        # Note that the injection of _mesh need to happen before the invocation
        # of __init__, since the class might need the mesh to create weights in
        # the __init__.
        if mesh is not None:
            instance._mesh = mesh
        init_method(instance, *args, **kwargs)

    return tf.__internal__.decorator.make_decorator(
        target=init_method, decorator_func=_wrap_function
    )


class SensitivitySpecificityBase(Metric, metaclass=abc.ABCMeta):
    """Abstract base class for computing sensitivity and specificity.

    For additional information about specificity and sensitivity, see
    [the following](https://en.wikipedia.org/wiki/Sensitivity_and_specificity).
    """

    def __init__(
        self, value, num_thresholds=200, class_id=None, name=None, dtype=None
    ):
        super().__init__(name=name, dtype=dtype)
        if num_thresholds <= 0:
            raise ValueError(
                "Argument `num_thresholds` must be an integer > 0. "
                f"Received: num_thresholds={num_thresholds}"
            )
        self.value = value
        self.class_id = class_id
        self.true_positives = self.add_weight(
            name="true_positives", shape=(num_thresholds,), initializer="zeros"
        )
        self.true_negatives = self.add_weight(
            name="true_negatives", shape=(num_thresholds,), initializer="zeros"
        )
        self.false_positives = self.add_weight(
            name="false_positives", shape=(num_thresholds,), initializer="zeros"
        )
        self.false_negatives = self.add_weight(
            name="false_negatives", shape=(num_thresholds,), initializer="zeros"
        )

        # Compute `num_thresholds` thresholds in [0, 1]
        if num_thresholds == 1:
            self.thresholds = [0.5]
            self._thresholds_distributed_evenly = False
        else:
            thresholds = [
                (i + 1) * 1.0 / (num_thresholds - 1)
                for i in range(num_thresholds - 2)
            ]
            self.thresholds = [0.0] + thresholds + [1.0]
            self._thresholds_distributed_evenly = True

    def update_state(self, y_true, y_pred, sample_weight=None):
        """Accumulates confusion matrix statistics.

        Args:
          y_true: The ground truth values.
          y_pred: The predicted values.
          sample_weight: Optional weighting of each example. Defaults to 1. Can
            be a `Tensor` whose rank is either 0, or the same rank as `y_true`,
            and must be broadcastable to `y_true`.

        Returns:
          Update op.
        """
        return update_confusion_matrix_variables(
            {
                ConfusionMatrix.TRUE_POSITIVES: self.true_positives,  # noqa: E501
                ConfusionMatrix.TRUE_NEGATIVES: self.true_negatives,  # noqa: E501
                ConfusionMatrix.FALSE_POSITIVES: self.false_positives,  # noqa: E501
                ConfusionMatrix.FALSE_NEGATIVES: self.false_negatives,  # noqa: E501
            },
            y_true,
            y_pred,
            thresholds=self.thresholds,
            thresholds_distributed_evenly=self._thresholds_distributed_evenly,
            class_id=self.class_id,
            sample_weight=sample_weight,
        )

    def reset_state(self):
        num_thresholds = len(self.thresholds)
        confusion_matrix_variables = (
            self.true_positives,
            self.true_negatives,
            self.false_positives,
            self.false_negatives,
        )
        backend.batch_set_value(
            [
                (v, np.zeros((num_thresholds,)))
                for v in confusion_matrix_variables
            ]
        )

    def get_config(self):
        config = {"class_id": self.class_id}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def _find_max_under_constraint(self, constrained, dependent, predicate):
        """Returns the maximum of dependent_statistic that satisfies the
        constraint.

        Args:
          constrained: Over these values the constraint
            is specified. A rank-1 tensor.
          dependent: From these values the maximum that satiesfies the
            constraint is selected. Values in this tensor and in
            `constrained` are linked by having the same threshold at each
            position, hence this tensor must have the same shape.
          predicate: A binary boolean functor to be applied to arguments
          `constrained` and `self.value`, e.g. `tf.greater`.

        Returns:
          maximal dependent value, if no value satiesfies the constraint 0.0.
        """
        feasible = tf.where(predicate(constrained, self.value))
        feasible_exists = tf.greater(tf.size(feasible), 0)
        max_dependent = tf.reduce_max(tf.gather(dependent, feasible))

        return tf.where(feasible_exists, max_dependent, 0.0)



class ThresholdAtPrecision(SensitivitySpecificityBase):
    """Computes best recall where precision is >= specified value.

    For a given score-label-distribution the required precision might not
    be achievable, in this case 0.0 is returned as recall.

    This metric creates four local variables, `true_positives`,
    `true_negatives`, `false_positives` and `false_negatives` that are used to
    compute the recall at the given precision. The threshold for the given
    precision value is computed and used to evaluate the corresponding recall.

    If `sample_weight` is `None`, weights default to 1.
    Use `sample_weight` of 0 to mask values.

    If `class_id` is specified, we calculate precision by considering only the
    entries in the batch for which `class_id` is above the threshold
    predictions, and computing the fraction of them for which `class_id` is
    indeed a correct label.

    Args:
      precision: A scalar value in range `[0, 1]`.
      num_thresholds: (Optional) Defaults to 200. The number of thresholds to
        use for matching the given precision.
      class_id: (Optional) Integer class ID for which we want binary metrics.
        This must be in the half-open interval `[0, num_classes)`, where
        `num_classes` is the last dimension of predictions.
      name: (Optional) string name of the metric instance.
      dtype: (Optional) data type of the metric result.

    Standalone usage:

    >>> m = tf.keras.metrics.RecallAtPrecision(0.8)
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9])
    >>> m.result().numpy()
    0.5

    >>> m.reset_state()
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9],
    ...                sample_weight=[1, 0, 0, 1])
    >>> m.result().numpy()
    1.0

    Usage with `compile()` API:

    ```python
    model.compile(
        optimizer='sgd',
        loss='mse',
        metrics=[tf.keras.metrics.RecallAtPrecision(precision=0.8)])
    ```
    """

    @inject_mesh
    def __init__(
        self,
        precision,
        num_thresholds=200,
        class_id=None,
        name=None,
        dtype=None,
    ):
        if precision < 0 or precision > 1:
            raise ValueError(
                "Argument `precision` must be in the range [0, 1]. "
                f"Received: precision={precision}"
            )
        self.precision = precision
        self.num_thresholds = num_thresholds
        super().__init__(
            value=precision,
            num_thresholds=num_thresholds,
            class_id=class_id,
            name=name,
            dtype=dtype,
        )

    def result(self):
        precisions = tf.math.divide_no_nan(
            self.true_positives,
            tf.math.add(self.true_positives, self.false_positives),
        )
        recalls = tf.math.divide_no_nan(
            self.true_positives,
            tf.math.add(self.true_positives, self.false_negatives),
        )
        return self._find_max_threshold_under_constraint(
            precisions, recalls, tf.greater_equal
        )

    def _find_max_threshold_under_constraint(self, constrained, dependent, predicate):
        """Returns the maximum of dependent_statistic that satisfies the
        constraint.

        Args:
          constrained: Over these values the constraint
            is specified. A rank-1 tensor.
          dependent: From these values the maximum that satiesfies the
            constraint is selected. Values in this tensor and in
            `constrained` are linked by having the same threshold at each
            position, hence this tensor must have the same shape.
          predicate: A binary boolean functor to be applied to arguments
          `constrained` and `self.value`, e.g. `tf.greater`.

        Returns:
          maximal dependent value, if no value satiesfies the constraint 0.0.
        """
        variable_dtype = self.true_positives.dtype
        thresholds = tf.convert_to_tensor(self.thresholds, dtype=variable_dtype)
        feasible = tf.where(predicate(constrained, self.value))
        feasible_exists = tf.greater(tf.size(feasible), 0)
        try:
            return tf.where(feasible_exists, tf.gather(thresholds, tf.gather(feasible, [0])), 0.0)
        except Exception as e:
            print("Error " + str(e))
            return 0.0 

    def get_config(self):
        config = {
            "num_thresholds": self.num_thresholds,
            "precision": self.precision,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ThresholdAtRecall(SensitivitySpecificityBase):
    """Computes best recall where precision is >= specified value.

    For a given score-label-distribution the required precision might not
    be achievable, in this case 0.0 is returned as recall.

    This metric creates four local variables, `true_positives`,
    `true_negatives`, `false_positives` and `false_negatives` that are used to
    compute the recall at the given precision. The threshold for the given
    precision value is computed and used to evaluate the corresponding recall.

    If `sample_weight` is `None`, weights default to 1.
    Use `sample_weight` of 0 to mask values.

    If `class_id` is specified, we calculate precision by considering only the
    entries in the batch for which `class_id` is above the threshold
    predictions, and computing the fraction of them for which `class_id` is
    indeed a correct label.

    Args:
      recall: A scalar value in range `[0, 1]`.
      num_thresholds: (Optional) Defaults to 200. The number of thresholds to
        use for matching the given precision.
      class_id: (Optional) Integer class ID for which we want binary metrics.
        This must be in the half-open interval `[0, num_classes)`, where
        `num_classes` is the last dimension of predictions.
      name: (Optional) string name of the metric instance.
      dtype: (Optional) data type of the metric result.

    Standalone usage:

    >>> m = tf.keras.metrics.RecallAtPrecision(0.8)
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9])
    >>> m.result().numpy()
    0.5

    >>> m.reset_state()
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9],
    ...                sample_weight=[1, 0, 0, 1])
    >>> m.result().numpy()
    1.0

    Usage with `compile()` API:

    ```python
    model.compile(
        optimizer='sgd',
        loss='mse',
        metrics=[tf.keras.metrics.RecallAtPrecision(precision=0.8)])
    ```
    """

    @inject_mesh
    def __init__(
        self,
        recall,
        num_thresholds=200,
        class_id=None,
        name=None,
        dtype=None,
    ):
        if recall < 0 or recall > 1:
            raise ValueError(
                "Argument `recall` must be in the range [0, 1]. "
                f"Received: recall={recall}"
            )
        self.recall = recall
        self.num_thresholds = num_thresholds
        super().__init__(
            value=recall,
            num_thresholds=num_thresholds,
            class_id=class_id,
            name=name,
            dtype=dtype,
        )

    def result(self):
        precisions = tf.math.divide_no_nan(
            self.true_positives,
            tf.math.add(self.true_positives, self.false_positives),
        )
        recalls = tf.math.divide_no_nan(
            self.true_positives,
            tf.math.add(self.true_positives, self.false_negatives),
        )
        return self._find_max_threshold_under_constraint(
            recalls, precisions, tf.greater_equal
        )

    def _find_max_threshold_under_constraint(self, constrained, dependent, predicate):
        """Returns the maximum of dependent_statistic that satisfies the
        constraint.

        Args:
          constrained: Over these values the constraint
            is specified. A rank-1 tensor.
          dependent: From these values the maximum that satiesfies the
            constraint is selected. Values in this tensor and in
            `constrained` are linked by having the same threshold at each
            position, hence this tensor must have the same shape.
          predicate: A binary boolean functor to be applied to arguments
          `constrained` and `self.value`, e.g. `tf.greater`.

        Returns:
          maximal dependent value, if no value satiesfies the constraint 0.0.
        """
        variable_dtype = self.true_positives.dtype
        thresholds = tf.convert_to_tensor(self.thresholds, dtype=variable_dtype)
        feasible = tf.where(predicate(constrained, self.value))
        feasible_exists = tf.greater(tf.size(feasible), 0)
        return tf.where(feasible_exists, tf.gather(thresholds, tf.gather(feasible, [0])), 0.0)

    def get_config(self):
        config = {
            "num_thresholds": self.num_thresholds,
            "recall": self.recall,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ThresholdAtNPV(SensitivitySpecificityBase):
    """Computes best recall where precision is >= specified value.

    For a given score-label-distribution the required precision might not
    be achievable, in this case 0.0 is returned as recall.

    This metric creates four local variables, `true_positives`,
    `true_negatives`, `false_positives` and `false_negatives` that are used to
    compute the recall at the given precision. The threshold for the given
    precision value is computed and used to evaluate the corresponding recall.

    If `sample_weight` is `None`, weights default to 1.
    Use `sample_weight` of 0 to mask values.

    If `class_id` is specified, we calculate precision by considering only the
    entries in the batch for which `class_id` is above the threshold
    predictions, and computing the fraction of them for which `class_id` is
    indeed a correct label.

    Args:
      npv: A scalar value in range `[0, 1]`.
      num_thresholds: (Optional) Defaults to 200. The number of thresholds to
        use for matching the given precision.
      class_id: (Optional) Integer class ID for which we want binary metrics.
        This must be in the half-open interval `[0, num_classes)`, where
        `num_classes` is the last dimension of predictions.
      name: (Optional) string name of the metric instance.
      dtype: (Optional) data type of the metric result.

    Standalone usage:

    >>> m = tf.keras.metrics.RecallAtPrecision(0.8)
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9])
    >>> m.result().numpy()
    0.5

    >>> m.reset_state()
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9],
    ...                sample_weight=[1, 0, 0, 1])
    >>> m.result().numpy()
    1.0

    Usage with `compile()` API:

    ```python
    model.compile(
        optimizer='sgd',
        loss='mse',
        metrics=[tf.keras.metrics.RecallAtPrecision(precision=0.8)])
    ```
    """

    @inject_mesh
    def __init__(
        self,
        npv,
        num_thresholds=200,
        class_id=None,
        name=None,
        dtype=None,
    ):
        if npv < 0 or npv > 1:
            raise ValueError(
                "Argument `npv` must be in the range [0, 1]. "
                f"Received: npv={npv}"
            )
        self.npv = npv
        self.num_thresholds = num_thresholds
        super().__init__(
            value=npv,
            num_thresholds=num_thresholds,
            class_id=class_id,
            name=name,
            dtype=dtype,
        )

    def result(self):
        npvs = tf.math.divide_no_nan(
            self.true_negatives,
            tf.math.add(self.true_negatives, self.false_negatives),
        )
        specificities = tf.math.divide_no_nan(
            self.true_negatives,
            tf.math.add(self.true_negatives, self.false_positives),
        )
        return self._find_max_threshold_under_constraint(
            npvs, specificities, tf.greater_equal
        )

    def _find_max_threshold_under_constraint(self, constrained, dependent, predicate):
        """Returns the maximum of dependent_statistic that satisfies the
        constraint.

        Args:
          constrained: Over these values the constraint
            is specified. A rank-1 tensor.
          dependent: From these values the maximum that satiesfies the
            constraint is selected. Values in this tensor and in
            `constrained` are linked by having the same threshold at each
            position, hence this tensor must have the same shape.
          predicate: A binary boolean functor to be applied to arguments
          `constrained` and `self.value`, e.g. `tf.greater`.

        Returns:
          maximal dependent value, if no value satiesfies the constraint 0.0.
        """
        variable_dtype = self.true_negatives.dtype
        thresholds = tf.convert_to_tensor(self.thresholds, dtype=variable_dtype)
        feasible = tf.where(predicate(constrained, self.value))
        feasible_exists = tf.greater(tf.size(feasible), 0)
        index = tf.size(feasible) - 1
        index = tf.where(tf.greater_equal(index, 0), index, 0)
        try:
            return tf.where(feasible_exists,
                            # tf.gather(thresholds, tf.gather(feasible, [tf.shape(feasible)[0] - 1])),
                            tf.gather(thresholds, tf.gather(feasible, [index])),
                            0.0)
        except Exception as e:
            print("Unexpected exception in thresholdAtNPV. " + str(e))
            return 0.0

    def get_config(self):
        config = {
            "num_thresholds": self.num_thresholds,
            "npv": self.npv,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


@tf.function
def tp_tf(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = y_true
    y_pred_label = y_pred
    real_positive_indexes_mask = tf.math.greater(y_true_label, 0)
    predicted_positive_indexes_mask = tf.math.greater(y_pred_label, threshold)
    positive_indexes_intersect_mask = tf.math.logical_and(predicted_positive_indexes_mask, real_positive_indexes_mask)
    predicted_positives = tf.cast(tf.size(tf.where(predicted_positive_indexes_mask)), tf.float32)
    predicted_positives_in_true_set = tf.cast(tf.size(tf.where(positive_indexes_intersect_mask)), tf.float32)
    tp = predicted_positives_in_true_set / (predicted_positives + tf.keras.backend.epsilon())
    return tp


@tf.function
def fp_tf(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = y_true
    y_pred_label = y_pred
    real_positive_indexes_mask = tf.math.greater(y_true_label, 0)
    predicted_positive_indexes_mask = tf.math.greater(y_pred_label, threshold)
    positive_indexes_intersect_mask = tf.math.logical_and(predicted_positive_indexes_mask, real_positive_indexes_mask)
    predicted_positives = tf.cast(tf.size(tf.where(predicted_positive_indexes_mask)), tf.float32)
    predicted_positives_in_true_set = tf.cast(tf.size(tf.where(positive_indexes_intersect_mask)), tf.float32)
    fp = (predicted_positives - predicted_positives_in_true_set) / (predicted_positives + K.epsilon())
    return fp


@tf.function
def fn_tf(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    real_negative_indexes_mask = tf.math.equal(y_true_label, 0)
    predicted_negative_indexes_mask = tf.math.less_equal(y_pred_label, threshold)
    negative_indexes_intersect_mask = tf.math.logical_and(predicted_negative_indexes_mask, real_negative_indexes_mask)
    predicted_negative_indexes_mask = tf.math.less_equal(y_pred_label, threshold)
    predicted_negatives = tf.cast(tf.size(tf.where(predicted_negative_indexes_mask)), tf.float32)
    predicted_negatives_in_true_set = tf.cast(tf.size(tf.where(negative_indexes_intersect_mask)), tf.float32)
    fn = (predicted_negatives - predicted_negatives_in_true_set) / (predicted_negatives + K.epsilon())
    return fn


@tf.function
def tn_tf(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    real_negative_indexes_mask = tf.math.equal(y_true_label, 0)
    predicted_negative_indexes_mask = tf.math.less_equal(y_pred_label, threshold)
    negative_indexes_intersect_mask = tf.math.logical_and(predicted_negative_indexes_mask, real_negative_indexes_mask)
    predicted_negative_indexes_mask = tf.math.less_equal(y_pred_label, threshold)
    predicted_negatives = tf.cast(tf.size(tf.where(predicted_negative_indexes_mask)), tf.float32)
    predicted_negatives_in_true_set = tf.cast(tf.size(tf.where(negative_indexes_intersect_mask)), tf.float32)
    tn = predicted_negatives_in_true_set / (predicted_negatives + tf.keras.backend.epsilon())
    return tn


@tf.function
def precision_tf(y_true, y_pred, label_index=0, threshold=0.5):
    tp = tp_tf(y_true, y_pred, label_index, threshold)
    fp = fp_tf(y_true, y_pred, label_index, threshold)
    return tp / (tp + fp + K.epsilon())


@tf.function
def recall_tf(y_true, y_pred, label_index=0, threshold=0.5):
    tp = tp_tf(y_true, y_pred, label_index, threshold)
    fn = fn_tf(y_true, y_pred, label_index, threshold)
    return tp / (tp + fn + K.epsilon())


@tf.function
def f1_score_tf(y_true, y_pred, label_index=0, threshold=0.5):
    precision = precision_tf(y_true, y_pred, label_index, threshold)
    recall = recall_tf(y_true, y_pred, label_index, threshold)
    return 2 * precision * recall / (precision + recall + K.epsilon())

@tf.function
def precision_at_k(y_true, y_pred, label_index=0, k=100, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    values, indices = tf.math.top_k(y_pred_label, k=k)
    y_true_label = tf.gather(y_true_label, indices)
    y_pred_label = tf.gather(y_pred_label, indices)
    return precision_tf(y_true_label, y_pred_label, label_index=0, threshold=threshold)

@tf.function
def mean_positive_value(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    positive_pred_indexes = tf.where(tf.greater(y_pred_label, threshold))
    return tf.reduce_mean(tf.gather(y_pred_label, positive_pred_indexes))

@tf.function
def mean_true_positive_value(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    tp_pred_indexes = tf.where(tf.logical_and(tf.greater(y_pred_label, threshold), tf.equal(y_true_label, 1)))
    return tf.reduce_mean(tf.gather(y_pred_label, tp_pred_indexes))

@tf.function
def mean_false_positive_value(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    fp_pred_indexes = tf.where(tf.logical_and(tf.greater(y_pred_label, threshold), tf.equal(y_true_label, 0)))
    return tf.reduce_mean(tf.gather(y_pred_label, fp_pred_indexes))

@tf.function
def mean_negative_value(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    negative_pred_indexes = tf.where(tf.less(y_pred_label, threshold))
    return tf.reduce_mean(tf.gather(y_pred_label, negative_pred_indexes))

@tf.function
def mean_true_negative_value(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    tp_pred_indexes = tf.where(tf.logical_and(tf.less(y_pred_label, threshold), tf.equal(y_true_label, 0)))
    return tf.reduce_mean(tf.gather(y_pred_label, tp_pred_indexes))

@tf.function
def mean_false_negative_value(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_true_label = y_true_label[:, 0]
    y_pred_label = y_pred_label[:, 0]
    tp_pred_indexes = tf.where(tf.logical_and(tf.less(y_pred_label, threshold), tf.equal(y_true_label, 1)))
    return tf.reduce_mean(tf.gather(y_pred_label, tp_pred_indexes))

@tf.function
def confusion_matrix_values_tf(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = tf.gather(y_true, [label_index], axis=1)
    y_pred_label = tf.gather(y_pred, [label_index], axis=1)
    y_pred_label = tf.reshape(y_pred_label, tf.shape(y_pred_label)[0])
    y_true_label = tf.reshape(y_true_label, tf.shape(y_true_label)[0])
    real_positive_indexes_mask = tf.math.greater(y_true_label, 0)
    predicted_positive_indexes_mask = tf.math.greater(y_pred_label, threshold)
    positive_indexes_intersect_mask = tf.math.logical_and(predicted_positive_indexes_mask, real_positive_indexes_mask)
    predicted_positives = tf.where(predicted_positive_indexes_mask).shape.as_list()[0]
    predicted_positives_in_true_set = tf.where(positive_indexes_intersect_mask).shape.as_list()[0]
    tp = predicted_positives_in_true_set / (predicted_positives + tf.keras.backend.epsilon())
    real_negative_indexes_mask = tf.math.equal(y_true_label, 0)
    predicted_negative_indexes_mask = tf.math.less_equal(y_pred_label, threshold)
    negative_indexes_intersect_mask = tf.math.logical_and(predicted_negative_indexes_mask, real_negative_indexes_mask)
    predicted_negatives = tf.where(predicted_negative_indexes_mask).shape.as_list()[0]
    predicted_negatives_in_true_set = tf.where(negative_indexes_intersect_mask).shape.as_list()[0]
    correct_predictions = predicted_positives_in_true_set + predicted_negatives_in_true_set
    total_predictions = y_true.shape.as_list()[0]
    accuracy = correct_predictions / (total_predictions + K.epsilon())
    error_rate = 1 - accuracy
    #TODO decide what values to be returned when no positives are detected
    if predicted_positives == 0:
        return [[np.nan, np.nan], [np.nan, np.nan]], accuracy, error_rate, np.nan, np.nan, np.nan, np.nan
    else:
        tn = predicted_negatives_in_true_set / (predicted_negatives + tf.keras.backend.epsilon())
        fp = (predicted_positives - predicted_positives_in_true_set) / (predicted_positives + K.epsilon())
        fn = (predicted_negatives - predicted_negatives_in_true_set) / (predicted_negatives + K.epsilon())
        precision = tp / (tp + fp + K.epsilon())
        recall = tp / (tp + fn + K.epsilon())
        f1_score = 2 * precision * recall / (precision + recall + K.epsilon())
        return [[tp, fp], [fn, tn]], accuracy, error_rate, precision, recall, f1_score, np.nan


def confusion_matrix_values(y_true, y_pred, label_index=0, threshold=0.5):
    y_true_label = np.transpose(y_true)[label_index]
    y_pred_label = np.transpose(y_pred)[label_index]
    real_positive_indexes_mask = y_true_label > 0
    predicted_positive_indexes_mask = y_pred_label > threshold
    positive_indexes_intersect_mask = np.logical_and(predicted_positive_indexes_mask, real_positive_indexes_mask)
    predicted_positives = len(np.argwhere(predicted_positive_indexes_mask).flatten())
    predicted_positives_in_true_set = len(np.argwhere(positive_indexes_intersect_mask).flatten())
    tp = predicted_positives_in_true_set / (predicted_positives + tf.keras.backend.epsilon())
    real_negative_indexes_mask = y_true_label == 0
    predicted_negative_indexes_mask = y_pred_label < threshold
    negative_indexes_intersect_mask = np.logical_and(predicted_negative_indexes_mask, real_negative_indexes_mask)
    predicted_negatives = len(np.argwhere(predicted_negative_indexes_mask).flatten())
    predicted_negatives_in_true_set = len(np.argwhere(negative_indexes_intersect_mask).flatten())
    correct_predictions = predicted_positives_in_true_set + predicted_negatives_in_true_set
    total_predictions = len(y_true)
    accuracy = correct_predictions / (total_predictions + K.epsilon())
    error_rate = 1 - accuracy
    #TODO decide what values to be returned when no positives are detected
    if predicted_positives == 0:
        return [[np.nan, np.nan], [np.nan, np.nan]], accuracy, error_rate, np.nan, np.nan, np.nan
    else:
        tn = predicted_negatives_in_true_set / (predicted_negatives + K.epsilon())
        fp = (predicted_positives - predicted_positives_in_true_set) / (predicted_positives + K.epsilon())
        fn = (predicted_negatives - predicted_negatives_in_true_set) / (predicted_negatives + K.epsilon())
        precision = tp / (tp + fp + K.epsilon())
        recall = tp / (tp + fn + K.epsilon())
        f1_score = 2 * precision * recall / (precision + recall + K.epsilon())
        return [[tp, fp], [fn, tn]], accuracy, error_rate, precision, recall, f1_score

def area_under_curve(y_true, y_pred, label_index=0, thresholds=100, method='roc'):
    confusion_matrixes = np.empty((thresholds, 2, 2))
    accuracies = np.zeros(thresholds)
    error_rates = np.zeros(thresholds)
    precisions = np.zeros(thresholds)
    recalls = np.zeros(thresholds)
    f1_scores = np.zeros(thresholds)
    threshold_values = np.flip(np.linspace(0, 1, thresholds))
    for index, threshold in enumerate(threshold_values):
        confusion_matrixes[index], accuracies[index], error_rates[index], precisions[index], recalls[index], \
            f1_scores[index] = confusion_matrix_values(y_true, y_pred, label_index=label_index, threshold=threshold)
    nan_values = np.logical_and(np.isnan(recalls), np.isnan(precisions))
    x = recalls[~nan_values]
    y = precisions[~nan_values]
    threshold_values = threshold_values[~nan_values]
    return x, y, threshold_values, np.trapz(y, x)


class CategoricalClassMetric(tf.keras.metrics.Metric):
    def __init__(self, class_index, metric_function, batch_size, name="categorical_class_metric", metric_threshold=0.5,
                 **kwargs):
        super(CategoricalClassMetric, self).__init__(name=name, **kwargs)
        self.batch_size = batch_size
        self.metric_function = metric_function
        self.metric_threshold = metric_threshold
        self.class_index = class_index
        self.metric = 0

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.metric = self.metric_function(y_true, y_pred, self.class_index, self.metric_threshold)

    def result(self):
        return self.metric

class NegativePredictiveValue(Metric):
    """Computes the NPV of the predictions with respect to the labels.

    The metric creates two local variables, `true_positives` and
    `false_positives` that are used to compute the precision. This value is
    ultimately returned as `precision`, an idempotent operation that simply
    divides `true_positives` by the sum of `true_positives` and
    `false_positives`.

    If `sample_weight` is `None`, weights default to 1.
    Use `sample_weight` of 0 to mask values.

    If `top_k` is set, we'll calculate precision as how often on average a class
    among the top-k classes with the highest predicted values of a batch entry
    is correct and can be found in the label for that entry.

    If `class_id` is specified, we calculate precision by considering only the
    entries in the batch for which `class_id` is above the threshold and/or in
    the top-k highest predictions, and computing the fraction of them for which
    `class_id` is indeed a correct label.

    Args:
      thresholds: (Optional) A float value, or a Python list/tuple of float
        threshold values in [0, 1]. A threshold is compared with prediction
        values to determine the truth value of predictions (i.e., above the
        threshold is `true`, below is `false`). If used with a loss function
        that sets `from_logits=True` (i.e. no sigmoid applied to predictions),
        `thresholds` should be set to 0. One metric value is generated for each
        threshold value. If neither thresholds nor top_k are set, the default is
        to calculate precision with `thresholds=0.5`.
      top_k: (Optional) Unset by default. An int value specifying the top-k
        predictions to consider when calculating precision.
      class_id: (Optional) Integer class ID for which we want binary metrics.
        This must be in the half-open interval `[0, num_classes)`, where
        `num_classes` is the last dimension of predictions.
      name: (Optional) string name of the metric instance.
      dtype: (Optional) data type of the metric result.

    Standalone usage:

    >>> m = tf.keras.metrics.Precision()
    >>> m.update_state([0, 1, 1, 1], [1, 0, 1, 1])
    >>> m.result().numpy()
    0.6666667

    >>> m.reset_state()
    >>> m.update_state([0, 1, 1, 1], [1, 0, 1, 1], sample_weight=[0, 0, 1, 0])
    >>> m.result().numpy()
    1.0

    >>> # With top_k=2, it will calculate precision over y_true[:2]
    >>> # and y_pred[:2]
    >>> m = tf.keras.metrics.Precision(top_k=2)
    >>> m.update_state([0, 0, 1, 1], [1, 1, 1, 1])
    >>> m.result().numpy()
    0.0

    >>> # With top_k=4, it will calculate precision over y_true[:4]
    >>> # and y_pred[:4]
    >>> m = tf.keras.metrics.Precision(top_k=4)
    >>> m.update_state([0, 0, 1, 1], [1, 1, 1, 1])
    >>> m.result().numpy()
    0.5

    Usage with `compile()` API:

    ```python
    model.compile(optimizer='sgd',
                  loss='binary_crossentropy',
                  metrics=[tf.keras.metrics.Precision()])
    ```

    Usage with a loss with `from_logits=True`:

    ```python
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=[tf.keras.metrics.Precision(thresholds=0)])
    ```
    """

    @inject_mesh
    def __init__(
        self, thresholds=None, top_k=None, class_id=None, name=None, dtype=None
    ):
        super().__init__(name=name, dtype=dtype)
        self.init_thresholds = thresholds
        self.top_k = top_k
        self.class_id = class_id

        default_threshold = 0.5 if top_k is None else NEG_INF
        self.thresholds = parse_init_thresholds(
            thresholds, default_threshold=default_threshold
        )
        self._thresholds_distributed_evenly = (
            is_evenly_distributed_thresholds(self.thresholds)
        )
        self.true_negatives = self.add_weight(
            name="true_negatives", shape=(len(self.thresholds),), initializer="zeros"
        )
        self.false_negatives = self.add_weight(
            name="false_negatives",
            shape=(len(self.thresholds),),
            initializer="zeros",
        )

    def update_state(self, y_true, y_pred, sample_weight=None):
        """Accumulates true positive and false positive statistics.

        Args:
          y_true: The ground truth values, with the same dimensions as `y_pred`.
            Will be cast to `bool`.
          y_pred: The predicted values. Each element must be in the range
            `[0, 1]`.
          sample_weight: Optional weighting of each example. Can
            be a `Tensor` whose rank is either 0, or the same rank as `y_true`,
            and must be broadcastable to `y_true`. Defaults to `1`.

        Returns:
          Update op.
        """
        return update_confusion_matrix_variables(
            {
                ConfusionMatrix.TRUE_NEGATIVES: self.true_negatives,  # noqa: E501
                ConfusionMatrix.FALSE_NEGATIVES: self.false_negatives,  # noqa: E501
            },
            y_true,
            y_pred,
            thresholds=self.thresholds,
            thresholds_distributed_evenly=self._thresholds_distributed_evenly,
            top_k=self.top_k,
            class_id=self.class_id,
            sample_weight=sample_weight,
        )

    def result(self):
        result = tf.math.divide_no_nan(
            self.true_negatives,
            tf.math.add(self.true_negatives, self.false_negatives),
        )
        return result[0] if len(self.thresholds) == 1 else result

    def reset_state(self):
        num_thresholds = len(to_list(self.thresholds))
        backend.batch_set_value(
            [
                (v, np.zeros((num_thresholds,)))
                for v in (self.true_negatives, self.false_negatives)
            ]
        )

    def get_config(self):
        config = {
            "thresholds": self.init_thresholds,
            "top_k": self.top_k,
            "class_id": self.class_id,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class Specificity(Metric):
    """Computes the NPV of the predictions with respect to the labels.

    The metric creates two local variables, `true_positives` and
    `false_positives` that are used to compute the precision. This value is
    ultimately returned as `precision`, an idempotent operation that simply
    divides `true_positives` by the sum of `true_positives` and
    `false_positives`.

    If `sample_weight` is `None`, weights default to 1.
    Use `sample_weight` of 0 to mask values.

    If `top_k` is set, we'll calculate precision as how often on average a class
    among the top-k classes with the highest predicted values of a batch entry
    is correct and can be found in the label for that entry.

    If `class_id` is specified, we calculate precision by considering only the
    entries in the batch for which `class_id` is above the threshold and/or in
    the top-k highest predictions, and computing the fraction of them for which
    `class_id` is indeed a correct label.

    Args:
      thresholds: (Optional) A float value, or a Python list/tuple of float
        threshold values in [0, 1]. A threshold is compared with prediction
        values to determine the truth value of predictions (i.e., above the
        threshold is `true`, below is `false`). If used with a loss function
        that sets `from_logits=True` (i.e. no sigmoid applied to predictions),
        `thresholds` should be set to 0. One metric value is generated for each
        threshold value. If neither thresholds nor top_k are set, the default is
        to calculate precision with `thresholds=0.5`.
      top_k: (Optional) Unset by default. An int value specifying the top-k
        predictions to consider when calculating precision.
      class_id: (Optional) Integer class ID for which we want binary metrics.
        This must be in the half-open interval `[0, num_classes)`, where
        `num_classes` is the last dimension of predictions.
      name: (Optional) string name of the metric instance.
      dtype: (Optional) data type of the metric result.

    Standalone usage:

    >>> m = tf.keras.metrics.Precision()
    >>> m.update_state([0, 1, 1, 1], [1, 0, 1, 1])
    >>> m.result().numpy()
    0.6666667

    >>> m.reset_state()
    >>> m.update_state([0, 1, 1, 1], [1, 0, 1, 1], sample_weight=[0, 0, 1, 0])
    >>> m.result().numpy()
    1.0

    >>> # With top_k=2, it will calculate precision over y_true[:2]
    >>> # and y_pred[:2]
    >>> m = tf.keras.metrics.Precision(top_k=2)
    >>> m.update_state([0, 0, 1, 1], [1, 1, 1, 1])
    >>> m.result().numpy()
    0.0

    >>> # With top_k=4, it will calculate precision over y_true[:4]
    >>> # and y_pred[:4]
    >>> m = tf.keras.metrics.Precision(top_k=4)
    >>> m.update_state([0, 0, 1, 1], [1, 1, 1, 1])
    >>> m.result().numpy()
    0.5

    Usage with `compile()` API:

    ```python
    model.compile(optimizer='sgd',
                  loss='binary_crossentropy',
                  metrics=[tf.keras.metrics.Precision()])
    ```

    Usage with a loss with `from_logits=True`:

    ```python
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=[tf.keras.metrics.Precision(thresholds=0)])
    ```
    """

    @inject_mesh
    def __init__(
        self, thresholds=None, top_k=None, class_id=None, name=None, dtype=None
    ):
        super().__init__(name=name, dtype=dtype)
        self.init_thresholds = thresholds
        self.top_k = top_k
        self.class_id = class_id

        default_threshold = 0.5 if top_k is None else NEG_INF
        self.thresholds = parse_init_thresholds(
            thresholds, default_threshold=default_threshold
        )
        self._thresholds_distributed_evenly = (
            is_evenly_distributed_thresholds(self.thresholds)
        )
        self.true_negatives = self.add_weight(
            name="true_negatives", shape=(len(self.thresholds),), initializer="zeros"
        )
        self.false_positives = self.add_weight(
            name="false_positives",
            shape=(len(self.thresholds),),
            initializer="zeros",
        )

    def update_state(self, y_true, y_pred, sample_weight=None):
        """Accumulates true positive and false positive statistics.

        Args:
          y_true: The ground truth values, with the same dimensions as `y_pred`.
            Will be cast to `bool`.
          y_pred: The predicted values. Each element must be in the range
            `[0, 1]`.
          sample_weight: Optional weighting of each example. Can
            be a `Tensor` whose rank is either 0, or the same rank as `y_true`,
            and must be broadcastable to `y_true`. Defaults to `1`.

        Returns:
          Update op.
        """
        return update_confusion_matrix_variables(
            {
                ConfusionMatrix.TRUE_NEGATIVES: self.true_negatives,  # noqa: E501
                ConfusionMatrix.FALSE_POSITIVES: self.false_positives,  # noqa: E501
            },
            y_true,
            y_pred,
            thresholds=self.thresholds,
            thresholds_distributed_evenly=self._thresholds_distributed_evenly,
            top_k=self.top_k,
            class_id=self.class_id,
            sample_weight=sample_weight,
        )

    def result(self):
        result = tf.math.divide_no_nan(
            self.true_negatives,
            tf.math.add(self.true_negatives, self.false_positives),
        )
        return result[0] if len(self.thresholds) == 1 else result

    def reset_state(self):
        num_thresholds = len(to_list(self.thresholds))
        backend.batch_set_value(
            [
                (v, np.zeros((num_thresholds,)))
                for v in (self.true_negatives, self.false_positives)
            ]
        )

    def get_config(self):
        config = {
            "thresholds": self.init_thresholds,
            "top_k": self.top_k,
            "class_id": self.class_id,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class SpecificityAtNPV(SensitivitySpecificityBase):
    """Computes best recall where precision is >= specified value.

    For a given score-label-distribution the required precision might not
    be achievable, in this case 0.0 is returned as recall.

    This metric creates four local variables, `true_positives`,
    `true_negatives`, `false_positives` and `false_negatives` that are used to
    compute the recall at the given precision. The threshold for the given
    precision value is computed and used to evaluate the corresponding recall.

    If `sample_weight` is `None`, weights default to 1.
    Use `sample_weight` of 0 to mask values.

    If `class_id` is specified, we calculate precision by considering only the
    entries in the batch for which `class_id` is above the threshold
    predictions, and computing the fraction of them for which `class_id` is
    indeed a correct label.

    Args:
      npv: A scalar value in range `[0, 1]`.
      num_thresholds: (Optional) The number of thresholds to
        use for matching the given precision. Defaults to `200`.
      class_id: (Optional) Integer class ID for which we want binary metrics.
        This must be in the half-open interval `[0, num_classes)`, where
        `num_classes` is the last dimension of predictions.
      name: (Optional) string name of the metric instance.
      dtype: (Optional) data type of the metric result.

    Standalone usage:

    >>> m = tf.keras.metrics.RecallAtPrecision(0.8)
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9])
    >>> m.result().numpy()
    0.5

    >>> m.reset_state()
    >>> m.update_state([0, 0, 1, 1], [0, 0.5, 0.3, 0.9],
    ...                sample_weight=[1, 0, 0, 1])
    >>> m.result().numpy()
    1.0

    Usage with `compile()` API:

    ```python
    model.compile(
        optimizer='sgd',
        loss='binary_crossentropy',
        metrics=[tf.keras.metrics.RecallAtPrecision(precision=0.8)])
    ```
    """

    @inject_mesh
    def __init__(
        self,
        npv,
        num_thresholds=200,
        class_id=None,
        name=None,
        dtype=None,
    ):
        if npv < 0 or npv > 1:
            raise ValueError(
                "Argument `npv` must be in the range [0, 1]. "
                f"Received: npv={npv}"
            )
        self.npv = npv
        self.num_thresholds = num_thresholds
        super().__init__(
            value=npv,
            num_thresholds=num_thresholds,
            class_id=class_id,
            name=name,
            dtype=dtype,
        )

    def result(self):
        npvs = tf.math.divide_no_nan(
            self.true_negatives,
            tf.math.add(self.true_negatives, self.false_negatives),
        )
        sensitivities = tf.math.divide_no_nan(
            self.true_negatives,
            tf.math.add(self.true_negatives, self.false_positives),
        )
        return self._find_max_under_constraint(
            npvs, sensitivities, tf.greater_equal
        )

    def get_config(self):
        config = {
            "num_thresholds": self.num_thresholds,
            "npv": self.npv,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))
