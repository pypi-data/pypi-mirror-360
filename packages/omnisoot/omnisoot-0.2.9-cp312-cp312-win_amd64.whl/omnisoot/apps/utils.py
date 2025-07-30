from collections.abc import Iterable
from operator import sub
import numpy as np

def is_positive_number(var) -> bool:
    return isinstance(var, (int, float)) and var > 0;

def is_nonnegative_number(var) -> bool:
    return isinstance(var, (int, float)) and var >= 0;

def is_iterable(profile) -> bool:
    return isinstance(profile, Iterable);

def is_numpy_array(profile) -> bool:
    return isinstance(profile, np.ndarray);

def is_iterable_of_numbers(vector) -> bool:
    return (
        isinstance(vector, Iterable) 
        and 
        all(
            map(
                lambda var: isinstance(var, (int, float)),
                vector
            )
        )
    );

def is_nonnegative_array(vector) -> bool:
     return (
        all(
            map(
                lambda var: var >= 0.0,
                vector
            )
        )
    )   

def is_increasing_vector(vector) -> bool:
    return (
        all(
            map(
                lambda var: var > 0, 
                map(sub, vector[1:], vector[:-1])
            )
        )
    )

def process_set_profile(profile) -> bool:
    # Numpy array
    if is_numpy_array(profile):
        if profile.shape[0] != 2 or profile.shape[1] < 2:
            raise ValueError("Expected a numpy array with the shape of (2,n)!");
        if not is_nonnegative_array(profile[0, :]):
            raise ValueError("The first row of profile must be a positive vector!");
        if not is_increasing_vector(profile[0, :]):
            raise ValueError("The first row of profile must be an increasing vector!");
        _profile = profile;
    # Other iterables
    elif is_iterable(profile):
        if len(profile) != 2:
            raise ValueError("Expected an iterable of two vectors!");
        if len(profile[0]) != len(profile[1]):
            raise ValueError("Expected an iterable of two iterables of the same size!");
        if not (is_iterable_of_numbers(profile[0]) and is_iterable_of_numbers(profile[1])):
            raise ValueError("Expected an iterable of two iterables of numbers!");
        if not is_nonnegative_array(profile[0]):
            raise ValueError("The first iterable of profile must be a positive vector!");
        if not is_increasing_vector(profile[0]):
            raise ValueError("The first iterable of profile must be an increasing vector!");
        _profile = np.array(profile);
    else:
        raise ValueError("Expected an iterable of two vectors or a numpy array with the shape of (2,n)!");
    return _profile;    
