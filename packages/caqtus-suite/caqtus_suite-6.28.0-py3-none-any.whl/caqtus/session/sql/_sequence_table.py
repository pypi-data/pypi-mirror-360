from __future__ import annotations

import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._path_table import SQLSequencePath
from ._shot_tables import SQLShot
from ._table_base import Base
from .._state import State


class SQLSequence(Base):
    """This table stores the sequences that are created by the user.

    Attributes:
        id_: The unique identifier of the sequence.
        path_id: The identifier of the path that the sequence is associated with.
        path: A reference to the path that the sequence is associated with.
        state: The state of the sequence.
        exception_traceback: The traceback of the exception that occurred while running
            the sequence.

            This is None if the sequence is not in the CRASHED state.

            It can be None even if the sequence is in the CRASHED state if the traceback
            was not captured.

        parameters: A reference to the parameters of the sequence.
        iteration: A reference to the iteration configuration of the sequence.
        time_lanes: A reference to the time lanes of the sequence.
        device_configurations: A reference to the device configurations of the sequence.

        start_time: The time at which the sequence started execution.

            Stored as a timezone naive datetime, with the assumption that the timezone
            is UTC.

        stop_time: The time at which the sequence stopped execution.

            Stored as a timezone naive datetime, with the assumption that the timezone
            is UTC.

        shots: A reference to the shots that are part of the sequence.
        expected_number_of_shots: The number of shots that are expected to be executed
            in total for this sequence, inferred from the iteration configuration.

            Can be None if this value is not known.
    """

    __tablename__ = "sequences"

    id_: Mapped[int] = mapped_column(name="id", primary_key=True)
    path_id: Mapped[str] = mapped_column(
        ForeignKey(SQLSequencePath.id_, ondelete="CASCADE"), unique=True, index=True
    )
    path: Mapped[SQLSequencePath] = relationship(back_populates="sequence")
    state: Mapped[State]
    exception_traceback: Mapped[Optional[SQLExceptionTraceback]] = relationship(
        cascade="all, delete", passive_deletes=True, back_populates="sequence"
    )

    parameters: Mapped[SQLSequenceParameters] = relationship(
        cascade="all, delete",
        passive_deletes=True,
        back_populates="sequence",
    )
    iteration: Mapped[SQLIterationConfiguration] = relationship(
        cascade="all",
        passive_deletes=True,
        back_populates="sequence",
    )
    time_lanes: Mapped[SQLTimelanes] = relationship(
        cascade="all, delete",
        passive_deletes=True,
        back_populates="sequence",
    )

    device_configurations: Mapped[list[SQLDeviceConfiguration]] = relationship(
        cascade="all, delete", passive_deletes=True, back_populates="sequence"
    )

    # Stored as timezone naive datetimes, with the assumption that the timezone is UTC.
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=False)
    )
    stop_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=False)
    )

    shots: Mapped[list["SQLShot"]] = relationship(
        back_populates="sequence",
        cascade="all, delete",
        passive_deletes=True,
    )
    # expected_number_of_shots indicates how many shots are expected to be executed in
    # total for this sequence.
    # It is written when the sequence iteration is set.
    # None indicates that this value is not known.
    expected_number_of_shots: Mapped[Optional[int]] = mapped_column()

    def number_shots(self) -> int:
        # TODO: replace with fast query
        return len(self.shots)


class SQLSequenceParameters(Base):
    __tablename__ = "sequence.parameters"

    id_: Mapped[int] = mapped_column(name="id", primary_key=True)
    sequence_id: Mapped[int] = mapped_column(
        ForeignKey(SQLSequence.id_, ondelete="CASCADE"), index=True
    )
    sequence: Mapped[SQLSequence] = relationship(
        back_populates="parameters", single_parent=True
    )
    content = mapped_column(sqlalchemy.types.JSON)

    __table_args__ = (UniqueConstraint(sequence_id),)


class SQLIterationConfiguration(Base):
    __tablename__ = "sequence.iteration"

    id_: Mapped[int] = mapped_column(name="id", primary_key=True)
    sequence_id: Mapped[int] = mapped_column(
        ForeignKey(SQLSequence.id_, ondelete="CASCADE"), index=True
    )
    sequence: Mapped[SQLSequence] = relationship(
        back_populates="iteration", single_parent=True
    )
    content = mapped_column(sqlalchemy.types.JSON)

    __table_args__ = (UniqueConstraint(sequence_id),)


class SQLTimelanes(Base):
    __tablename__ = "sequence.time_lanes"

    id_: Mapped[int] = mapped_column(name="id", primary_key=True)
    sequence_id: Mapped[int] = mapped_column(
        ForeignKey(SQLSequence.id_, ondelete="CASCADE"), index=True
    )
    sequence: Mapped[SQLSequence] = relationship(
        back_populates="time_lanes", single_parent=True
    )
    content = mapped_column(sqlalchemy.types.JSON)

    __table_args__ = (UniqueConstraint(sequence_id),)


class SQLDeviceConfiguration(Base):
    __tablename__ = "sequence.device_configurations"

    id_: Mapped[int] = mapped_column(primary_key=True)
    sequence_id: Mapped[int] = mapped_column(
        ForeignKey(SQLSequence.id_, ondelete="CASCADE")
    )
    sequence: Mapped[SQLSequence] = relationship(back_populates="device_configurations")
    name: Mapped[str] = mapped_column(String(255))
    device_type: Mapped[str] = mapped_column(String(255))
    content = mapped_column(sqlalchemy.types.JSON)

    __table_args__ = (
        sqlalchemy.UniqueConstraint(sequence_id, name, name="device_configuration"),
    )


class SQLExceptionTraceback(Base):
    __tablename__ = "sequence.exception_tracebacks"

    id_: Mapped[int] = mapped_column(name="id", primary_key=True)
    sequence_id: Mapped[int] = mapped_column(
        ForeignKey(SQLSequence.id_, ondelete="CASCADE"), index=True
    )
    sequence: Mapped[SQLSequence] = relationship(
        back_populates="exception_traceback", single_parent=True
    )
    content = mapped_column(sqlalchemy.types.JSON, nullable=False)

    __table_args__ = (UniqueConstraint(sequence_id),)
