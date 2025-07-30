from pyspark.sql.functions import lit
from pyspark.sql.types import StructType, StringType, IntegerType, DateType, StructField, TimestampType
from dnalib.writer import BatchTableWriter
from dnalib.core import Table
from dnalib.tables import DynamicTable
from dnalib.log import *
from .block import Block
from .key import Key

class BlockBucket(Table,
                  BatchTableWriter,
                  DynamicTable):
    """
        Classe que controla os "buckets", ou seja os baldes de blocos.
    """
    
    fields_comment = {
        "is_block_processed": {'comment': "Flag que indica se o bloco já foi processado, ou seja carregado em alguma blockchain."}
    }

    schema = (StructType([field for field in Block.schema])
                    .add(StructField("is_block_processed", IntegerType(), True, fields_comment["is_block_processed"])))
    
    layer = "blockchain"

    def __init__(self, table_name):    
        # chamando o super para criar a tabela
        Table.__init__(self, self.layer, table_name, self.schema)          
        BatchTableWriter.__init__(self, self.layer, table_name)        
        self.create()
        # chamando o super para a DynamicTable
        DynamicTable.__init__(self, self.layer, table_name, json_fields=["payload"])      

    def add_block_metadata(self, block, prev_block_name=None, prev_block_join_rules=None):
        # the metadata is necessary to translate rules to blockchain
        tbl_properties = {f"blockchain.{block.block_name}.prev_block_name": prev_block_name, 
                          f"blockchain.{block.block_name}.prev_block_join_rules": prev_block_join_rules.serialize() if prev_block_join_rules is not None else None}
        # we store metadata as tbl_properties
        self.add_tbl_properties(tbl_properties)

    def add_block(self, block, prev_block_name=None, prev_block_join_rules=None):        
        # add block metadata
        self.add_block_metadata(block.load(), prev_block_name, prev_block_join_rules)
        # adding field to control if the block is already in the blockchain
        df_block = block.df_block.withColumn("is_block_processed", lit(0))
        # inserting block for only new data (ignoring updates)
        log(__name__).info(f"Appeding new blocks to bucket table {self.layer}.{self.table_name}.")
        self.upsert(df_block, "source.id_block == update.id_block", ignore_updates=True)
        # get operation metrics to see new blocks
        total_new_blocks = self.parse_last_operation_metrics().get("numTargetRowsInserted", 0)
        log(__name__).info(f"Total of {total_new_blocks} blocks of type {block.block_name} were added to bucket.")

    def load(self, block_name):    
        # load block
        df_block = self.spark.table(self.table_catalog_path).filter(f"block_name == '{block_name}' and is_block_processed = 0").drop("is_block_processed")
        # get metadata
        tbl_properties = self.parse_tbl_properties()
        # load block metadata
        prev_block_name = tbl_properties.get(f"blockchain.{block_name}.prev_block_name", None)
        prev_block_join_rules = tbl_properties.get(f"blockchain.{block_name}.prev_block_join_rules", None)
        # loading join rules
        if prev_block_join_rules is not None:
            prev_block_join_rules = Key.from_serialized(prev_block_join_rules)
        # retorna o bloco carregado
        return df_block, prev_block_name, prev_block_join_rules
            