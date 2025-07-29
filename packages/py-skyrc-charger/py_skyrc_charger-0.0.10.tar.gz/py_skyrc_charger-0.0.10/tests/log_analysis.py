import unittest

import sys
import os
import csv

if True:  # pylint: disable=W0125
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")


from py_skyrc_charger.commands import parse_data


class TestCommands(unittest.TestCase):

    def test_parse_data(self):
        line_count = 0
        out = []
        with open('tests/usb_data_2025-02-27_12-44-46.txt', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) != 2:
                    continue

                time_str = parts[0].strip()
                hex_data = parts[1].strip()
                if not hex_data:
                    continue

                try:
                    data = bytes.fromhex(hex_data)
                    result = parse_data(data)
                    self.assertIsNotNone(result)
                    self.assertEqual(result.is_error, False)
                    if result:
                        result.data['time'] = time_str
                        # if line_count % 100 == 0:
                        out.append(result.data)
                        # print(f"{parts[0]}: {result}")
                except ValueError:
                    continue
                line_count += 1
        print(f"parsed {line_count} lines")
        # self._write_to_csv(out)

    def _write_to_csv(self, out):
        # Write data to CSV
        with open('log_output.csv', 'w', newline='', encoding='utf-8') as csv_file:
            if len(out) > 0:
                # Get field names from first result dict
                fieldnames = list(out[0].keys())
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(out)


if __name__ == '__main__':
    unittest.main()
