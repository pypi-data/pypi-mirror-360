import logging

import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from tensorflow.keras.utils import Sequence
from matplotlib import pyplot as plt


class SantoGlobalGenerator(Sequence):
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
            flux = np.loadtxt(f"{self.lcs_dir}/{target_file}", delimiter=",")
            
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
        generator_info_df = pd.DataFrame(data_rows) if data_rows else pd.DataFrame(columns=["filename", "file_index", "batch_index"])
        
        return (batch_index - 1) if batch_index > 0 else 0, generator_info_df

    def __len__(self):
        return self.generator_info_df["batch_index"].max()

    def __getitem__(self, index):
        filename: str = self.generator_info_df.iloc[index]["filename"]
        file_index: int = self.generator_info_df.loc[index]["file_index"]
        flux = np.loadtxt(f"{self.lcs_dir}/{filename}", delimiter=",")
        # train_fluxes = np.full((self.batch_size, self.input_size, 33), 0)
        train_fluxes = np.full((self.batch_size, self.input_size, 1), 0.0)
        train_tags = np.full((self.batch_size, self.input_size, 1), float(0))
        for iteration_index in np.arange(file_index, file_index + self.batch_size):
            if iteration_index < 0:
                # flux_data = flux[np.r_[1, 4:36], 0:iteration_index + self.input_size]
                flux_data = flux[1, 0 : iteration_index + self.input_size]
                tags_data = flux[3, 0 : iteration_index + self.input_size]
                # flux_data = np.pad(flux_data, (0, self.input_size - flux_data.shape[1]), mode='constant', constant_values=0)
                flux_data = np.pad(
                    flux_data,
                    (self.input_size - flux_data.shape[0], 0),
                    mode="constant",
                    constant_values=0,
                )
                tags_data = np.pad(
                    tags_data,
                    (self.input_size - tags_data.shape[0], 0),
                    mode="constant",
                    constant_values=0,
                )
            elif iteration_index >= flux.shape[1] - self.input_size:
                # flux_data = flux[np.r_[1, 4:36], iteration_index:flux.shape[1]]
                flux_data = flux[1, iteration_index : flux.shape[1]]
                tags_data = flux[3, iteration_index : flux.shape[1]]
                # flux_data = np.pad(flux_data, [(0, 0), (0, self.input_size - flux_data.shape[1])],
                #                   mode='constant', constant_values=0)
                flux_data = np.pad(
                    flux_data,
                    (0, self.input_size - flux_data.shape[0]),
                    mode="constant",
                    constant_values=0,
                )
                tags_data = np.pad(
                    tags_data,
                    (0, self.input_size - tags_data.shape[0]),
                    mode="constant",
                    constant_values=0,
                )
            else:
                # flux_data = flux[np.r_[1, 4:36], iteration_index:iteration_index + self.input_size]
                flux_data = flux[1, iteration_index : iteration_index + self.input_size]
                tags_data = flux[3, iteration_index : iteration_index + self.input_size]
            # import matplotlib.pyplot as plt
            #
            # fig, axs = plt.subplots(2, 1, figsize=(16, 16), constrained_layout=True)
            # axs[0].scatter(np.arange(0, len(np.transpose(flux_data[0].flatten()))),
            #                np.transpose(flux_data[0].flatten()))
            # axs[1].plot(np.arange(0, len(np.transpose(flux_data[0].flatten()))),
            #             np.transpose(flux[3, iteration_index:iteration_index + self.input_size]).flatten())
            # plt.show()
            # flux_data[0] = flux_data[0] / 2
            flux_data = flux_data / 2
            item_index = iteration_index - file_index
            try:
                # train_fluxes[item_index] = np.transpose(flux_data)
                train_fluxes[item_index] = flux_data.reshape((self.input_size, 1))
                tags_data = tags_data.reshape((self.input_size, 1))
            except Exception as e:
                logging.exception(
                    f"Error with file {filename}. file_index {file_index}, "
                    f"iteration_index {iteration_index}, batch_size {self.batch_size}, "
                    f"input_size {self.input_size}"
                )
                raise e
            train_tags[item_index] = tags_data
            # if self.plot:
            #     fig, ax = plt.subplots(2, 1, figsize=(16, 8), constrained_layout=True)
            #     ax[0].scatter(np.arange(0, len(train_fluxes[item_index])), train_fluxes[item_index])
            #     ax[1].plot(np.arange(0, train_tags[item_index]), train_tags[item_index])
            #     plt.show()
        self.assert_in_range(filename, train_fluxes)
        np.all(
            train_tags != train_tags.astype(int)
        ), "train_tags contains integer values!"
        return train_fluxes, train_tags

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
