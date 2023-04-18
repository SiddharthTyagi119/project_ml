import importlib
from pyexpat import model
import numpy as np
import yaml
from visa.exception import CustomException
import os
import sys

from collections import namedtuple
from typing import List
from visa.logger import logging
from sklearn.metrics import accuracy_score, f1_score

#defining the variables from model.yaml
GRID_SEARCH_KEY = 'grid_search'
MODULE_KEY = 'module'
CLASS_KEY = 'class'
PARAM_KEY = 'params'
MODEL_SELECTION_KEY = 'model_selection'
SEARCH_PARAM_GRID_KEY = "search_param_grid"

#defining named tuple to call above variables
#for model
InitializedModelDetail = namedtuple("InitializedModelDetail",
                                    ["model_serial_number", "model", "param_grid_search", "model_name"])

#for grid search
GridSearchedBestModel = namedtuple("GridSearchedBestModel", ["model_serial_number",
                                                             "model",
                                                             "best_model",
                                                             "best_parameters",
                                                             "best_score",
                                                             ])
#best model
BestModel = namedtuple("BestModel", ["model_serial_number",
                                     "model",
                                     "best_model",
                                     "best_parameters",
                                     "best_score", ])
#for metrics
MetricInfoArtifact = namedtuple("MetricInfoArtifact",
                                ["model_name", "model_object", "train_f1", "test_f1", "train_accuracy",
                                 "test_accuracy", "model_accuracy", "index_number"])


# can be used in case of classification model
def evaluate_classification_model(model_list: list, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray,
                                  y_test: np.ndarray, base_accuracy: float = 0.6) -> MetricInfoArtifact:
    """
    Description:
    This function compare multiple classification models and returns best model
    Params:
    model_list: List of model
    X_train: Training dataset input feature
    y_train: Training dataset target feature
    X_test: Testing dataset input feature
    y_test: Testing dataset input feature
    return
    It returned a named tuple
    
    MetricInfoArtifact = namedtuple("MetricInfo",
                                ["model_name", "model_object", "train_f1", "train_f1", "train_accuracy",
                                 "test_accuracy", "model_accuracy", "index_number"])
    """
    try:

        index_number = 0
        metric_info_artifact = None # Model accuracy is none becuase right now we didn't have any model where we can check accuracy
        for model in model_list:
            model_name = str(model)  # getting model name based on model object
            logging.info(f"{'>>' * 30}Started evaluating model: [{type(model).__name__}] {'<<' * 30}")

            # Getting prediction for training and testing dataset
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # Calculating r squared score on training and testing dataset
            train_acc = accuracy_score(y_train, y_train_pred)
            test_acc = accuracy_score(y_test, y_test_pred)


            # Calculating mean squared error on training and testing dataset
            train_f1 = f1_score(y_train, y_train_pred)
            test_f1 = f1_score(y_test, y_test_pred)

            # Calculating harmonic mean of train_accuracy and test_accuracy
            model_accuracy = (2 * (train_acc * test_acc)) / (train_acc + test_acc)
            diff_test_train_acc = abs(test_acc - train_acc)

            # logging all important metric
            logging.info(f"{'>>' * 30} Score {'<<' * 30}")
            logging.info(f"Train Score\t\t Test Score\t\t Average Score")
            logging.info(f"{train_acc}\t\t {test_acc}\t\t{model_accuracy}")

            logging.info(f"{'>>' * 30} F1 Score {'<<' * 30}")
            logging.info(f"Diff test train accuracy: [{diff_test_train_acc}].")
            logging.info(f"Train root mean squared error: [{train_f1}].")
            logging.info(f"Test root mean squared error: [{test_f1}].")

            # if model accuracy is greater than base accuracy and train and test score is within certain threshold
            # we will accept that model as accepted model
            if model_accuracy >= base_accuracy and diff_test_train_acc < 0.10:
                base_accuracy = model_accuracy
                metric_info_artifact = MetricInfoArtifact(model_name=model_name,
                                                          model_object=model,
                                                          train_f1=train_f1,
                                                          test_f1=test_f1,
                                                          train_accuracy=train_acc,
                                                          test_accuracy=test_acc,
                                                          model_accuracy=model_accuracy,
                                                          index_number=index_number)

                logging.info(f"Acceptable model found {metric_info_artifact}. ")
            index_number += 1
        if metric_info_artifact is None:
            logging.info(f"No model found with higher accuracy than base accuracy")
        return metric_info_artifact
    except Exception as e:
        raise CustomException(e, sys) from e


def evaluate_regression_model(model_list: list, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray,
                              y_test: np.ndarray, base_accuracy: float = 0.6) -> MetricInfoArtifact:
    pass



