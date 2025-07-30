import calendar
import datetime
import json
import logging
from copy import copy
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from jsonschema import validate
from scipy.interpolate import CubicSpline

from ioos_qc.config_creator import fx_parser

L = logging.getLogger(__name__)


QC_CONFIG_CREATOR_SCHEMA = {
    "type": "object",
    "title": "QcConfigCreator Schema",
    "description": "Schema to validate configuration for QcCreatorConfig",
    "required": [
        "datasets",
    ],
    "definitions": {
        "variable": {
            "type": "object",
            "title": "Variable map (variable name in QcConfig -> variable name in dataset",
            "items": {"type": "object"},
        },
        "dataset": {
            "type": "object",
            "title": "Dataset description",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of dataset",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file used to create configuration.",
                },
                "variables": {
                    "type": "object",
                    "description": "Variables in file used to create configuration.",
                },
                "3d": {
                    "type": "string",
                    "description": "Include if 3d dataset with value being the name of the 3rd dimension",
                },
            },
            "required": [
                "name",
                "file_path",
                "variables",
            ],
        },
    },
    "properties": {
        "datasets": {
            "type": "array",
            "description": "Array of datasets used for QcCreatorConfig",
            "items": {
                "$ref": "#/definitions/dataset",
            },
        },
    },
}

VARIABLE_CONFIG_SCHEMA = {
    "type": "object",
    "title": "QcVariableConfig",
    "description": "Schema to validate configuration for QcVariableConfig",
    "required": [
        "variable",
        "bbox",
        "start_time",
        "end_time",
        "tests",
    ],
    "definitions": {
        "test": {
            "type": "object",
            "description": "Test (gross_range_test, etc.) definition",
            "required": [
                "suspect_min",
                "suspect_max",
                "fail_min",
                "fail_max",
            ],
            "properties": {
                "suspect_min": {
                    "type": "string",
                    "description": "Function or value to define suspect min",
                },
                "suspect_max": {
                    "type": "string",
                    "description": "Function or value to define suspect max",
                },
                "fail_min": {
                    "type": "string",
                    "description": "Function or value to define fail min",
                },
                "fail_max": {
                    "type": "string",
                    "description": "Function or value to define fail max",
                },
            },
        },
    },
    "properties": {
        "variable": {
            "type": "string",
            "description": "Variable name. The same name used as a key in 'variable' object in CreatorConfig",
        },
        "bbox": {
            "type": "array",
            "description": "Bounding box of region in deployment (xmin, ymin, xmax, ymax)",
        },
        "start_time": {
            "type": "string",
            "description": "Start time of deployment (YYYY-MM-DD)",
        },
        "end_time": {
            "type": "string",
            "description": "Exclusive end time of deployment (YYYY-MM-DD)",
        },
        "tests": {
            "type": "object",
            "items": {
                "$ref": "#/definitions/test",
            },
        },
    },
}


class CreatorConfig(dict):
    """Defines the dataset(s) configuration used by QcConfigCreator.

    :param path_or_dict: QcConfigCreator configuration, one of the following formats:
        python dict
        JSON filepath (str or Path object)
    :param dict: JSON schema for CreatorConfig
    """

    def __init__(self, path_or_dict, schema=QC_CONFIG_CREATOR_SCHEMA) -> None:
        if isinstance(path_or_dict, (Path, str)):
            path_or_dict = Path(path_or_dict)
            with path_or_dict.open() as f:
                config = json.load(f)
        elif isinstance(path_or_dict, dict):
            config = path_or_dict
        else:
            msg = f"Input {path_or_dict} is not valid file path or dict."
            raise TypeError(msg)
        validate(instance=config, schema=schema)

        datasets = {}
        for dataset in config["datasets"]:
            if "3d" in dataset:
                datasets[dataset["name"]] = {
                    "file_path": dataset["file_path"],
                    "variables": dataset["variables"],
                    "3d": dataset["3d"],
                }
            else:
                datasets[dataset["name"]] = {
                    "file_path": dataset["file_path"],
                    "variables": dataset["variables"],
                }
        self.update(datasets)

    def __str__(self) -> str:
        return json.dumps(self, indent=4, sort_keys=True)


