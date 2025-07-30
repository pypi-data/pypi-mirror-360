from pyspark.sql.functions import from_utc_timestamp, current_timestamp, col, upper, trim, regexp_replace, to_date, when, date_format, lit, coalesce, xxhash64, expr
from dnalib.writer import WriteModes, BatchTableWriter
from dnalib.utils import Utils
from dnalib.log import log

class LayerTable:    
    """ 
        A classe LayerTable é uma implementação de alto nível de uma tabela baseado na arquitetura que seguimos. Deve ser usada como base para implementar tabelas específicas (silver, gold, diamond e etc). A ideia geral é sempre carregar de um dataframe source (camada de entrada) para um target (camada de saída).
    
        Args:
            layer (str): parâmetro que indica a layer de destino onde o target_df será persistido.
            table_name (str): string que representa o nome da tabela.            
            source_df (spark Dataframe, optional): dataframe do spark onde os dados serão consumidos para compor o target_df. 
            include_checksum (bool, optional): se verdadeiro adiciona o campo de checksum no target_df.                  

        Attributes:
            table_name (str): string que representa o nome da tabela.    
            source_df (spark Dataframe): dataframe do spark onde os dados serão consumidos para compor o target_df.                    
            include_checksum (bool): se verdadeiro adiciona o campo de checksum no target_df.     
            writer (BatchTableWriter): intância interna do BatchTableWriter para persistir o dataframe target_df.
            target_df (spark Dataframe): dataframe para onde os dados consumidos de source_df serão materializados. Deve ser populado pela implementação.
            has_add_checksum (bool): parâmetro interno para controle de se o dataframe target_df foi adicionado o parâmetro de checksum.
            has_add_data_carga (bool): parâmetro interno para controle de se o dataframe target_df foi adicionado o parâmetro de dataCarga.
            parsed_source_df_query (str): resultado do método parse_df_source_query() populado após a chamada do load_source_df_data().
            has_loaded (bool): parâmetro interno para controle de se o método load() foi chamado.
    """

    def __init__(self, layer, table_name, source_df=None, include_checksum=False):                
        """ Construtor da classe """
        self.table_name = table_name
        self.source_df = source_df 
        self.include_checksum = include_checksum
        self.writer = BatchTableWriter(layer, self.table_name)
        self.target_df = None      
        self.has_add_checksum = False  
        self.has_add_data_carga = False        
        self.has_loaded = False                   

    def parse_df_source(self):
        """
            Método abstrato para ser implementado. Deve retornar um dataframe que representa os dados da camada de entrada. 

            Returns:
                source_df (spark Dataframe): dataframe do spark onde os dados serão consumidos para compor o target_df.      
        """
        raise NotImplementedError("This method must be implemented")

    def load_fields_from_source(self):
        """
            Método abstrato para ser implementado. Deve retornar uma lista de fields que será populada no target_df. 

            Returns:
                list_of_fields (list): lista com as fields para gerar o dataframe target_df a partir do source_df.
        """
        raise NotImplementedError("This method must be implemented")

    def load_source_df_data(self):
        """
            Método que faz a chamada do parser do dataframe gerando o dataframe de entrada (source_df). O source_df é preenchido nesse processo. Internamente usa a implementação do parse_df_source().
        """
        # assert that the dataframe is not None
        if self.source_df is None:                      
            self.source_df = self.parse_df_source()  

    def load_target_df_data(self): 
        """
            Método que carrega as fields a partir do dataframe source. Internamente usa a implementação de load_fields_from_source().
        """       
        # get fields from source
        self.target_df = self.source_df.select(self.load_fields_from_source())

    def add_checksum(self):       
        """ 
            Método que adiciona ao final do dataframe o parâmetro de checksum no dataframe target_df usando a função xxhash64. Por default só é possível usar campos primitivos para gerar o hash (string, int, float e etc). 
        """         
        columns = self.target_df.columns
        # it prevents to add checksum with dataCarga parameter   
        if "dataCarga" in columns:         
            columns.remove("dataCarga")        
        # It appends checkum as the last parameter
        self.target_df = self.target_df.select("*", xxhash64(*columns).alias("checksum"))
        # boolean parameter to internal control
        self.has_add_checksum = True  
    
    def add_data_carga(self):
        """ 
            Método que adiciona a dataCarga no começo do dataframe, isso garante que o parâmetro de dataCarga pode ser usado no z-order. 
        """
        # It guarantees that dataCarga is the first parameter
        self.target_df = self.target_df.select(from_utc_timestamp(current_timestamp(), "America/Sao_Paulo").alias("dataCarga"), "*")
        # boolean parameter to internal control
        self.has_add_data_carga = True  

    def load(self):        
        """
            Método que executa os steps pra carregar o dataframe que representa os dados para o target_df. Primeiro são carregados os dados do source para o target (usando a estratégia implementada no método load_source_df_data()). Em seguida, executa as tratativas dos campos que são levados de uma camada para a outra. Finalmente, os campos de checksum (se include_checksum=True) e dataCarga são adicionados.

            Returns:
                self: a instância da classe LayerTable.
        """
        # load inicial dataframe
        self.load_source_df_data()

        # load fields from source layer
        self.load_target_df_data()

        # add checksum column at the target dataframe
        if self.include_checksum:
            self.add_checksum()

        # automatic append dataCarga
        self.add_data_carga()

        # mark method as loaded
        self.has_loaded = True        
        log(__name__).info(f"Sucessfully loaded {self.target_df.count()} rows.") 
        return self

    def persist(self, mode=WriteModes.OVERWRITE, partition_fields=[], optimize=True, source_df_name="source", update_df_name="update", merge_condition=None):             
        """ 
            Método wrapper do BatchTableWriter.persist, automaticamente detecta se no dataframe foi adicionado o checksum e preeenche o campo has_checksum_field. 
        """
        self.writer.persist(self.target_df, mode=mode, partition_fields=partition_fields, optimize=optimize, merge_condition=merge_condition, has_checksum_field=self.has_add_checksum)      
        return self  


