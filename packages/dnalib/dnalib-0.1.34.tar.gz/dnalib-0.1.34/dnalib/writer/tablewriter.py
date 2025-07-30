from dnalib.log import log
from dnalib.utils import Utils
from delta.tables import DeltaTable
from enum import Enum

class WriteType(Enum):
    """ Classe com os tipos de escrita, batch e streaming """
    BATCH = "batch"
    STREAMING = "streaming"

class WriteModes(Enum):
    """ Classe com os modos de escritas válidos: overwrite, append e upsert. """
    OVERWRITE = "overwrite"    
    APPEND = "append"    
    UPSERT = "upsert"   
    UPDATE = "update" 

class TableWriter:
    """ Interface """

    def __init__(self, layer, table_name):        
        self.layer = layer        
        self.table_name = table_name

    def append(self):
        # TODO: implementar a escrita via append. 
        raise NotImplementedError("Method append() must be implemented.")

    def overwrite(self):
        # TODO: implementar a escrita via overwrite. 
        raise NotImplementedError("Method overwrite() must be implemented.")

    def upsert(self):
        # TODO: implementar a escrita via upsert. 
        raise NotImplementedError("Method upsert() must be implemented.")

    def update(self):
        # TODO: implementar a escrita via upsert. 
        raise NotImplementedError("Method update() must be implemented.")

    def optimize(self):        
        """ 
            Método interno para executar o OPTIMIZE.
        """     
        log(__name__).info(f"Optimizing table: {self.layer}.{self.table_name}.") 
        Utils.spark_instance().sql(f"OPTIMIZE {self.layer}.{self.table_name}")

class BatchTableWriter(TableWriter):

    def __init__(self, layer, table_name):
        TableWriter.__init__(self, layer, table_name)

    def __overwrite_or_append(self, df, mode, partition_fields=[]):
        # load df and mode
        df_write = df.write.format("delta").mode(mode.value)        
        # verify partitions
        if len(partition_fields) > 0:
            df_write = df_write.partitionBy(partition_fields)          
        # saving data in delta table                                
        df_write.saveAsTable(f"{self.layer}.{self.table_name}", path=Utils.lakehouse_path(self.layer, self.table_name))  

    def update(self, df_update, merge_condition, source_df_name="source", update_df_name="update", set_dict={}):
        """
            Método interno que executa o update.
                
            Args:   
                merge_condition (str): uma condição valida para fazer merge entre o "source_df_name" e o "update_df_name".
                has_checksum_field (bool): uma flag que indica se a tabela tem ou não o campo de checksum.            
        """
        df_source = DeltaTable.forName(Utils.spark_instance(), f"{self.layer}.{self.table_name}")
        merge = (df_source.alias(source_df_name)
            .merge(
                df_update.alias(update_df_name),
                merge_condition
            )            
            .whenMatchedUpdate(set=set_dict))        
        merge.execute()
        return self

    def upsert(self, df_update, merge_condition, source_df_name="source", update_df_name="update", has_checksum_field=False, ignore_updates=False, set_dict={}):
        """
            Método interno que executa o upsert.
                
            Args:   
                merge_condition (str): uma condição valida para fazer merge entre o "source_df_name" e o "update_df_name".
                has_checksum_field (bool): uma flag que indica se a tabela tem ou não o campo de checksum.            
        """
        df_source = DeltaTable.forName(Utils.spark_instance(), f"{self.layer}.{self.table_name}")
        # it improves merge performance in write operations
        update_condition = None
        if has_checksum_field:
            update_condition = f"nvl({source_df_name}.checksum, '') != {update_df_name}.checksum"
        # runing a normal merge operation
        merge = (df_source.alias(source_df_name)
            .merge(
                df_update.alias(update_df_name),
                merge_condition
            )            
            .whenNotMatchedInsertAll())
        # in upsert we may ignore updates            
        if not ignore_updates:
            if len(set_dict) > 0:
                merge = merge.whenMatchedUpdate(condition=update_condition, set=set_dict)
            else:
                merge = merge.whenMatchedUpdateAll(condition=update_condition)
        merge.execute()
        return self
    
    def delete(self, key_columns, delete_condition):
        """
        Método que executa a exclusão de dados da tabela com base em um conjunto de chaves e uma condição.

        Args:
            key_columns (str): Chaves para realizar o delete.
        
        Returns:
            self: uma instância da classe TableWriter.
        """                    
        try:            
            df_delete = Utils.spark_instance().sql(f"""DELETE FROM {self.layer}.{self.table_name}
                           WHERE concat({key_columns}) IN ({delete_condition}) """)                        
            num_affected_rows = df_delete.first()["num_affected_rows"]
            log(__name__).info(f"{num_affected_rows} records where deleted from {self.layer}.{self.table_name}.")
        except:
            log(__name__).error(f"Error while trying to delete records from {self.layer}.{self.table_name}.")
            raise Exception(f"Error while trying to delete records from {self.layer}.{self.table_name}.")

        return self

    def overwrite(self, df, partition_fields=[]):
        """ """
        self.__overwrite_or_append(df, WriteModes.OVERWRITE, partition_fields)
        return self

    def append(self, df, partition_fields=[]):
        """ """
        self.__overwrite_or_append(df, WriteModes.APPEND, partition_fields)
        return self

    def persist(self, df, mode=WriteModes.OVERWRITE, partition_fields=[], optimize=True, source_df_name="source", update_df_name="update", merge_condition=None, has_checksum_field=False, ignore_updates=False, set_dict={}):
        """ """
        df_count = df.count() 
        if df_count == 0:                                        
            log(__name__).warning(f"No data to persist in {self.table_name}, so nothing will be done.")       
        else:     
             # overwrite or append has same sintax
            if mode.value == WriteModes.OVERWRITE.value:
                self.overwrite(df, partition_fields)
            elif mode.value == WriteModes.APPEND.value:         
                self.append(df, partition_fields)        
            elif mode.value == WriteModes.UPSERT.value:
                if merge_condition is None:
                    log(__name__).error(f"The merge_condition parameter is required for upsert mode")           
                    raise Exception(f"The merge_condition parameter is required for upsert mode")                
                self.upsert(df, merge_condition, source_df_name, update_df_name, has_checksum_field, ignore_updates, set_dict)
            else:
                log(__name__).error(f"The mode parameter {mode} is not valid. Valid values are: {[m.value for m in WriteModes]}")            
                raise Exception(f"The mode parameter {mode} is not valid. Valid values are: {[m.value for m in WriteModes]}")            
            log(__name__).info(f"Sucessfully persisted {df_count} rows to {self.layer}.{self.table_name} using {mode.value} mode.") 
            # runing optimize operation
            if optimize:            
                self.optimize()                
        return self

