from dnalib.log import *
from dnalib.utils import Utils, LandingZoneUtils
from .loader import Loader

class SqlParquetLandingLoader(Loader):
    """ 
        This implementation is based on our adf process:
            table/date/ -> incremental path
            table/date/ -> cdc path
            table/date/ -> full path = if process run in incremental mode, but you specified a full query
            table/ -> full path
    """

    metadata_columns = ["Dt_Inclusao"]

    def __init__(self, source_path, loader_type, table_config):
        super().__init__(source_path, loader_type) 
        self.spark = Utils.spark_instance()  # Obtém a instância do Spark usando Utils.spark_instance()                        
        self.table_config = table_config

    def load_df_parquet(self):
        # le o path mais recente dentro da pasta indicada por source_path
        file_path = LandingZoneUtils.load_last_updated_path(self.source_path)
        # Lê os dados do parquet atual
        try:
            df = self.spark.read.parquet(file_path).drop(*self.metadata_columns) 
        except Exception as e:
            log(__name__).error(f"Error reading parquet file: {e}")          
            raise Exception(f"Error reading parquet file: {e}")
        return df

    def load_incremental(self):       
        return self.load_df_parquet()

    def load_full(self):
        return self.load_df_parquet()
        
class SqlServerParquetLandingLoader(SqlParquetLandingLoader):

    # only applied in cdc purposes
    cdc_metadata_columns = ["LAST_UPDATE", "start_lsn", "end_lsn", "seqval", "operation", "update_mask", "command_id", "data_alteracao"]

    def __init__(self, source_path, loader_type, table_config):
        super().__init__(source_path, loader_type, table_config)

    def load_cdc(self):
        df = self.load_incremental()                

        # query que pega a última alteração de cada registro
        df = (df.withColumnRenamed("__$start_lsn", "start_lsn") 
               .withColumnRenamed("__$end_lsn", "end_lsn") 
               .withColumnRenamed("__$seqval", "seqval") 
               .withColumnRenamed("__$operation", "operation") 
               .withColumnRenamed("__$update_mask", "update_mask") 
               .withColumnRenamed("__$command_id", "command_id"))
        
        # view para filtrar as alterações
        df.createOrReplaceTempView("vw_table_logs")
        self.spark.sql(f"""
            CREATE OR REPLACE TEMP VIEW vw_table_logs_rownumber AS (
                SELECT * FROM (
                    SELECT 
                        *, 
                        ROW_NUMBER() OVER(PARTITION BY {self.table_config['key']} ORDER BY data_alteracao DESC, command_id DESC) AS LAST_UPDATE FROM vw_table_logs
                    WHERE operation <> 3                                                
                )
                WHERE LAST_UPDATE = 1
            );
        """)

        # filtra as operações de insert e update
        df_upinsert = self.spark.sql(""" 
            SELECT * 
            FROM vw_table_logs_rownumber 
            WHERE operation IN (2, 3, 4);
            """).drop(*self.cdc_metadata_columns)                      
        return df_upinsert        

class OracleParquetLandingLoader(SqlParquetLandingLoader):

    def __init__(self, source_path, loader_type, table_config):
        super().__init__(source_path, loader_type, table_config)
        
