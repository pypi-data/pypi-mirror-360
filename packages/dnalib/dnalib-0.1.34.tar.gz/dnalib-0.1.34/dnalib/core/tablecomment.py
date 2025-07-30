from dnalib.utils import TableUtils, Utils
from dnalib.log import log

class TableComment:             
    """
        Classe construída para compilar o template do comentário da tabela, seguindo os critérios do catalogo do Atlan.

        Args:
            layer (str): camada da tabela no lake.   
            table_name (str): string que representa o nome da tabela.
            yml (yml object or str, optional): caminho do arquivo yml ou instância do objeto com os parâmetros necessários para o Create Table. Padrão é None.
            anonimized_fields (list, optional): lista de campos para serem anonimizados.
            comment (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.
            comment_squad (dict, optional): dicionário com o padrão table_comment_atlan_pattern.key:comment_squad (veja TableComment.table_comment_atlan_pattern). Se não for informado, será inferido a partir do yml.

        Attributes:
            table_comment_atlan_pattern (dict): dicionário com as chaves para o comentário da tabela, seguindo os critérios do catalogo do Atlan.
            yml (yml object ou None): instância do objeto yml, é None caso nenhum arquivo seja informado.
            layer (str): camada da tabela no lake.   
            table_name (str): string que representa o nome da tabela.
            anonimized_fields (list): lista de campos para serem anonimizados.
            comment (dict): dicionário com o padrão table_comment_atlan_pattern.key.
            comment_squad (dict): dicionário com o padrão table_comment_atlan_pattern.key.
            parsed_comment (str): string com o template do comentário da tabela compilado, preenchido após a chamada do método parse.
            comment_complete (dict): merge entre os dicionários comment e comment_squad, preenchido após a chamada do método parse.
            parsed_template (str): template do comentário da tabela compilado, preenchido após a chamada do método parse.
    """ 

    table_comment_keywords = {
        'descricao': '- **Descrição**:',
        'sistema_origem': '- **Sistema Origem**:',
        'calendario': '- **Calendário de Disponibilização**:',
        'tecnologia': '- **Tecnologia Sistema Origem**:',
        'camada': '- **Camada de Dados**:',
        'peridiocidade': '- **Periodicidade de Atualização**:',
        'retencao': '- **Período de Retenção**:',
        'vertical': '- **Vertical**:',
        'dominio': '- **Domínio**:',
        'squad': '- **Squad Responsável**:',
        'categoria_portosdm': '- **Categoria e Grupo PortoSDM**:',
        'confidencialidade': '- **Classificação da Confidencialidade**:',
        'classificacao': '- **Classificação**:',
        'campos_anonimizados': '- **Campos Anonimizados**:',
        'deprecated': '- **Deprecated**:'
    }

    table_squad_keywords = {
        'gi': '- **GI - Gestor da Informação**:',
        'gdn': '- **GDN - Gestor de Negócio**:',
        'curador': '- **Curador**:',
        'custodiante': '- **Custodiante**:',
    }

    table_comment_atlan_pattern =  {
        'descricao': '- **Descrição**:',
        'sistema_origem': '- **Sistema Origem**:',
        'calendario': '- **Calendário de Disponibilização**:',
        'tecnologia': '- **Tecnologia Sistema Origem**:',
        'camada': '- **Camada de Dados**:',
        'peridiocidade': '- **Periodicidade de Atualização**:',
        'retencao': '- **Período de Retenção**:',
        'vertical': '- **Vertical**:',
        'dominio': '- **Domínio**:',
        'gi': '- **GI - Gestor da Informação**:',
        'gdn': '- **GDN - Gestor de Negócio**:',
        'curador': '- **Curador**:',
        'custodiante': '- **Custodiante**:',
        'squad': '- **Squad Responsável**:',
        'categoria_portosdm': '- **Categoria e Grupo PortoSDM**:',
        'confidencialidade': '- **Classificação da Confidencialidade**:',
        'classificacao': '- **Classificação**:',
        'campos_anonimizados': '- **Campos Anonimizados**:',
        'deprecated': '- **Deprecated**:'
    }

    def __init__(self, 
                 layer, 
                 table_name, 
                 yml={}, 
                 anonimized_fields=[], 
                 comment={}, 
                 comment_squad={}):
        self.yml = yml
        # yml must be either a string or a dict from the yml file
        if isinstance(self.yml, str):
            self.yml = Utils.safe_load_and_parse_yml(yml)
        self.table_name = table_name.strip().lower()
        self.layer = layer.strip().lower()   
        self.anonimized_fields = self.yml.get("anonimized_fields", anonimized_fields)
        self.comment = self.yml.get("comment", comment)
        self.comment_squad = self.yml.get("comment_squad", comment_squad)
        self.parsed_comment = ""
        self.comment_complete = {}
        self.parsed_template = ""

    def parse_parameters_from_table_comment(self):
        """ 
            Método interno para tentar parsear a string do comentário da tabela.
        """
        parsed_str_comment = TableUtils.table_comment(self.layer, self.table_name)
        list_comment_pattern_clean = []

        # in this solution we consider that each keyword is separated by '\n'
        for table_content in parsed_str_comment.split('\n'):
            # remove empty string
            comment_patern_clean = table_content.strip()
            if comment_patern_clean != '':
                list_comment_pattern_clean.append(comment_patern_clean)

        comment = dict.fromkeys(self.table_comment_keywords.keys(), "")
        comment_squad = dict.fromkeys(self.table_squad_keywords.keys(), "")

        # for each keyword we try to find its definition in the list of the table comment
        for table_comment_key in self.table_comment_atlan_pattern:
            table_keyword = self.table_comment_atlan_pattern[table_comment_key]    
            for comment_patern_clean in list_comment_pattern_clean:                
                comment_idx = comment_patern_clean.find(":")+1        
                if table_keyword.upper() in comment_patern_clean.upper() and comment_idx < len(comment_patern_clean):    
                    if table_comment_key in comment:        
                        comment[table_comment_key] = comment_patern_clean[comment_idx:].strip()
                    else:
                        comment_squad[table_comment_key] = comment_patern_clean[comment_idx:].strip()  

        # try to load anonimized fields from the table comment
        str_anonimized_fields = comment["campos_anonimizados"]       
        list_anonimized_fields = str_anonimized_fields.replace(".", "").replace(" e ", ",").split(",")  
        anonimized_fields = [] 
        for anonimized_field in list_anonimized_fields:
            anonimized_field_clean = anonimized_field.strip()
            if anonimized_field_clean != '':
                anonimized_fields.append(anonimized_field_clean.lower())

        return comment, comment_squad, anonimized_fields

    def __load_and_verify_params(self):
        """
            Método interno que carrega as estruturas principais para popular os comentários da tabela.

            Raises:
                ValueError: Ocorre se alguma das estruturas comment ou comment_squad não forem informadas. Ou devem ser passadas por parâmetros, ou devem estar dentro do yml.
        """                
        if len(self.yml) == 0:
            (comment, comment_squad, anonimized_fields) = self.parse_parameters_from_table_comment()
            if len(self.comment) == 0:  
                self.comment = comment              
            if len(self.comment_squad) == 0:
                self.comment_squad = comment_squad
            if len(self.anonimized_fields) == 0:
                self.anonimized_fields = anonimized_fields
    
        # merge both dicts
        self.comment_complete = {**self.comment, **self.comment_squad}
        self.comment_complete["campos_anonimizados"] = ", ".join(self.anonimized_fields)
        # deprecated can be or not informed
        self.comment_complete["deprecated"] = self.comment_complete.get("deprecated", "")
    
    def parse(self): 
        """
            Método que faz o parse dos comentários baseados na estrutura do Atlan. Os valores estão no dicionário TableComment.table_comment_atlan_pattern.

            Returns:
                self: a instância da classe TableComment.

            Raises:
                ValueError: Se a estrutura do comentário não for informada corretamente (ou seja, se faltar alguma chave).
        """        
        self.__load_and_verify_params()         
        for key in self.table_comment_atlan_pattern:
            if not key in self.comment_complete:
                log(__name__).error(f"You must inform the parameter {key} in table comment.")
                raise ValueError(f"You must inform the parameter {key} in table comment.")
            else:                
                self.parsed_comment += f"{self.table_comment_atlan_pattern[key]} {TableUtils.format_comment_content(self.comment_complete[key])}\n"
        return self
    
    def template(self):             
        """
            Método que constroí o template da estrutura do comentário da tabela baseado nos parâmetros informados.

            .. code-block:: SQL

                COMMENT ON TABLE layer.table_name IS "comentário compilado"
            
            Returns:
                self: a instância da classe TableComment.
        """   

        self.parse()    
        self.parsed_template = """
            COMMENT ON TABLE {}.{} IS "{}"
        """.format(self.layer, self.table_name, self.parsed_comment)           

        return self             

    def execute(self):        
        """
            Método que executa todo processo para gerar e escrever o comentário da tabela.              
            
            Returns:                
                self: a instância da classe TableComment.

            Raises:
                Exception: Se a tabela informada não existir.
        """

        # verify if table exists
        if not TableUtils.table_exists(self.layer, self.table_name):
            log(__name__).error(f"Table {self.layer}.{self.table_name} does not exist")
            raise Exception(f"Table {self.layer}.{self.table_name} does not exist")

        # generate final template
        self.template()

        # run comment on table
        Utils.spark_instance().sql(self.parsed_template)        
        return self
