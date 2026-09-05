import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from mazegen.cli import main


class DimensionValidationCliTests(unittest.TestCase):
    def run_with_dimensions(
        self,
        width: str,
        height: str,
    ) -> tuple[int, str]:
        config = (
            f"WIDTH={width}\n"
            f"HEIGHT={height}\n"
            "ENTRY=0,0\n"
            "EXIT=1,1\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )

        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.txt"
            config_path.write_text(config, encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                exit_code = main([str(config_path)])

        return exit_code, stderr.getvalue()

    def test_rejects_non_numeric_dimension_without_traceback(self) -> None:
        exit_code, error_message = self.run_with_dimensions("abc", "15")

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            error_message,
            "Config error: WIDTH must be an integer: 'abc'\n",
        )
        self.assertNotIn("Traceback", error_message)

    def test_rejects_non_positive_dimension_with_clear_message(self) -> None:
        exit_code, error_message = self.run_with_dimensions("20", "-10")

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            error_message,
            "Config error: HEIGHT must be greater than zero: '-10'\n",
        )
        self.assertNotIn("Traceback", error_message)


if __name__ == "__main__":
    unittest.main()
