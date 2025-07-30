from typing import Dict, Union
from ...config.manager import conf
from cached_property import cached_property

class DevConf:
    def __init__(self):
        self.args: Union[Dict, None] = None
        self._dir_stock = None

    def generate_devconf(self, args):
        self.args = args

    @cached_property
    def dir_stock(self):
        return self._dir_stock

    def set_dir_stock(self, version, csc):
        self._dir_stock = conf.dir_stock / version / csc


devconf = DevConf()











