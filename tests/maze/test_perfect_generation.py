import pytest

from mazegen.maze.generator import MazeGenerator


@pytest.mark.parametrize(
    ("width", "height", "seed"),
    [
        (1, 1, 0),
        (1, 5, 42),
        (5, 1, -10),
        (3, 3, 42),
        (20, 15, 123),
    ],
)
def test_generation_visits_every_cell(
    width: int,
    height: int,
    seed: int,
) -> None:
    """Verify generation visits every position and preserves borders."""
    generator = MazeGenerator(width, height, seed)

    maze = generator.generate_perfect()

    assert maze is generator.grid
    assert len(generator.visited) == width * height
    generator.validate_external_walls()


def test_generation_opens_exactly_one_passage_per_new_cell() -> None:
    """Verify the generated grid has the edge count of a tree."""
    generator = MazeGenerator(5, 4, seed=42)

    generator.generate_perfect()

    passages = 0

    for y in range(generator.height):
        for x in range(generator.width):
            cell = generator.get_cell(x, y)

            if x + 1 < generator.width and not cell.east:
                passages += 1

            if y + 1 < generator.height and not cell.south:
                passages += 1

    assert passages == generator.width * generator.height - 1


def test_same_seed_reproduces_the_same_first_generation() -> None:
    """Verify identical inputs reproduce the first generated maze."""
    first = MazeGenerator(5, 4, seed=42)
    second = MazeGenerator(5, 4, seed=42)

    assert first.generate_perfect() == second.generate_perfect()


def test_regeneration_discards_previous_passages() -> None:
    """Verify regeneration resets walls as well as visited cells."""
    generator = MazeGenerator(2, 2, seed=42)

    for row in generator.grid:
        for cell in row:
            cell.north = False
            cell.east = False
            cell.south = False
            cell.west = False

    generator.mark_visited(0, 0)

    generator.generate_perfect()

    assert len(generator.visited) == 4
    generator.validate_external_walls()

    passages = 0

    for row in generator.grid:
        for cell in row:
            passages += int(not cell.east)
            passages += int(not cell.south)

    assert passages == 3
