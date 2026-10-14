import sys
import os
import time
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGraphicsDropShadowEffect,
    QCalendarWidget, QDialog, QMessageBox, QMenu, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QDate, QEvent
from PyQt6.QtGui import QColor, QFont, QCursor, QIcon, QAction, QPixmap, QPainter

import database
import styles

def create_tray_icon_pixmap(is_active=False):
    """Draws a monochrome Swiss tray icon."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Outer black ring with crisp white border
    painter.setBrush(QColor("#000000"))
    painter.setPen(QColor("#FFFFFF"))
    painter.drawEllipse(4, 4, 24, 24)
    
    # Inner dot (solid white if active, subtle dot if idle)
    if is_active:
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(11, 11, 10, 10)
    else:
        painter.setBrush(QColor("#888888"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(13, 13, 6, 6)
    painter.end()
    return pixmap

class CalendarDialog(QDialog):
    """Simple date picker dialog styled in Swiss Monochrome."""
    def __init__(self, current_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0E0E0E;
                border: 1.5px solid #FFFFFF;
                border-radius: 8px;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #0A0A0A;
                background-color: #0E0E0E;
                color: #FFFFFF;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #FFFFFF;
                background-color: #0E0E0E;
                selection-background-color: #FFFFFF;
                selection-color: #000000;
            }
        """)
        layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget()
        qdate = QDate(current_date.year, current_date.month, current_date.day)
        self.calendar.setSelectedDate(qdate)
        self.calendar.clicked.connect(self.accept)
        layout.addWidget(self.calendar)
        
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Cancel")
        close_btn.setObjectName("dateNavBtn")
        close_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def get_selected_date(self):
        qdate = self.calendar.selectedDate()
        return date(qdate.year(), qdate.month(), qdate.day())

