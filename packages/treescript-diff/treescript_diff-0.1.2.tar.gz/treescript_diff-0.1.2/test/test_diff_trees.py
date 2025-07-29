""" Testing Dictionary Files Diff Methods
"""
from treescript_diff.diff_trees import diff_trees_additions, diff_trees_double, diff_trees_removals

from test.conftest import get_simple_tree, get_simple_tree_add_newline, get_simple_tree_add_file, get_big_tree


def test_diff_trees_additions_empty_simple_returns_empty():
    generator = diff_trees_additions("", get_simple_tree())
    result = list(generator)
    assert len(result) == 1


def test_diff_trees_additions_simple_simple_returns_empty():
    generator = diff_trees_additions(get_simple_tree(), get_simple_tree())
    result = list(generator)
    assert len(result) == 0


def test_diff_trees_additions_newline():
    generator = diff_trees_additions(get_simple_tree(), get_simple_tree_add_newline())
    result = list(generator)
    assert len(result) == 0


def test_diff_trees_additions_add_file():
    generator = diff_trees_additions(get_simple_tree(), get_simple_tree_add_file())
    result = list(generator)
    assert len(result) == 1


def test_diff_trees_additions_remove_file():
    generator = diff_trees_additions(get_simple_tree_add_file(), get_simple_tree())
    result = list(generator)
    assert len(result) == 0


def test_diff_trees_additions_simple_to_big():
    generator = diff_trees_additions(get_simple_tree(), get_big_tree())
    result = list(generator)
    assert len(result) == 727


def test_diff_trees_additions_big_to_simple():
    generator = diff_trees_additions(get_big_tree(), get_simple_tree())
    result = list(generator)
    assert len(result) == 1


def test_diff_trees_removals_simple_simple_returns_empty():
    generator = diff_trees_removals(get_simple_tree(), get_simple_tree())
    result = list(generator)
    assert len(result) == 0


def test_diff_trees_removals_newline():
    generator = diff_trees_removals(get_simple_tree(), get_simple_tree_add_newline())
    result = list(generator)
    assert len(result) == 0


def test_diff_trees_removals_add_file():
    generator = diff_trees_removals(get_simple_tree(), get_simple_tree_add_file())
    result = list(generator)
    assert len(result) == 0


def test_diff_trees_removals_remove_file():
    generator = diff_trees_removals(get_simple_tree_add_file(), get_simple_tree())
    result = list(generator)
    assert len(result) == 1


def test_diff_trees_removals_simple_to_big():
    generator = diff_trees_removals(get_simple_tree(), get_big_tree())
    result = list(generator)
    assert len(result) == 1


def test_diff_trees_removals_big_to_simple():
    generator = diff_trees_removals(get_big_tree(), get_simple_tree())
    result = list(generator)
    assert len(result) == 727


def test_diff_trees_double_simple_simple_returns_empty():
    result = diff_trees_double(get_simple_tree(), get_simple_tree())
    additions, removals = result[0], result[1]
    assert len(additions) == 0
    assert len(removals) == 0


def test_diff_trees_double_newline_returns_empty():
    result = diff_trees_double(get_simple_tree(), get_simple_tree_add_newline())
    additions, removals = result[0], result[1]
    assert len(additions) == 0
    assert len(removals) == 0


def test_diff_trees_double_add_file_returns_1_addition():
    result = diff_trees_double(get_simple_tree(), get_simple_tree_add_file())
    additions, removals = result[0], result[1]
    assert len(additions) == 1
    assert len(removals) == 0


def test_diff_trees_double_remove_file_returns_1_removal():
    result = diff_trees_double(get_simple_tree_add_file(), get_simple_tree())
    additions, removals = result[0], result[1]
    assert len(additions) == 0
    assert len(removals) == 1


def test_diff_trees_double_simple_to_big_returns_many_addition_and_1_removal():
    result = diff_trees_double(get_simple_tree(), get_big_tree())
    additions, removals = result[0], result[1]
    assert len(additions) == 727
    assert len(removals) == 1


def test_diff_trees_double_big_to_simple_returns_1_addition_and_many_removals():
    result = diff_trees_double(get_big_tree(), get_simple_tree())
    additions, removals = result[0], result[1]
    assert len(additions) == 1
    assert len(removals) == 727
