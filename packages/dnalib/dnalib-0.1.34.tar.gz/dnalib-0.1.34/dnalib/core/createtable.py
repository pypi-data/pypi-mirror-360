from pyspark.sql import SparkSession
from dnalib.utils import TableUtils, Utils
from dnalib.log import log
from .tablecomment import TableComment

class CreateTable:
    """
        Classe de alto nível para o create table. Define o método abstrato de parser para as fields. Não deve ser alocada.

        Args:      
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            yml (yml object, string or {}): caminho do arquivo yml ou instância do objeto com os parâmetros necessários para o Create Table. Padrão é {}.
            partition_fields (list, optional): lista de campos utilizados como partição da tabela.      
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            replace (bool, optional): opção que força o replace da tabela caso ela exista. Por padrão é False.

        Attributes:
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            table_path (str): caminho da tabela no lakehouse.
            yml (yml object ou {}): instância do objeto yml, é {} caso nenhum arquivo seja informado.
            partition_fields (list): lista de campos utilizados como partição da tabela.            
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            replace (bool): opção que força o replace da tabela caso ela exista. Por padrão é False.
            has_created_table (bool): parâmetro de controle interno, se True indica que a tabela foi criada ou substituída após a chamada do método execute.
            parsed_template (str): template da criação da tabela compilado, preenchido após a chamada do método template.
    """

    def __init__(self, 
                 schema,  
                 table_name, 
                 yml={},                  
                 partition_fields=[],
                 tbl_properties={},
                 replace=False):        
        self.table_name = table_name.strip().lower()
        self.schema = schema
        self.table_path = Utils.lakehouse_path(self.layer, self.table_name) 
        self.yml = yml
        if isinstance(self.yml, str):
            self.yml = Utils.safe_load_and_parse_yml(yml)
        self.partition_fields = self.yml.get("partition_fields", partition_fields)
        self.tbl_properties = self.yml.get("tbl_properties", tbl_properties)
        self.replace = replace         
        self.has_created_table = False         
        self.parsed_template = ""

    def parse_fields(self):
        """
            Método abstrato para ser implementado, faz o trabalho de parsear as fields para gerar o template do Create Table.
        """
        return NotImplementedError("Method parse_fields must be implemented")
    
    def template(self):        
        """
            Método que gera o template do Create Table e injeta no objeto self.parsed_template.
            
            .. code-block:: SQL

                CREATE OR REPLACE TABLE layer.table (
                    field_name field_type COMMENT '' nullable or not,
                    ...
                )
                USING DELTA
                TBLPROPERTIES (tbl_properties)
                PARTITIONED BY (partition_fields)

           Returns:
                self: a instância da classe CreateTable.
        """        
        # parse fields to string
        self.parse_fields()        
        # parse table partition_fields to a string
        partition_fields = ""
        if len(self.partition_fields) > 0:
            partition_fields = ", ".join(self.partition_fields)
            partition_fields = f"PARTITIONED BY ({partition_fields})"
        # tbl properties
        tbl_properties = ""
        if len(self.tbl_properties) > 0:
            parsed_tbl_properties = ", ".join([f"{key}='{value}'" for key, value in self.tbl_properties.items()])
            tbl_properties = f"TBLPROPERTIES ({parsed_tbl_properties})"
        # generate template for create table
        self.parsed_template = """
            CREATE OR REPLACE TABLE {}.{} (
                {}
            )
            USING delta
            {}
            {}
            LOCATION '{}'
        """.format(self.layer, self.table_name, self.parsed_fields, tbl_properties, partition_fields, self.table_path)
        return self    

    def execute(self):  
        """
            Método que executa o create table com base no template gerado. Caso a tabela já exista, não é executado nada a não ser que o parâmetro replace=True.

            Returns:
                self: a instância da classe CreateTable.
        """        
        if not TableUtils.table_exists(self.layer, self.table_name) or self.replace:                 
            ## generate final create table template
            self.template() 
            Utils.spark_instance().sql(self.parsed_template)                                            
            # mark table has been created or replaced by class
            self.has_created_table = True    
        else:
            log(__name__).warning(f"The table already exists, so nothing will be done.")
        return self

