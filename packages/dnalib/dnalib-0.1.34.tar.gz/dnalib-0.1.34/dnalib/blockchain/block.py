from pyspark.sql.functions import xxhash64, col, lit, concat, from_utc_timestamp, current_timestamp, to_json, struct
from pyspark.sql.types import StructType, StringType, IntegerType, DateType, StructField, TimestampType

class Block:    
    """ 
        A classe Block representa um bloco na cadeia do Blockchain.

        Args:
            df (DataFrame): dataframe que representa os dados que serão adicionados a blockchain.
            block_name (str): nome do bloco.
            block_business_keys (list): chaves de negócio que são usadas pra conectar os blocos.      
            fields_to_hash (list, default=[]): lista de campos que serão usados para gerar o hash identificador do bloco. se vazia, todos os campos são usados na geração do hash.
            fields_to_non_hash (list, default=[]): lista de campos que serão ignorados para gerar o hash identificador do bloco.

        Attributes:
            fields_ignored_to_hash (list): lista que contém os campos que são ignorados por padrão para gerar o hash identificador do bloco.
            df (DataFrame): dataframe que representa os dados que serão adicionados a blockchain.
            block_name (str): nome do bloco.
            block_business_keys (list): chaves de negócio que são usadas pra conectar os blocos.      
            fields_to_hash (list, default=[]): lista de campos que serão usados para gerar o hash identificador do bloco. se vazia, todos os campos são usados na geração do hash.
            fields_to_non_hash (list, default=[]): lista de campos que serão ignorados para gerar o hash identificador do bloco.
            df_block (DataFrame): dataframe que contém a estrutura inicial do bloco.
    """

    fields_comment = {
        "block_name":  {'comment':"Nome do bloco, utilizado para otimizar as conexões do blockchain."},
        "block_level":  {'comment':"Nível do bloco, usado para identificar a sua profundidade na blockchain."},
        "block_business_keys":  {'comment':"Campo com as chaves de negócio concatenadas."},
        "id_block_gen":  {'comment':"Identificador gerado no primeiro bloco e propagado por toda a cadeia."},
        "id_block":  {'comment':"Identificador único do bloco, gerado a partir de um hash."},
        "id_block_prev":  {'comment':"Identificador id_block do bloco anterior."},
        "is_gen":  {'comment':"Flag que indica se o bloco é gerador (1 se sim e 0 se não)."},
        "block_timestamp":  {'comment':"Timestamp da inserção do bloco na blockchain."},
        "payload":  {'comment':"Metadados em formato JSON, são as colunas do dataframe que representa o bloco."},
        "last_block":  {'comment':"Flag que indica que o bloco é o último na cadeia."},
    }

    schema = StructType([
        StructField("block_name", StringType(), True, fields_comment["block_name"]),
        StructField("block_level", IntegerType(), True, fields_comment["block_level"]),
        StructField("block_business_keys", StringType(), True, fields_comment["block_business_keys"]),
        StructField("id_block_gen", StringType(), True, fields_comment["id_block_gen"]),
        StructField("id_block", StringType(), True, fields_comment["id_block"]),
        StructField("id_block_prev", StringType(), True, fields_comment["id_block_prev"]),
        StructField("is_gen", IntegerType(), True, fields_comment["is_gen"]),
        StructField("block_timestamp", TimestampType(), True, fields_comment["block_timestamp"]),
        StructField("payload", StringType(), True, fields_comment["payload"]),
        StructField("last_block", IntegerType(), True, fields_comment["last_block"]),  
    ])

    fields_ignored_to_hash = ["dataCarga", "checksum", "data_carga"]

    def __init__(self, 
                 df, 
                 block_name,    
                 block_business_keys,             
                 fields_to_hash=[], 
                 fields_to_non_hash=[]):
        self.df = df
        self.block_name = block_name       
        self.block_business_keys = block_business_keys 
        self.fields_to_hash = fields_to_hash
        if len(self.fields_to_hash) == 0:            
            self.fields_to_hash = self.df.columns
        self.fields_to_non_hash = fields_to_non_hash + self.fields_ignored_to_hash
        self.df_block = None
    
    def hash(self):
        hash_fields = sorted(set(self.fields_to_hash) - set(self.fields_to_non_hash))
        return xxhash64(*hash_fields)
    
    def concat_business_keys(self):
        list_of_end_keys = []
        for i, key in enumerate(self.block_business_keys):        
            separator = [lit("|")] if i < len(self.block_business_keys)-1 else []                
            list_of_end_keys = list_of_end_keys + [col(key)] + separator
        return concat(*list_of_end_keys)

    def load(self):
        # load data to dataframe
        self.df_block = (self.df.select(
            lit(self.block_name).alias("block_name"),
            lit(0).alias("block_level"),
            self.concat_business_keys().alias("block_business_keys"),
            self.hash().alias("id_block_gen"),
            self.hash().alias("id_block"), 
            lit(None).alias("id_block_prev"), 
            lit(1).alias("is_gen"),             
            from_utc_timestamp(current_timestamp(), "America/Sao_Paulo").alias("block_timestamp"),     
            to_json(struct("*")).alias("payload"),
            lit(1).alias("last_block")
        ))
        return self
        
