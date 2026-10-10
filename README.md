*This project has been created as part of the 42 curriculum by vneves-c, brde-car.*

# A-Maze-ing

## Description

A Python 3.10+ maze generator with seeded randomness, a hexadecimal output
file and an interactive ASCII view. It implements the mandatory subject:
perfect mazes, playable non-perfect boards, the closed-cell "42" drawing,
shortest-path solving, regeneration, solution visibility and wall colors.
The program uses the standard library at runtime; MiniLibX is not required
because the subject permits ASCII rendering. No optional algorithm or
generation animation is included.

## Instructions

From the repository root:

```sh
python3 -m venv .venv
```

Activate with `source .venv/bin/activate` in bash/zsh, or
`source .venv/bin/activate.fish` in fish. Then:

```sh
make install
make check
python3 a_maze_ing.py config.txt
```

`make run` runs the same default configuration; `make run CONFIG=custom.txt`
selects another file. `make debug` uses pdb, `make lint` checks flake8 and
mypy, and `make clean` removes Python caches. Commands accept
`PYTHON=.venv/bin/python` if the virtual environment is not activated.

An interactive terminal offers:

| Key | Action |
| --- | --- |
| `r` + Enter | Generate a new maze and update the configured output file |
| `s` + Enter | Show/hide the shortest solution without changing the maze |
| `c` + Enter | Cycle wall colors without changing the maze |
| `q` + Enter | Quit |

EOF and Ctrl-C also exit the menu. `E` marks entry, `X` exit, `.` the visible
solution and `#` the fully closed drawing cells. Without an interactive
terminal (for example, redirected input), the program writes the output,
prints one plain ASCII view and exits without waiting for input.

## Configuration

One `KEY=VALUE` per line. Empty lines and lines starting with `#` are ignored.
The following six keys are required; `SEED` is optional:

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

- `WIDTH` and `HEIGHT`: positive integer columns and rows.
- `ENTRY` and `EXIT`: distinct in-bounds `x,y` coordinates. `x` grows to the
  right, `y` downward, and cells are stored as `grid[y][x]`.
- `OUTPUT_FILE`: output path, relative to the current working directory or
  absolute. Its parent directory must already exist.
- `PERFECT`: exactly `True` or `False`. The supplied default is `False`.
- `SEED`: any integer; omission uses system randomness. A new generator with
  the same seed and parameters reproduces the same result. Regeneration
  advances that generator's random state, yielding a new maze.

Unknown keys, malformed lines and invalid values produce a readable error
and nonzero exit status. Duplicate keys use the last occurrence. The
implementation supports up to 10,000 cells to bound memory/display costs.
Non-perfect boards need at least 2x3 or 3x2 cells; geometrically impossible
parameters are rejected rather than outputting an invalid board.

## Algorithms and invariants

The generator uses iterative **Recursive Backtracker (depth-first search)**.
A stack records the current exploration path. A random unvisited neighbor is
chosen, the shared wall is opened on both sides, and the neighbor is marked
visited. When no neighbor is available, the stack pops to backtrack.
This simple algorithm was chosen because each newly visited cell adds one
edge, producing a connected tree with no cycles, without Python recursion
limits. Neighbor order is stable and all choices use a local `random.Random`.

For `PERFECT=False`, generation starts from the same tree and opens additional
safe internal passages, prioritizing dead ends. The mandatory thresholds
match the supplied analyzer: at least **two independent cycles** and at most
**two real dead ends**. Dead ends enclosed entirely by the drawing/border are
reported separately by the analyzer and tolerated. Zero dead ends is not a
target or a claimed bonus. Failed braiding attempts are retried at most 30
times using the same random stream, then rejected with a clear error.

Both modes preserve external borders, shared-wall coherence and all corridor
connectivity. A proposed extra passage is rejected if it completes a fully
open 3x3 area. A 2x3 or 3x2 open area is allowed.

The immutable 5x7 "42" pattern contains 20 closed cells. Placement tries
origins nearest the geometric center, breaking ties upward then leftward.
It never occupies ENTRY/EXIT; non-perfect placement also protects the four
corners and center `(width // 2, height // 2)`. Placement checks whether the
remaining geometric corridors can connect before carving. If no safe
position exists, the pattern is omitted with a console warning. Generation
then validates the actual passages, excluding only explicit reservations.

**BFS** finds the shortest solution: a FIFO queue explores increasing
distances, a visited set prevents repetitions, and predecessors reconstruct
the path. Both sides of every shared passage must be open. The final path is
validated for endpoints, walls and minimum length before export.

