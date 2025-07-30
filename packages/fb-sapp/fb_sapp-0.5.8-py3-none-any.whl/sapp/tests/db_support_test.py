# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase

from ..db_support import DBID, dbid_resolution_context


class DBSupportTest(TestCase):
    def test_dbid_basic(self) -> None:
        primary_key = DBID()
        foreign_key = DBID(primary_key)

        primary_key.resolve(42)

        self.assertEqual(primary_key.resolved(), 42)
        self.assertEqual(foreign_key.resolved(), 42)

    def test_dbid_reassign(self) -> None:
        primary_key = DBID()
        primary_key.resolve(1)
        primary_key.resolve(2)
        primary_key.resolve(42)
        self.assertEqual(primary_key.resolved(), 42)

    def test_dbid_reassign_after_resolved(self) -> None:
        primary_key = DBID()
        primary_key.resolve(1)
        self.assertEqual(primary_key.resolved(), 1)

        primary_key.resolve(42)
        self.assertEqual(primary_key.resolved(), 42)

    def test_dbid_resolved_to_none(self) -> None:
        primary_key = DBID()
        self.assertEqual(None, primary_key.resolved())

    def test_dbid_resolution_context(self) -> None:
        primary_key = DBID()
        foreign_key = DBID(primary_key)
        with dbid_resolution_context():
            primary_key.resolve(1)
            self.assertEqual(primary_key.resolved(), 1)
            self.assertEqual(foreign_key.resolved(), 1)
        self.assertIsNone(primary_key.resolved())
        self.assertIsNone(foreign_key.resolved())
        primary_key.resolve(2)
        with dbid_resolution_context():
            primary_key.resolve(3)
            self.assertEqual(primary_key.resolved(), 3)
            self.assertEqual(foreign_key.resolved(), 3)
        self.assertEqual(primary_key.resolved(), 2)
        self.assertEqual(foreign_key.resolved(), 2)
