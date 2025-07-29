import os
import sys

import clyp.cli as cli_mod


def _run_cli(args, cwd, monkeypatch, capsys):
    # Change to working directory and set argv
    monkeypatch.chdir(cwd)
    monkeypatch.setenv("PYTHONPATH", os.getcwd())
    monkeypatch.setattr(sys, "argv", ["clyp"] + args)
    # Capture output
    try:
        cli_mod.main()
    except SystemExit as e:
        # Allow clean exit
        if e.code not in (0, None):
            raise
    return capsys.readouterr()


def test_build_and_run_single_file(tmp_path, monkeypatch, capsys):
    # Create a simple Clyp file
    clyp_file = tmp_path / "hello.clyp"
    clyp_file.write_text('print("Hello, Clyp Testing!");\n')

    # Build the Clyp file
    _run_cli(["build", str(clyp_file)], tmp_path, monkeypatch, capsys)

    # Verify the .clb file is created
    build_dir = tmp_path / "build"
    assert build_dir.exists(), "Build directory not created"
    clb_file = build_dir / "hello.clb"
    assert clb_file.exists(), ".clb file not created"

    # Run the built module and capture output
    result = _run_cli(["run", str(clb_file)], tmp_path, monkeypatch, capsys)
    # The Clyp code prints to stdout
    assert "Hello, Clyp Testing!" in result.out


def test_build_and_run_project(tmp_path, monkeypatch, capsys):
    # Initialize a new Clyp project
    _run_cli(["init", "myproj"], tmp_path, monkeypatch, capsys)
    project_dir = tmp_path / "myproj"
    # Build the project
    _run_cli(["build"], project_dir, monkeypatch, capsys)
    # Verify the .clb file is created in dist
    build_dir = project_dir / "dist"
    assert build_dir.exists(), "Project dist directory not created"
    clb_file = build_dir / "myproj.clb"
    assert clb_file.exists(), "Project .clb file not created"
    # Run the built project
    result = _run_cli(["run", str(clb_file)], project_dir, monkeypatch, capsys)
    assert "Hello from Clyp!" in result.out
