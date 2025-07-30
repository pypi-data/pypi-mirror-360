from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel, QScrollArea,
    QTabWidget, QLineEdit, QHBoxLayout, QToolButton, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt
import json
from collections import defaultdict
import os

class CollapsibleSection(QWidget):
    def __init__(self, title, widgets):
        super().__init__()
        self.toggle_button = QToolButton(text=title)
        self.toggle_button.setStyleSheet("""
            QToolButton {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
                text-align: left;
            }
            QToolButton:checked {
                background-color: #34495e;
            }
        """)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-left: 2px solid #3498db;
                padding: 10px;
            }
        """)
        self.content_area.setVisible(False)

        content_layout = QVBoxLayout()
        for widget in widgets:
            content_layout.addWidget(widget)
        self.content_area.setLayout(content_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

        self.toggle_button.toggled.connect(self.toggle_content)

    def toggle_content(self, checked):
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.content_area.setVisible(checked)

    def setVisibleContent(self, visible):
        self.setVisible(visible)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinuxBoost - Quick Setup for Linux")
        self.setGeometry(300, 100, 600, 600)
        self.checkboxes_apps = []
        self.checkboxes_commands = []
        self.app_sections = []
        self.command_sections = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        apps_tab = self.create_apps_tab()
        commands_tab = self.create_commands_tab()

        tabs.addTab(apps_tab, "📦 Apps")
        tabs.addTab(commands_tab, "🛠️ Commands")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_apps_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Select Apps to Install")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)

        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.clicked.connect(lambda: self.toggle_all_sections(self.app_sections, True))
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.clicked.connect(lambda: self.toggle_all_sections(self.app_sections, False))

        btn_row = QHBoxLayout()
        btn_row.addWidget(expand_all_btn)
        btn_row.addWidget(collapse_all_btn)
        layout.addLayout(btn_row)

        self.search_bar_apps = QLineEdit()
        self.search_bar_apps.setPlaceholderText("Search apps...")
        self.search_bar_apps.textChanged.connect(self.filter_apps)
        layout.addWidget(self.search_bar_apps)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.apps_content = QWidget()
        self.apps_layout = QVBoxLayout()

        # For apps.json
        apps_path = os.path.join(os.path.dirname(__file__), "apps.json")
        print("Looking for apps.json at:", apps_path)

        with open(apps_path, "r") as f:
            self.apps_data = json.load(f)


        self.apps_by_category = defaultdict(list)

        for app in self.apps_data:
            checkbox = QCheckBox(app["name"])
            checkbox.setToolTip(app["description"])
            description = QLabel(app["description"])
            description.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-left: 10px;")
            self.checkboxes_apps.append((checkbox, app["command"], app["name"], app["description"], description))
            self.apps_by_category[app.get("category", "Other")].append((checkbox, description))

        for category, items in self.apps_by_category.items():
            widgets = []
            for checkbox, description in items:
                widgets.append(checkbox)
                widgets.append(description)
            section = CollapsibleSection(category, widgets)
            self.apps_layout.addWidget(section)
            self.app_sections.append((section, widgets))

        self.apps_content.setLayout(self.apps_layout)
        scroll.setWidget(self.apps_content)
        layout.addWidget(scroll)

        install_btn = QPushButton("Install Selected Apps")
        install_btn.setStyleSheet("padding: 10px; font-size: 16px;")
        install_btn.clicked.connect(self.install_selected_apps)
        layout.addWidget(install_btn)

        tab.setLayout(layout)
        return tab

    def create_commands_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Select Commands to Install")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)

        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.clicked.connect(lambda: self.toggle_all_sections(self.command_sections, True))
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.clicked.connect(lambda: self.toggle_all_sections(self.command_sections, False))

        btn_row = QHBoxLayout()
        btn_row.addWidget(expand_all_btn)
        btn_row.addWidget(collapse_all_btn)
        layout.addLayout(btn_row)

        self.search_bar_commands = QLineEdit()
        self.search_bar_commands.setPlaceholderText("Search commands...")
        self.search_bar_commands.textChanged.connect(self.filter_commands)
        layout.addWidget(self.search_bar_commands)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.commands_content = QWidget()
        self.commands_layout = QVBoxLayout()

        # For commands.json
        commands_path = os.path.join(os.path.dirname(__file__), "commands.json")
        with open(commands_path, "r") as f:
            self.commands_data = json.load(f)


        self.commands_by_category = defaultdict(list)

        for command in self.commands_data:
            checkbox = QCheckBox(command["name"])
            checkbox.setToolTip(command["description"])
            description = QLabel(command["description"])
            description.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-left: 10px;")
            self.checkboxes_commands.append((checkbox, command["command"], command["name"], command["description"], description))
            self.commands_by_category[command.get("category", "Other")].append((checkbox, description))

        for category, items in self.commands_by_category.items():
            widgets = []
            for checkbox, description in items:
                widgets.append(checkbox)
                widgets.append(description)
            section = CollapsibleSection(category, widgets)
            self.commands_layout.addWidget(section)
            self.command_sections.append((section, widgets))

        self.commands_content.setLayout(self.commands_layout)
        scroll.setWidget(self.commands_content)
        layout.addWidget(scroll)

        install_btn = QPushButton("Install Selected Commands")
        install_btn.setStyleSheet("padding: 10px; font-size: 16px;")
        install_btn.clicked.connect(self.install_selected_commands)
        layout.addWidget(install_btn)

        tab.setLayout(layout)
        return tab

    def toggle_all_sections(self, sections, expand):
        for section, _ in sections:
            section.toggle_button.setChecked(expand)

    def filter_apps(self):
        search_text = self.search_bar_apps.text().lower()
        for cb, _, name, desc, desc_label in self.checkboxes_apps:
            match = search_text in name.lower() or search_text in desc.lower()
            cb.setVisible(match)
            desc_label.setVisible(match)

        for section, widgets in self.app_sections:
            any_visible = any(w.isVisible() for w in widgets)
            section.setVisibleContent(any_visible)

    def filter_commands(self):
        search_text = self.search_bar_commands.text().lower()
        for cb, _, name, desc, desc_label in self.checkboxes_commands:
            match = search_text in name.lower() or search_text in desc.lower()
            cb.setVisible(match)
            desc_label.setVisible(match)

        for section, widgets in self.command_sections:
            any_visible = any(w.isVisible() for w in widgets)
            section.setVisibleContent(any_visible)

    def install_selected_apps(self):
        from .installer import install_commands
        commands = [cmd for cb, cmd, _, _, _ in self.checkboxes_apps if cb.isChecked()]
        install_commands(commands)

    def install_selected_commands(self):
        from .installer import install_commands
        commands = [cmd for cb, cmd, _, _, _ in self.checkboxes_commands if cb.isChecked()]
        install_commands(commands)
