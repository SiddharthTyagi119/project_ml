#using this to store the things as a key value pair of some of configuration of (config.yaml) 
#to define the things of config.yaml file. and later we can load/call the key in our main file.
#the key are associated with yaml file and constant init file

from collections import namedtuple
DataIngestionConfig: namedtuple("DataIngestionConfig",
                                ["dataset_download_url","raw_data_dir","ingested_train_dir","ingested_test_dir"])

DataValidationConfig = namedtuple("DataValidationConfig", ["schema_file_path"])

TrainingPipelineConfig = namedtuple("TrainingPipelineConfig", ["artifact_dir"])
