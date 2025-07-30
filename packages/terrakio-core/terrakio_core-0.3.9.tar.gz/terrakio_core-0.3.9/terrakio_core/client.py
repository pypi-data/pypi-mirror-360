from typing import Optional
import logging
from terrakio_core.config import read_config_file, DEFAULT_CONFIG_FILE
from abc import abstractmethod

class BaseClient():
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, verbose: bool = False):

        self.verbose = verbose
        self.logger = logging.getLogger("terrakio")
        if verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)

        self.timeout = 300
        self.retry = 3

        self.session = None

        self.url = url
        self.key = api_key

        config = read_config_file( DEFAULT_CONFIG_FILE, logger = self.logger)
        
        if self.url is None:
            self.url = config.get('url')
        
        if self.key is None:
            self.key = config.get('key')

        self.token = config.get('token')

        
    @abstractmethod
    def _setup_session(self):
        """Initialize the HTTP session - implemented by sync/async clients"""
        pass