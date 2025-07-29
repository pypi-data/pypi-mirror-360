import flet as ft
import typing
from flet import OptionalNumber
from .page_meta import PageMeta

try:
    from rich import print
except:
    pass


def get_label(label: typing.Union[str, typing.Callable]) -> str:
    if isinstance(label, str):
        return label
    else:
        return label()


class UIBase:
    the_page: ft.Page
    pages: typing.List[PageMeta]
    current_index: int
    main_content: ft.Control
    animated_switcher: ft.AnimatedSwitcher
    ching: bool
    progress_ring: ft.ProgressRing
    use_custom_titlebar: bool
    is_phone: bool
    is_web: bool
    is_mac: bool
    

    def __init__(
        self, pages: typing.List[PageMeta], the_page: ft.Page, use_custom_titlebar: bool = True
    ):
        self.pages = pages
        self.the_page = the_page
        self.current_index = 0
        self.ching = False
        self.progress_ring = ft.ProgressRing(width=48, height=48)
        self.use_custom_titlebar = use_custom_titlebar
        # 系统类型
        self.get_ui()

    def setup_window(self, page: ft.Page) -> None:
        self.the_page = page
        """初始化窗口设置"""
        page.title = self.the_page.title
        if self.use_custom_titlebar:
            page.window.title_bar_hidden = True
            page.window.title_bar_buttons_hidden = True
        page.padding = 0
        self.is_phone = (
            self.the_page.platform == ft.PagePlatform.ANDROID
            or self.the_page.platform == ft.PagePlatform.IOS
        )
        self.is_web = self.the_page.web
        self.is_mac = self.the_page.platform == ft.PagePlatform.MACOS

    def create_window_controls(self) -> ft.Row:
        """创建窗口控制按钮"""
        self.top = ft.IconButton(
            icon=ft.Icons.PUSH_PIN_OUTLINED,
            selected_icon=ft.Icons.PUSH_PIN_ROUNDED,
            icon_size=16,
            selected=False,
            on_click=self.toggle_always_on_top,
            style=self.get_button_style(),
            tooltip="置顶窗口",
        )
        self.full = ft.IconButton(
            icon=ft.Icons.FULLSCREEN_ROUNDED,
            selected_icon=ft.Icons.FULLSCREEN_EXIT_ROUNDED,
            icon_size=16,
            selected=False,
            on_click=self.toggle_fullscreen,
            style=self.get_button_style(),
            tooltip="全屏",
        )
        self.min = ft.IconButton(
            icon=ft.Icons.REMOVE_ROUNDED,
            icon_size=16,
            on_click=self.minimize_window,
            style=self.get_button_style(),
            tooltip="最小化",
        )
        self.max = ft.IconButton(
            icon=ft.Icons.BRANDING_WATERMARK,
            selected_icon=ft.Icons.BRANDING_WATERMARK_OUTLINED,
            selected=False,
            icon_size=16,
            on_click=self.toggle_maximize,
            style=self.get_button_style(),
            tooltip="最大化",
        )
        self.close = ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_size=16,
            hover_color=ft.Colors.RED_900,
            on_click=self.close_window,
            style=self.get_button_style(),
            tooltip="关闭",
        )
        if self.is_mac:
            # 修改颜色
            self.close.icon_color = ft.Colors.RED
            self.close.icon = ft.Icons.CIRCLE
            self.min.icon_color = ft.Colors.YELLOW
            self.min.icon = ft.Icons.CIRCLE
            self.max.icon_color = ft.Colors.GREEN
            self.max.selected_icon = ft.Icons.CIRCLE
            self.max.selected_icon_color = ft.Colors.GREEN
            self.max.icon = ft.Icons.CIRCLE
            self.close.hover_color = None

        if self.is_mac:
            return ft.Row(
                controls=[
                    self.close,
                    self.min,
                    self.max,
                    self.top,
                    self.full,
                ],
                spacing=5,
            )
        return ft.Row(
            controls=[
                self.top,
                self.full,
                self.min,
                self.max,
                self.close,
            ],
            spacing=5,
        )

    def get_button_style(self) -> ft.ButtonStyle:
        """获取按钮样式"""
        return ft.ButtonStyle(
            padding=12,
            shape=ft.RoundedRectangleBorder(radius=0),
        )

    def create_title_bar(self, page: ft.Page) -> ft.Container:
        controls = [
            ft.WindowDragArea(
                content=ft.Container(
                    content=ft.Row(
                        controls=(
                            [
                                ft.Image(f"/icon.png"),
                                ft.Text(
                                    page.title,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                            ]
                        ),
                        spacing=8,
                        expand=True,
                        alignment=(
                            ft.MainAxisAlignment.START
                            if not self.is_mac
                            else ft.MainAxisAlignment.CENTER
                        ),
                    ),
                    padding=ft.padding.only(left=12, top=8, bottom=8, right=100),
                    expand=True,
                ),
                expand=True,
            ),
            self.create_window_controls(),
        ]
        """创建标题栏"""
        return ft.Container(
            content=ft.Row(
                controls=controls if not self.is_mac else controls[::-1],
                spacing=0,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=40,
            border=ft.border.only(bottom=ft.BorderSide(1)),
            bgcolor="background",
        )

    def create_navigation_bar(self, change_page_handler: typing.Callable) -> ft.NavigationBar:
        return ft.NavigationBar(
            elevation=-100,
            selected_index=self.current_index,
            destinations=[
                ft.NavigationBarDestination(
                    icon=i.icon,
                    selected_icon=i.selected_icon,
                    label=i.title(),
                )
                for i in self.pages
            ],
            on_change=change_page_handler,
        )

    def create_navigation_rail(self, change_page_handler: typing.Callable) -> ft.NavigationRail:
        """创建导航栏"""
        return ft.NavigationRail(
            selected_index=self.current_index,
            leading=(
                ft.Column(
                    [
                        ft.Image(f"/icon.png", height=75),
                        ft.Text(self.the_page.title, size=16),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                if self.is_web
                else None
            ),
            min_width=100,
            min_extended_width=200,
            extended=True,
            destinations=[
                ft.NavigationRailDestination(
                    icon=i.icon,
                    selected_icon=i.selected_icon,
                    label=i.title(),
                )
                for i in self.pages
            ],
            on_change=change_page_handler,
        )

    def create_content_area(self) -> ft.Container:
        """创建内容区域"""
        self.animated_switcher = ft.AnimatedSwitcher(
            content=ft.Text("主页内容"),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
        )
        return ft.Container(
            content=self.animated_switcher,
            expand=True,
            padding=20,
            alignment=ft.alignment.center,
            bgcolor=self.the_page.bgcolor,
        )

    def create_main_layout(self, page: ft.Page) -> typing.Union[ft.Column, ft.SafeArea, ft.Row]:
        """创建主布局"""
        self.content_area = self.create_content_area()

        # 单页时不显示侧边栏
        if len(self.pages) <= 1:
            controls = [self.content_area]
            if self.use_custom_titlebar:
                controls.insert(0, self.create_title_bar(page))
            return ft.Column(
                controls=controls,
                spacing=0,
                expand=True,
            )
        else:
            if self.is_phone:
                self.navigation = self.create_navigation_bar(self.change_page_content)
                return ft.SafeArea(
                    ft.Column(
                        controls=[
                            self.content_area,
                            self.navigation,
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                )
            else:
                self.navigation = self.create_navigation_rail(self.change_page_content)
                r = ft.Row(
                    controls=[
                        self.navigation,
                        ft.VerticalDivider(width=1),
                        self.content_area,
                    ],
                    spacing=0,
                    expand=True,
                )
                return (
                    r
                    if self.is_web
                    else ft.Column(
                        controls=(
                            [self.create_title_bar(page), r]
                            if self.use_custom_titlebar
                            else [r]
                        ),
                        spacing=0,
                        expand=True,
                    )
                )

    def change_page_content(self, e: ft.ControlEvent) -> None:
        """处理页面切换"""
        # 判断是否点击当前页
        if self.current_index == int(e.control.selected_index):
            return
        if not self.ching:
            self.ching = True
            self.current_index = int(e.control.selected_index)
            # 使用动画切换内容
            if (
                hasattr(self, "animated_switcher")
                and self.animated_switcher.page is not None
            ):
                self.animated_switcher.content = self.progress_ring
                self.animated_switcher.update()

                content = (
                    self.pages[self.current_index].func(self)
                    if callable(self.pages[self.current_index].func)
                    else ft.Container()
                )
                self.animated_switcher.content = content
                self.animated_switcher.update()
            self.ching = False
        else:
            e.control.selected_index = self.current_index
            e.control.update()

    def toggle_always_on_top(self, e: ft.ControlEvent) -> None:
        """切换窗口置顶状态"""
        e.control.page.window.always_on_top = not e.control.page.window.always_on_top
        e.control.selected = e.control.page.window.always_on_top
        e.control.page.update()

    def minimize_window(self, e: ft.ControlEvent) -> None:
        """最小化窗口"""
        e.control.page.window.minimized = True
        e.control.page.update()

    def toggle_maximize(self, e: ft.ControlEvent) -> None:
        """切换最大化状态"""
        if e.control.page.window.full_screen:
            self.toggle_fullscreen(e)
        else:
            e.control.page.window.maximized = not e.control.page.window.maximized
        self.max.selected = e.control.page.window.maximized
        e.control.page.update()

    def toggle_fullscreen(self, e: ft.ControlEvent) -> None:
        """切换全屏状态"""
        is_fullscreen = not e.control.page.window.full_screen
        e.control.page.window.full_screen = is_fullscreen
        self.full.selected = is_fullscreen
        e.control.page.update()

    def close_window(self, e: ft.ControlEvent) -> None:
        """关闭窗口"""
        e.control.page.window.close()

    def update_pages(self, new_pages: typing.Optional[typing.List[PageMeta]] = None) -> None:
        """更新页面配置"""
        if new_pages is None:
            new_pages = self.pages
        # 记住当前选中的页面
        current_label = self.pages[self.current_index].label if self.pages else None

        self.pages = new_pages

        if self.the_page:
            # 清除当前页面内容
            self.the_page.clean()

            # 创建新的布局
            self.main_content = self.create_main_layout(self.the_page)

            # 恢复之前的选中状态
            if current_label:
                for i, page in enumerate(self.pages):
                    if page.label == current_label:
                        self.current_index = i
                        break

            # 先添加主内容到页面
            self.the_page.add(self.main_content)
            
            # 更新当前显示的内容
            if hasattr(self, "animated_switcher"):
                self.animated_switcher.content = self.progress_ring
                self.animated_switcher.update()
                content = (
                    self.pages[self.current_index].func(self)
                    if callable(self.pages[self.current_index].func)
                    else ft.Container()
                )
                self.animated_switcher.content = content
                self.animated_switcher.update()
            
            self.the_page.update()

    def the_page_wh(self) -> typing.Tuple[OptionalNumber, OptionalNumber]:
        return self.the_page.width, self.the_page.height

    def change_page_by_label(self, label: str) -> None:
        """通过页面label切换当前页面"""
        for i, page in enumerate(self.pages):
            if page.label == label:
                if self.current_index != i:
                    self.current_index = i
                    # 更新内容区域
                    # 使用动画切换内容
                    self.animated_switcher.content = self.progress_ring
                    self.animated_switcher.update()
                    content = (
                        self.pages[self.current_index].func(self)
                        if callable(self.pages[self.current_index].func)
                        else ft.Container()  # 默认空容器
                    )
                    self.animated_switcher.content = content
                    self.animated_switcher.update()

                    # 更新导航栏选中状态
                    if hasattr(self, "navigation"):
                        if isinstance(self.navigation, ft.NavigationBar):
                            self.navigation.selected_index = self.current_index
                            self.navigation.update()
                        elif isinstance(self.navigation, ft.NavigationRail):
                            self.navigation.selected_index = self.current_index
                            self.navigation.update()
                return
        raise ValueError(f"未找到label为'{label}'的页面")

    def get_ui(self) -> None:
        """获取UI函数"""
        self.the_page.clean()
        self.setup_window(self.the_page)
        self.main_content = self.create_main_layout(self.the_page)
        self.ching = True
        # 初始化动画组件
        self.animated_switcher.content = self.progress_ring
        self.the_page.add(self.main_content)
        # 设置初始内容
        content = (
            self.pages[self.current_index].func(self)
            if callable(self.pages[self.current_index].func)
            else ft.Container()
        )
        self.animated_switcher.content = content
        self.the_page.update()
        self.ching = False