class CreateTableBronze(CreateTable):
    """
        Classe que implementa o create table para a camada bronze, é o processo mais simples de todos.

        Args:      
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            yml (yml object, string or {}): caminho do arquivo yml ou instância do objeto com os parâmetros necessários para o Create Table. Padrão é {}.
            partition_fields (list): lista de campos utilizados como partição da tabela.
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            replace (bool): opção que força o replace da tabela caso ela exista. Por padrão é False.
    """

    layer = "bronze"

    def __init__(self, schema, table_name, yml={}, partition_fields=[], tbl_properties={}, replace=False):        
        super().__init__(schema, table_name, yml, partition_fields, tbl_properties, replace)
    
    def __load_and_verify_params(self):
        if not "dataCarga" in self.schema.names:
            log(__name__).error("Any bronze table must have a dataCarga field.")
            raise Exception("Any bronze table must have a dataCarga field.")

    def parse_fields(self): 
        """
            Método que faz o parse dos campos para o create table na bronze. O método faz a leitura de cada field e gera o seguinte padrão:
            
             .. code-block:: SQL

                field_name field_type nullable or not           
            
            Returns:
                self: a instância da classe CreateTable.
        """
        self.__load_and_verify_params()      
        list_of_parsed_fields = ["{} {}{}".format(field.name, field.dataType.simpleString(), " NOT NULL" if not field.nullable else "") for field in self.schema]
        self.parsed_fields = ", ".join(list_of_parsed_fields)
        return self
    
class CreateTableSilver(CreateTable):
    """
        Classe que implementa um create table para a camada silver, baseado nos padrões do catalogo de dados do Atlan.
        
        Args:
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            yml (yml object, string or {}): caminho do arquivo yml ou instância do objeto com os parâmetros necessários para o Create Table. Padrão é {}.
            partition_fields (list): lista de campos utilizados como partição da tabela.      
            anonimized_fields (list, optional): lista de campos para serem anonimizados.
            comment (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            comment_squad (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment_squad (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            fields (dict, optional): dicionário com o padrão field_name:comment. Se não for informado, será inferido a partir do yml.
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            replace (bool, optional): opção que força o replace da tabela caso ela exista. Por padrão é False.

        Attributes:
            layer (str): constante com o valor "silver".
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            table_path (str): caminho da tabela no lakehouse.
            yml (yml object ou {}): instância do objeto yml, é {} caso nenhum arquivo seja informado.
            partition_fields (list): lista de campos utilizados como partição da tabela.            
            replace (bool): opção que força o replace da tabela caso ela exista. Por padrão é False.
            has_created_table (bool): parâmetro de controle interno, se True indica que a tabela foi criada ou substituída após a chamada do método execute.
            template (str): template da criação da tabela compilado, preenchido após a chamada do método template().
            fields (dict): dicionário com o padrão field_name:comment. 
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            tbl_comment (TableComment): instância da classe TableComment para gerar o comentário da tabela.
            parsed_fields (str): string com os comentários das fields parseados no padrão do create table, preenchido após a chamada do método parse_fields().
    """

    layer = "silver"
    
    def __init__(self, 
                 schema, 
                 table_name, 
                 yml={}, 
                 partition_fields=[],
                 anonimized_fields=[], 
                 comment={}, 
                 comment_squad={}, 
                 fields={},
                 tbl_properties={},
                 replace=False):        
        super().__init__(schema, table_name, yml, partition_fields, tbl_properties, replace)
        self.fields = self.yml.get("fields", fields)
        self.field_comments = {}
        self.tbl_comment = TableComment(self.layer, self.table_name, self.yml, anonimized_fields, comment, comment_squad)
        self.parsed_fields = ""

    def __load_and_verify_params(self):
        """
            Método interno que executa a verificação dos parâmetros necessários para o create table ser executado.

            Raises:
                ValueError: Caso os parâmetro fields não seja informado; Se nem os campos do dicionário fields possuem um comentário; Se a tabela não tem o campo dataCarga.
        """     
        # comments are required in silver layer
        if len(self.fields) == 0:            
            log(__name__).error(f"If not informed, the fields parameter is required in yml table template for {self.layer} layer.")
            raise ValueError(f"If not informed, the fields parameter is required in yml table template for {self.layer} layer.")                          

        # we manually insert dataCarga to the object (if it is passed it will be generated in comments)
        if not "dataCarga" in self.schema.names:
            log(__name__).error("Any silver table must have a dataCarga field.")
            raise ValueError("Any silver table must have a dataCarga field.")
        else:            
            self.fields["dataCarga"] = ["Data de carga dos dados."]

        # verify if checksum is added to the silver table
        if "checksum" in self.schema.names:            
            self.fields["checksum"] = ["CheckSum/Hash das informações do registro (linha)."]

        # populate comments structure
        for field_name, field_params in self.fields.items():                                    
            self.field_comments[field_name] = field_params[0]

    def parse_fields(self): 
        """
            Método que faz o parse dos campos para o create table na silver. O método faz a leitura de cada field e gera o seguinte padrão:
            
             .. code-block:: SQL
            
                field_name field_type COMMENT 'field_comment' nullable or not         
            
            Returns:
                self: a instância da classe CreateTable.
        """     
        self.__load_and_verify_params()
        list_of_parsed_fields = ["{} {} COMMENT '{}'{}".format(field.name, 
                                                                field.dataType.simpleString(), 
                                                                TableUtils.format_comment_content(self.field_comments[field.name]), 
                                                                " NOT NULL" if not field.nullable else "") for field in self.schema]
        self.parsed_fields = ", ".join(list_of_parsed_fields)
        return self
        
    def execute(self):    
        """
            Método que executa o create table na camada silver e faz a chamada do comment on table, respectivamente. O comentário é gerado novamente, caso a tabela seja criada ou recriada.

            Returns:
                self: a instância da classe CreateTable.
        """      
        super().execute()
        # it forces comment on table when table is recreated
        if self.has_created_table:
            self.tbl_comment.execute()
        return self
    
