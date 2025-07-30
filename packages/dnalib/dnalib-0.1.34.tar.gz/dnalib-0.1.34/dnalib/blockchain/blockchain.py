from pyspark.sql.functions import col, lit
from dnalib.utils import TableUtils, Utils
from dnalib.log import log
from dnalib.tables import DynamicTable
from dnalib.writer import BatchTableWriter
from dnalib.core import Table
from .block import Block
from delta.tables import DeltaTable

class BlockChain(Table,
                 BatchTableWriter,
                 DynamicTable):
    """
        Implementação da blockchain
    """

    layer = "blockchain"

    def __init__(self, table_name):            
        # chamando o super para criar a tabela
        Table.__init__(self, self.layer, table_name, Block.schema)          
        BatchTableWriter.__init__(self, self.layer, table_name)        
        self.create()        
        # carragndo dados da tabela de blockchain
        self.df_block_chain = self.spark.table(self.table_catalog_path) 
        # armazenando a computação corrente da blockchain
        self.df_block_chain_current = None 
        # chamando o super para a DynamicTable
        DynamicTable.__init__(self, self.layer, table_name, json_fields=["payload"])                       

    def compute_blockchain(self, df_block, block_name, prev_block_name=None, prev_block_join_rules=None):            
        # cleaning the current blockchain to allow new computations
        self.df_block_chain_current = self.spark.createDataFrame([], Block.schema)  
        # usa a blockchain como o "bloco anterior"
        df_block_chain = self.df_block_chain.alias("block_prev")      
        # colunas que são usadas nas queries  
        columns = df_block.columns
        #
        #   É preciso determinar primeiro quais transações são novas
        #   e isso pode ser feito a partir do id block (hash)
        #   toda transação nova não pode estar na blockchain
        #   
        #   Dado que A é o bloco novo e B a blockchain, 
        #   então A \ B são as novas transações (garantia de unicidade de registro na blockchain).
        #
        df_block = (
            df_block.join(
                df_block_chain, 
                on=[col("block.id_block") == col("block_prev.id_block")], 
                how="leftanti"
        )).alias("block")        
        # blocos que iniciam a cadeia não tem estrutura de prev (são raízes do grafo) 
        if prev_block_join_rules is not None:                          
            # otimizando a consulta filtrando pelo tipo do block anterior (usando o nome), já que todo bloco deve ter apenas um parent
            if prev_block_name is not None:                
                df_block_chain = df_block_chain.filter(col("block_name") == lit(prev_block_name))                
            #
            # Primeira operação é verificar se existe conexão com bloco anterior (usando left anti join)
            # nesse caso os blocos são geradores (ou seja não possuem conexão anterior na cadeia).
            #
            df_next_block = (
                df_block.join(
                    df_block_chain, 
                    on=prev_block_join_rules.field_rep, # chaves de negócio
                    how="leftanti"
            ))          
            # o bloco é inserido na blockchain       
            df_block_union = df_next_block.select(*columns)     
            self.df_block_chain_current = self.df_block_chain_current.union(df_block_union)
            # agora é verificado os blocks que tem conexão na cadeia (via inner join)
            df_next_block = (
                df_block.join(
                    df_block_chain, 
                    on=prev_block_join_rules.field_rep, # chaves de negócio
                    how="inner"
            ))   

            #
            # As colunas do blockchain são agora propagadas para o próximo bloco:
            #   o id_block_gen vem do bloco anterior
            #   o id_block_prev é o id do bloco anterior 
            #   como conectou, esse bloco não é gerador
            #
            propagate_block_fields = (
                col("block.block_name"),
                (col("block_prev.block_level") + lit(1)).alias("block_level"),
                col("block.block_business_keys"),
                col("block_prev.id_block_gen"),  
                col("block.id_block"),
                col("block_prev.id_block").alias("id_block_prev"),    
                lit(0).alias("is_gen"),
                col("block.block_timestamp"),
                col("block.payload"),
                lit(1).alias("block.last_block")
            )            
            # o bloco é inserido na blockchain                         
            df_block_union = df_next_block.select(*propagate_block_fields)
            self.df_block_chain_current = self.df_block_chain_current.union(df_block_union)                                  
        else:
            # quando o bloco é a "raíz" ele não possui bloco prev, portanto ele é inserido direto na blockchain
            df_block_union = df_block.select(*columns)                   
            self.df_block_chain_current = self.df_block_chain_current.union(df_block_union)           
        return self
    
    def update_last_block(self):              
        # para todo bloco A na cadeia, se existe B tal que B \neq A e id_block_prev(B) = id_block(A), então last_block(A) = 0
        log(__name__).info(f"Updating last_block column to previously blockchain blocks.")
        df_non_last_blocks = self.df_block_chain_current.select(col("id_block_prev").alias("_id_block_prev")).filter("_id_block_prev is not null").distinct()
        # como a computação é incremental, então existem blocos onde o last_block(A) = 0, porém last_block_{-1}(A) = 1 (ou seja, estão salvos na tabela delta como 1)
        df_prev_last_blocks = df_non_last_blocks.alias("block").join(
            self.df_block_chain_current.alias("block_prev"),
            on=[col("block._id_block_prev") == col("block_prev.id_block")],
            how="leftanti",
        )
        # atualizando somente os blocos anteriores
        self.update(df_prev_last_blocks, "source.id_block = update._id_block_prev", set_dict={"last_block":lit(0)})

    # atualiza a tabela dos blocos
    def update_blocks(self):                
         # logando o número de novos blocos
        total_new_blocks = self.df_block_chain_current.count() 
        # atualizando a blockchain
        if total_new_blocks > 0:
            self.update_last_block()                        
            # as novas transações são inseridas na tabela do blockchain
            log(__name__).info(f"Appeding new blocks to blockchain table {self.layer}.{self.table_name}.")
            self.append(self.df_block_chain_current)
        # logging new blocks
        log(__name__).info(f"Total of {total_new_blocks} blocks were added to blockchain.")

    def add_block_bucket(self, block_bucket, list_of_block_names):
        # compute blockchain structure based on a bucket of blocks
        for block_name in list_of_block_names:
            # carregando dados do bucket de acordo com o bloco que está sendo processado
            df_block, prev_block_name, prev_block_join_rules = block_bucket.load(block_name)
            # computando a blockchain
            self.compute_blockchain(df_block.alias("block"), block_name, prev_block_name, prev_block_join_rules)                    
            # atualizar a blockchain
            self.update_blocks()
            # "marcando como processados" os novos blocos da blockchain            
            df_block_in_chain = (df_block.alias("bucket").join(
                self.df_block_chain.alias("blockchain"), 
                on=[col("bucket.id_block") == col("blockchain.id_block")], 
                how="inner")
            )
            block_bucket.update(df_block_in_chain.select(col("bucket.id_block")).distinct(), "source.id_block = update.id_block", set_dict={"is_block_processed":lit(1)})
        # otimizando a tabela ao final das atualizações
        self.optimize()   

    def add_block(self, block, prev_block_name=None, prev_block_join_rules=None):  
        # compute blockchain structure based on single block
        self.compute_blockchain(block.load().df_block.alias("block"), block.block_name, prev_block_name, prev_block_join_rules)      
        # atualizar a blockchain
        self.update_blocks()
             