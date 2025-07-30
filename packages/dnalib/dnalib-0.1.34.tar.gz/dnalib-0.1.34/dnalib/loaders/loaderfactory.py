from .loader import SourceType
from .sqlparquetlandingloader import *
from .firebaseloader import *
from dnalib.log import *

class LoaderFactory:
    @staticmethod
    def create_loader(source_type, 
                      source_path, 
                      loader_type, 
                      table_config, 
                      collection_name = None,                      
                      order_by = '__name__', 
                      page_size = 1000, 
                      init_load = None, 
                      end_load = None,
                      flat_json = True,
                      db_name = None,
                      spark_num_partitions = None):
        if source_type.value == SourceType.SQLSERVER.value:
            return SqlServerParquetLandingLoader(source_path, loader_type, table_config)
        elif source_type.value == SourceType.ORACLE.value:
            return OracleParquetLandingLoader(source_path, loader_type, table_config)
        elif source_type.value == SourceType.FIREBASE.value:
            return FireBaseLoader(source_path, loader_type, collection_name, order_by, page_size, init_load, end_load, flat_json, db_name, spark_num_partitions)
        else:
            log(__name__).error(f"file_loader could not be created for source_type {source_type}")
            raise ValueError(f"file_loader could not be created for source_type {source_type}")