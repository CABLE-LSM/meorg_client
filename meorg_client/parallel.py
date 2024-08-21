"""Methods for parallel execution."""

import pandas as pd
import multiprocessing as mp
from tqdm import tqdm


def _execute(mp_args: tuple):
    """Execute an instance of the parallel function.

    Parameters
    ----------
    mp_args : tuple
        2-tuple consisting of a callable and an arguments dictionary.

    Returns
    -------
    mixed
        Returning value of the callable.
    """
    return mp_args[0](**mp_args[1])


def _convert_kwargs(**kwargs):
    """Convert a dict of lists and scalars into even lists for parallel execution.

    Returns
    -------
    dict
        A dictionary of lists of arguments.
    """
    return pd.DataFrame(kwargs).to_dict("records")


def parallelise(func: callable, num_threads: int, progress=True, **kwargs):
    """Execute `func` in parallel over `num_threads`.

    Parameters
    ----------
    func : callable
        Function to parallelise.
    num_threads : int
        Number of threads.
    **kwargs :
        Keyword arguments for `func` all lists must have equal length, scalars will be converted to lists.

    Returns
    -------
    mixed
        Returning value of `func`.
    """

    # Convert the kwargs to argument list of dicts
    mp_args = _convert_kwargs(**kwargs)

    # Attach the function pointer as the first argument
    mp_args = [[func, mp_arg] for mp_arg in mp_args]

    # Start with empty results
    results = list()

    # Establish a pool of workers (blocking)
    with mp.Pool(processes=num_threads) as pool:

        if progress:

            with tqdm(total=len(mp_args)) as pbar:
                for result in pool.map(_execute, mp_args):
                    results.append(result[0])
                    pbar.update()

        else:

            for result in pool.map(_execute, mp_args):
                results.append(result[0])

    # Return the results
    return results
