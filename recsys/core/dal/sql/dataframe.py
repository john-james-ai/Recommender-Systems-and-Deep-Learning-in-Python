#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Recommender Systems: Towards Deep Learning State-of-the-Art                         #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.6                                                                              #
# Filename   : /recsys/core/dal/sql/dataframe.py                                                   #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/Recommender-Systems                                #
# ------------------------------------------------------------------------------------------------ #
# Created    : Sunday December 4th 2022 06:37:18 am                                                #
# Modified   : Wednesday January 4th 2023 01:24:05 pm                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass
from recsys.core.dal.sql.base import SQL, DDL, DML
from recsys.core.dal.dto import DTO
from recsys.core.entity.base import Entity
from recsys.core.entity.dataset import DataFrame

# ================================================================================================ #
#                                        DATASET                                                   #
# ================================================================================================ #


# ------------------------------------------------------------------------------------------------ #
#                                          DDL                                                     #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class CreateDataFrameTable(SQL):
    name: str = "dataframe"
    sql: str = """CREATE TABLE IF NOT EXISTS dataframe (id MEDIUMINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(128) NOT NULL, description VARCHAR(255), datasource_id SMALLINT NOT NULL, mode VARCHAR(32) NOT NULL, stage VARCHAR(64) NOT NULL, size BIGINT, nrows BIGINT, ncols SMALLINT, nulls SMALLINT, pct_nulls FLOAT, parent_id SMALLINT, created DATETIME, modified DATETIME, UNIQUE(name, mode));"""
    args: tuple = ()
    description: str = "Created the dataframe table."


# ------------------------------------------------------------------------------------------------ #
@dataclass
class DropDataFrameTable(SQL):
    name: str = "dataframe"
    sql: str = """DROP TABLE IF EXISTS dataframe;"""
    args: tuple = ()
    description: str = "Dropped the dataframe table."


# ------------------------------------------------------------------------------------------------ #


@dataclass
class DataFrameTableExists(SQL):
    name: str = "dataframe"
    sql: str = """SELECT COUNT(TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_NAME = 'dataframe';"""
    args: tuple = ()
    description: str = "Checked existence of dataframe table."


# ------------------------------------------------------------------------------------------------ #
@dataclass
class DataFrameDDL(DDL):
    entity: type(Entity) = DataFrame
    create: SQL = CreateDataFrameTable()
    drop: SQL = DropDataFrameTable()
    exists: SQL = DataFrameTableExists()


# ------------------------------------------------------------------------------------------------ #
#                                          DML                                                     #
# ------------------------------------------------------------------------------------------------ #


@dataclass
class InsertDataFrame(SQL):
    dto: DTO
    sql: str = """INSERT INTO dataframe (name, description, datasource_id, mode, stage, size, nrows, ncols, nulls, pct_nulls, parent_id, created, modified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (
            self.dto.name,
            self.dto.description,
            self.dto.datasource_id,
            self.dto.mode,
            self.dto.stage,
            self.dto.size,
            self.dto.nrows,
            self.dto.ncols,
            self.dto.nulls,
            self.dto.pct_nulls,
            self.dto.parent_id,
            self.dto.created,
            self.dto.modified,
        )


# ------------------------------------------------------------------------------------------------ #


@dataclass
class UpdateDataFrame(SQL):
    dto: DTO
    sql: str = """UPDATE dataframe SET name = %s, description = %s, datasource_id = %s, mode = %s, stage = %s, size = %s, nrows = %s, ncols = %s, nulls = %s, pct_nulls = %s, parent_id = %s, created = %s, modified = %s WHERE id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (
            self.dto.name,
            self.dto.description,
            self.dto.datasource_id,
            self.dto.mode,
            self.dto.stage,
            self.dto.size,
            self.dto.nrows,
            self.dto.ncols,
            self.dto.nulls,
            self.dto.pct_nulls,
            self.dto.parent_id,
            self.dto.created,
            self.dto.modified,
            self.dto.id,
        )


# ------------------------------------------------------------------------------------------------ #


@dataclass
class SelectDataFrame(SQL):
    id: int
    sql: str = """SELECT * FROM dataframe WHERE id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.id,)

# ------------------------------------------------------------------------------------------------ #


@dataclass
class SelectDataFrameByParentId(SQL):
    dataset_id: int
    sql: str = """SELECT * FROM dataframe WHERE dataset_id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.dataset_id,)

# ------------------------------------------------------------------------------------------------ #


@dataclass
class SelectDataFrameByNameMode(SQL):
    name: str
    mode: str
    sql: str = """SELECT * FROM dataframe WHERE name = %s AND mode = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.name, self.mode,)


# ------------------------------------------------------------------------------------------------ #


@dataclass
class SelectAllDataset(SQL):
    sql: str = """SELECT * FROM dataframe;"""
    args: tuple = ()


# ------------------------------------------------------------------------------------------------ #


@dataclass
class DataFrameExists(SQL):
    id: int
    sql: str = """SELECT COUNT(*) FROM dataframe WHERE id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.id,)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class DeleteDataFrame(SQL):
    id: int
    sql: str = """DELETE FROM dataframe WHERE id = %s;"""
    args: tuple = ()

    def __post_init__(self) -> None:
        self.args = (self.id,)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class DataFrameDML(DML):
    entity: type(Entity) = DataFrame
    insert: type(SQL) = InsertDataFrame
    update: type(SQL) = UpdateDataFrame
    select: type(SQL) = SelectDataFrame
    select_by_name_mode: type(SQL) = SelectDataFrameByNameMode
    select_by_parent_id: type(SQL) = SelectDataFrameByParentId
    select_all: type(SQL) = SelectAllDataset
    exists: type(SQL) = DataFrameExists
    delete: type(SQL) = DeleteDataFrame
