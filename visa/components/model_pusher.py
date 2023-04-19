from visa.logger import logging
from visa.exception import CustomException
from visa.entity.artifact_entity import ModelPusherArtifact, ModelEvaluationArtifact 
from visa.entity.config_entity import ModelPusherConfig
import os, sys
import shutil



class ModelPusher:

    def __init__(self, model_pusher_config: ModelPusherConfig,
                 model_evaluation_artifact: ModelEvaluationArtifact    #just to get best model from yaml artifact to push
                 ):
        try:
            logging.info(f"{'>>' * 30}Model Pusher log started.{'<<' * 30} ")
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact
        
        except Exception as e:
            raise CustomException(e,sys) from e 
    
    def export_model(self)-> ModelPusherConfig:
        try:
            #pushing the best model under export dir
            #taking the path of best model which is present under evaluation file
            evaluated_model_file_path = self.model_evaluation_artifact.evaluated_model_path
           
           #creating export dir, under this  we are pushing whatever the best model we have under evaluated model file 
            export_dir = self.model_pusher_config.export_dir_path
            model_file_name = os.path.basename(evaluated_model_file_path)
            
            #joining everything
            export_model_file_path = os.path.join(export_dir, model_file_name)
            logging.info(f"Exporting model file: [{export_model_file_path}]")
            os.makedirs(export_dir, exist_ok=True)

            #src-taking evaluation file and dst-to push the model at this path
            #copying the best model from evaluation file to saved model folder
            shutil.copy(src=evaluated_model_file_path, dst=export_model_file_path)

            logging.info(
                f"Trained model: {evaluated_model_file_path} is copied in export dir:[{export_model_file_path}]")
            
            #artifact
            model_pusher_artifact = ModelPusherArtifact(is_model_pusher=True,
                                                        export_model_file_path=export_model_file_path
                                                        )
            logging.info(f"Model Pusher artifact: [{model_pusher_artifact}")
            return model_pusher_artifact
        except Exception as e:
            raise CustomException(e,sys) from e 
    
    def initiate_model_pusher(self)-> ModelPusherArtifact:
        try:
            return self.export_model()
        except Exception as e:
            raise CustomException(e,sys) from e
    
    def __del__(self):
        logging.info(f"{'>>'*20}Model Pusher log completed.{'<<'*20}")