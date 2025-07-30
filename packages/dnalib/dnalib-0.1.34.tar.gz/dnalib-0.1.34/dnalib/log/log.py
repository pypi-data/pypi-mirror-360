import logging

def log(logger_name):   
    """
        Método simples que cria um logger para ser usado em todos os processos internos da dnalib. Garante que um handler é adicionado apenas uma vez ao logger_name.

        Args:
            logger_name (str): geralmente é passado o parâmetro __name__ do módulo, que permite uma identificação mais interessante nos arquivos de log.

        Returns:
            logger: objeto de logger.
    """ 
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        # set logger level
        logger.setLevel(logging.INFO)            
        logger.propagate = False

        # define handler and formatter
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

        # add formatter to handler
        handler.setFormatter(formatter)

        # add handler to logger
        logger.addHandler(handler)
    return logger