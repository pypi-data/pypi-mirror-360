from collections.abc import Iterable
from typing import Optional, Union, Any
from enum import Enum
from statistics import mode, mean

from .lookup import download_lookup, get_table_value, column_name
from .tools import non_empty_list


def get_lookup_value(blank_node: dict, column: str):
    term = blank_node.get('term', {})
    table_name = f"{term.get('termType')}.csv" if term else None
    value = get_table_value(
        download_lookup(table_name), 'termid', term.get('@id'), column_name(column)
    ) if table_name else None
    return value


class ArrayTreatment(Enum):
    """
    Enum representing different treatments for arrays of values.
    """
    MEAN = 'mean'
    MODE = 'mode'
    SUM = 'sum'
    FIRST = 'first'
    LAST = 'last'


def _should_run_array_treatment(value):
    return isinstance(value, Iterable) and len(value) > 0


DEFAULT_ARRAY_TREATMENT = ArrayTreatment.MEAN
ARRAY_TREATMENT_TO_REDUCER = {
    ArrayTreatment.MEAN: lambda value: mean(non_empty_list(value)) if _should_run_array_treatment(value) else None,
    ArrayTreatment.MODE: lambda value: mode(non_empty_list(value)) if _should_run_array_treatment(value) else None,
    ArrayTreatment.SUM: lambda value: sum(non_empty_list(value)) if _should_run_array_treatment(value) else None,
    ArrayTreatment.FIRST: lambda value: value[0] if _should_run_array_treatment(value) else None,
    ArrayTreatment.LAST: lambda value: value[-1] if _should_run_array_treatment(value) else None
}
"""
A dictionary mapping ArrayTreatment enums to corresponding reducer functions.
"""


def _retrieve_array_treatment(
    node: dict,
    is_larger_unit: bool = False,
    default: ArrayTreatment = ArrayTreatment.MEAN
) -> ArrayTreatment:
    """
    Retrieves the array treatment for a given node.

    Array treatments are used to reduce an array's list of values into
    a single value. The array treatment is retrieved from a lookup on
    the node's term.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    is_larger_unit : bool, optional
        Flag indicating whether to use the larger unit lookup, by default `False`.
    default : ArrayTreatment, optional
        Default value to return if the lookup fails, by default `ArrayTreatment.MEAN`.

    Returns
    -------
    ArrayTreatment
        The retrieved array treatment.

    """
    ARRAY_TREATMENT_LOOKUPS = [
        'arrayTreatmentLargerUnitOfTime',
        'arrayTreatment'
    ]
    lookup = ARRAY_TREATMENT_LOOKUPS[0] if is_larger_unit else ARRAY_TREATMENT_LOOKUPS[1]

    lookup_value = get_lookup_value(node, lookup)

    return next(
        (treatment for treatment in ArrayTreatment if treatment.value == lookup_value),
        default
    )


def get_node_value(
    node: dict,
    key: str = 'value',
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
    default: Any = 0
) -> Union[float, bool]:
    """
    Get the value from the dictionary representing the node,
    applying optional array treatment if the value is a list.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    key : str
        The key to retrieve the value for. Will use `value` by default.
    is_larger_unit : bool, optional
        A flag indicating whether the unit of time is larger, by default `False`.
    array_treatment : ArrayTreatment, optional
        An optional override for the treatment to be applied to an array value, if `None` the array treatment in the
        node's term's lookup is used (which defaults to `FIRST` if no array treatment is specified), by default `None`.
    default : any
        The default value, if no value is found or it could not be parsed.

    Returns
    -------
    float | bool
        The extracted value from the node.
    """
    value = node.get(key)

    reducer = ARRAY_TREATMENT_TO_REDUCER[(
        array_treatment or _retrieve_array_treatment(
            node, is_larger_unit=is_larger_unit)
    )] if isinstance(value, list) and len(value) > 0 else None

    return reducer(value) if reducer else (
        value if any([isinstance(value, float), isinstance(value, int), isinstance(value, bool)])
        else (value or default)
    )
