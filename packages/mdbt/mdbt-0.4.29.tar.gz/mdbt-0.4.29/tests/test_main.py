import unittest

from click.core import Command

from mdbt.main import MDBT
from mdbt.main import MockCtx


class TestCdbt(unittest.TestCase):
    def setUp(self):
        self.cdbt = MDBT()
        self.cdbt.test_mode = True
        self.incremental_ls_example = """22:06:42 Running with dbt=1.7.9
22:06:43 Registered adapter: snowflake=1.7.2
22:06:43 Found 123 models, 26 snapshots, 118 tests, 9 seeds, 46 sources, 0 exposures, 0 metrics, 992 macros, 0 groups, 0 semantic models
{"name": "dim_patients", "resource_type": "model", "config": {"materialized": "incremental"}}"""

        self.non_incremental_ls_example = """22:06:42 Running with dbt=1.7.9
22:06:43 Registered adapter: snowflake=1.7.2
22:06:43 Found 123 models, 26 snapshots, 118 tests, 9 seeds, 46 sources, 0 exposures, 0 metrics, 992 macros, 0 groups, 0 semantic models
{"name": "dim_patients", "resource_type": "model", "config": {"materialized": "view"}}"""

    def test_build_command_full_refresh(self):
        self.cdbt.build(
            ctx=MockCtx(Command("test")),
            full_refresh=True,
            select="model1",
            fail_fast=True,
            threads=None,
        )
        expected_command = [
            "dbt",
            "build",
            "--select",
            "model1",
            "--fail-fast",
            "--full-refresh",
        ]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

        # Test threads
        mc = MockCtx(Command("test"))
        mc.obj["threads"] = 5
        self.cdbt.build(
            ctx=mc, full_refresh=True, select="model1", fail_fast=True, threads=5
        )
        expected_command = [
            "dbt",
            "build",
            "--threads",
            "5",
            "--select",
            "model1",
            "--fail-fast",
            "--full-refresh",
        ]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

    def test_build_command_no_full_refresh(self):
        self.cdbt.build(
            ctx=MockCtx(Command("test")),
            full_refresh=False,
            select="model1",
            fail_fast=False,
            threads=None,
        )
        expected_command = ["dbt", "build", "--select", "model1"]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

    def test_trun_command(self):
        self.cdbt.trun(
            ctx=MockCtx(Command("test")),
            full_refresh=True,
            select="model2",
            fail_fast=False,
            threads=None,
        )
        expected_command = [
            "dbt",
            "build",
            "--select",
            "model2",
            "--full-refresh",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
        ]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

    def test_run_command_full_refresh(self):
        self.cdbt.run(
            ctx=MockCtx(Command("test")),
            full_refresh=True,
            select="model3",
            fail_fast=True,
            threads=None,
        )
        expected_command = [
            "dbt",
            "run",
            "--select",
            "model3",
            "--fail-fast",
            "--full-refresh",
        ]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

    def test_test_command_selective(self):
        self.cdbt.test(
            ctx=MockCtx(Command("test")), select="model4", fail_fast=True, threads=None
        )
        expected_command = ["dbt", "test", "--select", "model4", "--fail-fast"]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

    def test_compile_command(self):
        self.cdbt.compile(ctx=MockCtx(Command("test")), select="abc")
        expected_command = ["dbt", "compile"]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

    def test_sbuild_output(self):
        self.cdbt.dbt_ls_test_mode_output = self.incremental_ls_example
        self.cdbt.sbuild(ctx=MockCtx(Command("test")), full_refresh=False, threads=None)
        expected_command = [
            "dbt",
            "build",
            "--select",
            "state:modified",
            "--state",
            "_artifacts/",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
            "--full-refresh",
        ]
        actual = self.cdbt.dbt_test_mode_command_check_value
        self.assertEqual(actual, expected_command)

        # Test build parents
        mc = MockCtx(Command("test"))
        mc.obj["build_parents"] = True
        self.cdbt.dbt_ls_test_mode_output = self.incremental_ls_example
        self.cdbt.sbuild(ctx=mc, full_refresh=False, threads=None)
        expected_command = [
            "dbt",
            "build",
            "--select",
            "+state:modified",
            "--state",
            "_artifacts/",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
            "--full-refresh",
        ]
        actual = self.cdbt.dbt_test_mode_command_check_value
        self.assertEqual(actual, expected_command)

        # Test build parents graph count limit (i.e. 3+sbuild)
        mc = MockCtx(Command("test"))
        mc.obj["build_parents"] = True
        mc.obj["build_parents_count"] = 3
        self.cdbt.dbt_ls_test_mode_output = self.incremental_ls_example
        self.cdbt.sbuild(ctx=mc, full_refresh=False, threads=None)
        expected_command = [
            "dbt",
            "build",
            "--select",
            "3+state:modified",
            "--state",
            "_artifacts/",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
            "--full-refresh",
        ]
        actual = self.cdbt.dbt_test_mode_command_check_value
        self.assertEqual(actual, expected_command)

        # Test build children
        mc = MockCtx(Command("test"))
        mc.obj["build_children"] = True
        self.cdbt.dbt_ls_test_mode_output = self.incremental_ls_example
        self.cdbt.sbuild(ctx=mc, full_refresh=False, threads=None)
        expected_command = [
            "dbt",
            "build",
            "--select",
            "state:modified+",
            "--state",
            "_artifacts/",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
            "--full-refresh",
        ]
        actual = self.cdbt.dbt_test_mode_command_check_value
        self.assertEqual(actual, expected_command)

        # Test build children graph count limit (i.e. sbuild+3)
        mc = MockCtx(Command("test"))
        mc.obj["build_children"] = True
        mc.obj["build_children_count"] = 2
        self.cdbt.dbt_ls_test_mode_output = self.incremental_ls_example
        self.cdbt.sbuild(ctx=mc, full_refresh=False, threads=None)
        expected_command = [
            "dbt",
            "build",
            "--select",
            "state:modified+2",
            "--state",
            "_artifacts/",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
            "--full-refresh",
        ]
        actual = self.cdbt.dbt_test_mode_command_check_value
        self.assertEqual(actual, expected_command)

    def test_pbuild_output(self):
        self.cdbt.dbt_ls_test_mode_output = self.incremental_ls_example
        self.cdbt.pbuild(
            ctx=MockCtx(Command("test")),
            full_refresh=False,
            threads=None,
            skip_download=True,
        )
        expected_command = [
            "dbt",
            "build",
            "--select",
            "state:modified",
            "--state",
            "logs/",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
            "--full-refresh",
        ]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)

        self.cdbt.dbt_ls_test_mode_output = self.non_incremental_ls_example
        self.cdbt.pbuild(
            ctx=MockCtx(Command("test")),
            full_refresh=False,
            threads=None,
            skip_download=True,
        )
        expected_command = [
            "dbt",
            "build",
            "--select",
            "state:modified",
            "--state",
            "logs/",
            "--exclude",
            "resource_type:snapshot resource_type:seed",
        ]
        self.assertEqual(self.cdbt.dbt_test_mode_command_check_value, expected_command)


if __name__ == "__main__":
    unittest.main()
