import unittest

from mazegen.config.validator import convert_dimensions


class ConvertDimensionsTests(unittest.TestCase):
    def test_converts_valid_dimensions_to_integers(self) -> None:
        config = {
            "WIDTH": "20",
            "HEIGHT": "15",
            "ENTRY": "0,0",
        }

        converted_config = convert_dimensions(config)

        self.assertEqual(converted_config["WIDTH"], 20)
        self.assertEqual(converted_config["HEIGHT"], 15)
        self.assertEqual(converted_config["ENTRY"], "0,0")
        self.assertEqual(config["WIDTH"], "20")
        self.assertEqual(config["HEIGHT"], "15")

    def test_rejects_non_numeric_dimensions(self) -> None:
        for key in ("WIDTH", "HEIGHT"):
            with self.subTest(key=key):
                config = {"WIDTH": "20", "HEIGHT": "15"}
                config[key] = "abc"

                with self.assertRaisesRegex(
                    ValueError,
                    rf"{key} must be an integer",
                ):
                    convert_dimensions(config)

    def test_rejects_non_positive_dimensions(self) -> None:
        for key in ("WIDTH", "HEIGHT"):
            for invalid_value in ("0", "-10"):
                with self.subTest(key=key, value=invalid_value):
                    config = {"WIDTH": "20", "HEIGHT": "15"}
                    config[key] = invalid_value

                    with self.assertRaisesRegex(
                        ValueError,
                        rf"{key} must be greater than zero",
                    ):
                        convert_dimensions(config)


if __name__ == "__main__":
    unittest.main()
