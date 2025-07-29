from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterable

project_dir = Path(__file__).resolve().parent.parent
tests_dir = project_dir / "tests"
test_data_dir = tests_dir / "data"
package_dir = project_dir / "bulkllm"


def _src_from_test(test_path: Path, src_root: Path) -> Path:
    """
    Reverse the mapping rule used for test generation:

        tests/test_pkg/test_mod/test_baz.py  ->  src_root/pkg/mod/baz.py
    """
    rel_parts: Iterable[str] = test_path.with_suffix("").relative_to(tests_dir).parts
    # strip the 'test_' prefix from every component
    stripped = [part.replace("test_", "", 1) for part in rel_parts]
    filename = stripped[-1] + ".py"
    return src_root.joinpath(*stripped[:-1], filename)


def create_missing_tests(
    src_root: str | Path,
    tests_root: str | Path,
    *,
    write_stub: bool = True,
    stub_template: str | None = None,
    skip_dunder: bool = True,
    skip_existing_tests: bool = True,
) -> None:
    """
    Ensure every *.py file under *src_root* has a corresponding test stub under *tests_root*.
    In addition, **delete** any *empty* test file that no longer has a matching source file.

    (Parameters unchanged - see original docstring.)
    """
    src_root = Path(src_root).resolve()
    tests_root = Path(tests_root).resolve()

    if not src_root.is_dir():
        msg = f"Source directory not found: {src_root}"
        raise NotADirectoryError(msg)

    # ---------------------------------------------------------------------
    # 1. PRUNE - delete empty orphan test files
    # ---------------------------------------------------------------------
    for test_file in tests_root.rglob("test_*.py"):
        if test_file.stat().st_size:  # not empty
            continue
        corresponding_src = _src_from_test(test_file, src_root)
        if not corresponding_src.exists():
            test_file.unlink()
            # clean up now-empty parent dirs (optional)
            parent = test_file.parent
            while parent != tests_root and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent

    # ---------------------------------------------------------------------
    # 2 & 3. COLLECT and CREATE - behaviour identical to the original
    # ---------------------------------------------------------------------
    default_stub = ""

    for src_file in src_root.rglob("*.py"):
        if skip_dunder and src_file.name == "__init__.py":
            continue
        if skip_existing_tests and src_file.name.startswith("test_"):
            continue
        if src_file.name == "_version.py":
            continue

        rel_parts = src_file.relative_to(src_root).with_suffix("").parts
        dir_parts = [f"test_{p}" for p in rel_parts[:-1]]
        test_fname = f"test_{rel_parts[-1]}.py"
        dest_path = tests_root.joinpath(*dir_parts, test_fname)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if dest_path.exists() and skip_existing_tests:
            continue

        if write_stub:
            module_path = ".".join(src_file.relative_to(src_root).with_suffix("").parts)
            content = (stub_template or default_stub).format(module=module_path)
            dest_path.write_text(content, encoding="utf-8")
        else:
            dest_path.touch()


@pytest.fixture(scope="session", autouse=True)
def _create_missing_tests():
    create_missing_tests(package_dir, tests_dir)
