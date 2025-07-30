from dnalib.core import *
from dnalib.custom import *
from dnalib.log import *
from dnalib.utils import *
from dnalib.tables import *

#  
#   Description:
#       This method creates a table based on our patterns (field comments, table comments, view for hashing and etc).
#
#   Parameters:      
#       schema[df.schema] = table schema (same of df.schema)
#       layer[str] = table layer (bronze, silver, gold, diamond or export)
#       table_name[str] = the name of the table.
#       yml[yml object, string or None] = yml file path (it is not required to create a bronze table). Default is none.
#
def create_table(schema, layer, table_name, yml={}, partition_fields=[], anonimized_fields=[], comment={}, comment_squad={}, fields={}, tbl_properties={}, replace=False):
    log(__name__).info(f"Running create_table method for {layer}.{table_name}")
    if layer != "bronze":
        ct = CreateTableSilver(schema, table_name, yml, partition_fields, anonimized_fields, comment, comment_squad, fields, tbl_properties, replace).execute()        
        CreateView(schema, layer, table_name, ct.yml, ct.tbl_comment.parsed_comment, anonimized_fields, comment, comment_squad, fields, replace).execute()
    else:
        CreateTableBronze(schema, table_name, yml, partition_fields, tbl_properties, replace).execute()
    log(__name__).info(f"End create_table method for {layer}.{table_name}")

#  
#   Description:
#       This method creates a table in bronze layer based on our patterns (field comments, table comments, view for hashing and etc).
#
#   Parameters:      
#       schema[df.schema] = table schema (same of df.schema)
#       table_name[str] = the name of the table.
#       yml[yml object, string or None] = yml file path (it is not required to create a bronze table). Default is none.
#
def create_table_bronze(schema, table_name, yml={}, partition_fields=[], tbl_properties={}, replace=False):
    log(__name__).info(f"Running create_table_bronze method for bronze.{table_name}")
    CreateTableBronze(schema, table_name, yml, partition_fields, tbl_properties, replace).execute()
    log(__name__).info(f"End create_table_bronze method for bronze.{table_name}")

#  
#   Description:
#       This method creates a table in silver layer based on our patterns (field comments, table comments, view for hashing and etc).
#
#   Parameters:      
#       schema[df.schema] = table schema (same of df.schema)
#       table_name[str] = the name of the table.
#       yml[yml object, string or None] = yml file path (it is not required to create a bronze table). Default is none.
#
def create_table_silver(schema, table_name, yml={}, partition_fields=[], anonimized_fields=[], comment={}, comment_squad={}, fields={}, tbl_properties={}, replace=False):
    log(__name__).info(f"Running create_table_silver method for silver.{table_name}")
    ct = CreateTableSilver(schema, table_name, yml, partition_fields, anonimized_fields, comment, comment_squad, fields, tbl_properties, replace).execute()        
    CreateView(schema, layer, table_name, ct.yml, ct.tbl_comment.parsed_comment, anonimized_fields, comment, comment_squad, fields, replace).execute()
    log(__name__).info(f"End create_table_silver method for silver.{table_name}")

#  
#   Description:
#       This method drops a table and all its files in storage.
#
#   Parameters:      
#       layer[str] = table layer (bronze, silver, gold, diamond or export)
#       table_name[str] = the name of the table.
#
def drop_table(layer, table_name):
    log(__name__).info(f"Running drop_table method for {layer}.{table_name}")
    TableUtils.drop_table(layer, table_name)
    log(__name__).info(f"End drop_table method for {layer}.{table_name}")

#  
#   Description:
#       This method drops a view from a table.
#
#   Parameters:      
#       layer[str] = table layer (bronze, silver, gold, diamond or export)
#       table_name[str] = the name of the table.
#
def drop_view(layer, table_name):
    log(__name__).info(f"Running drop_view method for {layer}.{table_name}")
    TableUtils.drop_view(layer, table_name)
    log(__name__).info(f"End drop_view method for {layer}.{table_name}")    