## Output format

One uppercase hexadecimal digit per cell, one grid row per line. Bits encode
closed walls: bit 0 North, bit 1 East, bit 2 South, bit 3 West. Thus `F` is
fully closed, `3` has North/East closed, and `A` has East/West closed.
After exactly one blank separator come ENTRY, EXIT and the N/E/S/W solution
on three lines. Every line ends in LF (`\n`). For example:

```text
D3
FE

0,0
1,1
ES
```

Output is first written to a temporary file in the destination directory,
then atomically replaced. Failed writing/publication preserves an existing
output and removes the temporary file.

## Reusable module

The reusable generation class is `MazeGenerator`; its algorithms do not read
terminal input or depend on the CLI. `MazeGrid` stores cells; it is not a
second generation algorithm. `Cell` exposes typed `north`, `east`, `south`
and `west` booleans, where `True` means closed.

Build the required root artifact with:

```sh
make package
python3 -m pip install ./mazegen-1.0.0-py3-none-any.whl
```

`python3 -m build` also builds a wheel and source archive in `dist/` from
`pyproject.toml`. The wheel embeds this README as package metadata and the
MIT license. It has no runtime dependencies.

Example from another project after installation:

```python
from mazegen import MazeGenerator

maze = MazeGenerator(width=20, height=15, seed=42)
maze.generate(perfect=False, entry=(0, 0), exit=(19, 14))
cell = maze.get_cell(2, 3)       # same object as maze.grid[3][2]
path = maze.solve((0, 0), (19, 14))
print(cell.north, path)
```

`generate()` selects the mode and safe pattern placement; `include_pattern=False`
is available for independent reuse. `generate_perfect()` is the lower-level
carving method using the current `reserved` set. `generate_non_perfect()`
adds the playable constraints. `solve()` returns coordinates including both
endpoints. Generation methods return the grid and never write files.

## Tests and evaluation

`make check` combines syntax, lint, strict typing and pytest. Tests exercise
configuration, cells, coherent walls, connectivity, reservations, seeds,
loops/dead ends, forbidden areas, shortest paths, file format, atomic writing,
ASCII rendering and menu actions. Independent tests decode output wall bits
and run their own BFS rather than trusting only the solver under test.

The analyzer supplied with the subject can be run separately with
`python3 maze_analyzer.py maze.txt`. Inspect its verdict, not merely its exit
code: a parsable but non-playable board may still return zero. It is not a
runtime dependency and is not redistributed as our own code.

Before evaluation, both teammates must explain DFS versus BFS, FIFO versus
LIFO, the bit order, cycle count `E - V + 1`, pattern placement, braiding and
file cleanup. Practice a small change, such as modifying the exit marker or
adding a wall color, then rerun the relevant tests. These human preparation
steps are not certified by automated tests.

## Team and project management

- **vneves-c**: repository/board coordination, incremental implementation and
  integration of the maze pipeline.
- **brde-car**: collaboration and PR review during development.
- Both are responsible for understanding, reviewing and defending the final
  code; roles are not claims that every function was written exclusively by
  one member.

The initial plan split the project into small learning issues: configuration,
representation, walls, DFS, BFS, encoding, output, pattern, non-perfect mode,
rendering, tests and packaging. It evolved toward greater AI assistance to
complete integration under time constraints. Git branches/PRs and GitHub
Projects tracked progress; CI gates lint/tests before merges. Small tests and
separating responsibilities worked well. Branch confusion, early integration
without CI gates, and copying partial test snippets showed the need for
clean-checkout audits, careful diffs and stronger human review.

## Resources

- [Python collections/deque](https://docs.python.org/3/library/collections.html#collections.deque)
  for BFS queues.
- [Python random](https://docs.python.org/3/library/random.html) for seeded RNGs.
- [Python integer/bitwise operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
  for wall encoding.
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
  for building/installing the reusable package.
- [MIT license](https://opensource.org/license/mit) for permissive reuse and
  distribution, retaining the license notice.
- The A-Maze-ing subject v2.3 and its provided analyzer define acceptance.

AI (Codex) assisted explanations, tests, refactoring, Git/CI troubleshooting,
pattern protection, non-perfect integration, ASCII interactions, packaging
and this documentation. Generated changes were checked with strict typing,
lint, automated tests, output decoding and the provided analyzer. AI support
does not replace the teammates' required understanding and peer review.
