import logging


class Loggable:

    def _get_logger(self) -> logging.Logger:
        if not hasattr(self, "_logger"):
            self._logger = logging.get_logger(self.get_logger_name())
        return self._logger

    def _get_logger_name(self) -> str:
        """Meant to be overridden
        """
        return self.__class__.__module__ + "." + self.__class__.__name__
    
    def _log(self, *args, **kwargs):
        self._get_logger().log(*args, **kwargs)
    
    def _debug(self, *args, **kwargs):
        self._get_logger().debug(*args, **kwargs)
    
    def _info(self, *args, **kwargs):
        self._get_logger().info(*args, **kwargs)
    
    def _warning(self, *args, **kwargs):
        self._get_logger().warning(*args, **kwargs)
    
    def _error(self, *args, **kwargs):
        self._get_logger().error(*args, **kwargs)
    
    def _critical(self, *args, **kwargs):
        self._get_logger().critical(*args, **kwargs)
    
    def _debug(self, *args, **kwargs):
        self._get_logger().debug(*args, **kwargs)