class QcVariableConfig(dict):
    """Used to generate a QcConfig for a specific variable.

    Parameters
    ----------
    path_or_dict
        QcVariableConfig configuration, one of the following formats:
            python dict
            JSON filepath (str or Path object)
    schema
        JSON schema for QcVariable

    """

    allowed_stats = (
        "min",
        "max",
        "mean",
        "std",
    )
    allowed_operators = (
        "+",
        "-",
        "*",
        "/",
    )
    allowed_groupings = (
        "(",
        ")",
    )

    def __init__(self, path_or_dict, schema=VARIABLE_CONFIG_SCHEMA) -> None:
        if isinstance(path_or_dict, (Path, str)):
            path_or_dict = Path(path_or_dict)
            with path_or_dict.open() as f:
                config = json.load(f)
        elif isinstance(path_or_dict, dict):
            config = path_or_dict
        else:
            msg = f"Input {path_or_dict} is not valid file path or dict."
            raise TypeError(msg)

        L.debug("Validating schema...")
        validate(instance=config, schema=schema)

        # validate test specifications only contain allowed stats and operators
        for test in config["tests"]:
            for test_name, test_def in config["tests"][test].items():
                if test_name == "bbox":
                    continue
                self._validate_fx(test_def, test_name)

        self.update(config)

    def _validate_fx(self, input_fx, test_name) -> None:
        """Throws exception if input_fx contains tokens not specifically allowed."""
        tokens = input_fx.split(" ")
        for token in tokens:
            try:
                _ = float(token)
            except ValueError as err:  # noqa: PERF203
                if token not in self.allowed_stats and token not in self.allowed_operators and token not in self.allowed_groupings:
                    msg = (
                        f"{token} not allowed in min/max specification in config of {test_name}.\n"
                        f"Allowable stats are: {list(self.allowed_stats)}.\n"
                        f"Allowable operators are: {list(self.allowed_operators)}."
                        f"Allowable groupings are: {list(self.allowed_groupings)}."
                    )
                    raise ValueError(msg) from err

    def __str__(self) -> str:
        return json.dumps(self, indent=4, sort_keys=True)


