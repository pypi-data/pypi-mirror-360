import logging
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np

from ioos_qc.qartod import QartodFlags

L = logging.getLogger(__name__)


class CallResult(NamedTuple):
    package: str
    test: str
    function: callable
    results: np.ndarray

    def __repr__(self) -> str:
        return f"<CallResult package={self.package} test={self.test}>"


class ContextResult(NamedTuple):
    stream_id: str
    results: list[CallResult]
    subset_indexes: np.ndarray
    data: np.ndarray = None
    tinp: np.ndarray = None
    zinp: np.ndarray = None
    lat: np.ndarray = None
    lon: np.ndarray = None

    def __repr__(self) -> str:
        return f"<ContextResult stream_id={self.stream_id}>"


@dataclass
class CollectedResult:
    stream_id: str
    package: str
    test: str
    function: callable
    results: np.ma.core.MaskedArray = None
    data: np.ndarray = None
    tinp: np.ndarray = None
    zinp: np.ndarray = None
    lat: np.ndarray = None
    lon: np.ndarray = None

    def __repr__(self) -> str:
        return f"<CollectedResult stream_id={self.stream_id} package={self.package} test={self.test}>"

    def function_name(self) -> str:
        return self.function.__name__

    @property
    def hash_key(self) -> str:
        return f"{self.stream_id}:{self.package}.{self.test}"


def collect_results(results, how="list"):
    if how in ["list", list]:
        return collect_results_list(results)
    if how in ["dict", dict]:
        return collect_results_dict(results)
    return None


def collect_results_list(results):
    """Turns a list of ContextResult objects into an iterator of CollectedResult objects
    by combining the subset_index information in each ContextResult together into
    a single array of results.
    """
    collected = OrderedDict()

    # ContextResults
    for r in results:
        cr = None
        # Shortcut for CallResult objects when someone uses QcConfig.run() directly
        # and doesn't go through a Stream object
        if isinstance(r, CallResult):
            cr = CollectedResult(
                stream_id=None,
                package=r.package,
                test=r.test,
                function=r.function,
                results=r.results,
            )
            collected[cr.hash_key] = cr
            continue

        # CallResults
        for tr in r.results:
            cr = CollectedResult(
                stream_id=r.stream_id,
                package=tr.package,
                test=tr.test,
                function=tr.function,
            )

            if cr.hash_key not in collected:
                # Set the initial values
                cr.results = np.ma.masked_all(
                    shape=r.subset_indexes.shape,
                    dtype=tr.results.dtype,
                )
                cr.data = np.ma.masked_all(
                    shape=r.subset_indexes.shape,
                    dtype=r.data.dtype,
                )
                cr.tinp = np.ma.masked_all(
                    shape=r.subset_indexes.shape,
                    dtype=r.tinp.dtype,
                )
                cr.zinp = np.ma.masked_all(
                    shape=r.subset_indexes.shape,
                    dtype=r.zinp.dtype,
                )
                cr.lat = np.ma.masked_all(
                    shape=r.subset_indexes.shape,
                    dtype=r.lat.dtype,
                )
                cr.lon = np.ma.masked_all(
                    shape=r.subset_indexes.shape,
                    dtype=r.lon.dtype,
                )
                collected[cr.hash_key] = cr

            collected[cr.hash_key].results[r.subset_indexes] = tr.results

        if cr is not None:
            if r.subset_indexes.all():
                collected[cr.hash_key].data = r.data
                collected[cr.hash_key].tinp = r.tinp
                collected[cr.hash_key].zinp = r.zinp
                collected[cr.hash_key].lat = r.lat
                collected[cr.hash_key].lon = r.lon
            else:
                collected[cr.hash_key].data[r.subset_indexes] = r.data
                collected[cr.hash_key].tinp[r.subset_indexes] = r.tinp
                collected[cr.hash_key].zinp[r.subset_indexes] = r.zinp
                collected[cr.hash_key].lat[r.subset_indexes] = r.lat
                collected[cr.hash_key].lon[r.subset_indexes] = r.lon

    return list(collected.values())


def collect_results_dict(results):
    """Turns a list of ContextResult objects into a dictionary of test results
    by combining the subset_index information in each ContextResult together into
    a single array of results. This is mostly here for historical purposes. Users
    should migrate to using the Result objects directly.
    """
    # Magic for nested key generation
    # https://stackoverflow.com/a/27809959
    collected = defaultdict(lambda: defaultdict(OrderedDict))

    # ContextResults
    for r in results:
        # Shortcut for CallResult objects when someone uses QcConfig.run() directly
        # and doesn't go through a Stream object
        if isinstance(r, CallResult):
            collected[r.package][r.test] = r.results
            continue

        flag_arr = np.ma.empty_like(r.subset_indexes, dtype="uint8")
        flag_arr.fill(QartodFlags.UNKNOWN)

        # iterate over the CallResults
        for tr in r.results:
            testpackage = tr.package
            testname = tr.test
            testresults = tr.results

            if testname not in collected[r.stream_id][testpackage]:
                collected[r.stream_id][testpackage][testname] = np.copy(
                    flag_arr,
                )
            collected[r.stream_id][testpackage][testname][r.subset_indexes] = testresults

    return collected