class SmallPillWidget(QWidget):
    """
    Compact floating pill widget anchored at the bottom-center of the screen.
    Displays live elapsed time or today's productivity summary.
    Clicking it toggles/opens the full dashboard widget.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.old_pos = None
        self.drag_start_pos = None
        self.is_dragging = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(styles.DARK_THEME)

        self.init_ui()
        self.position_bottom_center()

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def init_ui(self):
        self.setObjectName("pillRoot")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setObjectName("pillFrame")
        self.frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.frame.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self.frame)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        # White/Green Status Dot
        self.dot_lbl = QLabel("●")
        self.dot_lbl.setObjectName("pillDot")
        self.dot_lbl.setStyleSheet("color: #FFFFFF; font-size: 11px;")

        # Time / Status Text
        self.time_lbl = QLabel("Today: 0.00h")
        self.time_lbl.setObjectName("pillText")

        # Circular Action Button
        self.quick_btn = QPushButton("▶")
        self.quick_btn.setObjectName("pillPlayBtn")
        self.quick_btn.setFixedSize(24, 24)
        self.quick_btn.setToolTip("Start / Stop Session")
        self.quick_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.quick_btn.clicked.connect(self.controller.toggle_session)

        # Expand icon
        self.expand_btn = QPushButton("⛶")
        self.expand_btn.setObjectName("pillExpandBtn")
        self.expand_btn.setToolTip("Open Full Dashboard")
        self.expand_btn.clicked.connect(self.controller.toggle_dashboard)

        layout.addWidget(self.dot_lbl)
        layout.addWidget(self.time_lbl)
        layout.addWidget(self.quick_btn)
        layout.addWidget(self.expand_btn)

        outer_layout.addWidget(self.frame)

    def position_bottom_center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        pill_w = 230
        pill_h = 48
        x = screen.x() + (screen.width() - pill_w) // 2
        y = screen.y() + screen.height() - pill_h - 75
        self.setGeometry(x, y, pill_w, pill_h)

    def update_state(self, is_active, elapsed_str="", today_total_str=""):
        if is_active:
            self.dot_lbl.setStyleSheet("color: #10B981; font-size: 11px;")
            self.time_lbl.setText(elapsed_str)
            self.time_lbl.setStyleSheet("color: #10B981; font-weight: 800; font-family: 'Consolas', monospace;")
            self.quick_btn.setText("■")
            self.quick_btn.setStyleSheet("background-color: #FFFFFF; color: #000000; border: none; border-radius: 12px; font-weight: 900;")
            self.quick_btn.setToolTip("Stop Session")
        else:
            self.dot_lbl.setStyleSheet("color: #FFFFFF; font-size: 11px;")
            disp = f"Today: {today_total_str}" if today_total_str else "Today: 0.00h"
            self.time_lbl.setText(disp)
            self.time_lbl.setStyleSheet("color: #F8FAFC; font-weight: 700; font-family: 'Consolas', 'Segoe UI', monospace;")
            self.quick_btn.setText("▶")
            self.quick_btn.setStyleSheet("background-color: #FFFFFF; color: #000000; border: none; border-radius: 12px; font-weight: 900;")
            self.quick_btn.setToolTip("Start Session")

    # Click anywhere on pill (except buttons) to toggle dashboard
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.drag_start_pos = event.globalPosition().toPoint()
            self.is_dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            current_pos = event.globalPosition().toPoint()
            if not self.is_dragging and self.drag_start_pos is not None:
                # If moved more than 5 pixels, it's a drag, not a click
                if (current_pos - self.drag_start_pos).manhattanLength() > 5:
                    self.is_dragging = True
            
            if self.is_dragging:
                delta = current_pos - self.old_pos
                self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = current_pos

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_dragging:
                # Avoid re-opening if dashboard just closed due to losing focus onto pill
                if time.time() - getattr(self.controller, "last_dashboard_close_time", 0) > 0.25:
                    self.controller.toggle_dashboard()
            self.is_dragging = False
            self.drag_start_pos = None
            self.old_pos = None

    def show_context_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0E0E0E;
                color: #FFFFFF;
                border: 1.5px solid #333333;
                border-radius: 6px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #FFFFFF;
                color: #000000;
                font-weight: bold;
            }
        """)
        action_toggle = menu.addAction("Open Dashboard" if not self.controller.dashboard.isVisible() else "Hide Dashboard")
        action_toggle.triggered.connect(self.controller.toggle_dashboard)

        action_start_stop = menu.addAction("Stop Session" if self.controller.active_session_id else "Start Session")
        action_start_stop.triggered.connect(self.controller.toggle_session)

        menu.addSeparator()
        action_reset_pos = menu.addAction("Reset to Bottom Center")
        action_reset_pos.triggered.connect(self.position_bottom_center)

        menu.addSeparator()
        action_exit = menu.addAction("Exit Prodigit")
        action_exit.triggered.connect(self.controller.quit_app)

        menu.exec(global_pos)

