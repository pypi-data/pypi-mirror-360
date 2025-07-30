from ..general import Architecture
from .code import assembly_code
from .config import QuarkConfig, QuarkLocalConfig
from .data import assembly_data

baqisArchitecture = Architecture('baqis', "", assembly_code, assembly_data,
                                 QuarkConfig, QuarkLocalConfig)
