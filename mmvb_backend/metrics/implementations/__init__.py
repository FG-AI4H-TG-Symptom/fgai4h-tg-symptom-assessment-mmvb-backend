from common.utils import get_all_subclasses, import_modules, natural_keys

from .base import Metric

# imports submodules to populate Metric subclasses list
import_modules(__name__)
METRICS = list(get_all_subclasses(Metric))
METRICS.sort(key=lambda obj: natural_keys(obj.name))

SUPPORTED_METRICS = {metric.name: metric for metric in METRICS}
