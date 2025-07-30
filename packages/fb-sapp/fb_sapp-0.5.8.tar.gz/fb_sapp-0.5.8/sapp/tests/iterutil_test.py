# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase

from ..iterutil import split_every


class UtilsTest(TestCase):
    def test_split_every(self) -> None:
        self.assertEqual(
            list(split_every(2, range(10))), [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
        )
