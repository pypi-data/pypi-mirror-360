from daydream.cli._app import app
from daydream.utils import import_submodules

import_submodules("daydream.cli")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
