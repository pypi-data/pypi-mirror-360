"""Testing Dictionary Files Diff Methods
"""
from test.conftest import get_big_tree, get_simple_tree

from treescript_diff.dictionary_files_diff import compare_files, load_original


def test_load_original():
    result = load_original(get_simple_tree())
    assert len(result.keys()) == 1


def test_load_original_big_tree():
    result = load_original(get_big_tree())
    assert len(result.keys()) == 727


def test_compare_files_simple_tree():
    original = load_original(get_simple_tree())
    updated = get_simple_tree()
    result = list(compare_files(original, updated))
    assert len(result) == 0


def test_compare_files_simple_tree_big_tree():
    original = load_original(get_simple_tree())
    updated = get_big_tree()
    result = list(compare_files(original, updated))
    assert len(result) == 727


def test_compare_files_big_tree_simple_tree():
    original = load_original(get_big_tree())
    updated = get_simple_tree()
    result = list(compare_files(original, updated))
    assert len(result) == 1
