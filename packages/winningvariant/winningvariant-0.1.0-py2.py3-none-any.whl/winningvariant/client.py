import logging
import asyncio
from typing import Callable, Union, Awaitable, Optional
from functools import wraps
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, call_udf
from ._internal import get_subject_id, get_experiment_id, has_valid_args
from .assignment import Assignment


class SnowflakeExecutionError(RuntimeError):
    """An error occurred while executing a Snowflake query."""

class WinningVariantClient:
    def __init__(self, session: Session, verbose: bool = False, cache: bool = True):
        self.session = session
        self.logger = logging.getLogger("WinningVariant")
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        self.logger.debug("Initialized WinningVariant")
        self.__assignment_cache = {} if cache else None
    
    def __del__(self):
        self.session.close()
        self.logger.debug("Closed WinningVariant session")

    def enable_cache(self):
        """Enable the assignment cache."""
        self.logger.debug("Enabling assignment cache")
        if self.__assignment_cache is None:
            self.__assignment_cache = {}
    
    def disable_cache(self):
        """Disable the assignment cache."""
        self.logger.debug("Disabling assignment cache")
        self.__assignment_cache = None

    def get_assignment_sql(self, subject_id: str, experiment_id: str) -> str | None:
        """Get the assignment for a subject in an experiment.

        :param session: The Snowflake session.
        :param subject_id: The subject ID.
        :param experiment_id: The experiment ID.
        :return: The assignment.
        """
        cache_key = f"{subject_id}_{experiment_id.upper()}"
        if self.__assignment_cache is not None and cache_key in self.__assignment_cache:
            return self.__assignment_cache[cache_key]
        
        self.logger.debug(f"Fetching assignment for subject={subject_id}, experiment={experiment_id.upper()}")
        assignment = (
            self.session.table("experimentation.assignments")
            .filter((col("subject_id") == subject_id) & (col("experiment_id") == experiment_id.upper()))
            .select("variant_id")
            .limit(1)
            .collect()
        )
        if assignment and len(assignment) == 1:
            variant = assignment[0]["VARIANT_ID"].upper()
            if self.__assignment_cache is not None:
              self.__assignment_cache[cache_key] = variant
            return variant
        return None

    def create_assignment_sql(self, subject_id: str, experiment_id: str) -> str | None:
        """Create an assignment for a subject in an experiment.

        :param session: The Snowflake session.
        :param subject_id: The subject ID.
        :param experiment_id: The experiment ID.
        :return: The assignment.
        """
        cache_key = f"{subject_id}_{experiment_id.upper()}"
        if self.__assignment_cache is not None and cache_key in self.__assignment_cache:
            return self.__assignment_cache[cache_key]
        
        df = self.session.create_dataframe([[subject_id, experiment_id.upper()]]).to_df("subject_id", "experiment_id")
        assignment = (
          df
            .with_column('variant_id', call_udf('experimentation.create_assignment', col('subject_id'), col('experiment_id')))
            .select("variant_id")
            .collect()
        )
        if assignment and len(assignment) == 1:
            variant = assignment[0]["VARIANT_ID"].upper()
            if self.__assignment_cache is not None:
              self.__assignment_cache[cache_key] = variant
            return variant
        return None # pragma: no cover - this is incredibly unlikely to happen and difficult to test

    def get_assignment(self, subject_id: str, experiment_id: str) -> Assignment | None:
        """Returns the assigned variant if it exists, otherwise None.

        :param subject_id: The ID of the subject to get the assignment for.
        :param experiment_id: The ID of the experiment to get the assignment for.
        :return: The assigned variant if it exists, otherwise None.
        :rtype: str | None
        :raises SnowflakeExecutionError: if the assignment cannot be fetched.
        """
        self.logger.debug(f"Fetching assignment for subject={subject_id}, experiment={experiment_id}")
        try:
            assignment = self.get_assignment_sql(subject_id, experiment_id)
            return Assignment(subject_id, experiment_id, assignment) if assignment else None
        except Exception as e:
            self.logger.error(f"Failed to fetch assignment: {e}")
            raise SnowflakeExecutionError(f"Failed to fetch assignment: {e}")

    def create_assignment(self, subject_id: str, experiment_id: str) -> Assignment | None:
        """Gets an assignment for a subject in an experiment or creates one if it doesn't exist.

        :param subject_id: The ID of the subject to get the assignment for.
        :param experiment_id: The ID of the experiment to get the assignment for.
        :return: The assigned variant if it exists, otherwise None.
        :rtype: str | None
        :raises SnowflakeExecutionError: if the assignment cannot be fetched or created.
        """
        self.logger.debug(f"Calling UDF to create assignment for subject={subject_id}, experiment={experiment_id}")
        try:
            assignment = self.create_assignment_sql(subject_id, experiment_id)
            return Assignment(subject_id, experiment_id, assignment) if assignment else None
        except Exception as e:
            self.logger.error(f"Failed to create assignment: {e}")
            raise SnowflakeExecutionError(f"Failed to create assignment: {e}")

    def check_variant(self, subject_id: str, experiment_id: str, variant_id: str, create_assignment: bool = True) -> bool:
        """Checks if a subject is assigned a specific variant.

        :param subject_id: The ID of the subject to check the assignment for.
        :param experiment_id: The ID of the experiment to check the assignment for.
        :param variant_id: The ID of the variant to check the assignment for.
        :param create_assignment: Whether to create an assignment if one doesn't exist.
        :return: True if the subject is assigned the variant, False otherwise.
        :rtype: bool
        """
        assigned = self.create_assignment(subject_id, experiment_id) if create_assignment else self.get_assignment(subject_id, experiment_id)
        self.logger.debug(f"Streamlit check_variant: {subject_id} in {experiment_id} -> {assigned}")
        return assigned == variant_id.upper()

    def assignment(self, subject_id: Optional[str] = None, experiment_id: Optional[str] = None, subject_arg: Optional[str] = None, experiment_arg: Optional[str] = None):
        """Decorator that provides a subject's assignment to a function. A new assignment is created if one doesn't exist. Requires a subject ID/arg AND experiment ID/arg.

        :param subject_id: The ID of the subject to get the assignment for.
        :param experiment_id: The ID of the experiment to get the assignment for.
        :param subject_arg: The name of the argument that contains the subject ID.
        :param experiment_arg: The name of the argument that contains the experiment ID.
        :return: A decorator that provides a subject's assignment to a function.
        :rtype: Callable
        :raises ValueError: if missing a subject ID/arg OR experiment ID/arg.
        """

        is_valid = has_valid_args(subject_id, subject_arg, experiment_id, experiment_arg)
        if isinstance(is_valid, ValueError):
            raise is_valid

        def decorator(func: Union[Callable, Awaitable]):
            if hasattr(func, '__call__') and hasattr(func, '__code__'):
                if asyncio.iscoroutinefunction(func):
                    @wraps(func)
                    async def wrapper(*args, **kwargs):
                        subject = get_subject_id(kwargs, subject_id, subject_arg)
                        experiment = get_experiment_id(kwargs, experiment_id, experiment_arg)
                        self.logger.debug(f"Making assignment for subject={subject}, experiment={experiment}")
                        assignment = self.create_assignment(subject, experiment)
                        return await func(*args, assignment=assignment, **kwargs)
                    return wrapper
                else:
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        subject = get_subject_id(kwargs, subject_id, subject_arg)
                        experiment = get_experiment_id(kwargs, experiment_id, experiment_arg)
                        self.logger.debug(f"Making assignment for subject={subject}, experiment={experiment}")
                        assignment = self.create_assignment(subject, experiment)
                        return func(*args, assignment=assignment, **kwargs)
                    return wrapper
            else: # pragma: no cover - any respectible IDE won't allow this to happen
                raise TypeError("Wrapped object must be a callable function")
        return decorator

    def if_assignment(self, variant_id: str, subject_id: Optional[str] = None, experiment_id: Optional[str] = None, subject_arg: Optional[str] = None, experiment_arg: Optional[str] = None, create_assignment: bool = True):
        """Decorator that only runs a function if a subject is assigned a specific variant within an experiment. Requires a subject ID/arg AND experiment ID/arg.

        :param subject_id: The ID of the subject to check the assignment for.
        :param experiment_id: The ID of the experiment to check the assignment for.
        :param subject_arg: The name of the argument that contains the subject ID.
        :param experiment_arg: The name of the argument that contains the experiment ID.
        :param create_assignment: Whether to create an assignment if one doesn't exist.
        :return: A decorator that only runs a function if a subject is assigned a specific variant within an experiment.
        :rtype: Callable
        :raises ValueError: if missing a subject ID/arg OR experiment ID/arg.
        """

        is_valid = has_valid_args(subject_id, subject_arg, experiment_id, experiment_arg)
        if isinstance(is_valid, ValueError):
            raise is_valid
        
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                subject = get_subject_id(kwargs, subject_id, subject_arg)
                experiment = get_experiment_id(kwargs, experiment_id, experiment_arg)
                return func(*args, **kwargs) if self.check_variant(subject, experiment, variant_id, create_assignment) else None
            return wrapper
        return decorator

    def unless_assignment(self, variant_id: str, subject_id: Optional[str] = None, experiment_id: Optional[str] = None, subject_arg: Optional[str] = None, experiment_arg: Optional[str] = None, create_assignment: bool = True):
        """Decorator that only runs a function if a subject is NOT assigned a specific variant within an experiment. Requires a subject ID/arg AND experiment ID/arg.

        :param subject_id: The ID of the subject to check the assignment for.
        :param experiment_id: The ID of the experiment to check the assignment for.
        :param subject_arg: The name of the argument that contains the subject ID.
        :param experiment_arg: The name of the argument that contains the experiment ID.
        :param create_assignment: Whether to create an assignment if one doesn't exist.
        :return: A decorator that only runs a function if a subject is assigned a specific variant within an experiment.
        :rtype: Callable
        :raises ValueError: if missing a subject ID/arg OR experiment ID/arg.
        """

        is_valid = has_valid_args(subject_id, subject_arg, experiment_id, experiment_arg)
        if isinstance(is_valid, ValueError):
            raise is_valid
        
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                subject = get_subject_id(kwargs, subject_id, subject_arg)
                experiment = get_experiment_id(kwargs, experiment_id, experiment_arg)
                return func(*args, **kwargs) if not self.check_variant(subject, experiment, variant_id, create_assignment) else None
            return wrapper
        return decorator
