from typing import Any, Callable, Literal, Optional, Union
from nicegui import Client, app,ui

def resolve(page:Callable):
    """
    Resolve a path to a file, expanding any environment variables and
    relative paths.
    """
    return Client.page_routes.get(page,None)


def is_active_page(path:str):
    """
    Check if current page is the same as the given path
    """
    return ui.context.client.page.path.startswith(path)


def notify(message: Any, *,
           position: Literal[
               'top-left',
               'top-right',
               'bottom-left',
               'bottom-right',
               'top',
               'bottom',
               'left',
               'right',
               'center',
           ] = 'bottom',
           close_button: Union[bool, str] = False,
           type: Optional[Literal[  # pylint: disable=redefined-builtin
               'positive',
               'negative',
               'warning',
               'info',
               'ongoing',
           ]] = None,
           color: Optional[str] = None,
           multi_line: bool = False,
           **kwargs: Any):
    """
    Notify the user with a message
    """
    for client in Client.instances.values():
        if not client.has_socket_connection:
            continue
        with client:
            ui.notify(
                message,
                position=position, 
                close_button=close_button, 
                type=type, 
                color=color, 
                multi_line=multi_line, 
                **kwargs)
            


def is_navigation_disable():
    return app.storage.general.get("navigataion_disable", False)


def set_navigation_disable(value:bool):
    app.storage.general["navigataion_disable"]= value