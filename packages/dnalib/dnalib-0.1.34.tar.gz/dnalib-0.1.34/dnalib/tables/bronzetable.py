from dnalib.utils import Utils
from dnalib.log import *
from dnalib.loaders import LoaderFactory, SourceType, LandingLoader
from dnalib.core import CreateTableBronze
from dnalib.writer import WriteModes
from .tables import LayerTable
        
class BronzeTable(LayerTable):

    layer = "bronze"

    def __init__(self,                  
                 table_name,                 
                 source_path,
                 yaml_config_path,
                 table_sufix = "",
                 source_type=SourceType.SQLSERVER, 
                 loader_type=LandingLoader.FULL,
                 source_df=None, 
                 name_filter="", 
                 unzip=True, 
                 include_checksum=False,  
                 collection_name=None,               
                 order_by = '__name__',
                 page_size = 1000,
                 init_load = None, 
                 end_load = None,
                 flat_json = True,
                 db_name = None,
                 spark_num_partitions = None):
        super().__init__(self.layer, f"{table_sufix}_{table_name}", source_df, include_checksum)        
        self.source_path = source_path
        self.name_filter = name_filter
        self.table_sufix = table_sufix
        self.source_type = source_type
        self.yaml_config_path = yaml_config_path
        self.table_config = Utils.yaml_table_parameters(table_name=f"{table_sufix}_{table_name}", yml_file_path=yaml_config_path)
        self.loader_type = loader_type
        self.unzip = unzip      
        self.collection_name = collection_name     
        self.order_by = order_by
        self.page_size = page_size
        self.init_load = init_load
        self.end_load = end_load  
        self.flat_json = flat_json
        self.db_name = db_name
        self.spark_num_partitions = spark_num_partitions
        self.except_fields = {}

        # Usa a fábrica para criar o file_loader correto
        self.file_loader = LoaderFactory.create_loader(            
            self.source_type,
            self.source_path,
            self.loader_type,            
            self.table_config,     
            self.collection_name,       
            self.order_by,
            self.page_size,
            self.init_load,
            self.end_load, 
            self.flat_json,
            self.db_name,
            self.spark_num_partitions
        )        

    def parse_df_source(self):
        """
            Método que executa o carregamento de dados da camada landing para a bronze

            Returns:
                source_df (spark DataFrame): dataframe carregado a partir da camada source, caso source_df seja None.

        """         
        # load strategy in this case is to check if the table exists        
        return self.file_loader.load().df_loader

    def load_fields_from_source(self):                
        return "*"
    
    def create_table(self, yml={}, partition_fields=[], tbl_properties={}, replace=False):
        if not self.has_loaded:
            self.load()
            log(__name__).warning(f"The load() method will be called internally because you call create_table first.") 
        self.creat_tbl = CreateTableBronze(self.target_df.schema, self.table_name, yml, partition_fields, tbl_properties, replace).execute()
        return self
    
    # implementar lógica usando mode = None (nesse caso a decisão usa o LandingLoader como parâmetro caso contrário fica a critério de quem escolheu)
    def persist(self, mode=None, partition_fields=[], optimize=True, source_df_name="source", update_df_name="update", merge_condition=None):        
        has_delete = False                
        # when you have cdc ingestion, you may need to upsert
        if mode is None:
            if self.loader_type.value == LandingLoader.CDC.value:
                mode = WriteModes.UPSERT
                merge_condition = self.table_config["merge"]
                has_delete = True        
            elif self.loader_type.value == LandingLoader.INCREMENTAL.value:
                mode = WriteModes.UPSERT
                merge_condition = self.table_config["merge"]  
            elif self.loader_type.value == LandingLoader.FULL.value:
                mode = WriteModes.OVERWRITE      

        # calling super persist method
        super().persist(mode=mode, partition_fields=partition_fields, optimize=optimize, source_df_name=source_df_name, update_df_name=update_df_name, merge_condition=merge_condition)

        # only for cdc purposes
        if has_delete:            
            key_columns = ",".join(self.table_config["key"]) if isinstance(self.table_config["key"], list) else self.table_config["key"]
            delete_condition = f"SELECT concat({key_columns}) FROM vw_table_logs_rownumber WHERE operation = 1"
            self.writer.delete(key_columns, delete_condition)       
        return self     

