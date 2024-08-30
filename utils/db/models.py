# Import all the models, so that Base has them before being
# imported by Alembic
from utils.db.base_class import Base  # noqa
from utils.demarchessimplifiees.data_extraction.models import *  # noqa
from utils.demarchessimplifiees.errors_management.models import *  # noqa
