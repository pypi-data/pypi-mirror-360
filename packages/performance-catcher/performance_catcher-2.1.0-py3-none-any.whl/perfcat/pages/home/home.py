import json
import os
from nicegui import app, ui
from fastapi.responses import RedirectResponse
from perfcat.components.layout import Page
from perfcat.services import RecordService


@ui.page("/")
def index():
    return RedirectResponse(url="/home")


class HomePage(Page):
    def __init__(self) -> None:
        super().__init__("/home", title="主页")

    async def render(self):

        with ui.row():
            ui.button("打开文件",icon="file_open",on_click=self._open_file)
            ui.button("查看目录",icon="folder",on_click=lambda: os.system(f"explorer {os.path.abspath('./records')}"))

        columns = [
            {"name": "name", "label": "日志名称", "field": "name", "align": "left"},
            {"name": "platform", "label": "平台", "field": "platform", "align": "left"},
            {"name":"abs_path","label":"绝对路径","field":"abs_path","align":"left","classes":"hidden","headerClasses":"hidden"},
            {"name": "model_name", "label": "测试机名", "field": "model_name"},
            {"name": "package_name", "label": "包名", "field": "package_name"},
            {"name": "process", "label": "进程名", "field": "process"},
            {"name": "version", "label": "构建版本", "field": "version"},
            {
                "name": "created_at",
                "label": "创建时间",
                "field": "created_at",
                "sortable": True,
                "sortOrder": "da",
            },
            {"name": "actions", "label": "操作", "field": "actions", "align": "center"},
        ]

        rows = self.load_record_data()
        with (
            ui.table(
                columns=columns,
                rows=rows,
                pagination={
                    "rowsPerPage": 50,
                    "sortBy": "created_at",
                    "descending": True,
                },
            )
            .classes("w-full h-full")
            .props("separator=cell bordered striped hoverable") as self.table
        ):
            self.table.add_slot(
                "body-cell-actions",
                """
                <q-td :props="props">
                    <q-btn @click="$parent.$emit('action_preview', props.row)" icon="preview" flat />
                    <q-btn @click="$parent.$emit('action_delete', props.row)" icon="delete" flat />
                </q-td>
            """,
            )

            self.table.on(
                "action_preview",
                lambda row: ui.navigate.to(f"/home/report?filename={row.args['abs_path']}",),
            )

            self.table.on("action_delete", self._remove_row)

    async def _remove_row(self,row):
        with ui.dialog() as dialog, ui.card():
            ui.label('确定要删除?')
            with ui.row():
                ui.button('是',color="red", on_click=lambda: dialog.submit('Yes'))
                ui.button('否', on_click=lambda: dialog.submit('No'))
        result = await dialog
        if result=="Yes":
            if row.args in self.table.rows:
                self.table.rows.remove(row.args)
                os.remove(row.args["abs_path"])
                self.table.update()
                ui.notify("删除成功",type="positive")

    async def _open_file(self):
        if app.native.main_window:
            filenames = await (
                app.native
                .main_window
                .create_file_dialog(
                    directory=os.path.abspath("./records"),
                    file_types=('PCAT Files (*.pcat)',)
                    )
            )
            if filenames:
                filename = filenames[0]
                ui.navigate.to(f"/home/report?filename={filename}")

    def load_record_data(self):
        files = RecordService.record_files()

        datas = []
        for file in files:
            abs_path = os.path.abspath(os.path.join("records",file))
            with open(abs_path, "r",encoding="utf-8") as f:
                info = json.loads(f.readline().strip())
                datas.append(
                    {
                        "name": file,
                        "abs_path":abs_path,
                        "platform": info.get("platform", "未知"),
                        "model_name": info.get("model", "未知"),
                        "package_name": info.get("app", "未知"),
                        "process": info.get("process", "未知"),
                        "version": info.get("version", "未知"),
                        "created_at": info.get("created_at", "未知"),
                    }
                )

        return datas


HomePage()
