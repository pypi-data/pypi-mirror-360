import csv
import sys

from budget.table import Table

from ._renderer import Renderer


class CSVRenderer(Renderer):
    def render_table(self, table: Table):
        writer = csv.writer(sys.stdout)

        if table.header:
            writer.writerow(h.text for h in table.header)

        for row in table.rows:
            writer.writerow([cell.text for cell in row])

        if table.footer:
            writer.writerow([f.text for f in table.footer])

        sys.stdout.flush()
