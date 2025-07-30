from dnalib.core import CreateTableSilver, TableComment, CreateView
from dnalib.utils import TableUtils, Utils
from dnalib.writer import WriteModes
from dnalib.log import log
from .tables import ProcessLayerTable
from pyspark.sql.functions import col
from enum import Enum

class SilverLoaderType(Enum):
    INCREMENTAL = "incremental" # read data from dataCarga
    FULL = "full" # read all    
    STREAMING = "streaming" # for streaming purpose

class SilverTable(ProcessLayerTable):
    """ 
        A classe SilverTable é uma implementação especializada da classe ProcessLayerTable que implementa todo o pipeline commons que seguimos em uma tabela da silver. Nela é possível carregar o dado da bronze, formatar, fazer cast, criar a tabela e persistir o dado com poucas linhas de código.

        Args:
            table_name (str): string que representa o nome da tabela.
            yml (yml object or str): caminho do arquivo yml ou instância do objeto com os parâmetros necessários.
            source_df (spark Dataframe): dataframe do spark onde os dados serão consumidos para compor o target_df.      
            include_checksum (bool): se verdadeiro adiciona o campo de checksum no target_df.     
            loader_type (SilverLoaderType): tipo de carregamento, se é incremental ou full.

        Attributes:
            layer (str): constante com o valor "silver".
            dict_of_fields (dict): estrutura que armazena as chamadas do método field(), utilizado para garantir que o processo seja lazy (como o spark).
    """

    layer = "silver"

    def __init__(self, source_table_name, yml, target_table_name=None, source_df=None, include_checksum=False, loader_type=SilverLoaderType.INCREMENTAL):
        if target_table_name is None:
            self.target_table_name = source_table_name
        else:
            self.target_table_name = target_table_name
        super().__init__(self.layer, self.target_table_name, source_df, include_checksum)    
        self.source_table_name = source_table_name
        self.yml = yml
        if isinstance(self.yml, str):
            self.yml = Utils.safe_load_and_parse_yml(yml)
        self.loader_type = loader_type
        self.source_df_query = self.yml.get("source_df_query", "")
        self.fields = self.yml.get("fields", {})
        self.dict_of_fields = {}     
        self.create_tbl = None
        self.create_vw = None                
        self.__populate_fields()

    def __populate_fields(self):
        # verify if the yml file has the fields parameter
        if len(self.fields) == 0:
            log(__name__).error("The parameter fields is required in the yml file")
            raise ValueError("The parameter fields is required in the yml file")        
        for field_name, field_params in self.fields.items():                        
            self.field(field_name, *field_params[1:]) 
        return self

    def parse_df_source(self):
        """
            Método que executa o carregamento de dados da camada bronze para a silver, o método é baseado no campo de dataCarga. Se a tabela não existir, os dados são carregados de maneira full,
            caso contrário os dados são carregados somente com os registros que foram atualizados.

            Returns:
                source_df (spark DataFrame): dataframe carregado a partir da camada source, caso source_df seja None.

            Raises:
                ValueError: caso a tabela bronze não exista.
        """         
        # verify if table exists in bronze layer
        if not TableUtils.table_exists("bronze", self.source_table_name):
            log(__name__).error(f"Table bronze.{self.source_table_name} does not exists")
            raise ValueError(f"Table bronze.{self.source_table_name} does not exists")        

        # this loads the "center" of the query
        if self.source_df_query == "":
            parsed_fields = ", ".join(self.dict_of_fields.keys())
            self.source_df_query = f"""
                SELECT      
                    {parsed_fields}               
                FROM bronze.{self.source_table_name}
            """
            
        # transform strategy in this case is to check if the table exists and the loader is incremental
        if TableUtils.table_exists(self.layer, self.table_name) and self.loader_type.value == SilverLoaderType.INCREMENTAL.value:
            # verify if it already has a where condition
            has_where = self.source_df_query.upper().find("WHERE")            
            # we will transform based on the last loaded dataCarga
            self.source_df_query += """ {} dataCarga > (SELECT COALESCE(MAX(dataCarga), '1700-01-01') FROM silver.{})
            """.format("AND" if has_where != -1 else "WHERE", self.table_name)           

        return Utils.spark_instance().sql(self.source_df_query)

    def load_fields_from_source(self):
        """
            Método interno que executa o processo de formatar, fazer cast e renomear as fields que serão levadas da bronze para a silver.

            Returns:
                target_fields (list): lista com as fields tratadas que serão consumidas da camada bronze para a silver.
        """        
        source_schema = self.source_df.schema
        target_fields = []
        for source_field_name, target_field_type, target_field_name, format_field in self.dict_of_fields.values():
            field = col(source_field_name)
            # automatic format field 
            formated_field = self.format_field(field, source_schema[source_field_name].dataType.simpleString(), target_field_type, format_field)
            # cast to field type        
            cast_field = self.cast_field(formated_field, target_field_type)
            # final field
            final_field = self.rename_field(cast_field, source_field_name, target_field_name)
            # append final fields
            target_fields.append(final_field)

        # return fields from source        
        return target_fields

    def create_table(self):     
        """
            Esse método é um wrapper para o método CreateTableSilver.execute() e CreateView.execute(). Ele cria a tabela e a view para a camada silver. Deve ser chamado após o load(), caso contrário o último será chamado internamente.

            Returns:
                self: a instância da classe SilverTable.
        """       
        if not self.has_loaded:
            self.load()
            log(__name__).warning(f"The load() method will be called internally because you call create_table first.")        
        self.create_tbl = CreateTableSilver(self.target_df.schema, self.table_name, self.yml).execute()           
        self.create_vw = CreateView(self.layer, self.table_name, self.create_tbl.yml, self.create_tbl.tbl_comment).execute()                
        return self    

    def field(self, source_field_name, field_type=None, target_field_name=None, format_field=True):
        """            
            Método que adiciona de maneira *lazy* as fields que serão consumidas da bronze para a silver.

            Args:
                source_field_name (str): string que representa o nome da field que será consumida da bronze.                
                field_type (str): string que representa o tipo da field que será casteada e formatada para a silver.                
                target_field_name (str): string que representa o nome da field que será adicionada na silver.
                format_field (bool): se verdadeiro formata a field para o tipo especificado.

            Returns:
                self: a instância da classe SilverTable.
        """
        self.dict_of_fields[source_field_name] = (source_field_name, field_type, None, format_field)
        #self.dict_of_fields[source_field_name] = (source_field_name, field_type, target_field_name, format_field)
        return self    

