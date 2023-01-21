#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Recommender Systems: Towards Deep Learning State-of-the-Art                         #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.6                                                                              #
# Filename   : /recsys/core/dal/sql/job.py                                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/Recommender-Systems                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday December 4th 2022 06:37:18 am                                                #
# Modified   : Saturday January 21st 2023 02:59:45 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
import os
import dotenv

from dataclasses import dataclass
from recsys.core.dal.sql.base import SQL, DDL, DML
from recsys.core.dal.dto import DTO
from recsys.core.entity.base import Entity
from recsys.core.workflow.process import Job

# ================================================================================================ #
#                                         JOB                                                      #
# ================================================================================================ #


# ------------------------------------------------------------------------------------------------ #
#                                          DDL                                                     #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class CreateJobTable(SQL):
    name: str = "job"
    sql: str = """CREATE TABLE IF NOT EXISTS job (id MEDIUMINT PRIMARY KEY AUTO_INCREMENT, oid VARCHAR(255) NOT NULL, name VARCHAR(128) NOT NULL, description VARCHAR(255), state VARCHAR(32), created DATETIME DEFAULT CURRENT_TIMESTAMP, modified DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, UNIQUE(name));"""
    args: tuple = ()
    description: str = "Created the job table."


# ------------------------------------------------------------------------------------------------ #
@dataclass
class DropJobTable(SQL):
    name: str = "job"
    sql: str = """DROP TABLE IF EXISTS job;"""
    args: tuple = ()
    description: str = "Dropped the job table."


# ------------------------------------------------------------------------------------------------ #


@dataclass
class JobTableExists(SQL):
    name: str = "job"
    sql: str = None
    args: tuple = ()
    description: str = "Checked existence of job table."

    def __post_init__(self) -> None:
        dotenv.load_dotenv()
        mode = os.getenv("MODE")
        self.sql = f"""SELECT COUNT(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA LIKE 'recsys_{mode}_events' AND TABLE_NAME = 'job';"""


# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobDDL(DDL):
    entity: type[Entity] = Job
    create: SQL = CreateJobTable()
    drop: SQL = DropJobTable()
    exists: SQL = JobTableExists()


# ------------------------------------------------------------------------------------------------ #
#                                          DML                                                     #
# ------------------------------------------------------------------------------------------------ #


@dataclass
class InsertJob(SQL):
    dto: DTO

    sql: str = """INSERT INTO job (oid, name, description, state) VALUES (%s, %s, %s, %s);"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (
            self.dto.oid,
            self.dto.name,
            self.dto.description,
            self.dto.state,
        )


# ------------------------------------------------------------------------------------------------ #


@dataclass
class UpdateJob(SQL):
    dto: DTO
    sql: str = """UPDATE job SET oid = %s, name = %s, description = %s, state = %s WHERE id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (
            self.dto.oid,
            self.dto.name,
            self.dto.description,
            self.dto.state,
            self.dto.id,
        )


# ------------------------------------------------------------------------------------------------ #


@dataclass
class SelectJob(SQL):
    id: int
    sql: str = """SELECT * FROM job WHERE id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.id,)


# ------------------------------------------------------------------------------------------------ #


@dataclass
class SelectJobByName(SQL):
    name: str
    sql: str = """SELECT * FROM job WHERE name = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.name,)


# ------------------------------------------------------------------------------------------------ #


@dataclass
class SelectAllJob(SQL):
    sql: str = """SELECT * FROM job;"""
    args: tuple = ()


# ------------------------------------------------------------------------------------------------ #


@dataclass
class JobExists(SQL):
    id: int
    sql: str = """SELECT EXISTS(SELECT 1 FROM job WHERE id = %s LIMIT 1);"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.id,)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class DeleteJob(SQL):
    id: int
    sql: str = """DELETE FROM job WHERE id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.id,)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class JobDML(DML):
    entity: type[Entity] = Job
    insert: type[SQL] = InsertJob
    update: type[SQL] = UpdateJob
    select: type[SQL] = SelectJob
    select_by_name: type[SQL] = SelectJobByName
    select_all: type[SQL] = SelectAllJob
    exists: type[SQL] = JobExists
    delete: type[SQL] = DeleteJob
