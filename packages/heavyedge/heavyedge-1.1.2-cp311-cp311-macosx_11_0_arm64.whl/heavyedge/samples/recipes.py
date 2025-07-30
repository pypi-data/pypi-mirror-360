"""Recipies to build sample data."""

from . import get_sample_path

RECIPES = {
    "Prep-Type1.h5": lambda path: [
        "heavyedge",
        "prep",
        "--type",
        "csvs",
        "--config",
        get_sample_path("config-prep.yml"),
        get_sample_path("Type1"),
        "-o",
        path,
    ],
    "Prep-Type2.h5": lambda path: [
        "heavyedge",
        "prep",
        "--type",
        "csvs",
        "--config",
        get_sample_path("config-prep.yml"),
        get_sample_path("Type2"),
        "-o",
        path,
    ],
    "Prep-Type3.h5": lambda path: [
        "heavyedge",
        "prep",
        "--type",
        "csvs",
        "--config",
        get_sample_path("config-prep.yml"),
        get_sample_path("Type3"),
        "-o",
        path,
    ],
}
