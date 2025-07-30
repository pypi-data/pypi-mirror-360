import os
import json
import yaml

class YamlLoader(yaml.SafeLoader):    
    """
        Classe que implementa um loader customizado do YAML, que permite adicionar uma diretiva para incluir um YAML dentro de outro. Em tempo de execução os YAMLs vão para o mesmo objeto.

        Baseado em: https://gist.github.com/joshbode/569627ced3076931b02f#file-loader-py
    """
    def __init__(self, stream):
        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)

def construct_include(loader, node):
    """
        Método executado internamente pela classe de loader do YAML. É ele que permite juntar os yml a partir da diretiva !include. Para mais detalhes ver a documentação do pyyaml.
    """

    filename = os.path.abspath(os.path.join(loader._root, loader.construct_scalar(node)))
    extension = os.path.splitext(filename)[1].lstrip('.')

    with open(filename, 'r') as f:
        if extension in ('yaml', 'yml'):
            return yaml.load(f, YamlLoader)
        elif extension in ('json', ):
            return json.load(f)
        else:
            return ''.join(f.readlines())

yaml.add_constructor('!include', construct_include, YamlLoader)