import os
import time
import zipfile
from dnalib.log import log
from .utils import Utils

class LandingZoneUtils:

    @staticmethod   
    def load_files(landing_path):
        file_path = Utils.landingzone_path(landing_path) 
        files = []
        try:
            files = Utils.dbutils().fs.ls(file_path)
        except Exception as e:
            log(__name__).error(f"Unable to load files for path {file_path}: {e}")            
            raise Exception(f"Unable to load files for path {file_path}")
        return files
    
    @staticmethod
    def load_last_updated_path(landing_path):
        files_list = LandingZoneUtils.load_files(landing_path)
        max_modification_time = -1
        max_path = ""
        for f in files_list:
            if f.name != 'processados/':
                if f.modificationTime > max_modification_time:
                    max_modification_time = f.modificationTime
                    max_path = f.path   
        return max_path

    """
    @staticmethod   
    def load_files_dataframe(landing_path, ascending=False):
        file_path = Utils.landingzone_path(landing_path) 
        files_dataframe = None       
        try:            
            files_dataframe = (
                Utils.spark_instance().createDataFrame(Utils.dbutils().fs.ls(file_path))
                .filter("(name <> 'processados/')") 
                .select('path', 'name', 'modificationTime')
                .orderBy("modificationTime", ascending=ascending)
                .select('path','name')                
            )
        except Exception as e:
            log(__name__).error(f"Unable to load files for path {file_path}: {e}")            
            raise Exception(f"Unable to load files for path {file_path}")

        return files_dataframe

    @staticmethod
    def load_last_updated_path(landing_path):
        files_dataframe = LandingZoneUtils.load_files_dataframe(landing_path)
        return files_dataframe.first()["path"]"""
    