class QcConfigCreator:
    """Creates level-0 configuration to create QcQonfig.

    Arguments:
    ---------
    creator_config (QcCreatorConfig)
        Configuration for datasets and variables used to create qc_config.

    Attributes:
    ----------
    allowed_stats (list)
        Specific statistics allowed to be used to configure each test.
    allowed_operators (list)
        Operators allowed to used to configure each test.

    """

    def __init__(self, creator_config) -> None:
        self.config = creator_config
        self.datasets = self._load_datasets()
        self.dataset_years = self._determine_dataset_years()

    def create_config(self, variable_config):
        """Create QARTOD QC config given QcVariableConfig.

        Parameters
        ----------
        variable_config (QcVariableConfig)
            Config for variable to be quality controlled

        Returns
        -------
        qc_config (dict)
            Config for ioos_qc

        """
        stats = self._get_stats(variable_config)
        L.debug("Creating config...")
        test_configs = {name: self._create_test_section(name, variable_config, stats) for name in variable_config["tests"]}

        return {
            f"{variable_config['variable']}": {
                "qartod": test_configs,
            },
        }

    def _load_datasets(self):
        """Load datasets."""
        L.debug(f"Loading {len(self.config)} datasets...")
        return {name: xr.load_dataset(self.config[name]["file_path"]) for name in self.config}

    def _determine_dataset_years(self):
        """Determine year used in datasets, return as dict {dataset_name, year}.

        Notes
        -----
        - Each dataset is from a unique climatology or source,
            so the monthly files have different years.

        """
        years = {}
        for dataset_name, dataset in self.datasets.items():
            years[dataset_name] = dataset["time.year"][0].data

        return years

    def _var2var_in_file(self, var):
        """Return variable name used in the dataset and dataset name."""
        for dataset_name, dataset in self.config.items():
            if var in dataset["variables"]:
                return dataset["variables"][var], dataset_name
        return None

    def var2dataset(self, var):
        """Return dataset name and dataset for given variable (as named in qc_config, not in the file)."""
        _, dataset_name = self._var2var_in_file(var)

        return dataset_name, self.datasets[dataset_name]

    def _create_test_section(self, test_name, variable_config, test_limits):
        """Given test_name, QcVariableConfig and test_limits, return qc_config section for that test."""
        if test_name == "spike_test":
            return self.__create_spike_section(
                test_name,
                variable_config,
                test_limits,
            )
        if test_name == "location_test":
            return self.__create_location_section(test_name, variable_config)
        if test_name == "rate_of_change_test":
            return self.__create_rate_of_change_section(
                test_name,
                variable_config,
                test_limits,
            )
        if test_name == "flat_line_test":
            return self.__create_flat_line_section(
                test_name,
                variable_config,
                test_limits,
            )
        return self.__create_span_section(
            test_name,
            variable_config,
            test_limits,
        )

    def __create_span_section(self, test_name, variable_config, stats):
        suspect_min = fx_parser.eval_fx(
            variable_config["tests"][test_name]["suspect_min"],
            stats,
        )
        suspect_max = fx_parser.eval_fx(
            variable_config["tests"][test_name]["suspect_max"],
            stats,
        )
        fail_min = fx_parser.eval_fx(
            variable_config["tests"][test_name]["fail_min"],
            stats,
        )
        fail_max = fx_parser.eval_fx(
            variable_config["tests"][test_name]["fail_max"],
            stats,
        )

        return {
            "suspect_span": [suspect_min, suspect_max],
            "fail_span": [fail_min, fail_max],
        }

    def __create_spike_section(self, test_name, variable_config, stats):
        suspect_threshold = fx_parser.eval_fx(
            variable_config["tests"][test_name]["suspect_threshold"],
            stats,
        )
        fail_threshold = fx_parser.eval_fx(
            variable_config["tests"][test_name]["fail_threshold"],
            stats,
        )

        return {
            "suspect_threshold": suspect_threshold,
            "fail_threshold": fail_threshold,
        }

    def __create_flat_line_section(self, test_name, variable_config, stats):
        suspect_threshold = fx_parser.eval_fx(
            variable_config["tests"][test_name]["suspect_threshold"],
            stats,
        )
        fail_threshold = fx_parser.eval_fx(
            variable_config["tests"][test_name]["fail_threshold"],
            stats,
        )
        tolerance = fx_parser.eval_fx(
            variable_config["tests"][test_name]["tolerance"],
            stats,
        )

        return {
            "suspect_threshold": suspect_threshold,
            "fail_threshold": fail_threshold,
            "tolerance": tolerance,
        }

    def __create_location_section(self, test_name, variable_config):
        return {
            "bbox": variable_config["tests"][test_name]["bbox"],
        }

    def __create_rate_of_change_section(
        self,
        test_name,
        variable_config,
        stats,
    ):
        threshold = fx_parser.eval_fx(
            variable_config["tests"][test_name]["threshold"],
            stats,
        )
        return {
            "threshold": threshold,
        }

    def _get_stats(self, variable_config):
        """Return dict of stats (min, max, mean, std) for given config."""
        start_time = datetime.datetime.strptime(
            variable_config["start_time"],
            "%Y-%m-%d",
        ).replace(tzinfo=datetime.timezone.utc)
        end_time = datetime.datetime.strptime(
            variable_config["end_time"],
            "%Y-%m-%d",
        ).replace(tzinfo=datetime.timezone.utc)
        time_range = slice(start_time, end_time)
        subset = self._get_subset(
            variable_config["variable"],
            variable_config["bbox"],
            time_range,
        )

        return {
            "min": np.nanmin(subset),
            "max": np.nanmax(subset),
            "mean": np.nanmean(subset),
            "std": np.nanstd(subset),
        }

    def _get_subset(self, var, bbox, time_slice, depth=0, pad_delta=0.5):
        """Get subset of data."""
        _, ds = self.var2dataset(var)

        lat_mask = np.logical_and(
            ds["lat"] >= bbox[1],
            ds["lat"] <= bbox[3],
        )
        lon_mask = np.logical_and(
            ds["lon"] >= bbox[0],
            ds["lon"] <= bbox[2],
        )

        # if there is no data in the subset, increase bounding box in an iterative fashion
        # - both are interpolated to daily values
        L.debug(f"Subsetting {var} by depth={depth} and {bbox}...")
        subset = self.__get_daily_interp_subset(
            var,
            time_slice,
            depth,
            lat_mask,
            lon_mask,
        )

        padded = 0
        while np.nansum(subset) == 0:
            old_bbox = copy(bbox)
            bbox = self.__apply_bbox_pad(bbox, pad_delta)

            if old_bbox == bbox:
                L.warning(f"No data found for {var} at depth={depth}")
                break

            lat_mask = np.logical_and(
                ds["lat"] >= bbox[1],
                ds["lat"] <= bbox[3],
            )
            lon_mask = np.logical_and(
                ds["lon"] >= bbox[0],
                ds["lon"] <= bbox[2],
            )

            padded += 1
            subset = self.__get_daily_interp_subset(
                var,
                time_slice,
                depth,
                lat_mask,
                lon_mask,
            )

        L.info(f"Used bounding box: {bbox}")
        return subset

    def __apply_bbox_pad(self, bbox, pad):
        # Prevent infinite attempts of expanding bounding box for valid data
        if bbox == ["-180", "-90", "180", "90"]:
            msg = f"No valid data found in maximum bounding box {bbox}"
            raise RuntimeError(msg)

        def apply_pad(val, lat_or_lon, min_or_max):
            if lat_or_lon == "lat":
                if min_or_max == "min":
                    return max(-90, val - pad)
                return min(90, val + pad)
            if val <= 0 and min_or_max == "min":
                return max(-180, val - pad)
            if val <= 0 and min_or_max == "max":
                return min(180, val + pad)
            if val > 0 and min_or_max == "min":
                return max(-180, val - pad)
            return min(180, val + pad)

        new_bbox = []
        new_bbox.append(apply_pad(bbox[0], "lon", "min"))
        new_bbox.append(apply_pad(bbox[1], "lat", "min"))
        new_bbox.append(apply_pad(bbox[2], "lon", "max"))
        new_bbox.append(apply_pad(bbox[3], "lat", "max"))

        L.debug(f"Expanded bounding box to {bbox}")

        return new_bbox

    def __get_daily_interp_subset(
        self,
        var,
        time_slice,
        depth,
        lat_mask,
        lon_mask,
    ):
        ds_name, ds = self.var2dataset(var)
        var_in_file, _ = self._var2var_in_file(var)

        var = ds[var_in_file][:, depth, lat_mask, lon_mask] if "3d" in self.config[ds_name] else ds[var_in_file][:, lat_mask, lon_mask]

        # try cubic interpolation to daily values
        try:
            return self.__daily_cubic_interp(var, time_slice)
        except ValueError:  # Raises exception is subset in bbox is all NaNs
            return 0

    def __daily_cubic_interp(self, var, time_slice):
        """Given DataArray and time_slice, interpolate to daily values and return NumPy array.

        Notes
        -----
        - Uses day of year for interpolation
        - Adds data for day 1 and 366 to ensure periodicity if required to ensure periodicity

        """
        full_year = 365
        if (time_slice.stop - time_slice.start).days > full_year:
            msg = "Maximum of 365 days available for config_creator"
            raise NotImplementedError(msg)

        x = var.time.dt.dayofyear
        y = var.data
        min_day, max_day = 1, 366
        if min_day not in x and max_day not in x:
            x = np.hstack([min_day, x, max_day])
            # add new average value at beginning and end to ensure periodicity
            end_value = (y[0:1, :, :] + y[-1:, :, :]) / 2
            y = np.concatenate([end_value, y, end_value])
        elif min_day not in x:
            x = np.hstack([min_day, x])
            # add new beginning value that is equal to end value to ensure periodicity
            y = np.concatenate([y[-1:, :, :], y])
        else:  # 366 must not be in x, but 1 is
            x = np.hstack([x, max_day])
            # add new end value that is equal to beginning value to ensure periodicity
            y = np.concatenate([y, y[0:1, :, :]])

        # Create interpolator
        # Need to handle NaNs in data before applying interpolator
        # - mask out NaNs
        # - reshape masked y to (ntimes, ...) where ntimes is y.shape[0]
        # - assume that NaNs are same shape through time (i.e. will not work with wetting-drying)
        y_no_nans = y[~np.isnan(y)].reshape(y.shape[0], -1)
        if y_no_nans.size == 0:
            msg = "CubicSpline require y to the finite."
            raise ValueError(msg)
        spline = CubicSpline(x, y_no_nans, bc_type="periodic")

        # Get days of year for independent variable
        # - special handling for when time-slice crosses new year
        doy_start = pd.Timestamp(time_slice.start).dayofyear
        doy_end = pd.Timestamp(time_slice.stop).dayofyear
        if doy_start > doy_end:  # days cross new year
            days = list(range(doy_start, 367)) + list(range(1, doy_end))
            if not calendar.isleap(time_slice.start.year):
                days.remove(366)
        else:
            days = list(range(doy_start, doy_end))

        return spline(days)

    def __str__(self) -> str:
        return json.dumps(self.config, indent=4, sort_keys=True)

    def __rpr__(self):
        return self.__str__


def to_json(qc_config, out_file=None):
    """Given qc_config return json."""
    out_file = Path(out_file)
    if out_file:
        with out_file.open("w") as f:
            json.dump(f, qc_config)
            return None
    else:
        return json.dumps(qc_config)
