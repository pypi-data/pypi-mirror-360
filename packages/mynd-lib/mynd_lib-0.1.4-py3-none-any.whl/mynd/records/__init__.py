"""Package with ORM record models."""

import sqlalchemy as sqla
import sqlmodel as sqlm

import mynd.database as db

from .records import ChunkGroupRecord as ChunkGroupRecord
from .records import ChunkRecord as ChunkRecord

from .records import CalibrationRecord as CalibrationRecord
from .records import RectifiedCalibrationRecord as RectifiedCalibrationRecord

from .records import SensorRecord as SensorRecord
from .records import RectifiedSensorRecord as RectifiedSensorRecord

from .records import PriorReferenceRecord as PriorReferenceRecord
from .records import AlignedReferenceRecord as AlignedReferenceRecord
from .records import AssimilatedReferenceRecord as AssimilatedReferenceRecord

from .records import CameraRecord as CameraRecord
from .records import PixelMapRecord as PixelMapRecord

from .records import StereoSensorComponentRecord as StereoSensorComponentRecord
from .records import StereoSensorRecord as StereoSensorRecord
from .records import StereoCameraPairRecord as StereoCameraPairRecord
from .records import StereoRigRecord as StereoRigRecord


def close_all_sessions() -> None:
    """Closes all SQLAlchemy sessions."""
    sqla.orm.session.close_all_sessions()


def create_database_tables(engine: db.Engine) -> None:
    """Creates database tables based on the schema of the imported SQL models."""
    sqlm.SQLModel.metadata.create_all(engine)


def clear_database_tables(engine: db.Engine) -> None:
    """Clears the SQLModel tables in a database."""
    close_all_sessions()
    sqlm.SQLModel.metadata.drop_all(engine)


def get_database_tables() -> dict:
    """Returns the registered SQL models."""
    tables: dict = {
        name: table for name, table in sqlm.SQLModel.metadata.tables.items()
    }
    return tables


__all__ = []
