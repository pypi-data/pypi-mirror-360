# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
import multiprocessing
from typing import Iterable, List, Set, Tuple, Type, Union

from ..analysis_output import AnalysisOutput, Metadata
from ..operating_system import get_rss_in_gb
from . import ParseConditionTuple, ParseIssueTuple
from .base_parser import BaseParser

log: logging.Logger = logging.getLogger("sapp")
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s")


# We are going to call this per process, so we need to pass in and return
# serializable data. And as a single arg, as far as I can tell. Which is why the
# args type looks so silly.
def parse(
    args: Tuple[Tuple[Type[BaseParser], Set[str], Metadata], str],
) -> List[Union[ParseConditionTuple, ParseIssueTuple]]:
    (base_parser, repo_dirs, metadata), path = args

    parser = base_parser(repo_dirs)
    parser.initialize(metadata)

    with open(path) as handle:
        return list(parser.parse_handle(handle))


class ParallelParser(BaseParser):
    def __init__(self, parser_class: Type[BaseParser], repo_dirs: Set[str]) -> None:
        super().__init__(repo_dirs)
        self.parser: Type[BaseParser] = parser_class

    def parse(
        self, input: AnalysisOutput
    ) -> Iterable[Union[ParseConditionTuple, ParseIssueTuple]]:
        log.info("Parsing in parallel")
        files = list(input.file_names())

        # Pair up the arguments with each file.
        num_files = len(files)
        args = zip([(self.parser, self.repo_dirs, input.metadata)] * num_files, files)
        initial_rss = get_rss_in_gb()
        log.info(f"RSS before parsing: {initial_rss:.2f} GB")

        with multiprocessing.get_context("spawn").Pool(processes=None) as pool:
            for idx, f in enumerate(pool.imap_unordered(parse, args)):
                if idx % 10 == 0:
                    cur = idx + 1
                    pct = (cur / num_files) * 100
                    log.info(f"{cur}/{num_files} ({pct:.2f}) files parsed")
                yield from f

        rss_after = get_rss_in_gb()
        log.info(
            f"RSS after parsing: {rss_after:.2f} GB, change: {rss_after - initial_rss:.2f} GB"
        )