def get_sample_model_config_yaml_file(export_dir: str):
    try:
        model_config = {
            GRID_SEARCH_KEY: {
                MODULE_KEY: "sklearn.model_selection",
                CLASS_KEY: "GridSearchCV",
                PARAM_KEY: {
                    "cv": 3,
                    "verbose": 1
                }

            },
            MODEL_SELECTION_KEY: {
                "module_0": {
                    MODULE_KEY: "module_of_model",
                    CLASS_KEY: "ModelClassName",
                    PARAM_KEY:
                        {"param_name1": "value1",
                         "param_name2": "value2",
                         },
                    SEARCH_PARAM_GRID_KEY: {
                        "param_name": ['param_value_1', 'param_value_2']
                    }

                },
            }
        }
        os.makedirs(export_dir, exist_ok=True)
        export_file_path = os.path.join(export_dir, "model.yaml")
        with open(export_file_path, 'w') as file:
            yaml.dump(model_config, file)
        return export_file_path
    except Exception as e:
        raise CustomException(e, sys)



######### starts from here
#making a constructor and calling the above variables
class ModelFactory:
    def __init__(self, model_config_path: str = None, ):
        try:
            self.config: dict = ModelFactory.read_params(model_config_path)
            
            
            self.grid_search_cv_module: str = self.config[GRID_SEARCH_KEY][MODULE_KEY]
            self.grid_search_class_name: str = self.config[GRID_SEARCH_KEY][CLASS_KEY]
            self.grid_search_property_data: dict = dict(self.config[GRID_SEARCH_KEY][PARAM_KEY])

            self.models_initialization_config: dict = dict(self.config[MODEL_SELECTION_KEY])

            #none is mentione in below because at first time we dont have any trained model
            self.initialized_model_list = None
            self.grid_searched_best_model_list = None 

        except Exception as e:
            raise CustomException(e, sys) from e
#what if you want to update all the params of the claasses so for this below function
#to update all properties/parameters of the classes that we have define under model.yaml file 
#example- we are updating the properties/params through UI to train a new model . Than those properties will be updated
#in the yaml file also.
    @staticmethod
    def update_property_of_class(instance_ref: object, property_data: dict):
        try:
            if not isinstance(property_data, dict):
                raise Exception("property_data parameter required to dictionary")
            print(property_data)
            for key, value in property_data.items():
                logging.info(f"Executing:$ {str(instance_ref)}.{key}={value}")
                setattr(instance_ref, key, value)
            return instance_ref
        except Exception as e:
            raise CustomException(e, sys) from e
        
# Read complete parameter from model.yaml file
#safe_load have complete functions to read yml file 
    @staticmethod
    def read_params(config_path: str) -> dict:
        try:
            with open(config_path) as yaml_file:
                config: dict = yaml.safe_load(yaml_file)
            return config
        except Exception as e:
            raise CustomException(e, sys) from e



# we defining the class to call our model file random forest and  KNN
    @staticmethod
    def class_for_name(module_name: str, class_name: str):
        try:
            # load the module, will raise ImportError if module cannot be loaded
            #importlib to call multiple objects or algorithms at a single time, to get list of algos at once
            module = importlib.import_module(module_name)
            # get the class, will raise AttributeError if class cannot be found
            logging.info(f"Executing command: from {module} import {class_name}")
            class_ref = getattr(module, class_name)
            return class_ref
        except Exception as e:
            raise CustomException(e, sys) from e


    def execute_grid_search_operation(self, initialized_model: InitializedModelDetail, input_feature,
                                      output_feature) -> GridSearchedBestModel:
        """
        execute_grid_search_operation(): function will perform parameter search operation, and
        it will return you the best optimistic  model with the best parameter:
        estimator: Model object
        param_grid: dictionary of parameter to perform search operation
        input_feature: you're all input features
        output_feature: Target/Dependent features
        ================================================================================
        return: Function will return GridSearchOperation object
        """
        try:
            # instantiating GridSearchCV class
            grid_search_cv_ref = ModelFactory.class_for_name(module_name=self.grid_search_cv_module,
                                                             class_name=self.grid_search_class_name
                                                             )

            #calling grid search
            grid_search_cv = grid_search_cv_ref(estimator=initialized_model.model,
                                                param_grid=initialized_model.param_grid_search)

             #calling to update the params                                   
            grid_search_cv = ModelFactory.update_property_of_class(grid_search_cv,
                                                                   self.grid_search_property_data)

            message = f'{">>" * 30} f"Training {type(initialized_model.model).__name__} Started." {"<<" * 30}'
            logging.info(message)
            grid_search_cv.fit(input_feature, output_feature)
            
            message = f'{">>" * 30} f"Training {type(initialized_model.model).__name__}" completed {"<<" * 30}'
            
            #will give you best model
            grid_searched_best_model = GridSearchedBestModel(model_serial_number=initialized_model.model_serial_number,
                                                             model=initialized_model.model,
                                                             best_model=grid_search_cv.best_estimator_,
                                                             best_parameters=grid_search_cv.best_params_,
                                                             best_score=grid_search_cv.best_score_
                                                             )

            return grid_searched_best_model
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_initialized_model_list(self) -> List[InitializedModelDetail]:
        """
        This function will return a list of model details.
        return List[ModelDetail]

        first it will pick the model and then execute the params 
        """
        try:
            #calling all the models(modules) with their keys and params in serial (one by one ) reagrding serial  to execute
            #calling the things 1st time
            initialized_model_list = []
            for model_serial_number in self.models_initialization_config.keys():
                #calling all the models regarding serial num
                #take all module key and classes 
                #it will pick the model
                model_initialization_config = self.models_initialization_config[model_serial_number]
                model_obj_ref = ModelFactory.class_for_name(module_name=model_initialization_config[MODULE_KEY],
                                                            class_name=model_initialization_config[CLASS_KEY]
                                                            )
                model1 = model_obj_ref()
 
                #after picking the model with serial num, executing all parameters and if any changes in params do update
                if PARAM_KEY in model_initialization_config:
                    model_obj_property_data = dict(model_initialization_config[PARAM_KEY])
                    #if you did not get good accuracy and want to update the params, then calling the func for that
                    model1 = ModelFactory.update_property_of_class(instance_ref=model1,
                                                                   property_data=model_obj_property_data)

                param_grid_search = model_initialization_config[SEARCH_PARAM_GRID_KEY]
                model_name = f"{model_initialization_config[MODULE_KEY]}.{model_initialization_config[CLASS_KEY]}"

                model_initialization_config = InitializedModelDetail(model_serial_number=model_serial_number,
                                                                     model=model1,
                                                                     param_grid_search=param_grid_search,
                                                                     model_name=model_name
                                                                     )

                initialized_model_list.append(model_initialization_config)

            self.initialized_model_list = initialized_model_list
            return self.initialized_model_list
        except Exception as e:
            raise CustomException(e, sys) from e

