#define whatever things we want to store under artifact dir
from collections import namedtuple

DataIngestionArtifact = namedtuple("DataIngestionArtifact",
[ "train_file_path", "test_file_path", "is_ingested", "message"])
