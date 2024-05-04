# Import all the models, so that Base has them before being
# imported by Alembic
from utils.db.base_class import Base  # noqa
from utils.demandessimplifiees.models import *  # noqa
