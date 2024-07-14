# Import all the models, so that Base has them before being
# imported by Alembic
from utils.db.base_class import Base  # noqa
from utils.demarchessimplifiees.data_extractions.models import *  # noqa
from utils.demarchessimplifiees.last_snapshot.models import *  # noqa
from utils.demarchessimplifiees.models import *  # noqa
