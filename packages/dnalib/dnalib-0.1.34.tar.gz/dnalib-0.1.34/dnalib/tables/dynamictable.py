from itertools import combinations
from functools import partial
from dnalib.utils import Utils
from .querytable import QueryTable

###########################################
###### methods by reflection #############
###########################################

class DynamicTable(QueryTable):

    """
        Classe de alto nível para implementar o design pattern reflection baseado nas tabelas do spark. Os métodos são criados dinamicamente a partir das colunas da tabela o que permite uma escrita mais amigável na hora de consultar as tabelas. Basicamente para cada coluna são criados diversos métodos que fazem tarefas simples para filtragem de dados.

        Baseado em: https://stackoverflow.com/questions/29642822/find-name-of-dynamic-method-in-python
        
    """
    def __init__(self, layer, table_name, table_fields=[], select_fields=[], except_fields=[], json_fields=[], query_view_name="view_query_table"):
        """
        """
        super().__init__(query_view_name)
        self.layer = layer
        self.table_name = table_name
        self.source_table = f"{layer}.{table_name}"                
        self.table_fields = table_fields        
        if len(self.table_fields) == 0:
            self.table_fields = Utils.spark_instance().table(self.source_table).columns                
        self.select_fields = select_fields        
        if len(select_fields) == 0:
            self.select_fields = self.table_fields        
        self.except_fields = except_fields        
        self.json_fields = json_fields        
        # campos que serão selecionados
        self.fields = ", ". join([field for field in self.select_fields if field not in self.json_fields])
        # cada combinação vai ser usada para fazer regra "and" e "or" para dois parâmetros
        self.table_fields_combinations = list(combinations(set(self.table_fields)-set(self.json_fields), 2))
        # cria os métodos baseados nas colunas da tabela
        self.reflect()

    def _generate_find_by_first_or_second_parameter(self):
        """
            find_by_{first_field}_or_{second_field}(first_value, second_value)
            find_by_{second_field}_or_{first_field}(second_value, first_value)
        """
        for first_field, second_field in self.table_fields_combinations:                                    
            func = partial(self._find_by_first_or_second_parameter, fields=self.fields, source_table=self.source_table, first_field=first_field, second_field=second_field)
            setattr(self, f"find_by_{first_field.lower()}_or_{second_field.lower()}", func)
            func = partial(self._find_by_first_or_second_parameter, fields=self.fields, source_table=self.source_table, first_field=second_field, second_field=first_field)
            setattr(self, f"find_by_{second_field.lower()}_or_{first_field.lower()}", func)

    def _generate_find_by_first_and_second_parameter(self):
        """
            find_by_{first_field}_and_{second_field}(first_value, second_value)
            find_by_{second_field}_and_{first_field}(second_value, first_value)
        """
        for first_field, second_field in self.table_fields_combinations:                                    
            func = partial(self._find_by_first_and_second_parameter, fields=self.fields, source_table=self.source_table, first_field=first_field, second_field=second_field)
            setattr(self, f"find_by_{first_field.lower()}_and_{second_field.lower()}", func)
            func = partial(self._find_by_first_and_second_parameter, fields=self.fields, source_table=self.source_table, first_field=second_field, second_field=first_field)
            setattr(self, f"find_by_{second_field.lower()}_and_{first_field.lower()}", func)

    def _generate_find_by_single_parameter(self):    
        """
            find_by_{field}(value)
        """
        for field in self.table_fields:     
            if field not in self.json_fields:
                func = partial(self._find_by_single_parameter, fields=self.fields, source_table=self.source_table, field=field)
            else:
                func = partial(self._find_by_json_parameter, fields=self.fields, source_table=self.source_table, json_field=field)
            setattr(self, f"find_by_{field.lower()}", func)

    # outra sintaxe para chamar o método usando apenas um parâmetro
    def find_by_single_parameter(self, **kwargs):
        field_name, field_value = kwargs.popitem()
        return getattr(self, f"find_by_{field_name.lower()}")(field_value)

    def reflect(self):
        # reflect find_all_by        
        self._generate_find_by_single_parameter()
        # reflect find_all_by_and
        self._generate_find_by_first_and_second_parameter()
        # reflect find_all_by_or
        self._generate_find_by_first_or_second_parameter()
