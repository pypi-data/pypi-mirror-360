from nicegui import ui, app
from perfcat.config import navigations
from perfcat.utils import is_active_page, is_navigation_disable, notify


class Header(ui.header):
    def __init__(self) -> None:
        super().__init__()
        self.classes("items-center p-[0.3rem] pywebview-drag-region")
        self.props("elevated")

        with self:
            with ui.row().style("gap:0px;"):
                self.btn_back = ui.button(
                    icon="arrow_back",
                    on_click=lambda: ui.navigate.back()
                    if not is_navigation_disable()
                    else notify("当前禁止跳转", type="warning"),
                ).props("flat color=white")
                self.btn_menu = ui.button(icon="menu").props("flat color=white")
            ui.icon("insights")
            ui.label("Performance Catcher 2").classes("mr-auto")

            with ui.row().classes("gap-0 hidden"):
                self.btn_minimize = ui.button(icon="minimize").props("flat color=white")
                self.btn_fullscreen = ui.button(icon="fullscreen").props(
                    "flat color=white"
                )
                self.btn_clsoe = (
                    ui.button(icon="close")
                    .classes("hover:bg-red-400")
                    .props("flat color=white")
                )


class NavigationBar(ui.drawer):
    def __init__(self) -> None:
        super().__init__(side="left")
        self.classes("p-0")
        self.props("elevated width=200")
        self.bind_value(app.storage.general, "navigationbar_expand")

        with self:
            with ui.scroll_area().classes("mb-auto h-full") as scroll_area:
                content = ui.query(f"#{scroll_area.html_id} .q-scrollarea__content")
                content.classes("!p-0")

                # 路由菜单
                with ui.list().props("padding").classes("full-width"):
                    for _, value in navigations.items():
                        with ui.item() as item:  # type: ignore
                            item.on_click(
                                lambda arg, path=value["path"]: ui.navigate.to(path)
                                if not is_navigation_disable()
                                else notify("当前禁止跳转", type="warning")
                            )
                            item.props["active"] = is_active_page(value["path"])
                            with ui.item_section().props("avatar"):
                                ui.icon(value["icon"])
                            with ui.item_section():
                                ui.item_label(value["title"])

            # 固定设定栏
            with ui.list().props("padding bordered").classes("full-width"):
                with ui.item(
                    on_click=lambda: ui.notification("尚未开发", type="warning")
                ) as self.setting_item:
                    with ui.item_section().props("avatar"):
                        ui.icon("settings")
                    with ui.item_section():
                        ui.item_label("设置")
                with ui.item(
                    on_click=lambda: ui.notification("尚未开发", type="warning")
                ) as self.setting_item:
                    with ui.item_section().props("avatar"):
                        ui.icon("info")
                    with ui.item_section():
                        ui.item_label("关于")


class Page:
    def __init__(self, path: str, *, title: str | None = None) -> None:
        @ui.page(path, title=title)
        async def _():
            await self._frame()
            await self.render()

    async def _frame(self, *args):
        ui.query("html").style("overflow:hidden")
        ui.query("main").style("height:92vh")
        ui.query("main .nicegui-content")
        ui.query(".nicegui-content").classes("pr-8")

        # 头
        self.header = Header()
        self.header.btn_menu.on_click(lambda e: self.navigationbar.toggle())

        # 导航菜单
        self.navigationbar = NavigationBar()

    async def render(self, *args, **kwargs):
        raise NotImplementedError
