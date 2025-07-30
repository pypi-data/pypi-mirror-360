# Copyright 2024 AtlasAI PBC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def render_block(title, description):
    title_text = Text(title, style="bold green")

    description_text = Text(description, style="dim")

    panel = Panel(
        Text.assemble(title_text, "\n", description_text),
        border_style="blue",
        padding=(1, 2),
        expand=False
    )

    console.print(panel)

def render_table(title, rows, columns=None):
    table = Table(title=title, title_style="bold green", show_lines=True)

    if not rows:
        console.print(table)
        return

    if isinstance(rows, dict):
        rows = [{"Key": k, "Value": v} for k, v in rows.items()]
        columns = ["Key", "Value"]

    if not columns:
        columns = list(rows[0].keys())

    for col in columns:
        table.add_column(str(col), style="dim", no_wrap=True)

    for row in rows:
        table.add_row(*(str(row.get(col, "")) for col in columns))

    console.print(table)
