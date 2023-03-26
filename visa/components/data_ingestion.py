#first we will define each and everything here
import os
import sys
from six.moves import urllib
import numpy as np
import pandas as pd
from visa.constant import *
from visa.logger import logging
from visa.entity.config_entity import DataIngestionConfig
from visa.entity.artifact_entity import DataIngestionArtifact
from visa.config.configuration import Configuartion
from visa.exception import CustomException
from visa.utils.utils import read_yaml_file
from sklearn.model_selection import train_test_split
from datetime import date
            


class DataIngestion:
#defining all the variables as data_ingestion_config, we already make these variables
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            logging.info(f"{'>>'*30}Data Ingestion log started.{'<<'*30} \n\n")
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise CustomException(e, sys) from e

#define a function to download a data
    def download_data(self) -> str:
        try:
            download_url = self.data_ingestion_config.dataset_download_url
            
            #directory to store raw data
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            #creating the raw data dir if not present
            os.makedirs(raw_data_dir, exist_ok=True)
            
            #basename of data
            us_visa_file_name = os.path.basename(download_url)

            #path of raw data file, merging the dir and file
            raw_file_path = os.path.join(raw_data_dir, us_visa_file_name)

            logging.info(
                f"Downloading file from :[{download_url}] into :[{raw_file_path}]")
            urllib.request.urlretrieve(download_url, raw_file_path)
            logging.info(
                f"File :[{raw_file_path}] has been downloaded successfully.")
            return raw_file_path

        except Exception as e:
            raise CustomException(e, sys) from e

#function to split the data and to return in dataingestionartifact format
    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            #getting raw data
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            
            #getting first file from raw dir
            file_name = os.listdir(raw_data_dir)[0]
            
            
            us_visa_file_path = os.path.join(raw_data_dir, file_name)

            logging.info(f"Reading csv file: [{us_visa_file_path}]")

            # creating the date object of today's date
            #whenever we get the file under raw data dir , it will store like below format
            todays_date = date.today()
            current_year= todays_date.year
            
            us_visa_dataframe = pd.read_csv(us_visa_file_path)
            
            us_visa_dataframe[COLUMN_COMPANY_AGE] = current_year-us_visa_dataframe[COLUMN_YEAR_ESTB]
            
            #drop some columns
            us_visa_dataframe.drop([COLUMN_ID,COLUMN_YEAR_ESTB], axis=1, inplace=True)
            us_visa_dataframe[COLUMN_CASE_STATUS] = np.where(us_visa_dataframe[COLUMN_CASE_STATUS] == 'Denied', 1,0)
                        
            logging.info(f"Splitting data into train and test")

            train_set = None
            test_set = None

            train_set, test_set = train_test_split(us_visa_dataframe, test_size=0.2, random_state=42)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,
                                           file_name)

            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,
                                          file_name)
# ***********************************************************************************************
           #if train and test is not null then create a dir just to store the data under train and test file
           #path
            if train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir, exist_ok=True)
                logging.info(f"Exporting training dataset to file: [{train_file_path}]")
                train_set.to_csv(train_file_path, index=False)

            if test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir, exist_ok=True)
                logging.info(f"Exporting test dataset to file: [{test_file_path}]")
                test_set.to_csv(test_file_path, index=False)

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                                            test_file_path=test_file_path,
                                                            is_ingested=True,
                                                            message=f"Data ingestion completed successfully."
                                                            )
            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact

        except Exception as e:
            raise CustomException(e, sys) from e

    #initiate data ingestion
    def initiate_data_ingestion(self):
        try:
            raw_file_path = self.download_data()
            return self.split_data_as_train_test()
        except Exception as e:
            raise CustomException(e, sys)from e