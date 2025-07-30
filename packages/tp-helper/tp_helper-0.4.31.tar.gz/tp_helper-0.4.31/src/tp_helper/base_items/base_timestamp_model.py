from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

from tp_helper.functions import timestamp


class BaseTimestampModel:
    updated_at: Mapped[int] = mapped_column(
        Integer, default=timestamp, onupdate=timestamp
    )

    created_at: Mapped[int] = mapped_column(Integer, default=timestamp)