#execute this  if you have only one algorithm
#calling all  the named tuples
    def initiate_best_parameter_search_for_initialized_model(self, initialized_model: InitializedModelDetail,
                                                             input_feature,
                                                             output_feature) -> GridSearchedBestModel:
        """
        initiate_best_model_parameter_search(): function will perform parameter search operation, and
        it will return you the best optimistic  model with the best parameter:
        estimator: Model object
        param_grid: dictionary of parameter to perform search operation
        input_feature: all input features
        output_feature: Target/Dependent features
        ================================================================================
        return: Function will return a GridSearchOperation
        """
        try:
            return self.execute_grid_search_operation(initialized_model=initialized_model,
                                                      input_feature=input_feature,
                                                      output_feature=output_feature)
        except Exception as e:
            raise CustomException(e, sys) from e

#calling multiples algos
    def initiate_best_parameter_search_for_initialized_models(self,
                                                              initialized_model_list: List[InitializedModelDetail],
                                                              input_feature,
                                                              output_feature) -> List[GridSearchedBestModel]:

        try:
            self.grid_searched_best_model_list = []
            for initialized_model_list in initialized_model_list:
                grid_searched_best_model = self.initiate_best_parameter_search_for_initialized_model(
                    initialized_model=initialized_model_list,
                    input_feature=input_feature,
                    output_feature=output_feature
                )
                self.grid_searched_best_model_list.append(grid_searched_best_model)
            return self.grid_searched_best_model_list
        except Exception as e:
            raise CustomException(e, sys) from e

#fetching the details of models that we have defined in named tuple above
    @staticmethod
    def get_model_detail(model_details: List[InitializedModelDetail],
                         model_serial_number: str) -> InitializedModelDetail:
        """
        This function return ModelDetail
        """
        try:
            for model_data in model_details:
                if model_data.model_serial_number == model_serial_number:
                    return model_data
        except Exception as e:
            raise CustomException(e, sys) from e

#searching the best model from grid search cv list
#suppose if we have 2 algos, based on base accuracy it will pick the best model based on accuracy
    @staticmethod
    def get_best_model_from_grid_searched_best_model_list(grid_searched_best_model_list: List[GridSearchedBestModel],
                                                          base_accuracy=0.6
                                                          ) -> BestModel:
        try:
            best_model = None
            for grid_searched_best_model in grid_searched_best_model_list:
                if base_accuracy < grid_searched_best_model.best_score:
                    logging.info(f"Acceptable model found:{grid_searched_best_model}")
                    base_accuracy = grid_searched_best_model.best_score

                    best_model = grid_searched_best_model
            if not best_model:
                raise Exception(f"None of Model has base accuracy: {base_accuracy}")
            logging.info(f"Best model: {best_model}")
            return best_model
        except Exception as e:
            raise CustomException(e, sys) from e

#get best model
    def get_best_model(self, X, y, base_accuracy=0.6) -> BestModel:
        try:
            logging.info("Started Initializing model from config file")
            initialized_model_list = self.get_initialized_model_list()
            logging.info(f"Initialized model: {initialized_model_list}")
            grid_searched_best_model_list = self.initiate_best_parameter_search_for_initialized_models(
                initialized_model_list=initialized_model_list,
                input_feature=X,
                output_feature=y
            )
            return ModelFactory.get_best_model_from_grid_searched_best_model_list(grid_searched_best_model_list,
                                                                                  base_accuracy=base_accuracy)
        except Exception as e:
            raise CustomException(e, sys)