class ProductivityWidget(QWidget):
    """Full dashboard widget with detailed timeline, stats, and calendar filtering."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.selected_date = date.today()
        self.current_filter_mode = "today"
        self.is_pinned = False  # Default to unpinned so clicking outside closes it
        self.modal_open = False
        self.old_pos = None

        self.base_completed_seconds = 0
        self.view_includes_today = True
        self.active_card_dur_lbl = None
        self.active_card_widget = None

        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(330)
        self.setMaximumWidth(360)
        self.setMinimumHeight(480)
        self.resize(340, 520)

        self.setStyleSheet(styles.DARK_THEME)
        self.init_ui()
        self.position_above_pill()

    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(6, 6, 6, 6)

        self.container = QFrame()
        self.container.setObjectName("mainFrame")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        # 1. Header Bar
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        
        title_box = QHBoxLayout()
        title_box.setSpacing(8)
        
        app_title = QLabel("⏱ PRODIGIT")
        app_title.setObjectName("appTitle")
        
        self.status_badge = QLabel("IDLE")
        self.status_badge.setObjectName("statusBadgeIdle")
        
        title_box.addWidget(app_title)
        title_box.addWidget(self.status_badge)

        self.cal_btn = QPushButton("📅")
        self.cal_btn.setObjectName("headerIconBtn")
        self.cal_btn.setToolTip("Pick Date from Calendar")
        self.cal_btn.clicked.connect(self.open_calendar_picker)

        self.pin_btn = QPushButton("📌")
        self.pin_btn.setObjectName("headerIconBtn")
        self.pin_btn.setToolTip("Click to Pin (Keeps window open when clicking outside)")
        self.pin_btn.clicked.connect(self.toggle_pin)

        collapse_btn = QPushButton("⌄")
        collapse_btn.setObjectName("headerIconBtn")
        collapse_btn.setToolTip("Collapse to Bottom Widget")
        collapse_btn.clicked.connect(self.hide)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("headerCloseBtn")
        close_btn.setToolTip("Close to Bottom Widget")
        close_btn.clicked.connect(self.hide)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(self.cal_btn)
        header.addWidget(self.pin_btn)
        header.addWidget(collapse_btn)
        header.addWidget(close_btn)
        layout.addLayout(header)

        # 2. Timer Control Card
        timer_card = QFrame()
        timer_card.setObjectName("timerCard")
        timer_card_layout = QVBoxLayout(timer_card)
        timer_card_layout.setContentsMargins(14, 12, 14, 14)
        timer_card_layout.setSpacing(4)

        timer_top = QLabel("Active Focus Session")
        timer_top.setObjectName("timerTopLabel")
        timer_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card_layout.addWidget(timer_top)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card_layout.addWidget(self.timer_label)

        self.start_time_label = QLabel("Ready to track focus")
        self.start_time_label.setObjectName("timerSubtext")
        self.start_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card_layout.addWidget(self.start_time_label)

        timer_card_layout.addSpacing(6)

        self.toggle_btn = QPushButton("▶  START PRODUCTIVITY")
        self.toggle_btn.setObjectName("startBtn")
        self.toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_btn.clicked.connect(self.controller.toggle_session)
        timer_card_layout.addWidget(self.toggle_btn)

        layout.addWidget(timer_card)

        # 3. Quick Stats Card
        stats_card = QFrame()
        stats_card.setObjectName("summaryCard")
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(14, 10, 14, 10)

        total_col = QVBoxLayout()
        total_col.setSpacing(2)
        today_sub = QLabel("TODAY'S FOCUS")
        today_sub.setObjectName("summaryLabel")
        self.today_total_label = QLabel("0.00h")
        self.today_total_label.setObjectName("summaryNumberBlue")
        total_col.addWidget(today_sub)
        total_col.addWidget(self.today_total_label)

        sessions_col = QVBoxLayout()
        sessions_col.setSpacing(2)
        sessions_col.setAlignment(Qt.AlignmentFlag.AlignRight)
        sessions_sub = QLabel("COMPLETED")
        sessions_sub.setObjectName("summaryLabel")
        sessions_sub.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.today_sessions_label = QLabel("0 Sessions")
        self.today_sessions_label.setObjectName("summaryNumberWhite")
        self.today_sessions_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        sessions_col.addWidget(sessions_sub)
        sessions_col.addWidget(self.today_sessions_label)

        stats_layout.addLayout(total_col)
        stats_layout.addStretch()
        stats_layout.addLayout(sessions_col)
        layout.addWidget(stats_card)

        # 4. Period Filter Tabs in pill container
        filter_box = QFrame()
        filter_box.setObjectName("filterBarContainer")
        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(3, 3, 3, 3)
        filter_layout.setSpacing(2)
        
        self.tab_today = QPushButton("Today")
        self.tab_7d = QPushButton("7 Days")
        self.tab_30d = QPushButton("30 Days")
        self.tab_90d = QPushButton("3 Months")

        self.filter_buttons = {
            "today": self.tab_today,
            "7days": self.tab_7d,
            "30days": self.tab_30d,
            "90days": self.tab_90d
        }

        for mode, btn in self.filter_buttons.items():
            btn.setObjectName("filterTab")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, m=mode: self.set_filter_mode(m))
            filter_layout.addWidget(btn)

        layout.addWidget(filter_box)

        # 5. Day Navigator (hidden to match Swiss Mono minimalist layout)
        self.nav_widget = QWidget()
        self.nav_widget.hide()
        nav_layout = QHBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        self.prev_day_btn = QPushButton("◀")
        self.prev_day_btn.setObjectName("dateNavBtn")
        self.prev_day_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.prev_day_btn.clicked.connect(self.prev_day)

        self.date_display_btn = QPushButton("Today")
        self.date_display_btn.setObjectName("dateNavBtn")
        self.date_display_btn.setStyleSheet("font-weight: 800; color: #FFFFFF; background-color: #161616; border: 1px solid #333333; border-radius: 4px; padding: 5px 12px;")
        self.date_display_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.date_display_btn.setToolTip("Click to pick date from calendar")
        self.date_display_btn.clicked.connect(self.open_calendar_picker)

        self.next_day_btn = QPushButton("▶")
        self.next_day_btn.setObjectName("dateNavBtn")
        self.next_day_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_day_btn.clicked.connect(self.next_day)

        nav_layout.addWidget(self.prev_day_btn)
        nav_layout.addWidget(self.date_display_btn, 1)
        nav_layout.addWidget(self.next_day_btn)
        layout.addWidget(self.nav_widget)

        # 6. Session List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_content = QWidget()
        self.session_list_layout = QVBoxLayout(self.scroll_content)
        self.session_list_layout.setContentsMargins(0, 0, 4, 0)
        self.session_list_layout.setSpacing(6)
        self.session_list_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, 1)

        outer_layout.addWidget(self.container)
        self.update_filter_button_styles()

        # Install wheel event filter so scrolling anywhere on the widget scrolls the session list
        self.installEventFilter(self)
        self.container.installEventFilter(self)
        self.scroll_area.installEventFilter(self)
        self.scroll_area.viewport().installEventFilter(self)
        self.scroll_content.installEventFilter(self)

    def position_above_pill(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w = 340
        h = 520
        x = screen.x() + (screen.width() - w) // 2
        y = screen.y() + screen.height() - h - 68
        if y < screen.y() + 10:
            y = screen.y() + 10
        self.setGeometry(x, y, w, h)

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        flags = self.windowFlags()
        if self.is_pinned:
            flags |= Qt.WindowType.WindowStaysOnTopHint
            self.pin_btn.setText("📌")
            self.pin_btn.setToolTip("Pinned (Always on top & stays open)")
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            self.pin_btn.setText("📍")
            self.pin_btn.setToolTip("Unpinned (Closes when clicking outside)")
        self.setWindowFlags(flags)
        self.show()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                # Close widget when clicking outside, unless pinned or opening calendar
                if not getattr(self, "modal_open", False) and not self.is_pinned:
                    self.controller.last_dashboard_close_time = time.time()
                    self.hide()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            delta = event.angleDelta().y()
            step = int((delta / 120.0) * 50)
            vbar = self.scroll_area.verticalScrollBar()
            vbar.setValue(vbar.value() - step)
            return True
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = int((delta / 120.0) * 50)
        vbar = self.scroll_area.verticalScrollBar()
        vbar.setValue(vbar.value() - step)
        event.accept()

    def set_filter_mode(self, mode):
        self.current_filter_mode = mode
        self.update_filter_button_styles()
        self.refresh_history()

    def update_filter_button_styles(self):
        for mode, btn in self.filter_buttons.items():
            if mode == self.current_filter_mode:
                btn.setObjectName("filterTabSelected")
            else:
                btn.setObjectName("filterTab")
            btn.setStyle(self.style())

    def prev_day(self):
        self.selected_date -= timedelta(days=1)
        self.refresh_history()

    def next_day(self):
        self.selected_date += timedelta(days=1)
        self.refresh_history()

    def open_calendar_picker(self):
        self.modal_open = True
        try:
            dlg = CalendarDialog(self.selected_date, self)
            if dlg.exec():
                self.selected_date = dlg.get_selected_date()
                self.refresh_history()
        finally:
            self.modal_open = False

    def refresh_history(self):
        self.active_card_dur_lbl = None
        self.active_card_widget = None

        while self.session_list_layout.count() > 1:
            child = self.session_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        today = date.today()
        if self.current_filter_mode == "today":
            date_str = self.selected_date.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date(date_str)
            self.view_includes_today = (self.selected_date == today)
            if self.selected_date == today:
                self.date_display_btn.setText(f"Today ({self.selected_date.strftime('%b %d')})")
            elif self.selected_date == today - timedelta(days=1):
                self.date_display_btn.setText(f"Yesterday ({self.selected_date.strftime('%b %d')})")
            else:
                self.date_display_btn.setText(self.selected_date.strftime("%a, %b %d, %Y"))
        
        elif self.current_filter_mode == "7days":
            start_str = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date_range(start_str, end_str)
            self.view_includes_today = True

        elif self.current_filter_mode == "30days":
            start_str = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date_range(start_str, end_str)
            self.view_includes_today = True

        elif self.current_filter_mode == "90days":
            start_str = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            data = database.get_sessions_by_date_range(start_str, end_str)
            self.view_includes_today = True

        self.base_completed_seconds = data["total_seconds"]

        # Check if active session should be counted in this view
        is_active = (self.controller.active_session_id is not None and self.controller.session_start_dt is not None)
        active_elapsed = 0
        if is_active and self.view_includes_today:
            active_elapsed = max(0, int((datetime.now() - self.controller.session_start_dt).total_seconds()))

        total_sec = self.base_completed_seconds + active_elapsed
        total_hours = round(total_sec / 3600.0, 2)
        self.today_total_label.setText(f"{total_hours:.2f}h")
        
        session_count = data["count"]
        self.today_sessions_label.setText(f"{session_count} {'Session' if session_count == 1 else 'Sessions'}")

        sessions = data["sessions"]
        insert_idx = 0

        # Insert active session card at top if running and in current view
        if is_active and self.view_includes_today:
            active_card = self.create_active_session_card(self.controller.session_start_dt, active_elapsed)
            self.active_card_widget = active_card
            self.session_list_layout.insertWidget(insert_idx, active_card)
            insert_idx += 1

        if not sessions and not (is_active and self.view_includes_today):
            empty_lbl = QLabel("No productivity sessions logged for this period.\nClick START to track your focus!")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #64748B; font-size: 12px; padding: 24px;")
            self.session_list_layout.insertWidget(0, empty_lbl)
            return

        for s in sessions:
            card = self.create_session_card(s)
            self.session_list_layout.insertWidget(insert_idx, card)
            insert_idx += 1

    def create_active_session_card(self, start_dt, elapsed_sec):
        card = QFrame()
        card.setObjectName("sessionItem")
        card.setStyleSheet("""
            #sessionItem {
                background-color: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-radius: 8px;
            }
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        start_disp = start_dt.strftime("%I:%M %p")
        time_lbl = QLabel(f"●  {start_disp} ➔ Ongoing")
        time_lbl.setStyleSheet("color: #34D399; font-weight: 700; font-size: 12px;")

        sub_lbl = QLabel("Active Right Now")
        sub_lbl.setStyleSheet("color: #6EE7B7; font-size: 10px;")

        info_col.addWidget(time_lbl)
        info_col.addWidget(sub_lbl)
        card_layout.addLayout(info_col, 1)

        hrs = elapsed_sec // 3600
        mins = (elapsed_sec % 3600) // 60
        secs = elapsed_sec % 60
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        self.active_card_dur_lbl = QLabel(time_str)
        self.active_card_dur_lbl.setObjectName("sessionDurationGreen")
        self.active_card_dur_lbl.setStyleSheet("color: #34D399; font-weight: 800; font-size: 13px; font-family: 'Consolas', monospace;")
        card_layout.addWidget(self.active_card_dur_lbl)

        card.installEventFilter(self)
        return card

    def create_session_card(self, session_data):
        card = QFrame()
        card.setObjectName("sessionItem")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        start_t = session_data.get("start_time_display") or ""
        end_t = session_data.get("end_time_display") or "Ongoing"
        time_lbl = QLabel(f"{start_t} ➔ {end_t}")
        time_lbl.setObjectName("sessionTime")
        time_lbl.setStyleSheet("color: #F8FAFC; font-weight: 600; font-size: 12px;")

        sub_lbl = QLabel("Focus Session · Completed")
        sub_lbl.setObjectName("sessionSubtext")
        sub_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")

        info_col.addWidget(time_lbl)
        info_col.addWidget(sub_lbl)
        card_layout.addLayout(info_col, 1)

        dur_sec = session_data.get("duration_seconds", 0)
        dur_lbl = QLabel(database.format_duration(dur_sec))
        dur_lbl.setObjectName("sessionDurationGreen")
        dur_lbl.setStyleSheet("color: #34D399; font-weight: 700; font-size: 12px; font-family: 'Consolas', monospace;")
        card_layout.addWidget(dur_lbl)

        del_btn = QPushButton("🗑")
        del_btn.setObjectName("deleteItemBtn")
        del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        del_btn.setToolTip("Delete this session record")
        session_id = session_data["id"]
        del_btn.clicked.connect(lambda checked, s_id=session_id: self.delete_session(s_id))
        card_layout.addWidget(del_btn)

        card.installEventFilter(self)
        return card

    def delete_session(self, session_id):
        database.delete_session(session_id)
        self.controller.refresh_all()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class AppController:
    """Coordinates state between the bottom pill widget, dashboard, system tray, and timer."""
    def __init__(self):
        self.active_session_id = None
        self.session_start_dt = None
        self.last_dashboard_close_time = 0

        self.pill = SmallPillWidget(self)
        self.dashboard = ProductivityWidget(self)

        self.setup_timer()
        self.setup_tray()
        self.check_resumed_session()
        self.refresh_all()

        # Start with the small bottom pill visible on desktop
        self.pill.show()
        self.pill.raise_()
        self.pill.activateWindow()

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.update_tray_icon()
        
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #0E0E0E;
                color: #FFFFFF;
                border: 1.5px solid #333333;
                padding: 6px;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #FFFFFF;
                color: #000000;
                font-weight: bold;
            }
        """)

        toggle_pill_action = QAction("Show / Hide Bottom Widget", tray_menu)
        toggle_pill_action.triggered.connect(self.toggle_pill)
        tray_menu.addAction(toggle_pill_action)

        open_dash_action = QAction("Open Full Dashboard", tray_menu)
        open_dash_action.triggered.connect(self.open_dashboard)
        tray_menu.addAction(open_dash_action)

        self.tray_start_stop_action = QAction("Start Session", tray_menu)
        self.tray_start_stop_action.triggered.connect(self.toggle_session)
        tray_menu.addAction(self.tray_start_stop_action)

        tray_menu.addSeparator()
        exit_action = QAction("Exit Prodigit", tray_menu)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def update_tray_icon(self):
        is_active = self.active_session_id is not None
        pixmap = create_tray_icon_pixmap(is_active)
        self.tray.setIcon(QIcon(pixmap))

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_dashboard()

    def toggle_pill(self):
        if self.pill.isVisible():
            self.pill.hide()
        else:
            self.pill.show()
            self.pill.raise_()

    def open_dashboard(self):
        self.dashboard.refresh_history()
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def toggle_dashboard(self):
        if self.dashboard.isVisible():
            self.dashboard.hide()
        else:
            self.open_dashboard()

    def check_resumed_session(self):
        active = database.get_active_session()
        if active:
            self.active_session_id = active["id"]
            self.session_start_dt = datetime.fromisoformat(active["start_timestamp"])
            self.dashboard.status_badge.setText("● PRODUCTIVE")
            self.dashboard.status_badge.setObjectName("statusBadgeActive")
            self.dashboard.status_badge.setStyle(self.dashboard.style())
            self.dashboard.start_time_label.setText(f"Since {active['start_time_display']} · Real-time sync")
            self.dashboard.toggle_btn.setText("■  STOP SESSION")
            self.dashboard.toggle_btn.setObjectName("stopBtn")
            self.dashboard.toggle_btn.setStyle(self.dashboard.style())
            self.tray_start_stop_action.setText("Stop Session")
            self.timer.start()
            self.tick()

    def toggle_session(self):
        if self.active_session_id is None:
            # START
            session_id, now_dt = database.start_session()
            self.active_session_id = session_id
            self.session_start_dt = now_dt
            
            self.dashboard.status_badge.setText("● PRODUCTIVE")
            self.dashboard.status_badge.setObjectName("statusBadgeActive")
            self.dashboard.status_badge.setStyle(self.dashboard.style())
            self.dashboard.start_time_label.setText(f"Since {now_dt.strftime('%I:%M:%S %p')} · Real-time sync")
            self.dashboard.toggle_btn.setText("■  STOP SESSION")
            self.dashboard.toggle_btn.setObjectName("stopBtn")
            self.dashboard.toggle_btn.setStyle(self.dashboard.style())
            
            self.tray_start_stop_action.setText("Stop Session")
            self.refresh_all()
            self.timer.start()
            self.tick()
        else:
            # STOP
            result = database.stop_session(self.active_session_id)
            self.timer.stop()
            self.active_session_id = None
            self.session_start_dt = None
            
            self.dashboard.status_badge.setText("IDLE")
            self.dashboard.status_badge.setObjectName("statusBadgeIdle")
            self.dashboard.status_badge.setStyle(self.dashboard.style())
            
            self.dashboard.start_time_label.setText("Ready to track focus")
            self.dashboard.timer_label.setText("00:00:00")
            self.dashboard.toggle_btn.setText("▶  START PRODUCTIVITY")
            self.dashboard.toggle_btn.setObjectName("startBtn")
            self.dashboard.toggle_btn.setStyle(self.dashboard.style())
            
            self.tray_start_stop_action.setText("Start Session")
            self.refresh_all()

        self.update_tray_icon()

    def tick(self):
        if not self.session_start_dt:
            return
        elapsed = max(0, int((datetime.now() - self.session_start_dt).total_seconds()))
        hrs = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        
        self.dashboard.timer_label.setText(time_str)
        self.pill.update_state(True, elapsed_str=time_str)

        # Real-time updates across dashboard sections while session is running:
        if self.dashboard.view_includes_today:
            curr_total = self.dashboard.base_completed_seconds + elapsed
            curr_hrs = round(curr_total / 3600.0, 2)
            self.dashboard.today_total_label.setText(f"{curr_hrs:.2f}h")

            if self.dashboard.active_card_dur_lbl:
                self.dashboard.active_card_dur_lbl.setText(time_str)

    def refresh_all(self):
        today_str = date.today().strftime("%Y-%m-%d")
        today_data = database.get_sessions_by_date(today_str)
        today_dur = database.format_duration(today_data["total_seconds"])
        
        if self.active_session_id is None:
            self.pill.update_state(False, today_total_str=today_dur)
        
        self.dashboard.refresh_history()
        self.update_tray_icon()

    def quit_app(self):
        QApplication.quit()

if __name__ == "__main__":
    import ctypes
    try:
        myappid = 'prodigit.productivity.widget.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in pill / tray

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prodigit.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    controller = AppController()
    sys.exit(app.exec())
