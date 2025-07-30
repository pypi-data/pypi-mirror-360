import logging
from redflagbpm.BPMService import BPMService


class BPMLoggingHandler(logging.Handler):
    """
        Ejemplo de uso:
        # Configurar el logger
        import redflagbpm
        from redflagbpm.Logging import BPMLoggingHandler

        bpm = redflagbpm.BPMService()
        logger = logging.getLogger('redflagbpm')
        logger.setLevel(logging.DEBUG)
        bpm_handler = BPMLoggingHandler(bpm)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        bpm_handler.setFormatter(formatter)
        logger.addHandler(bpm_handler)

        # Ejemplo de emisión de logs con diferentes niveles
        logger.debug('Este es un mensaje de depuración')
        logger.info('Este es un mensaje informativo')
        logger.warning('Este es un mensaje de advertencia')
        logger.error('Este es un mensaje de error')
        logger.critical('Este es un mensaje crítico')
    """

    def __init__(self, bpm: BPMService):
        super().__init__()
        self.bpm = bpm
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        log_level = record.levelname
        msg = self.format(record)
        if log_level == 'DEBUG':
            self.bpm.logger.debug(record.name, msg)
        elif log_level == 'CRITICAL' or log_level == 'ERROR':
            self.bpm.logger.error(record.name, msg)
        elif log_level == 'WARN' or log_level == 'WARNING':
            self.bpm.logger.info(record.name, msg)
        else:
            self.bpm.logger.info(record.name, msg)
