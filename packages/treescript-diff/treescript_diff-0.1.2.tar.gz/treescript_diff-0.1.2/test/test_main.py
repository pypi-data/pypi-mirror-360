""" Testing Main Module.
"""
import builtins
import os
import sys

import pytest
from pathlib import Path

from test.conftest import get_simple_tree, get_simple_tree_add_file, PrintCollector, get_big_tree
from treescript_diff.__main__ import main


def test_main_():
    from sys import argv, orig_argv
    argv.clear()
    argv.append('treescript-diff')
    argv.append('original')
    argv.append('updated')
    collector = PrintCollector()
    # Mock files
    with pytest.MonkeyPatch().context() as c:
        c.setattr(Path, 'exists', lambda _: True)
        c.setattr(Path, 'read_text', lambda _: "src/")
        c.setattr(builtins, 'print', collector.get_mock_print())
        main()

    print(collector.get_output())
    argv.clear()
    for i in orig_argv:
        argv.append(i)


def test_main_original_tree_not_found_raises_exit(tmp_path):
    sys.argv = ['treescript-diff', 'original', 'updated']
    os.chdir(tmp_path)
    with pytest.raises(SystemExit, match='The tree file does not exist: original'):
        main()


def test_main_original_tree_empty_raises_exit(tmp_path):
    sys.argv = ['treescript-diff', 'original', 'updated']
    os.chdir(tmp_path)
    (tmp_path / 'original').touch()
    with pytest.raises(SystemExit, match='This TreeScript file was empty: original'):
        main()


def test_main_updated_tree_not_found_raises_exception(tmp_path):
    sys.argv = ['treescript-diff', 'original', 'updated']
    os.chdir(tmp_path)
    (original_treescript := tmp_path / 'original').touch()
    original_treescript.write_text('src/')
    with pytest.raises(SystemExit, match='The tree file does not exist: updated'):
        main()


def test_main_updated_tree_empty_raises_exit(tmp_path):
    sys.argv = ['treescript-diff', 'original', 'updated']
    os.chdir(tmp_path)
    (original_treescript := tmp_path / 'original').touch()
    original_treescript.write_text('src/')
    (tmp_path / 'updated').touch()
    with pytest.raises(SystemExit, match='This TreeScript file was empty: updated'):
        main()


def test_main_default_simple_tree_add_file(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree())
    mock_treescript_dir.write_latest_tree(get_simple_tree_add_file())
    #
    expected = """src/welcome.css\n"""
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    collector.assert_expected(expected)


def test_main_a_simple_tree_add_file(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', '-a', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree())
    mock_treescript_dir.write_latest_tree(get_simple_tree_add_file())
    #
    expected = """src/welcome.css\n"""
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    collector.assert_expected(expected)


def test_main_r_simple_tree_add_file(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', '-r', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree())
    mock_treescript_dir.write_latest_tree(get_simple_tree_add_file())
    #
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    collector.assert_expected("\n")


def test_main_default_simple_tree_remove_file(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree_add_file())
    mock_treescript_dir.write_latest_tree(get_simple_tree())
    #
    expected = """\nsrc/welcome.css\n"""
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    collector.assert_expected(expected)


def test_main_a_simple_tree_remove_file(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', '-a', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree_add_file())
    mock_treescript_dir.write_latest_tree(get_simple_tree())
    #
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    collector.assert_expected("\n")


def test_main_r_simple_tree_remove_file(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', '-r', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree_add_file())
    mock_treescript_dir.write_latest_tree(get_simple_tree())
    #
    expected = """src/welcome.css\n"""
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    collector.assert_expected(expected)


def test_main_default_simple_tree_to_big_tree(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree())
    mock_treescript_dir.write_latest_tree(get_big_tree())
    #
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    assert len(collector.get_output().splitlines()) == 729


def test_main_a_simple_tree_to_big_tree(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', '-a', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree())
    mock_treescript_dir.write_latest_tree(get_big_tree())
    #
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    assert len(collector.get_output().splitlines()) == 727


def test_main_r_simple_tree_to_big_tree(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', '-r', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    # Insert Text into Temp TreeScript Files
    mock_treescript_dir.write_init_tree(get_simple_tree())
    mock_treescript_dir.write_latest_tree(get_big_tree())
    #
    expected = """src/hello.js\n"""
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    main()
    collector.assert_expected(expected)


def test_main_ar_simple_tree_to_big_tree(monkeypatch, mock_treescript_dir):
    sys.argv = ['treescript-diff', '-ar', mock_treescript_dir.initial_treescript_path, mock_treescript_dir.latest_treescript_path]
    os.chdir(mock_treescript_dir.get_root_dir())
    #
    collector = PrintCollector()
    monkeypatch.setattr(builtins, 'print', collector.get_mock_print())
    with pytest.raises(SystemExit, match='Added and Removed files are printed by default, separated by a blank line.'):
        main()
