from typing import get_origin, get_args, Union, Type, Any
from dataclasses import dataclass
import enum
import types
import datetime
import sqlite3
from pydantic import BaseModel

from database import transaction


class Unique:
    def __init__(self, *columns_names: tuple[str]):
        self.columns_names = columns_names


class Base(BaseModel):

    id: int = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime | None = None

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        for name, info in cls.model_fields.items():
            field = Field.from_pydantic_info(name, info)
            print()
            print(field)
            print()
        # exit()

    @classmethod
    def _execute(cls, sql: str, parameters: list=[]):
        print()
        print(sql)
        print(parameters)
        print()
        with transaction() as t:
            try:
                return t.execute(sql, parameters)
            except sqlite3.OperationalError as e:
                if not str(e).startswith("no such table: "):
                    raise
                cls._create_table()
                return t.execute(sql, parameters)

    # CREATE TABLE

    @classmethod
    def _create_table(cls):
        for key, info in cls.model_fields.items():
            reference = cls._get_reference(key)
            if reference:
                reference.to._create_table()
        translate_type = {
            int: "INTEGER NOT NULL",
            int|None: "INTEGER",
            str: "TEXT NOT NULL",
            str|None: "TEXT",
            datetime.datetime: "TIMESTAMP NOT NULL",
            datetime.datetime|None: "TIMESTAMP",
            list[str]: "JSON NOT NULL",
        }
        sql = f"CREATE TABLE IF NOT EXISTS {cls._get_table_name()} ({", ".join([
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at TIMESTAMP NULL",
        ] + [
            (f"{key}_id INTEGER" + (" NULL" if cls._get_reference(key).is_nullable else "")
             if cls._get_reference(key) else
             (
                f"{key} TEXT CHECK({key} in ('{"', '".join(e.value for e in info.annotation)}')) NOT NULL"
                if issubclass(info.annotation, enum.Enum) else
                f"{key} {translate_type[info.annotation]}") 
             )
            for key, info in cls.model_fields.items()
            if key not in Base.model_fields
        ] + [
            f"FOREIGN KEY ({key}_id) REFERENCES {cls._get_reference(key).to._get_table_name()}(id)"
            for key, info in cls.model_fields.items()
            if key not in Base.model_fields
            and cls._get_reference(key)
        ])})"
        print()
        print(sql)
        print()
        cls._execute(sql)

    def _get_data(self) -> dict[str, any]:
        data = {}
        for key in self.__class__.model_fields:
            if key in Base.model_fields:
                continue
            value = getattr(self, key)
            if isinstance(value, enum.Enum):
                value = value.value
            elif self._get_reference(key):
                key += "_id"
                value = value.id if value else None
            data[key] = value
        return data

    # INSERT
    def model_post_init(self, __context: any) -> None:
        if self.id is None:
            data = self._get_data() | {"id": None}
            sql = f"INSERT INTO {self._get_table_name()} ({", ".join(data.keys())})\nVALUES  ({", ".join("?" for v in data.values())})"
            self._execute(sql, list(data.values()))
            cursor = self._execute(f"SELECT id, created_at FROM {self._get_table_name()} WHERE id = last_insert_rowid()")
            row = cursor.fetchone()
            self.id = row[0]
            self.created_at = datetime.datetime.fromisoformat(row[1])

    # UPDATE
    def save(self):
        data = self._get_data()
        sql = f"UPDATE {self._get_table_name()} SET {", ".join(
            f"{key} = ?"
            for key in data.keys()
        )}, updated_at = CURRENT_TIMESTAMP WHERE id = {self.id}"
        self._execute(sql, list(data.values()))

    # SELECT
    @classmethod
    def load(cls, last_created:bool=False, as_collection:bool=False, **criteria):
        values = []
        # SELECT
        sql = f"SELECT "
        def get_selected(model=cls, parent_alias=cls._get_table_name()):
            for key, info in model.model_fields.items():
                alias = f"{parent_alias}__{key}"
                reference = model._get_reference(key)
                if reference:
                    yield from get_selected(model=reference.to,
                                            parent_alias=alias)
                else:
                    yield alias, f"{parent_alias}.{key}"
        selected = dict(get_selected())
        sql += ", ".join(f"{column} AS {alias}" for alias, column in selected.items())
        # FROM
        sql += f"\nFROM {cls._get_table_name()}"
        # JOIN
        def get_sql_joins(model=cls, parent_alias=cls._get_table_name()):
            for key, info in model.model_fields.items():
                reference = model._get_reference(key)
                if reference:
                    alias = f"{parent_alias}__{key}"
                    sql_join = f"\nLEFT JOIN {reference.to._get_table_name()} AS {alias} ON {alias}.id = {parent_alias}.{key}_id"
                    yield sql_join
                    yield from get_sql_joins(model=reference.to,
                                             parent_alias=alias)
        for sql_join in get_sql_joins():
            sql += sql_join

        # WHERE
        if criteria:
            is_first = True
            for key, value in criteria.items():
                if is_first:
                    sql += "\nWHERE "
                else:
                    sql += "\nAND "
                    is_first = False
                sql += f"{key} = ?"
                values.append(value)
        if last_created:
            sql += f"\nORDER BY {cls._get_table_name()}.created_at DESC\nLIMIT 1"
        # restitute results
        def get_data(row):
            data = {}
            empty_paths = []
            for key, value in zip(selected, row):
                path = key.split("__")[1:]
                if path[-1] == "id" and value is None:
                    empty_paths.append(path[:-1])
                position = data
                for k in path[:-1]:
                    if k not in position:
                        position[k] = {}
                    position = position[k]
                position[path[-1]] = value
            for path in empty_paths:
                position = data
                for k in path[:-1]:
                    if k not in position:
                        position[k] = {}
                    position = position[k]
                position[path[-1]] = None
            return data
        if as_collection:
            rows = cls._execute(sql, values).fetchall()
            return [
                cls(**get_data(row))
                for row in rows
            ]
        else:
            row = cls._execute(sql, values).fetchone()
            if row is None:
                return None
            return cls(**get_data(row))

    @classmethod
    def load_all(cls, **criteria):
        return cls.load(as_collection=True, **criteria)

    @classmethod
    def _build_instance(cls, row) -> BaseModel:
        data = dict(zip(cls._get_columns_names(), row))
        return cls(**data)
    
    @classmethod
    def _get_columns_names(cls) -> list[str]:
        return [
            name + ("_id" if cls._get_reference(name) else "")
            for name in cls.model_fields
        ]

    @classmethod
    def _get_reference(cls, column_name) -> Reference | None:
        if not hasattr(cls, "_references"):
            cls._references = {}
        if column_name not in cls._references:
            cls._references[column_name] = cls._compute_reference(column_name)
        return cls._references[column_name]

    @classmethod
    def _compute_reference(cls, column_name) -> Reference | None:
        type_hint = cls.model_fields[column_name].annotation
        if issubclass(type_hint, Base):
            return Reference(to=type_hint, is_nullable=False)
        # 1. Check if the origin is Union (which Optional expands to)
        origin = get_origin(type_hint)
        if origin is not Union and (hasattr(types, "UnionType") and origin is not types.UnionType):
            return None
        # 2. Get the arguments of the Union
        args = get_args(type_hint)
        # Check if type(None) is one of the arguments
        if type(None) not in args:
            return None
        # 3. Check the other argument(s) for being a derived class of Base
        for arg in args:
            if arg is not type(None):
                # Ensure the argument is actually a class (not a TypeVar, etc.)
                if isinstance(arg, type) and issubclass(arg, Base):
                    return Reference(name=column_name, to=arg, is_nullable=True)
        return None
    
    @classmethod
    def _get_table_name(cls) -> str:
        return cls.__name__.lower()


if __name__ == "__main__":
    # company model
    class Company(Base):
        name: str
    # employee model, with a foreign key to company
    class Employee(Base):
        firstname: str
        lastname: str
        company: Company
    # show columns
    c1 = Company.load(id=4)
    c2 = Company.load(name="AutoKod", last_created=True)
    c3 = Company.load(name="AutoKod II", last_created=True)
    c4 = Company(name="AutoKod")
    c5 = Company(name="AutoKod")
    c5.name += " II"
    c5.save()
    print(c1)
    print(c2)
    print(c3)
    print(c4)
    e1 = Employee(firstname="Mathieu", lastname="Rodic", company=c1)
    e2 = Employee.load(company_id=c1.id, last_created=True)
    e_all = Employee.load_all(company_id=c1.id)
    print(e1)
    print(e2)
    print(e_all)
    exit()
    # e = Employee.load(id=23)
    print(Company._get_columns_names())
    print(Employee._get_columns_names())
    print(Company._build_instance({"id": 12, "name": "Hello :)"}))
