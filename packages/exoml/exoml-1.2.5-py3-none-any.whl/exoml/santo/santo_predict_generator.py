import logging

import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from tensorflow.keras.utils import Sequence
from matplotlib import pyplot as plt

def clean_to_float(x):
    return float(str(x).strip("\"'"))

class SantoPredictGenerator(Sequence):
    def __init__(
            self,
            lcs_dir,
            target_files,
            input_size=500,
            step_size=1,
            batch_size=500,
            shuffle=True,
            zero_epsilon=1e-7,
            indexes_steps=1,
            plot=False,
    ):
        self.lcs_dir = lcs_dir
        self.target_files = target_files
        self.input_size = input_size
        self.step_size = step_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.zero_epsilon = zero_epsilon
        self.plot = plot
        self.steps_count, self.generator_info_df = self._count_inputs()

    def _count_inputs(self):
        batch_index = 0
        file_count = 0

        # Create a list to collect all rows and build DataFrame once at the end
        data_rows = []

        for target_file in self.target_files:
            # Load file dimensions only once per file
            flux = pd.read_csv(f"{self.lcs_dir}/{target_file}").values
            if flux.shape[0] > 40:
                flux = np.transpose(flux)

            # Calculate all batch indices at once
            file_batch_indexes = np.arange(
                -self.input_size // 2,
                flux.shape[1] - self.input_size // 2 - self.batch_size - 1,
                self.batch_size,
            )

            logging.info(f"Doing file {file_count} with {len(file_batch_indexes)} batches")

            # Add all rows for this file to our list at once
            for file_index in file_batch_indexes:
                data_rows.append({
                    "filename": target_file,
                    "file_index": file_index,
                    "batch_index": batch_index
                })
                batch_index += 1

            file_count += 1

        # Create DataFrame once with all data
        generator_info_df = pd.DataFrame(data_rows) if data_rows else pd.DataFrame(
            columns=["filename", "file_index", "batch_index"])

        return (batch_index - 1) if batch_index > 0 else 0, generator_info_df

    def __len__(self):
        return self.generator_info_df["batch_index"].max()

    def __getitem__(self, index):
        filename: str = self.generator_info_df.iloc[index]["filename"]
        file_index: int = self.generator_info_df.loc[index]["file_index"]
        flux = pd.read_csv(f"{self.lcs_dir}/{filename}").values
        flux_key = 1
        if flux.shape[0] > 40:
            flux_key = 2
            flux = np.transpose(flux)
        flux = np.vectorize(clean_to_float)(flux)
        train_fluxes = np.full((self.batch_size, self.input_size, 1), 0.0)
        for iteration_index in np.arange(file_index, file_index + self.batch_size):
            try:
                if iteration_index < 0:
                    flux_data = flux[flux_key, 0: iteration_index + self.input_size]
                    flux_data = np.pad(flux_data, [(self.input_size - flux_data.shape[0], 0)], mode='constant',
                                       constant_values=0)
                elif iteration_index >= flux.shape[1] - self.input_size:
                    flux_data = flux[flux_key, iteration_index:flux.shape[1]]
                    flux_data = np.pad(flux_data, [(0, self.input_size - flux_data.shape[0])], mode='constant',
                                       constant_values=0)
                else:
                    flux_data = flux[flux_key, iteration_index:iteration_index + self.input_size]
                flux_data = flux_data / 2
                item_index = iteration_index - file_index
                train_fluxes[item_index] = flux_data.reshape((self.input_size, 1))
            except Exception as e:
                logging.exception(
                    f"Error with file {filename}. file_index {file_index}, "
                    f"iteration_index {iteration_index}, batch_size {self.batch_size}, "
                    f"input_size {self.input_size}"
                )
                raise e
        self.assert_in_range(filename, train_fluxes)
        return train_fluxes, None

    def assert_in_range(self, object_id, array, values_range=(0, 1)):
        if np.isnan(array).any():
            raise ValueError("Target " + str(object_id) + " contains NaN values")
        elif np.max(array) >= values_range[1]:
            raise ValueError("Target " + str(object_id) + " contains values > 1")
        elif np.min(array) < values_range[0]:
            raise ValueError("Target " + str(object_id) + " contains values < 0")
        # elif np.all(array == values_range[0]):
        #     raise ValueError("Target " + str(object_id) + " contains all values == 0")

    def on_epoch_end(self):
        if self.shuffle:
            self.generator_info_df = shuffle(self.generator_info_df)

    def class_weights(self):
        return {0: 1, 1: 1}

    def steps_per_epoch(self):
        return self.steps_count