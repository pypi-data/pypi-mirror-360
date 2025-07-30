import time
from typing import Dict, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QSizePolicy, QMenu,
                               QScrollArea, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QTimer, QObject, QRectF
from PySide6.QtGui import (QColor, QPainter, QBrush, QPainterPath,
                           QPen)

from .base_page import PageBase
from .utils.BotTools import BotToolKit
from .utils.subpages.roster import PermissionConfigurator
from .utils.client import talker, ResponsePayload


class BotCard(QFrame):
    """Bot卡片"""
    status_changed = Signal(bool)
    matcher_signal = Signal(ResponsePayload)

    def __init__(self, bot_id: str, adapter: str, parent=None):
        super().__init__(parent)
        self.bot_id = bot_id
        self.adapter_type = adapter
        self._is_online = True
        self.offline_color = QColor("#DCDCDC")
        self.theme_color = self.original_theme_color
        if not self.theme_color.isValid():
            self.theme_color = QColor("#6A11CB")
        self.last_update_time = time.time()
        self._init_style()
        self._init_ui()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.status_changed.connect(self._toggle_status)
        self.matcher_signal.connect(self._roster)

    @property
    def original_theme_color(self):
        return QColor(BotToolKit.color.get(self.bot_id, "#6A11CB"))

    def _init_style(self):
        self.setMinimumSize(280, 220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Preferred)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.setStyleSheet(f"""
            BotCard {{
                background: white;
                border-radius: 12px;
                border: none;
                padding: 0;
                margin: 0;
            }}
            QLabel {{
                margin: 0;
                padding: 0;
            }}
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        self.setLayout(main_layout)

        # 顶部装饰条
        self._add_top_decorator()

        # 头部区域
        header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        # 状态指示器
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(12, 12)
        self.status_indicator.setStyleSheet(f"""
            background: {'#4CAF50' if self._is_online else '#F44336'};
            border-radius: 6px;
            border: 2px solid white;
        """)

        # ID显示
        self.id_label = QLabel(self.bot_id)
        self.id_label.setStyleSheet(f"""
            font: bold 16px '微软雅黑';
            color: {self.theme_color.darker().name()};
        """)

        # 适配器图标
        self.adapter_icon = QLabel()
        self.adapter_icon.setFixedSize(24, 24)
        self.adapter_icon.setStyleSheet(f"""
            font: 16px;
            color: white;
            background: {self.theme_color.name()};
            border-radius: 12px;
            qproperty-alignment: AlignCenter;
        """)

        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.id_label)
        header_layout.addStretch()
        header_layout.addWidget(self.adapter_icon)
        header.setLayout(header_layout)
        self.header = header
        main_layout.addWidget(header)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"""
            color: {self.theme_color.lighter(180).name()};
            margin: 4px 0;
        """)
        main_layout.addWidget(separator)

        # 内容区域 - 层级化布局
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        content_layout.addStretch(1)

        # 统计信息（缩进布局）
        self.total_msg = QLabel("0")
        self.rate_label = QLabel("0/min")
        self.time_label = QLabel("--")

        # 构造 metrics 列表
        metrics = [
            ("消息总量", self.total_msg, "#2196F3"),
            ("近30分钟处理速率", self.rate_label, "#4CAF50"),
            ("在线时长", self.time_label, "#FF9800")
        ]

        for title, value, color in metrics:
            metric_widget = QWidget()
            metric_layout = QHBoxLayout()
            metric_layout.setContentsMargins(8, 6, 8, 6)
            metric_layout.setSpacing(10)

            # 左侧装饰条
            decorator = QLabel()
            decorator.setFixedWidth(4)
            decorator.setStyleSheet(
                f"background: {color}; border-radius: 2px;")

            metric_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            decorator.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            text_widget = QWidget()
            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(4)

            title_label = QLabel(title)
            title_label.setStyleSheet(f"color: {color}; font: 12px;")

            value.setWordWrap(True)
            value.setAlignment(Qt.AlignmentFlag.AlignLeft |
                               Qt.AlignmentFlag.AlignVCenter)
            value.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
            value.setStyleSheet(f"""
                color: {color};
                padding-left: 8px;
                font: bold 16px 'Segoe UI';
                margin-right: 8px;
            """)

            text_layout.addWidget(title_label)
            text_layout.addWidget(value)
            text_widget.setLayout(text_layout)

            metric_layout.addWidget(decorator)
            metric_layout.addWidget(text_widget)
            metric_layout.addStretch()
            metric_widget.setLayout(metric_layout)
            content_layout.addWidget(metric_widget)

        content.setLayout(content_layout)
        main_layout.addWidget(content)

        # 底部状态栏
        self.footer = QWidget()
        self.footer.setStyleSheet(f"""
            background: {self.theme_color.lighter(115).name()};
            border-radius: 6px;
            padding: 6px 12px;
            color: white; 
        """)
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(8)

        self.status_text = QLabel("在线" if self._is_online else "离线")
        self.status_text.setStyleSheet(f"""
            color: {self.theme_color.darker(150).name()};
            font: 12px;
        """)

        footer_layout.addWidget(self.status_text)
        footer_layout.addStretch()

        self.last_update = QLabel()
        self._update_time_text()
        self.last_update.setStyleSheet("color: #666666; font: 11px;")
        footer_layout.addWidget(self.last_update)

        self.footer.setLayout(footer_layout)
        main_layout.addWidget(self.footer)

    def _add_top_decorator(self):
        """添加顶部装饰渐变条"""
        self.decorator = QWidget(self)
        self.decorator.setFixedHeight(4)
        self.decorator.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.theme_color.name()}, 
                stop:1 {self.theme_color.lighter(120).name()});
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        """)
        self.decorator.setGeometry(0, 0, self.width(), 4)
        self.decorator.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def _update_time_text(self):
        """更新时间显示为时:分:秒格式"""
        time_str = time.strftime(
            "%H:%M:%S", time.localtime(self.last_update_time))
        self.last_update.setText(f"更新: {time_str}")

    def format_uptime(self, seconds: int) -> str:
        """将秒数转换为标准时间格式"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = ((seconds % 3600) + 30) // 60  # 四舍五入
        return f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

    def update_data(self, total: int, rate: float, uptime: Optional[int] = None):
        """更新所有数据字段"""
        self.last_update_time = time.time()
        try:
            total = int(total)
            self.total_msg.setText(f"{total:,}")
        except (ValueError, TypeError):
            self.total_msg.setText("--")

        try:
            rate = float(rate)
            self.rate_label.setText(f"{rate:.1f}/min")
        except (ValueError, TypeError):
            self.rate_label.setText("--/min")

        try:
            uptime = int(uptime) if uptime is not None else None
            self.time_label.setText(self.format_uptime(
                uptime) if uptime and uptime > 0 else "--")
        except (ValueError, TypeError):
            self.time_label.setText("--")

        # 更新适配器图标
        adapter_icons = {
            "WebSocket": "🌐",
            "HTTP": "⚡",
            "gRPC": "📡",
            "MQTT": "📶"
        }
        icon = adapter_icons.get(self.adapter_type, "🔌")
        self.adapter_icon.setText(icon)

        # 更新时间显示
        self._update_time_text()
        self.adjustSize()
        self.updateGeometry()

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #EEE;
                border-radius: 8px;
                padding: 8px 0;
                min-width: 140px;
            }
            QMenu::item {
                padding: 8px 24px;
                color: #333;
                font: 14px;
            }
            QMenu::item:selected {
                background: #F0F4F8;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background: #EEE;
                margin: 4px 0;
            }
        """)

        status_action = menu.addAction("下线" if self._is_online else "上线")
        menu.addAction("📊 统计详情")
        menu.addSeparator()
        roster_action = menu.addAction("⚙️ 名单设置")

        action = menu.exec_(self.mapToGlobal(pos))
        if action == status_action:
            self._toggle_status()

        elif action == roster_action:
            talker.send_request(
                "get_matchers", success_signal=self.matcher_signal)

    def _roster(self, data: ResponsePayload):
        page = PermissionConfigurator(data.data, bot_id=self.bot_id)
        parent = self.parent()
        show_method = None

        while parent is not None:
            method = getattr(parent, "show_subpage", None)

            if callable(method):
                show_method = method
                break

            parent = parent.parent()

        if show_method:
            show_method(page, f"{self.bot_id} 命令管理")

    def _toggle_status(self, status: Optional[bool] = None):
        if status is None:
            self._is_online = not self._is_online
        else:
            self._is_online = status

        if self._is_online:
            BotToolKit.timer.set_online(self.bot_id)
        else:
            BotToolKit.timer.set_offline(self.bot_id)
        # 切换主题颜色
        self.theme_color = self.original_theme_color if self._is_online else self.offline_color
        # 更新所有颜色相关的部件
        self._update_colors()

    def resizeEvent(self, event):
        self._add_top_decorator()
        super().resizeEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 绘制背景
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 12, 12)
        painter.fillPath(path, QBrush(
            QColor("white" if self._is_online else self.offline_color)))

        # 绘制边框
        border_path = QPainterPath()
        border_path.addRoundedRect(
            QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)
        painter.setPen(QPen(self.theme_color.lighter(150), 1))
        painter.drawPath(border_path)

    def _update_colors(self):
        """更新所有颜色相关的UI元素"""
        # 状态指示器
        self.status_indicator.setStyleSheet(f"""
            background: {'#4CAF50' if self._is_online else '#F44336'};
            border-radius: 6px;
            border: 2px solid white;
        """)

        # 顶部装饰条
        self.decorator.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.theme_color.name()}, 
                stop:1 {self.theme_color.lighter(50).name()});
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        """)

        # 头部
        self.header.setStyleSheet(f"""
            background: {"white" if self._is_online else self.theme_color.lighter(100).name()};
        """)

        # ID颜色
        self.id_label.setStyleSheet(f"""
            font: bold 16px '微软雅黑';
            color: {self.theme_color.darker().name()};
        """)

        # 适配器图标背景
        self.adapter_icon.setStyleSheet(f"""
            font: 16px;
            color: white;
            background: {self.theme_color.name()};
            border-radius: 12px;
            qproperty-alignment: AlignCenter;
        """)

        # 底部状态栏
        self.footer.setStyleSheet(f"""
            background: {self.theme_color.lighter(105).name()};
            border-radius: 6px;
            padding: 6px 12px;
            color: white; 
        """)

        self.update()


class BotCardManager(QObject):
    update_signal = Signal(str, float, float, float)

    def __init__(self):
        super().__init__()
        self.cards: Dict[str, BotCard] = {}
        self.update_signal.connect(self._handle_update)

    def _handle_update(self, bot_id: str, total: int, rate: float, uptime: str):
        if bot_id in self.cards:
            uptime = uptime or str(BotToolKit.timer.get_elapsed_time(bot_id))
            self.cards[bot_id].update_data(total, rate, int(uptime))

    def add_bot(self, bot_id: str, adapter: str):
        if bot_id not in self.cards:
            card = BotCard(bot_id, adapter)
            self.cards[bot_id] = card
        return self.cards[bot_id]

    def is_online(self, bot_id: str) -> bool:
        """检查指定的 bot 是否在线"""
        return self.cards[bot_id]._is_online if bot_id in self.cards else False

    def has_bot(self, bot_id: str) -> bool:
        """检查指定的 bot 是否存在"""
        return bot_id in self.cards


class BotInfoPage(PageBase):
    set_bot_signal = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.card_manager = BotCardManager()
        self._init_ui()
        self._init_data_refresh()
        self.set_bot_signal.connect(self.set_bot)
        talker.subscribe("bot_connect", "bot_disconnect",
                         signal=self.set_bot_signal)

    def _init_ui(self):
        self.setStyleSheet("""
            background: #F5F7FA;
            padding: 0;
            margin: 0;
        """)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 标题栏
        title_bar = QWidget()
        title_bar.setStyleSheet("""
            border-radius: 12px;
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 12, 20, 12)

        title = QLabel("Bot 管理")
        title.setStyleSheet("""
            color: #279BFA; 
            font: bold 18px;
        """)

        title_layout.addWidget(title)
        title_layout.addStretch()

        self.bot_count = QLabel("0 个实例")
        self.bot_count.setStyleSheet("""
            color: #279BFA;
            font: 14px;
        """)
        title_layout.addWidget(self.bot_count)

        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)

        # 卡片滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #E0E0E0;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Policy.Expanding,
                              QSizePolicy.Policy.Maximum)
        self.card_layout = QVBoxLayout()
        self.card_layout.setSpacing(15)
        self.card_layout.setContentsMargins(2, 2, 2, 2)
        self.card_layout.addStretch()
        content.setLayout(self.card_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def _init_data_refresh(self):
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self._refresh_all_data)

    def _refresh_all_data(self):
        on_line_count = 0
        off_line_count = 0
        for bot_id in self.card_manager.cards:
            if self.card_manager.is_online(bot_id):
                on_line_count += 1
                on_line_time = BotToolKit.timer.get_elapsed_time(bot_id)
                on_line_minute = round(on_line_time / 60)
                if on_line_minute <= 0:
                    on_line_minute = 1
                self.card_manager.update_signal.emit(
                    str(bot_id),
                    float(BotToolKit.counter.get_total_count(bot_id)),
                    float(BotToolKit.counter.get_period_count(
                        bot_id, 1800)/(on_line_minute if on_line_minute < 30 else 30)),
                    float(on_line_time)
                )
            else:
                off_line_count += 1
        self.bot_count.setText(f"{on_line_count} 在线实例 / {off_line_count} 离线实例")

    def add_bot(self, bot_id: str, adapter: str):
        if bot_id not in self.card_manager.cards:
            BotToolKit.add_bot(bot_id)
            card = self.card_manager.add_bot(bot_id, adapter)
            self.card_layout.addWidget(card)

    def set_bot_status(self, bot_id: str, status: bool):
        """设置指定 bot 的在线状态"""
        if bot_id in self.card_manager.cards:
            self.card_manager.cards[bot_id].status_changed.emit(status)

    def set_bot(self, type_: str, data: dict) -> None:
        if type_ == "bot_connect":
            if not self.card_manager.has_bot(data["bot"]):
                self.add_bot(data["bot"], data["adapter"])
            else:
                self.set_bot_status(data["bot"], True)
        elif type_ == "bot_disconnect":
            if self.card_manager.has_bot(data["bot"]):
                self.set_bot_status(data["bot"], False)

    def on_enter(self):
        """页面进入时启动定时刷新"""
        self.data_timer.start(1000)

    def on_leave(self):
        """页面离开时停止定时刷新"""
        self.data_timer.stop()
