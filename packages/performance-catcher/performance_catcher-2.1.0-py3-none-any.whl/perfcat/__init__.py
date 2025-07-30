import secrets
from . import pages, logger  # noqa
from nicegui import app, ui, App
from importlib import resources
from perfcat.services import AndroidProfielerService

with resources.path("perfcat", "static") as path:
    app.add_static_files("/static", path.as_posix())

with resources.path("perfcat", "media") as path:
    app.add_static_files(
        "/media",
        path.as_posix(),
    )


@app.on_shutdown
async def teardown(app: App):
    await AndroidProfielerService.stop_adb_server()


def run(debug: bool = False):

    app.native.window_args["resizable"] = True
    app.native.window_args["text_select"] = True
    app.native.start_args['debug'] = debug
    app.native.start_args['user_agent'] = "native"
    app.native.settings['ALLOW_DOWNLOADS'] = True

    ui.run(
        native=True,
        reload=False,
        window_size=(1280, 800),
        title="Performance Catcher",
        frameless=False,
        storage_secret=secrets.token_hex(16),
    )
