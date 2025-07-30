from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils
from dnalib.custom import YamlLoader
import yaml
from dnalib.log import log

class Utils:
    
    #  
    #   Description:
    #       This method removes a table from the lakehouse (it deletes the files).
    #
    #   Parameters:      
    #       layer = table layer (bronze, silver, gold, diamond or export)
    #       table_name = the name of the table.    
    #
    @staticmethod
    def remove_table_from_lakehouse(layer, table):
        table_path = Utils.lakehouse_path(layer, table)        
        return Utils.dbutils().fs.rm(table_path, True)        

    #  
    #   Description:
    #       This method returns spark instance.
    #
    @staticmethod
    def spark_instance():        
        return SparkSession.builder.getOrCreate()

    #  
    #   Description:
    #       This method returns a new dbutils instance.
    #
    @staticmethod
    def dbutils():  
        return DBUtils(Utils.spark_instance())
    
    @staticmethod
    def key_vault_value(key_vault):
        SCOPE = "key-vault-secrets"
        return Utils.dbutils().secrets.get(scope=SCOPE, key=key_vault)

    #  
    #   Description:
    #       This method returns storage var according to key vault secret scope.
    #
    @staticmethod
    def storage():
        SCOPE = "key-vault-secrets"
        return Utils.dbutils().secrets.get(scope=SCOPE, key="externalLocation")
    
    #  
    #   Description:
    #       This method returns the lakehouse path considering our storage configuration.
    #
    #   Parameters:      
    #       layer [optional] = table layer (bronze, silver, gold, diamond or export)
    #       table_name [optional] = the name of the table.
    #
    @staticmethod
    def lakehouse_path(layer=None, table_name=None):        
        storage = Utils.storage()
        if layer != None and table_name != None:
            return f"abfss://lakehouse@{storage}/{layer}/{table_name}"
        else:
            return f"abfss://lakehouse@{storage}"
        
    @staticmethod
    def landingzone_path(dir_path):
        storage = Utils.storage()
        return f"abfss://landingzone@{storage}/{dir_path}"
    
    @staticmethod
    def container_path(container_name, file_name):
        storage = Utils.storage()
        return f"abfss://{container_name}@{storage}/{file_name}"
        
    #  
    #   Description:
    #       This method loads and parse a yml file, it is based on custom YamlLoader (see source).
    #
    #   Parameters:      
    #       yml_file_path = the yaml file path.   
    #
    @staticmethod
    def safe_load_and_parse_yml(yml_file_path, write_workspace=False):
         # load yaml config file
        if write_workspace:
            yml_file_path = f'file:{yml_file_path}'
        try:
            yml_text = (
                Utils.spark_instance().read.text(
                    f'{yml_file_path}', wholetext=True)
                .first()[0]
            )
        except:
            log(__name__).error(f"Unable to read {yml_file_path}.")
            raise Exception(f"Unable to read {yml_file_path}.")

        ## parse the yaml
        try:
            parsed_yml = yaml.load(yml_text, YamlLoader)
        except:
            log(__name__).error(f"Unable to parse {yml_file_path}.")
            raise Exception(f"Unable to parse {yml_file_path}.")

        return parsed_yml
    
    @staticmethod
    def yaml_table_parameters(table_name, yml_file_path):
        table_config = None
        yaml_config = Utils.safe_load_and_parse_yml(yml_file_path)
        # Extração das chaves e regras de merge do YAML
        if table_name in yaml_config['tables']:
            table_config = yaml_config['tables'][table_name]            
        else:            
            log(__name__).error(f"Table {table_name} not found in yaml configuration.")
            raise Exception(f"Table {table_name} not found in yaml configuration.")
        return table_config
