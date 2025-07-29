import numpy as np


def binary_encode_times(times, length):
    times_binary_str = np.binary_repr(times)
    return [np.array(''.split(times_binary_str.zfill(length))).astype(int) for time_binary_str in times_binary_str]


def value_encode_times(times, max_time=1000):
    return times % max_time / max_time