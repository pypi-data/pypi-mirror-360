from dnalib.log import *
from enum import Enum

class SourceType(Enum):
    """ 
        Enum que define os métodos validos para origem de dados: TXT, CSV, PARQUET, KAFKA e EVENTHUB (WIP); SQLSERVER, ORACLE (implementados).
    """
    TXT = "txt"
    CSV = "csv"
    PARQUET = "parquet"    
    KAFKA = "kafka"
    EVENTHUB = "eventhub"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    FIREBASE = "firebase"

class LandingLoader(Enum):
    """ 
        Enum que define a forma como os dados serão carregados a partir da origem: 
        INCREMENTAL: considera que a origem é um arquivo incremental e define automaticamente que será feito um upsert.
        FULL: considera que a origem é um arquivo completo, e define automaticamente que será feito um overwrite.
        CDC: considera que a origem é um arquivo CDC (funciona somente para SourceType.SQLSERVER) e define automaticamente que será feito um upsert.
        STREAMING: WIP.
    """
    INCREMENTAL = "incremental" # read a single part, and merge data
    FULL = "full" # read all, then overwrite    
    CDC = "cdc" # only for cdc loader    
    STREAMING = "streaming" # for streaming purpose

class Loader:
    """
        A classe Loader é uma implementação de alto nível que define a carga de um arquivo da landing zone (todas ingestões batch são baseadas em arquivos
        seja csv, txt ou banco, que nesse último caso usa parquet).

        Args:
            source_path (str): caminho na landingzone de onde o arquivo será lido.
            table_name (str): string que representa o nome da tabela.          
            loader_type (LandingLoader): algum dos tipos válidos da LandingLoader.            
            name_filter (str, optional): utilizado caso seja necessário filtrar arquivos dentro de um mesmo diretório da landing.

        Attributes:
            source_path (str): caminho na landingzone de onde o arquivo será lido.
            table_name (str): string que representa o nome da tabela.    
            loader_type (LandingLoader): algum dos tipos válidos da LandingLoader.            
            name_filter (str, optional): utilizado caso seja necessário filtrar arquivos dentro de um mesmo diretório da landing.

    """
    def __init__(self, source_path, loader_type):
        self.source_path = source_path        
        self.loader_type = loader_type                
        self.df_loader = None

    def load_incremental(self):
        # TODO: implementar o load do tipo incremental. (deve retornar um DataFrame Spark)
        raise NotImplementedError("Method load_incremental() must be implemented.")

    def load_full(self):
        # TODO: implementar o load do tipo full. (deve retornar um DataFrame Spark)
        raise NotImplementedError("Method load_full() must be implemented.")

    def load_cdc(self):
        # TODO: implementar o load do tipo cdc. (deve retornar um DataFrame Spark)
        raise NotImplementedError("Method load_cdc() must be implemented.")    

    def load(self):
        if self.loader_type.value == LandingLoader.INCREMENTAL.value:
            self.df_loader = self.load_incremental()
        elif self.loader_type.value == LandingLoader.FULL.value:
            self.df_loader = self.load_full()
        elif self.loader_type.value == LandingLoader.CDC.value:
            self.df_loader = self.load_cdc()
        else:
            log(__name__).error(f"Invalid load type {self.loader_type}")
            raise ValueError(f"Invalid load type {self.loader_type}")
        log(__name__).info(f"Load of {self.loader_type.value} type completed successfully.")
        return self