class ProcessLayerTable(LayerTable):
    """ 
        A classe ProcessLayerTable é uma implementação mais especializada da classe Table que implementa métodos para tratativa de campos (renonemar, formatar, fazer cast, etc).

        Args:
            layer (str): parâmetro que indica a layer de destino onde o target_df será persistido (passado para a classe pai internamente).
            table_name (str): string que representa o nome da tabela.            
            source_df (spark Dataframe, optional): dataframe do spark onde os dados serão consumidos para compor o target_df.    
            include_checksum (bool, optional): se verdadeiro adiciona o campo de checksum no target_df.         

        Attributes:
            real_types (list): lista de tipos reais válidos para cast.            
            valid_date_formats (list): lista de formatos válidos de converção inferida de datas.
    """

    real_types = ["float", "decimal", "double", "real"]
    valid_date_formats = ['M/d/yyyy', 'yyyy/M/d', 'd-M-yyyy', 'yyyy-M-d', 'yyyyMMdd', 'ddMMyyyy'] 

    def __init__(self, layer, table_name, source_df=None, include_checksum=False):
        """ Construtor da classe """
        super().__init__(layer, table_name, source_df, include_checksum)    
    
    def format_field(self, field, source_field_type, target_field_type, format_field):
        """
            Método que formata campos strings para tipos primitivos (string para float, decimal, double, real e date)

                .. code-block:: portugol
                    se format_field é verdadeiro:
                        se source é uma string então:
                            remova espaços e deixa o conteúdo do texto em maiúsculo.
                            se cast para float, decimal, real ou double então:
                                remove caracteres especiais (ex: R$:123.56 vai ser formatado para 123.56 antes do cast)
                            se cast para date:
                                tenta converter para qualquer um dos formatos de data válidos (M/d/yyyy, yyyy/M/d, d-M-yyyy, yyyy-M-d, yyyyMMdd, ddMMyyyy)
                    se format_field é string:
                        aplica a função expr para formatar o campo.

            Args:
                field (col): campo a ser formatado, um col para spark
                source_field_type (str): tipo do campo na camada de origem (ex: bronze)               
                target_field_type (str): tipo do campo na camada de destino (ex: silver, vai ser forçado cast após a formatação)
                format_field (bool or str): se True, indica que o campo deve ser formatado de acordo com seu tipo na camada de destino. Se str é executado via função expr.

            Returns:
                formated_field (col): campo formatado.
        """
        formated_field = field
        if format_field:
            # formata o campo usando a função expr do spark
            if isinstance(format_field, str):
                formated_field = expr(format_field)
            else:
                # format string fields from source         
                if source_field_type.lower() == "string":
                    formated_field = upper(trim(formated_field))                    

                    # format real types before cast
                    if target_field_type != None:
                        if any(real in target_field_type.lower() for real in self.real_types):
                            # remove non valid characters before cast
                            formated_field = regexp_replace(formated_field, '[^\d.,+-]?', '')

                        # try to infer date
                        if target_field_type.lower() == "date":             
                            list_of_formated_fields = [to_date(formated_field, date_to_format) for date_to_format in self.valid_date_formats]
                            formated_field = coalesce(*list_of_formated_fields)                                                  

        return formated_field      

    def rename_field(self, field, source_field_name, target_field_name=None):  
        """
            Esse método implementa um rename de maneira "safe", isto é, caso o campo tenha feito algum processamento anterior, garante que o nome seja mantido.

            Args:
                field (col): o campo que deve ser renomeado.
                source_field_name (str): string com o nome do campo na camada de origem.
                target_field_name (str or None): string com o nome do campo na camada de destino.
            
            Returns:
                field (col): o campo renomeado
        """      
        if target_field_name != None:
            return field.alias(target_field_name)
        else:
            return field.alias(source_field_name)
        
    def cast_field(self, field, field_type=None):      
        """
            Método que faz o cast de um campo para o tipo informado.

            Args:                
                field (col): o campo que deve ser formatado.                
                field_type (str): string com o tipo do campo (qualquer um da documentação [https://spark.apache.org/docs/latest/sql-ref-datatypes.html]).            
            Returns:                
                field (col): o campo após o cast.
        """  
        if field_type != None:
            return field.cast(field_type)
        else: 
            return field

