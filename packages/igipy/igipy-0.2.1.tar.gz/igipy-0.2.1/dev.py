# ------------------------------------------------------

dev_app = typer.Typer(
    name="dev",
    short_help="Submodule with development commands",
    add_completion=False,
)


def print_formats(counter: defaultdict) -> None:
    typer.echo(
        tabulate(
            tabular_data=sorted(counter.items(), key=lambda item: item[1], reverse=True),
            headers=["Format", "Count"],
            tablefmt="pipe",
        )
    )


def print_zip_formats(counter: defaultdict) -> None:
    typer.echo(
        tabulate(
            tabular_data=[
                (filename, extension, count)
                for filename in sorted(counter.keys())
                for extension, count in sorted(counter[filename].items(), key=lambda item: item[1], reverse=True)
            ],
            headers=["File", "Format", "Count"],
            tablefmt="pipe",
        )
    )


def dir_glob(directory: Path, pattern: str, absolute: bool = False) -> None:
    for number, path in enumerate(directory.glob(pattern), start=1):
        if path.is_file():
            typer.echo(f"[{number:>04}] {(path.absolute() if absolute else path.relative_to(directory)).as_posix()}")


@dev_app.callback(invoke_without_command=True)
def dev_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@dev_app.command(short_help="List files in game directory by pattern")
def game_dir_glob(pattern: str = "**/*", absolute: bool = False) -> None:
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

    dir_glob(directory=settings.game_dir, pattern=pattern, absolute=absolute)


@dev_app.command(short_help="List formats in game directory")
def source_dir_formats() -> None:
    settings = Config.load()
    settings.is_valid(exit_on_error=True)

    formats_counter = defaultdict(lambda: 0)

    for path in settings.source_dir.glob("**/*"):
        if not path.is_file():
            continue

        if path.suffix != ".dat":
            format_name = f"`{path.suffix}`"
        elif path.with_suffix(".mtp").exists():
            format_name = "`.dat` (mtp)"
        else:
            format_name = "`.dat` (graph)"

        formats_counter[format_name] += 1

    print_formats(formats_counter)


@dev_app.command(short_help="Search words in binary files")
def words(src: Path, min_length: int = 5, charset: str = string.printable) -> None:
    data = src.read_bytes()
    word = bytearray()

    charset = charset.encode()

    for byte in data:
        if byte in charset:
            word.append(byte)
        else:
            if len(word) >= min_length:
                typer.echo(word.decode())
            word.clear()
