import os
import tensorflow as tf


def setup_threads(num_threads=os.cpu_count() - 1):
    num_threads_str = str(num_threads)
    os.environ["OMP_NUM_THREADS"] = num_threads_str
    os.environ["TF_NUM_INTRAOP_THREADS"] = num_threads_str
    os.environ["TF_NUM_INTEROP_THREADS"] = num_threads_str
    tf.config.threading.set_inter_op_parallelism_threads(
        num_threads
    )
    tf.config.threading.set_intra_op_parallelism_threads(
        num_threads
    )
    tf.config.set_soft_device_placement(True)