from pyupgrade._main import main as pyupgrade_main
from pyupgrade._data import FUNCS
import argparse
from dataclasses import dataclass


@dataclass
class Plugin:
    callback: callable
    disabled: bool = False

    @property
    def name(self):
        callback_module = self.callback.__module__
        _, _, name = callback_module.rpartition(".")
        return name

    def disable(self):
        self.disabled = True

    def __call__(self, *args, **kwargs):
        if self.disabled:
            return

        yield from self.callback(*args, **kwargs)


def arg_parser():
    parser = argparse.ArgumentParser(description="pyupgradex CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # plugins command
    plugins_parser = subparsers.add_parser("plugins", help="List registered plugin module names")

    # run command
    run_parser = subparsers.add_parser("run", help="Run pyupgrade with optional plugin disabling")
    run_parser.add_argument(
        "--disable-plugins",
        nargs="*",
        default=[],
        help="Specify plugin module names to disable",
    )

    return parser


def main():
    parser = arg_parser()
    args, unknown_args = parser.parse_known_args()

    plugins = {}
    for funcs in FUNCS.values():
        for i, func in enumerate(funcs):
            plugin = Plugin(callback=func)
            plugins[plugin.name] = plugin
            funcs[i] = plugin

    if args.command == "plugins":
        print("\n".join(plugins.keys()))
        return

    elif args.command == "run":
        for p in args.disable_plugins:
            plugins[p].disable()

        pyupgrade_main(unknown_args)


if __name__ == "__main__":
    main()