class StreamingTableWriter(TableWriter):
    """
        Classe para escrita de streaming
    """

    def __init__(self, layer, table_name, checkpoint_path="_checkpoints", processing_time="10 minutes"):
        TableWriter.__init__(self, layer, table_name)
        self.checkpoint_path = checkpoint_path
        self.processing_time = processing_time
        self.checkpoint_location = Utils.lakehouse_path(f"{self.layer}/{self.checkpoint_path}/{self.table_name}")    

    def upsert(self, df, merge_condition, source_df_name="source", update_df_name="update", drop_keys=[]):
        layer = self.layer
        table_name = self.table_name
        # inner method to execute merge based on our implementation
        def merge_micro_df(micro_df, batch_id):
            if not microdf.isEmpty():                
                df_source = DeltaTable.forName(Utils.spark_instance(), f"{layer}.{table_name}")
                ## Merge
                df_updates = microdf.dropDuplicates(drop_keys)
                (df_source.alias(source_df_name)
                    .merge(
                        df_update.alias(update_df_name),
                        merge_condition
                    )
                    .whenMatchedUpdateAll()
                    .whenNotMatchedInsertAll()
                    .execute()) 
        # call writestream
        (df.writeStream.format("delta")
            .outputMode('append')  
            .trigger(processingTime=self.processing_time)
            .foreachBatch(merge_micro_df) 
            .option("checkpointLocation", self.checkpoint_location)
            .start())
        return self

    def append(self, df):
        (df.writeStream.format("delta")
            .outputMode('append')
            .trigger(processingTime=self.processing_time)
            .option("checkpointLocation", self.checkpoint_location) 
            .start(Utils.lakehouse_path(f"{self.layer}/{self.table_name}")))
        return self

    def persist(self, df, mode=WriteModes.APPEND, partition_fields=[], optimize=True, source_df_name="source", update_df_name="update", merge_condition=None, drop_keys=[]):
        if mode.value == WriteModes.APPEND.value:
            self.append(df)
        elif mode.value == WriteModes.UPSERT.value:
            if merge_condition is None:
                log(__name__).error(f"The merge_condition parameter is required for upsert mode")           
                raise Exception(f"The merge_condition parameter is required for upsert mode")
            self.upsert(df, merge_condition, source_df_name, update_df_name, drop_keys)
        else:
            log(__name__).error(f"The mode parameter {mode} is not valid. Valid values are: {[m.value for m in WriteModes]}")            
            raise Exception(f"The mode parameter {mode} is not valid. Valid values are: {[m.value for m in WriteModes]}")  

        # implementar logica de desligamento do streaming
        
        return self
    