class CreateTableGold(CreateTableSilver):
    """
        Classe que implementa um create table para a camada gold, baseado nos padrões do catalogo de dados do Atlan.
        
        Args:
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            yml (yml object, string or {}): caminho do arquivo yml ou instância do objeto com os parâmetros necessários para o Create Table. Padrão é {}.
            partition_fields (list): lista de campos utilizados como partição da tabela.      
            anonimized_fields (list, optional): lista de campos para serem anonimizados.
            comment (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            comment_squad (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment_squad (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            fields (dict, optional): dicionário com o padrão field_name:comment. Se não for informado, será inferido a partir do yml.
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            replace (bool, optional): opção que força o replace da tabela caso ela exista. Por padrão é False.

        Attributes:
            layer (str): constante com o valor "gold".
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            table_path (str): caminho da tabela no lakehouse.
            yml (yml object ou {}): instância do objeto yml, é {} caso nenhum arquivo seja informado.
            partition_fields (list): lista de campos utilizados como partição da tabela.            
            replace (bool): opção que força o replace da tabela caso ela exista. Por padrão é False.
            has_created_table (bool): parâmetro de controle interno, se True indica que a tabela foi criada ou substituída após a chamada do método execute.
            template (str): template da criação da tabela compilado, preenchido após a chamada do método template().
            fields (dict): dicionário com o padrão field_name:comment. 
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            tbl_comment (TableComment): instância da classe TableComment para gerar o comentário da tabela.
            parsed_fields (str): string com os comentários das fields parseados no padão do create table, preenchido após a chamada do método parse_fields().
    """

    layer = "gold"

    def __init__(self, 
                 schema, 
                 table_name, 
                 yml={}, 
                 partition_fields=[],
                 anonimized_fields=[], 
                 comment={}, 
                 comment_squad={}, 
                 fields={},
                 tbl_properties={},
                 replace=False):  
        super().__init__(schema, table_name, yml, partition_fields, anonimized_fields, comment, comment_squad, fields, tbl_properties, replace)

