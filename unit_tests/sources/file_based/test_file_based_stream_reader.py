#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from io import IOBase
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set

import pytest
from pydantic.v1 import AnyUrl

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from unit_tests.sources.file_based.helpers import make_remote_files

reader = AbstractFileBasedStreamReader

"""
The rules are:

- All files at top-level: /*
- All files at top-level of mydir: mydir/*
- All files anywhere under mydir: mydir/**/*
- All files in any directory: **/*
- All files in any directory that end in .csv: **/*.csv
- All files in any directory that have a .csv extension: **/*.csv*
"""

FILEPATHS = [
    "a",
    "a.csv",
    "a.csv.gz",
    "a.jsonl",
    "a/b",
    "a/b.csv",
    "a/b.csv.gz",
    "a/b.jsonl",
    "a/c",
    "a/c.csv",
    "a/c.csv.gz",
    "a/c.jsonl",
    "a/b/c",
    "a/b/c.csv",
    "a/b/c.csv.gz",
    "a/b/c.jsonl",
    "a/c/c",
    "a/c/c.csv",
    "a/c/c.csv.gz",
    "a/c/c.jsonl",
    "a/b/c/d",
    "a/b/c/d.csv",
    "a/b/c/d.csv.gz",
    "a/b/c/d.jsonl",
]
FILES = make_remote_files(FILEPATHS)

DEFAULT_CONFIG = {
    "streams": [],
}


class TestStreamReader(AbstractFileBasedStreamReader):
    @property
    def config(self) -> Optional[AbstractFileBasedSpec]:
        return self._config

    @config.setter
    def config(self, value: AbstractFileBasedSpec) -> None:
        self._config = value

    def get_matching_files(self, globs: List[str]) -> Iterable[RemoteFile]:
        pass

    def open_file(self, file: RemoteFile) -> IOBase:
        pass

    def file_size(self, file: RemoteFile) -> int:
        return 0

    def get_file(
        self, file: RemoteFile, local_directory: str, logger: logging.Logger
    ) -> Dict[str, Any]:
        return {}

    def get_file_acl_permissions(self, file: RemoteFile, logger: logging.Logger) -> Dict[str, Any]:
        return {}

    def load_identity_groups(self, logger: logging.Logger) -> Iterable[Dict[str, Any]]:
        return [{}]

    @property
    def file_permissions_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def identities_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}


class TestSpec(AbstractFileBasedSpec):
    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl(scheme="https", url="https://docs.airbyte.com/integrations/sources/test")  # type: ignore


