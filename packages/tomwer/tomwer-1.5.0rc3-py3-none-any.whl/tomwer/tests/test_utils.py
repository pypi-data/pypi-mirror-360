from tomwer.utils import Launcher


def test_launcher():
    launcher = Launcher(prog="tomwer", version="1.0")
    launcher.add_command(
        "canvas", module_name="tomwer.app.canvas", description="open the orange-canvas"
    )
    launcher.print_help()
    launcher.execute_help(["tomwer", "canvas"])
