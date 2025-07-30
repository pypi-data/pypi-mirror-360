from sqlmodel import SQLModel

from common.database.utils import find_primary_key


class NotFoundInDatabaseError(Exception):
    pass


def get_job_parameters(job_fn: callable, ensure_sql_model: bool = True) -> dict:
    retval = {}
    retval["method_name"] = job_fn.__name__
    
    # Check if the function is bound
    if hasattr(job_fn, "__self__"):
        # Function is bound
        instance = job_fn.__self__
        if ensure_sql_model:
            # Ensure that the class is a SQL model
            assert isinstance(instance, SQLModel), "The class must be a SQLModel"

        # Get the class name and module
        retval["model_name"] = instance.__class__.__name__
        retval["module_name"] = instance.__class__.__module__  # Add module name of the instance's class

        # Get the primary key name
        primary_key_name = find_primary_key(instance.__class__)
        if primary_key_name is not None:
            retval["instance_primary_key"] = getattr(instance, primary_key_name)
    return retval