class CreateTableDiamond(CreateTableSilver):
    """
        Classe que implementa um create table para a camada diamond, baseado nos padrões do catalogo de dados do Atlan.
        
        Args:
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            yml (yml object, string or {}): caminho do arquivo yml ou instância do objeto com os parâmetros necessários para o Create Table. Padrão é {}.
            partition_fields (list): lista de campos utilizados como partição da tabela.      
            anonimized_fields (list, optional): lista de campos para serem anonimizados.
            comment (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            comment_squad (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment_squad (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            fields (dict, optional): dicionário com o padrão field_name:comment. Se não for informado, será inferido a partir do yml.
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            replace (bool, optional): opção que força o replace da tabela caso ela exista. Por padrão é False.

        Attributes:
            layer (str): constante com o valor "diamond".
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            table_path (str): caminho da tabela no lakehouse.
            yml (yml object ou {}): instância do objeto yml, é {} caso nenhum arquivo seja informado.
            partition_fields (list): lista de campos utilizados como partição da tabela.            
            replace (bool): opção que força o replace da tabela caso ela exista. Por padrão é False.
            has_created_table (bool): parâmetro de controle interno, se True indica que a tabela foi criada ou substituída após a chamada do método execute.
            template (str): template da criação da tabela compilado, preenchido após a chamada do método template().
            fields (dict): dicionário com o padrão field_name:comment. 
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            tbl_comment (TableComment): instância da classe TableComment para gerar o comentário da tabela.
            parsed_fields (str): string com os comentários das fields parseados no padão do create table, preenchido após a chamada do método parse_fields().
    """

    layer = "diamond"

    def __init__(self, 
                 schema, 
                 table_name, 
                 yml={}, 
                 partition_fields=[],
                 anonimized_fields=[], 
                 comment={}, 
                 comment_squad={}, 
                 fields={},
                 replace=False):  
        super().__init__(schema, table_name, yml, partition_fields, anonimized_fields, comment, comment_squad, fields, tbl_properties, replace)

class CreateTableExport(CreateTableSilver):
    """
        Classe que implementa um create table para a camada export, baseado nos padrões do catalogo de dados do Atlan.
        
        Args:
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            yml (yml object, string or {}): caminho do arquivo yml ou instância do objeto com os parâmetros necessários para o Create Table. Padrão é {}.
            partition_fields (list): lista de campos utilizados como partição da tabela.      
            anonimized_fields (list, optional): lista de campos para serem anonimizados.
            comment (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            comment_squad (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment_squad (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            fields (dict, optional): dicionário com o padrão field_name:comment. Se não for informado, será inferido a partir do yml.
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            replace (bool, optional): opção que força o replace da tabela caso ela exista. Por padrão é False.

        Attributes:
            layer (str): constante com o valor "export".
            schema (df.schema): schema do dataframe, mesmo que df.schema.
            table_name (str): string que representa o nome da tabela.
            table_path (str): caminho da tabela no lakehouse.
            yml (yml object ou {}}): instância do objeto yml, é {} caso nenhum arquivo seja informado.
            partition_fields (list): lista de campos utilizados como partição da tabela.            
            replace (bool): opção que força o replace da tabela caso ela exista. Por padrão é False.
            has_created_table (bool): parâmetro de controle interno, se True indica que a tabela foi criada ou substituída após a chamada do método execute.
            template (str): template da criação da tabela compilado, preenchido após a chamada do método template().
            fields (dict): dicionário com o padrão field_name:comment. 
            tbl_properties (dict, optional): dicionário com a definição chave e valor de propriedades da tabela. Padrão é {}.
            tbl_comment (TableComment): instância da classe TableComment para gerar o comentário da tabela.
            parsed_fields (str): string com os comentários das fields parseados no padão do create table, preenchido após a chamada do método parse_fields().
    """

    layer = "export"

    def __init__(self, 
                 schema, 
                 table_name, 
                 yml={}, 
                 partition_fields=[],
                 anonimized_fields=[], 
                 comment={}, 
                 comment_squad={}, 
                 fields={},
                 replace=False):  
        super().__init__(schema, table_name, yml, partition_fields, anonimized_fields, comment, comment_squad, fields, tbl_properties, replace)
