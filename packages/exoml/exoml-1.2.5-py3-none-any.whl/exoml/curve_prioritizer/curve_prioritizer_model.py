from curve_prioritizer.curve_prioritizer_generator import CurvePrioritizerGenerator

model = 1 # keras model
batch_size = 100
injected_objects_df = pd.read_csv("injected_objects_combined.csv")
# TODO split in training/validation/test dfs
injected_objects_training_df = 1
curve_initializer_generator = CurvePrioritizerGenerator(injected_objects_training_df, batch_size=batch_size)
curve_initializer_generator_val = CurvePrioritizerGenerator(injected_objects_validation_df, batch_size=batch_size)
fit_history = model.fit(x=curve_initializer_generator,
                           steps_per_epoch=steps_per_epoch,
                           epochs=epochs, verbose=1,
                           validation_data=curve_initializer_generator_val,
                           callbacks=hyperparams.callbacks,
                           use_multiprocessing=cores > 0, cores)