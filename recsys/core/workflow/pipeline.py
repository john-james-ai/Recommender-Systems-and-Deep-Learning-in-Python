#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Recommender Systems: Towards Deep Learning State-of-the-Art                         #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.6                                                                              #
# Filename   : /recsys/core/workflow/pipeline.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/Recommender-Systems                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday December 19th 2022 03:34:43 pm                                               #
# Modified   : Wednesday December 28th 2022 03:27:38 am                                            #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
"""Pipeline Module"""
from abc import ABC, abstractmethod
from collections import OrderedDict

from .task import Task
from recsys.core.repo.uow import UnitOfWork


# ------------------------------------------------------------------------------------------------ #
#                                     PIPELINE BASE CLASS                                          #
# ------------------------------------------------------------------------------------------------ #
class Pipeline(ABC):
    """Base class for Pipelines"""
    def __init__(self) -> None:
        self._tasks = OrderedDict()
        self._data = None

    def __len__(self) -> int:
        return len(self._tasks)

    def add_task(self, task: Task) -> None:
        self._tasks[task.name] = task

    @abstractmethod
    def run(self, uow: UnitOfWork = UnitOfWork()) -> None:
        """Runs the pipeline"""


# ------------------------------------------------------------------------------------------------ #
#                                      DATA PIPELINE                                               #
# ------------------------------------------------------------------------------------------------ #
class DataPipeline(Pipeline):
    def __init__(self) -> None:
        super().__init__()

    def run(self, uow: UnitOfWork = UnitOfWork()) -> None:
        """Runs the pipeline"""
        data = self._data

        for _, task in self._tasks.items():
            result = task.run(data, uow)
            data = result or data
