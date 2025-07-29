import zipfile
from collections.abc import Generator
from fnmatch import fnmatch
from io import BytesIO
from pathlib import Path

import typer

from igipy import formats


def validate_file_path_exists(path: Path | str) -> Path:
    path = Path(path)

    if not path.exists():
        typer.echo(typer.style(f"{path.as_posix()} doesn't exists", fg=typer.colors.RED))

    if not path.is_file(follow_symlinks=False):
        typer.echo(typer.style(f"{path.as_posix()} is not a file", fg=typer.colors.RED))

    return path


def validate_file_path_not_exists(path: Path) -> Path:
    path = Path(path)

    if path.exists():
        typer.echo(typer.style(f"{path.as_posix()} exists", fg=typer.colors.RED))

    return path


def search_for_convert_in_directory(patterns: list[str], directory: Path) -> Generator[tuple[Path, Path, BytesIO]]:
    for src in directory.glob("**/*"):
        for pattern in patterns:
            if fnmatch(src.as_posix(), pattern) and src.is_file():
                src_path = src.relative_to(directory)
                src_stream = BytesIO(src.read_bytes())
                yield src, src_path, src_stream


def search_for_convert_in_zip(patterns: list[str], directory: Path) -> Generator[tuple[Path, Path, BytesIO]]:
    for zip_path in directory.glob("**/*.zip"):
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            for file_info in zip_file.infolist():
                for pattern in patterns:
                    if fnmatch(file_info.filename, pattern):
                        src = zip_path.joinpath(file_info.filename)
                        src_path = src.relative_to(directory)
                        src_stream = BytesIO(zip_file.read(file_info))
                        yield src, src_path, src_stream


def search_for_convert(
    patterns: list[str], src_dir: Path | None = None, zip_dir: Path | None = None
) -> Generator[tuple[Path, Path, BytesIO]]:
    if src_dir:
        yield from search_for_convert_in_directory(patterns=patterns, directory=src_dir)

    if zip_dir:
        yield from search_for_convert_in_zip(patterns=patterns, directory=zip_dir)


def convert_all(  # noqa: PLR0913
    patterns: list[str],
    formater: type[formats.FileModel],
    dst_dir: Path | dict[str, Path],
    src_dir: Path | None = None,
    zip_dir: Path | None = None,
    dry: bool = True,
) -> None:
    searcher = search_for_convert(patterns=patterns, src_dir=src_dir, zip_dir=zip_dir)

    for i, (src, src_path, src_stream) in enumerate(searcher, start=1):
        try:
            dst_path, dst_stream = formater.model_validate_stream(src_stream).model_dump_file(src_path)
        except formats.base.FileIgnored:
            typer.echo(f"Convert [{i:>05}]: {typer.style(src.as_posix(), fg='yellow')} ignored")
            continue

        if isinstance(dst_dir, dict):
            dst = dst_dir[dst_path.suffix].joinpath(dst_path)
        elif isinstance(dst_dir, Path):
            dst = dst_dir.joinpath(dst_path)
        else:
            raise TypeError(f"dst_dir must be Path or dict[str, Path], not {type(dst_dir)}")

        typer.echo(
            f'Convert [{i:>05}]: "{typer.style(src.as_posix(), fg="green")}" '
            f'to "{typer.style(dst.as_posix(), fg="yellow")}"'
        )

        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(dst_stream.getvalue())