@pytest.mark.parametrize(
    "globs,config,expected_matches,expected_path_prefixes",
    [
        pytest.param([], DEFAULT_CONFIG, set(), set(), id="no-globs"),
        pytest.param([""], DEFAULT_CONFIG, set(), set(), id="empty-string"),
        pytest.param(["**"], DEFAULT_CONFIG, set(FILEPATHS), set(), id="**"),
        pytest.param(
            ["**/*.csv"],
            DEFAULT_CONFIG,
            {"a.csv", "a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"},
            set(),
            id="**/*.csv",
        ),
        pytest.param(
            ["**/*.csv*"],
            DEFAULT_CONFIG,
            {
                "a.csv",
                "a.csv.gz",
                "a/b.csv",
                "a/b.csv.gz",
                "a/c.csv",
                "a/c.csv.gz",
                "a/b/c.csv",
                "a/b/c.csv.gz",
                "a/c/c.csv",
                "a/c/c.csv.gz",
                "a/b/c/d.csv",
                "a/b/c/d.csv.gz",
            },
            set(),
            id="**/*.csv*",
        ),
        pytest.param(["*"], DEFAULT_CONFIG, {"a", "a.csv", "a.csv.gz", "a.jsonl"}, set(), id="*"),
        pytest.param(["*.csv"], DEFAULT_CONFIG, {"a.csv"}, set(), id="*.csv"),
        pytest.param(["*.csv*"], DEFAULT_CONFIG, {"a.csv", "a.csv.gz"}, set(), id="*.csv*"),
        pytest.param(
            ["*/*"],
            DEFAULT_CONFIG,
            {
                "a/b",
                "a/b.csv",
                "a/b.csv.gz",
                "a/b.jsonl",
                "a/c",
                "a/c.csv",
                "a/c.csv.gz",
                "a/c.jsonl",
            },
            set(),
            id="*/*",
        ),
        pytest.param(["*/*.csv"], DEFAULT_CONFIG, {"a/b.csv", "a/c.csv"}, set(), id="*/*.csv"),
        pytest.param(
            ["*/*.csv*"],
            DEFAULT_CONFIG,
            {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz"},
            set(),
            id="*/*.csv*",
        ),
        pytest.param(
            ["*/**"],
            DEFAULT_CONFIG,
            {
                "a/b",
                "a/b.csv",
                "a/b.csv.gz",
                "a/b.jsonl",
                "a/c",
                "a/c.csv",
                "a/c.csv.gz",
                "a/c.jsonl",
                "a/b/c",
                "a/b/c.csv",
                "a/b/c.csv.gz",
                "a/b/c.jsonl",
                "a/c/c",
                "a/c/c.csv",
                "a/c/c.csv.gz",
                "a/c/c.jsonl",
                "a/b/c/d",
                "a/b/c/d.csv",
                "a/b/c/d.csv.gz",
                "a/b/c/d.jsonl",
            },
            set(),
            id="*/**",
        ),
        pytest.param(
            ["a/*"],
            DEFAULT_CONFIG,
            {
                "a/b",
                "a/b.csv",
                "a/b.csv.gz",
                "a/b.jsonl",
                "a/c",
                "a/c.csv",
                "a/c.csv.gz",
                "a/c.jsonl",
            },
            {"a/"},
            id="a/*",
        ),
        pytest.param(["a/*.csv"], DEFAULT_CONFIG, {"a/b.csv", "a/c.csv"}, {"a/"}, id="a/*.csv"),
        pytest.param(
            ["a/*.csv*"],
            DEFAULT_CONFIG,
            {"a/b.csv", "a/b.csv.gz", "a/c.csv", "a/c.csv.gz"},
            {"a/"},
            id="a/*.csv*",
        ),
        pytest.param(
            ["a/b/*"],
            DEFAULT_CONFIG,
            {"a/b/c", "a/b/c.csv", "a/b/c.csv.gz", "a/b/c.jsonl"},
            {"a/b/"},
            id="a/b/*",
        ),
        pytest.param(["a/b/*.csv"], DEFAULT_CONFIG, {"a/b/c.csv"}, {"a/b/"}, id="a/b/*.csv"),
        pytest.param(
            ["a/b/*.csv*"], DEFAULT_CONFIG, {"a/b/c.csv", "a/b/c.csv.gz"}, {"a/b/"}, id="a/b/*.csv*"
        ),
        pytest.param(
            ["a/*/*"],
            DEFAULT_CONFIG,
            {
                "a/b/c",
                "a/b/c.csv",
                "a/b/c.csv.gz",
                "a/b/c.jsonl",
                "a/c/c",
                "a/c/c.csv",
                "a/c/c.csv.gz",
                "a/c/c.jsonl",
            },
            {"a/"},
            id="a/*/*",
        ),
        pytest.param(
            ["a/*/*.csv"], DEFAULT_CONFIG, {"a/b/c.csv", "a/c/c.csv"}, {"a/"}, id="a/*/*.csv"
        ),
        pytest.param(
            ["a/*/*.csv*"],
            DEFAULT_CONFIG,
            {"a/b/c.csv", "a/b/c.csv.gz", "a/c/c.csv", "a/c/c.csv.gz"},
            {"a/"},
            id="a/*/*.csv*",
        ),
        pytest.param(
            ["a/**/*"],
            DEFAULT_CONFIG,
            {
                "a/b",
                "a/b.csv",
                "a/b.csv.gz",
                "a/b.jsonl",
                "a/c",
                "a/c.csv",
                "a/c.csv.gz",
                "a/c.jsonl",
                "a/b/c",
                "a/b/c.csv",
                "a/b/c.csv.gz",
                "a/b/c.jsonl",
                "a/c/c",
                "a/c/c.csv",
                "a/c/c.csv.gz",
                "a/c/c.jsonl",
                "a/b/c/d",
                "a/b/c/d.csv",
                "a/b/c/d.csv.gz",
                "a/b/c/d.jsonl",
            },
            {"a/"},
            id="a/**/*",
        ),
        pytest.param(
            ["a/**/*.csv"],
            DEFAULT_CONFIG,
            {"a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"},
            {"a/"},
            id="a/**/*.csv",
        ),
        pytest.param(
            ["a/**/*.csv*"],
            DEFAULT_CONFIG,
            {
                "a/b.csv",
                "a/b.csv.gz",
                "a/c.csv",
                "a/c.csv.gz",
                "a/b/c.csv",
                "a/b/c.csv.gz",
                "a/c/c.csv",
                "a/c/c.csv.gz",
                "a/b/c/d.csv",
                "a/b/c/d.csv.gz",
            },
            {"a/"},
            id="a/**/*.csv*",
        ),
        pytest.param(
            ["**/*.csv", "**/*.gz"],
            DEFAULT_CONFIG,
            {
                "a.csv",
                "a.csv.gz",
                "a/b.csv",
                "a/b.csv.gz",
                "a/c.csv",
                "a/c.csv.gz",
                "a/b/c.csv",
                "a/b/c.csv.gz",
                "a/c/c.csv",
                "a/c/c.csv.gz",
                "a/b/c/d.csv",
                "a/b/c/d.csv.gz",
            },
            set(),
            id="**/*.csv,**/*.gz",
        ),
        pytest.param(
            ["*.csv", "*.gz"], DEFAULT_CONFIG, {"a.csv", "a.csv.gz"}, set(), id="*.csv,*.gz"
        ),
        pytest.param(
            ["a/*.csv", "a/*/*.csv"],
            DEFAULT_CONFIG,
            {"a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv"},
            {"a/"},
            id="a/*.csv,a/*/*.csv",
        ),
        pytest.param(
            ["a/*.csv", "a/b/*.csv"],
            DEFAULT_CONFIG,
            {"a/b.csv", "a/c.csv", "a/b/c.csv"},
            {"a/", "a/b/"},
            id="a/*.csv,a/b/*.csv",
        ),
        pytest.param(
            ["**/*.csv"],
            {"start_date": "2023-06-01T03:54:07.000Z", "streams": []},
            {"a.csv", "a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"},
            set(),
            id="all_csvs_modified_after_start_date",
        ),
        pytest.param(
            ["**/*.csv"],
            {"start_date": "2023-06-10T03:54:07.000Z", "streams": []},
            set(),
            set(),
            id="all_csvs_modified_before_start_date",
        ),
        pytest.param(
            ["**/*.csv"],
            {"start_date": "2023-06-05T03:54:07.000Z", "streams": []},
            {"a.csv", "a/b.csv", "a/c.csv", "a/b/c.csv", "a/c/c.csv", "a/b/c/d.csv"},
            set(),
            id="all_csvs_modified_exactly_on_start_date",
        ),
    ],
)
def test_globs_and_prefixes_from_globs(
    globs: List[str],
    config: Mapping[str, Any],
    expected_matches: Set[str],
    expected_path_prefixes: Set[str],
) -> None:
    reader = TestStreamReader()
    reader.config = TestSpec(**config)
    assert (
        set([f.uri for f in reader.filter_files_by_globs_and_start_date(FILES, globs)])
        == expected_matches
    )
    assert set(reader.get_prefixes_from_globs(globs)) == expected_path_prefixes


@pytest.mark.parametrize(
    "config, source_file, expected_file_relative_path, expected_local_file_path, expected_absolute_file_path",
    [
        pytest.param(
            {
                "streams": [],
                "delivery_method": {
                    "delivery_type": "use_file_transfer",
                    "preserve_directory_structure": True,
                },
            },
            "mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            id="preserve_directories_present_and_true",
        ),
        pytest.param(
            {
                "streams": [],
                "delivery_method": {
                    "delivery_type": "use_file_transfer",
                    "preserve_directory_structure": False,
                },
            },
            "mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/monthly-kickoff-202402.mpeg",
            id="preserve_directories_present_and_false",
        ),
        pytest.param(
            {"streams": [], "delivery_method": {"delivery_type": "use_file_transfer"}},
            "mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            id="preserve_directories_not_present_defaults_true",
        ),
        pytest.param(
            {"streams": []},
            "mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            "/tmp/transfer-files/mirror_paths_testing/not_duplicates/data/jan/monthly-kickoff-202402.mpeg",
            id="file_transfer_flag_not_present_defaults_true",
        ),
    ],
)
def test_preserve_sub_directories_scenarios(
    config: Mapping[str, Any],
    source_file: str,
    expected_file_relative_path: str,
    expected_local_file_path: str,
    expected_absolute_file_path: str,
) -> None:
    remote_file = RemoteFile(
        uri=source_file,
        last_modified=datetime(2025, 1, 9, 11, 27, 20),
        mime_type=None,
    )
    reader = TestStreamReader()
    reader.config = TestSpec(**config)
    file_relative_path, local_file_path, absolute_file_path = reader._get_file_transfer_paths(
        remote_file, "/tmp/transfer-files/"
    )

    assert file_relative_path == expected_file_relative_path
    assert local_file_path == expected_local_file_path
    assert absolute_file_path == expected_absolute_file_path
