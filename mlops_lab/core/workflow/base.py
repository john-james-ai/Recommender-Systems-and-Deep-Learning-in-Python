#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Enter Project Name in Workspace Settings                                            #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.6                                                                              #
# Filename   : /mlops_lab/core/workflow/base.py                                                    #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : Enter URL in Workspace Settings                                                     #
# ------------------------------------------------------------------------------------------------ #
# Created    : Saturday January 21st 2023 04:01:43 am                                              #
# Modified   : Tuesday January 24th 2023 08:13:47 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
from abc import ABC, abstractmethod
from datetime import datetime
import logging

from dependency_injector.wiring import Provide, inject

from mlops_lab.core.service.validation import Validator
from mlops_lab.core.repo.container import EventRepoContainer
from mlops_lab import IMMUTABLE_TYPES, SEQUENCE_TYPES
from mlops_lab.core.dal.dto import DTO
from mlops_lab.core.workflow import STATES


# ------------------------------------------------------------------------------------------------ #
#                               PROCESS ABSTRACT BASE CLASS                                        #
# ------------------------------------------------------------------------------------------------ #
class Process(ABC):
    """Base component class from which Task (Leaf) and DAG (Composite) objects derive."""

    def __init__(
        self,
        name: str,
        description: str = None,
    ) -> None:
        self._id = None
        self._name = name
        self._description = description
        self._oid = self._get_oid()

        self._callback = None  # Overriden by subclass specific callbacks.

        self._created = datetime.now()  # Overriden by autogenerated values on database tables
        self._modified = datetime.now()  # Overriden by autogenerated values on database tables

        self._validator = Validator()

        self._logger = logging.getLogger(
            f"{self.__module__}.{self.__class__.__name__}",
        )

    # -------------------------------------------------------------------------------------------- #
    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        if self._id is None:
            self._id = id
        elif self._id != id:
            msg = "Item re-assignment is not supported for 'id' instance variable."
            self._logger.error(msg)
            raise TypeError(msg)

    # -------------------------------------------------------------------------------------------- #
    @property
    def oid(self) -> str:
        return self._oid

    # -------------------------------------------------------------------------------------------- #
    @property
    def name(self) -> str:
        return self._name

    # -------------------------------------------------------------------------------------------- #
    @property
    def description(self) -> str:
        return self._description

    # -------------------------------------------------------------------------------------------- #
    @property
    def state(self) -> str:
        return self._state

    # -------------------------------------------------------------------------------------------- #
    @state.setter
    def state(self, state: str) -> None:
        self._state = state
        self._validate()

    # -------------------------------------------------------------------------------------------- #
    @property
    @abstractmethod
    def is_composite(self) -> str:
        """True for DAGs and False for Tasks."""

    # -------------------------------------------------------------------------------------------- #
    @abstractmethod
    def as_dto(self) -> DTO:
        """Creates a dto representation of the process."""

    # -------------------------------------------------------------------------------------------- #
    def on_create(self) -> None:
        self._state = STATES[0]
        try:
            self._callback.on_create(self)
        except AttributeError:
            msg = f"A Callback for {self.__class__.__name__} has not been set or is invalid."
            self._logger.error(msg)
            raise

    # -------------------------------------------------------------------------------------------- #
    def on_load(self) -> None:
        self._state = STATES[1]
        try:
            self._callback.on_load(self)
        except AttributeError:
            msg = f"A Callback for {self.__class__.__name__} has not been set or is invalid."
            self._logger.error(msg)
            raise

    # -------------------------------------------------------------------------------------------- #
    def on_start(self) -> None:
        self._state = STATES[2]
        try:
            self._callback.on_start(self)
        except AttributeError:
            msg = f"A Callback for {self.__class__.__name__} has not been set or is invalid."
            self._logger.error(msg)
            raise

    # -------------------------------------------------------------------------------------------- #
    def on_fail(self) -> None:
        self._state = STATES[3]
        try:
            self._callback.on_fail(self)
        except AttributeError:
            msg = f"A Callback for {self.__class__.__name__} has not been set or is invalid."
            self._logger.error(msg)
            raise

    # -------------------------------------------------------------------------------------------- #
    def on_end(self) -> None:
        self._state = STATES[4]
        try:
            self._callback.on_end(self)
        except AttributeError:
            msg = f"A Callback for {self.__class__.__name__} has not been set or is invalid."
            self._logger.error(msg)
            raise

    # -------------------------------------------------------------------------------------------- #
    def as_dict(self) -> dict:
        """Returns a dictionary representation of the the Config object."""
        return {
            k.replace("_", "", 1) if k[0] == "_" else k: self._export_config(v)
            for k, v in self.__dict__.items()
        }

    @classmethod
    def _export_config(cls, v):
        """Returns v with Configs converted to dicts, recursively."""
        if isinstance(v, IMMUTABLE_TYPES):
            return v
        elif isinstance(v, SEQUENCE_TYPES):
            return type(v)(map(cls._export_config, v))
        elif isinstance(v, datetime):
            return v
        elif isinstance(v, dict):
            return v
        elif hasattr(v, "as_dict"):
            return v.as_dict()
        else:
            """Else nothing. What do you want?"""

    # -------------------------------------------------------------------------------------------- #
    def _get_oid(self) -> str:
        return f"{self.__class__.__name__.lower()}_{self._name}"

    # -------------------------------------------------------------------------------------------- #
    def _validate(self) -> None:
        response = self._validator.validate(self)
        if not response.is_ok:
            self._logger.error(response.msg)
            raise response.exception(response.msg)


# ------------------------------------------------------------------------------------------------ #
#                            ABSTRACT BASE CLASS FOR CALLBACKS                                     #
# ------------------------------------------------------------------------------------------------ #
class Callback(ABC):
    """Abstract base class used for defining callbacks."""

    @inject
    def __init__(self, events: EventRepoContainer = Provide[EventRepoContainer]) -> None:
        self._events = events

    @property
    def name(self) -> str:
        """Returns the callback name or lowercase class name if none provided."""
        self._name = self._name or self.__class__.__name__.lower()

    @abstractmethod
    def on_create(self, process: Process) -> None:
        """Called at process (dag, task) creation

        Args:
            process (Process): Process object representation of the process being created.

        """

    @abstractmethod
    def on_start(self, process: Process) -> None:
        """Called when a process (dag, task) begins execution.

        Args:
            process (Process): Process object representation of the process which has started.

        """

    @abstractmethod
    def on_fail(self, process: Process) -> None:
        """Called at process (dag, task) ends either successfully or otherwise.

        Args:
            process (Process): Process object representation of the process which has ended.

        """

    @abstractmethod
    def on_end(self, process: Process) -> None:
        """Called at process (dag, task) ends either successfully or otherwise.

        Args:
            process (Process): Process object representation of the process which has ended.

        """