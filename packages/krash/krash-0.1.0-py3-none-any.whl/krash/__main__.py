from .cli import CLI, CLIAdapter


def main() -> None:
    cli = CLI()
    cli_adapter = CLIAdapter(cli)
    cli_adapter.run()


if __name__ == "__main__":
    main()
