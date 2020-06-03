from common.utils import get_all_subclasses, import_modules

from .base import ToyAI

# imports submodules to populate ToyAI subclasses list
import_modules(__name__)
TOY_AIS = get_all_subclasses(ToyAI)
