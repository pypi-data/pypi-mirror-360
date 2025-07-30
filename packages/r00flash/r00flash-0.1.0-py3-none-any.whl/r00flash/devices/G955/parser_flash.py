from ..G950.main import process_stock
from .devconf import devconf

def podgotovka_k_zapysky(args):
    devconf.generate_devconf(args)
    if args.command == 'stock':
        devconf.set_dir_stock(args.version, args.csc)
        return process_stock()


def setup_flash_parser(subparsers):
    pass