from typing import Optional

def has_valid_args(subject_id: Optional[str] = None, subject_arg: Optional[str] = None, experiment_id: Optional[str] = None, experiment_arg: Optional[str] = None) -> bool | ValueError:
    """Check if the arguments are valid.
    
    :param subject_id: The subject ID.
    :param subject_arg: The subject argument containing the subject ID.
    :param experiment_id: The experiment ID.
    :param experiment_arg: The experiment argument containing the experiment ID.
    :return: True if the arguments are valid, a ValueError if the arguments are invalid.
    """
    if subject_id and subject_arg:
        return ValueError("Either subject_id or subject_arg must be provided, not both")
    if experiment_id and experiment_arg:
        return ValueError("Either experiment_id or experiment_arg must be provided, not both")

    # Make sure we have at least one of subject_id or subject_arg, and one of experiment_id or experiment_arg
    if not subject_id and not subject_arg:
        return ValueError("Either subject_id or subject_arg must be provided")
    if not experiment_id and not experiment_arg:
        return ValueError("Either experiment_id or experiment_arg must be provided")
    
    return True

def get_subject_id(kwargs: dict, subject_id: Optional[str] = None, subject_arg: Optional[str] = None) -> str | None:
    """Get the subject ID from the kwargs or the subject_id argument.

    :param kwargs: The kwargs passed to the function.
    :param subject_id: The subject ID.
    :param subject_arg: The subject argument containing the subject ID.
    :return: The subject ID.
    :raises ValueError: if missing a subject ID/arg.
    """
    if subject_arg:
        subject = kwargs.get(subject_arg)
        if not subject:
            raise ValueError(f"Missing subject argument '{subject_arg}'")
        return subject
    elif subject_id:
        return subject_id
    else:
        # This should never happen since we check for this in the decorators, but we'll raise an error if it does
        raise ValueError("Either subject_id or subject_arg must be provided")
    
def get_experiment_id(kwargs: dict, experiment_id: Optional[str] = None, experiment_arg: Optional[str] = None) -> str | None:
    """Get the experiment ID from the kwargs or the experiment_id argument.

    :param kwargs: The kwargs passed to the function.
    :param experiment_id: The experiment ID.
    :param experiment_arg: The experiment argument containing the experiment ID.
    :return: The experiment ID.
    :raises ValueError: if missing an experiment ID/arg.
    """
    if experiment_arg:
        experiment = kwargs.get(experiment_arg)
        if not experiment:
            raise ValueError(f"Missing experiment argument '{experiment_arg}'")
        return experiment
    elif experiment_id:
        return experiment_id
    else:
        # This should never happen since we check for this in the decorators, but we'll raise an error if it does
        raise ValueError("Either experiment_id or experiment_arg must be provided")