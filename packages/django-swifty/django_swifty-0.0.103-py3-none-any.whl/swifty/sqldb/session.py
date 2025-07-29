"""DB Session"""

from typing import Type, List, Dict, Union, Any, Optional, Tuple
from functools import wraps

import six
from django.conf import settings

from sqlalchemy import create_engine, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from swifty.utils.decorators import once_trigger
from swifty.utils.mapper import getpath
from swifty.logging.logger import SwiftyLoggerMixin
from swifty.sqldb.constants import SqlConnectionEvents


DB_CACHE_PATTERN: Dict[str, Union[str, int, List[str]]] = {
    "prefix": "DB_SESSION",
    "ttl": 86400,
    "vary_by": [""],
    "db": 2,
}


class DBSessionException(Exception):
    """Custom exception for database session errors."""


def get_session() -> Session:
    """Create and return a new SQLAlchemy session instance."""
    session = sessionmaker()
    session.configure(bind=create_engine(settings.DB_URL, echo=True))  # type: ignore
    return session()


def commit_or_rollback_model(func: Any) -> Any:
    """Decorator to handle commit or rollback for model operations."""

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        with self.session.begin():
            try:
                db_objects = func(self, *args, **kwargs)
                if isinstance(db_objects, list):
                    self.session.add_all(db_objects)
                else:
                    self.session.add(db_objects)
                self.session.flush()
            except Exception as e:
                self.session.rollback()
                self.logger.error(
                    SqlConnectionEvents.ERROR_WHEN_COMMIT,
                    error_messages=six.text_type(e),
                )
                raise e

            self.session.commit()
            self.logger.info(
                SqlConnectionEvents.SUCCESSFULLY_COMMIT,
                db_objects=db_objects,
            )
            return db_objects

    return wrapper


