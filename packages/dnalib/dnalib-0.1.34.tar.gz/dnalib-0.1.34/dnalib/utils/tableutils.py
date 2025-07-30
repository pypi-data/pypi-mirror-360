from pyspark.sql import SparkSession
from .utils import Utils 
from dnalib.log import log
from delta.tables import DeltaTable
from pyspark.sql.functions import monotonically_increasing_id
import json

class TableUtils:

    #  
    #   Description:
    #       This method formats a comment (for field or table).
    #
    #   Parameters:      
    #       comment_content = the content of the comment.
    # 
    @staticmethod
    def format_comment_content(comment_content):
        # remove whitespaces        
        if len(comment_content) > 0:
            value = comment_content.strip()
            # insert ponctuation at the end of string
            if value[-1] != '.':
                value += '.'
            # first digit in upper case        
            return value[0].upper() + value[1:]
        else: 
            return comment_content

    #  
    #   Description:
    #       This method formats a field to a hash type.
    #
    #   Parameters:      
    #       field = field name to be a hashed field
    # 
    @staticmethod
    def hash_field_str(field):        
        return f"sha2(cast({field} as string), 256) AS {field}"

    #  
    #   Description:
    #       This method loads a dataframe from path (usefull if table does not exists in catalog yet).
    #
    #   Parameters:      
    #       layer = table layer (bronze, silver, gold, diamond or export)
    #       table_name = the name of the table.    
    # 
    @staticmethod
    def load_df_from_lakehouse(layer, table_name):        
        root_path = Utils.lakehouse_path()
        try:
           df = Utils.spark_instance().read.load(f'{root_path}/{layer}/{table_name}')
        except:
            log(__name__).error(f"Unable to read '{root_path}/{layer}/{table_name}'")
            raise Exception(f"Unable to read '{root_path}/{layer}/{table_name}'")
        return df
    #  
    #   Description:
    #       This method gets schema table from path (usefull if table does not exists in catalog yet).
    #
    #   Parameters:      
    #       layer = table layer (bronze, silver, gold, diamond or export)
    #       table_name = the name of the table.    
    #     
    @staticmethod
    def table_schema_from_lakehouse(layer, table_name):                        
        return TableUtils.load_df_from_lakehouse(layer, table_name).schema
    
    #  
    #   Description:
    #       This method checks if a view exists from a table name in catalog.
    #
    #   Parameters:      
    #       layer = table layer (bronze, silver, gold, diamond or export)
    #       view_name = the name of the table.    
    # 
    @staticmethod
    def view_exists(layer, view_name):                                
        return Utils.spark_instance().catalog.tableExists(f"{layer}.{view_name}")        
    
    #  
    #   Description:
    #       This method checks if a table exists in catalog.
    #
    #   Parameters:      
    #       layer = table layer (bronze, silver, gold, diamond or export)
    #       table_name = the name of the table.    
    # 
    @staticmethod
    def table_exists(layer, table_name):                
        return Utils.spark_instance().catalog.tableExists(f"{layer}.{table_name}")
        #try:
            #DeltaTable.forName(Utils.spark_instance(), f"{layer}.{table_name}")
            #return True
        #except:
            #return False
    
    @staticmethod
    def describe_table(layer, table_name):
        df_describe = Utils.spark_instance().sql(f"DESCRIBE EXTENDED {layer}.{table_name}")
        return df_describe.withColumn("rowId", monotonically_increasing_id())

    @staticmethod
    def drop_table(layer, table_name):
        """           
            Esse método executa um drop deep, removendo a tabela e a sua pasta no lakehouse.
    
            Args:
                layer (str): nome da camada.
                table_name (str): nome da tabela para ser dropada.
        """
        Utils.spark_instance().sql(f"drop table if exists {layer}.{table_name}")
        is_removed = Utils.remove_table_from_lakehouse(layer, table_name)
        if not is_removed:
            log(__name__).warning(f"Table {layer}.{table_name} does not exists in lakehouse")  
        return is_removed
    
    @staticmethod    
    def drop_view(layer, view_name):
        """            
            Esse método dropa uma view de maneira safe, isto é caso ela exista.

            Args:
                layer (str): nome da camada.
                view_name (str): nome da view para ser dropada.
        """
        Utils.spark_instance().sql(f"drop view if exists {layer}.{view_name}")     

    @staticmethod
    def describe_history(layer, table_name, limit=None):
        return Utils.spark_instance().sql(f"DESCRIBE HISTORY {layer}.{table_name}").limit(limit)

    @staticmethod
    def table_comment(layer, table_name):   
        if not TableUtils.table_exists(layer, table_name):
            log(__name__).error(f"Table {layer}.{table_name} does not exist")
            raise ValueError(f"Table {layer}.{table_name} does not exist")        
        table_comment = ""    
        df_comment = Utils.spark_instance().sql(f"DESCRIBE EXTENDED {layer}.{table_name}").filter("col_name == 'Comment'").select('data_type')
        if df_comment.count() > 0:                
            table_comment = df_comment.collect()[0][0]
        return table_comment
    
    @staticmethod
    def table_fields_metadata(layer, table_name):
        fields = {}
        if not TableUtils.table_exists(layer, table_name):
            log(__name__).error(f"Table {layer}.{table_name} does not exist")
            raise ValueError(f"Table {layer}.{table_name} does not exist")
        try:
            df_metadata = Utils.spark_instance().sql(f"desc table extended {layer}.{table_name}").withColumn("rowId", monotonically_increasing_id())
            rowId = df_metadata.filter("col_name like '#%'").select('rowId').first()[0]                        
            fields_params = df_metadata.filter(f"(rowId < {rowId}) and col_name != ''").drop('rowId', 'data_type').toJSON().collect()
        except:
            log(__name__).error(f"Unable to load fields from table {layer}.{table_name}.")
            raise ValueError(f"Unable to load fields from table {layer}.{table_name}.") 
        for field_param in fields_params:
            field_param_json = json.loads(field_param)
            fields[field_param_json.get('col_name')] = [field_param_json.get('comment')]
        return fields

    @staticmethod
    def clone_table(source_layer, table_name, target_layer, target_table_name):
        """ 
            Método que executa um clone "safe" entre duas tabelas.

            Args:
                source_layer (str): nome da camada de origem.
                table_name (str): nome da tabela de origem.
                target_layer (str): nome da camada de destino.
                target_table_name (str): nome da tabela de destino.
        """
        if TableUtils.table_exists(f"{source_layer}", table_name):        
            Utils.spark_instance().sql(f"""
                CREATE OR REPLACE TABLE {target_layer}.{target_table_name}
                CLONE {source_layer}.{table_name} 
              """)
            df_comment = Utils.spark_instance().sql(f"DESCRIBE EXTENDED {source_layer}.{table_name}").filter("col_name == 'Comment'").select('data_type')
            if df_comment.count() > 0:                
                table_comment = df_comment.collect()[0][0]
                Utils.spark_instance().sql(f"COMMENT ON TABLE {target_layer}.{target_table_name} IS '{table_comment}'")
        else:
            log(__name__).warning(f"Table {source_layer}.{table_name} does not exists in lakehouse")

    @staticmethod
    def grant_select(layer, table_name, users):
        """ 
            Método que executa grant select para uma tabela e uma lista de usuários.

            Args:
                layer (str): nome da camada.
                table_name (str): nome da tabela.
                users (str ou list): nome ou lista de usuários.
        """
        if isintance(users, str):
            users = [users]
        if TableUtils.table_exists(f"{layer}", table_name):        
            for user in users:                
                try:
                    Utils.spark_instance().sql(f"""GRANT SELECT ON TABLE {layer}.{table_name} TO `{user}`""")           
                except:
                    log(__name__).warning(f"Could not grant SELECT in table {layer}.{table_name} to user {end_user}.")
        else:
            log(__name__).warning(f"Table {layer}.{table_name} does not exists in lakehouse.")
                            