def commit_or_rollback(func: Optional[Any] = None) -> Any:
    """Decorator to manage SQLAlchemy session transactions."""

    @wraps(func)  # type: ignore
    def inner(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            with self.session.begin():
                return func(self, *args, **kwargs)  # type: ignore
        except SQLAlchemyError as error:
            self.logger.error(
                SqlConnectionEvents.ERROR_WHEN_COMMIT,
                error_messages=six.text_type(error),
            )
            raise DBSessionException(
                getpath(error, "orig.diag.message_primary", error)
            ) from error

    return inner


class SwiftyDBSessionMixin(SwiftyLoggerMixin):
    """Mixin class for managing database sessions with logging capabilities."""

    db_url: str = settings.DB_URL
    cache_pattern: Dict[str, Union[str, int, List[str]]] = (
        getattr(settings, "DB_CACHE_PATTERN", None) or DB_CACHE_PATTERN
    )

    @property
    @once_trigger
    def session(self) -> Session:
        """Get the current SQLAlchemy session instance."""
        return get_session()

    def get_simple_model_data(
        self,
        model: Type[Any],
        query_data: Optional[Dict[str, Any]] = None,
        columns: Optional[List[Any]] = None,
        order_by: Optional[Tuple[str, int]] = None,
        extra_filters: Optional[List[Any]] = None,
    ) -> List[Any]:
        """Retrieve data from a simple model.

        Args:
            model (Type[Any]): SQLAlchemy model class.
            query_data (Optional[Dict[str, Any]]): Query filters.
            columns (Optional[List[Any]]): Columns to select.
            order_by (Optional[Tuple[str, int]]): Order by clause.
            extra_filters (Optional[List[Any]]): Additional filters.

        Returns:
            List[Any]: List of query results.
        """
        query = self.query_simple_model_data(
            model,
            query_data=query_data,
            columns=columns,
            order_by=order_by,
            extra_filters=extra_filters,
        )
        return query.all()  # type: ignore

    def query_simple_model_data(
        self,
        model: Type[Any],
        query_data: Optional[Dict[str, Any]] = None,
        columns: Optional[List[Any]] = None,
        order_by: Optional[Tuple[str, int]] = None,
        extra_filters: Optional[List[Any]] = None,
    ) -> Any:
        """Query data from a simple model.

        Args:
            model (Type[Any]): SQLAlchemy model class.
            query_data (Optional[Dict[str, Any]]): Query filters.
            columns (Optional[List[Any]]): Columns to select.
            order_by (Optional[Tuple[str, int]]): Order by clause.
            extra_filters (Optional[List[Any]]): Additional filters.

        Returns:
            Any: SQLAlchemy query object.
        """
        try:
            query_set = (
                self.session.query(model, *(columns or []))
                .filter(*(extra_filters or []))
                .filter_by(**(query_data or {}))
            )

            if isinstance(order_by, (list, tuple)) and len(order_by) == 2:
                order_method = getattr(model, order_by[0])
                query_set = query_set.order_by(
                    order_method.desc() if order_by[1] == -1 else order_method.asc()
                )
            return query_set

        except SQLAlchemyError as err:
            self.logger.error(
                SqlConnectionEvents.ERROR_WHEN_QUERY_DATA,
                model=model,
                query_data=query_data,
                error_message=err,
            )

    def valid_columns(self, db_object: Union[Table, Any]) -> List[str]:
        """Get valid column names for a model or table.

        Args:
            db_object (Union[Table, Any]): SQLAlchemy model or table.

        Returns:
            List[str]: List of column names.
        """
        return [
            column.name
            for column in (
                db_object.columns
                if isinstance(db_object, Table)
                else db_object.__table__.columns
            )
        ]

    def valid_model(self, model, data):
        """_summary_

        Args:
            model (_type_): _description_
            data (_type_): _description_
        """

        return model(
            **{
                key: value
                for key, value in data.items()
                if key in self.valid_columns(model)
            }
        )

    def update_model_data(
        self,
        model: Type[Any],
        data: dict,
        pk_filter: Optional[Dict[str, Any]] = None,
        extra_data_dict: Optional[Dict[str, Any]] = None,
    ):
        """_summary_

        Args:
            model (Type[Any]): _description_
            data (Union[list[dict], dict]): _description_
            pk_filter (Optional[Dict[str, Any]], optional): _description_. Defaults to None.
            extra_data_dict (Optional[Dict[str, Any]], optional): _description_. Defaults to None.

        Raises:
            NoResultFound: _description_

        Returns:
            _type_: _description_
        """
        query_object = self.session.query(model).filter_by(**pk_filter)
        updated_status = query_object.update(
            values=self.valid_model(
                model, {**data, **(extra_data_dict or {})}
            ).as_dict()
        )

        if updated_status:
            self.session.flush()
            return query_object.one()

        raise NoResultFound

    def update_or_create_model_data(
        self,
        model: Type[Any],
        data: Union[list[dict], dict],
        pk_filter: Optional[Dict[str, Any]] = None,
        extra_data_dict: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Update existing model instance or create a new one.

        Args:
            model (Type[Any]): SQLAlchemy model class.
            data (Dict[str, Any]): Data to update or create with.
            pk_filter (Dict[str, Any]): Primary key filter.
            extra_data_dict (Optional[Dict[str, Any]]): Additional data.

        Returns:
            Any: Updated or created model instance.
        """
        extra_data_dict = extra_data_dict or {}
        pk_filter = pk_filter or {}
        try:
            return self.update_model_data(
                model=model,
                data=data,
                pk_filter=pk_filter,
                extra_data_dict=extra_data_dict,
            )

        except NoResultFound:
            return self.create_model_data(
                model=model,
                data={**data, **pk_filter},
                extra_data_dict=extra_data_dict,
            )

    def create_model_data(
        self,
        model: Type[Any],
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        extra_data_dict: Optional[Dict[str, Any]] = None,
        bulk: Optional[bool] = False,
    ) -> Union[Any, List[Any]]:
        """Create new model instance(s).

        Args:
            model (Type[Any]): SQLAlchemy model class.
            data (Union[Dict[str, Any], List[Dict[str, Any]]]): Data to create instance(s) with.
            extra_data_dict (Optional[Dict[str, Any]]): Additional data.
            valid_columns (Optional[List[str]]): List of valid columns.

        Returns:
            Union[Any, List[Any]]: Created model instance(s).
        """
        extra_data_dict = extra_data_dict or {}
        if bulk or isinstance(data, (list, tuple)):
            instance = [
                self.valid_model(model, {**sub_data, **extra_data_dict})
                for sub_data in data
            ]
            self.session.add_all(instance)
        else:
            instance = self.valid_model(model, {**data, **(extra_data_dict or {})})
            self.session.add(instance)

        self.session.flush()
        return instance

    def valid_data(
        self, valid_columns: List[str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter data dictionary to only include valid columns.

        Args:
            valid_columns (List[str]): List of valid column names.
            data (Dict[str, Any]): Data dictionary to filter.

        Returns:
            Dict[str, Any]: Filtered data dictionary.
        """
        return {key: value for key, value in data.items() if key in valid_columns}

    def save_many_to_many_table(
        self,
        association_table: Table,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        extra_data_dict: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Save many-to-many relationships.

        Args:
            association_table (Table): SQLAlchemy association table.
            data (Union[Dict[str, Any], List[Dict[str, Any]]]): Relationship data.
            extra_data_dict (Optional[Dict[str, Any]]): Additional data.

        Returns:
            Any: Result proxy from the insert operation.
        """
        valid_columns = self.valid_columns(association_table)
        associations = [
            self.valid_data(valid_columns, {**sub_data, **(extra_data_dict or {})})
            for sub_data in (data if isinstance(data, (list, tuple)) else [data])
        ]
        result_proxy = self.session.execute(
            association_table.insert().values(associations).returning(association_table)
        )
        self.session.flush()
        return result_proxy
