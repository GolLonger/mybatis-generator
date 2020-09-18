# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'templates.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from src.constant.constant import TEMPLATE_TABLE_HEADER_LABELS
from src.dialog.draggable_dialog import DraggableDialog
from src.scrollable_widget.scrollable_widget import MyTableWidget
from src.table.table_header import CheckBoxHeader
from src.table.table_item import MyTableWidgetItem


class TemplatesDialog(DraggableDialog):

    def __init__(self, templates, screen_rect):
        super().__init__()
        self.templates = templates
        self.main_screen_rect = screen_rect
        self.selected_templates = list()
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("Dialog")
        self.resize(self.main_screen_rect.width() * 0.6, self.main_screen_rect.height() * 0.6)
        # 不透明度
        self.setWindowOpacity(0.95)
        # 隐藏窗口边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 设置窗口背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.table_frame = QtWidgets.QFrame(self)
        self.table_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.table_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.table_frame.setObjectName("template_table_frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.table_frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.table_header_label = QtWidgets.QLabel(self.table_frame)
        self.table_header_label.setObjectName("template_table_header_label")
        self.verticalLayout.addWidget(self.table_header_label)
        # 添加表格
        self.tableWidget = MyTableWidget(self.table_frame)
        self.tableWidget.setObjectName("tableWidget")
        # 表头
        self.make_header()
        # 填充表格数据
        self.fill_table()
        # 交替行颜色
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setAttribute(Qt.WA_TranslucentBackground, True)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.verticalLayout.addWidget(self.tableWidget)
        # 按钮区域 添加模板 批量复制 批量删除 退出
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.add_template = QtWidgets.QPushButton(self.table_frame)
        self.add_template.setObjectName("add_template")
        self.gridLayout.addWidget(self.add_template, 0, 0, 1, 1)
        self.batch_copy = QtWidgets.QPushButton(self.table_frame)
        self.batch_copy.setObjectName("batch_copy")
        self.gridLayout.addWidget(self.batch_copy, 0, 1, 1, 1)
        self.button_blank = QtWidgets.QLabel(self.table_frame)
        self.gridLayout.addWidget(self.button_blank, 0, 2, 1, 1)
        self.batch_delete = QtWidgets.QPushButton(self.table_frame)
        self.batch_delete.setObjectName("batch_delete")
        self.gridLayout.addWidget(self.batch_delete, 0, 3, 1, 1)
        self.quit_button = QtWidgets.QPushButton(self.table_frame)
        self.quit_button.setObjectName("quit_button")
        self.gridLayout.addWidget(self.quit_button, 0, 4, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.main_layout.addWidget(self.table_frame)

        # 事件
        self.quit_button.clicked.connect(self.close)

        self.tableWidget.item_checkbox_clicked.connect(self.on_checkbox_changed)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.table_header_label.setText("代码模板列表")
        self.add_template.setText("添加模板")
        self.batch_copy.setText("批量复制")
        self.batch_delete.setText("批量删除")
        self.quit_button.setText("退出")

    def make_header(self):
        self.tableWidget.setColumnCount(8)
        # 实例化自定义表头
        self.table_header = CheckBoxHeader()
        self.table_header.setObjectName("table_header")
        self.tableWidget.setHorizontalHeader(self.table_header)
        self.tableWidget.setHorizontalHeaderLabels(TEMPLATE_TABLE_HEADER_LABELS)
        # 设置表头列宽度
        self.tableWidget.horizontalHeader().resizeSection(0, 60)
        self.tableWidget.horizontalHeader().resizeSection(2, 60)
        self.tableWidget.horizontalHeader().resizeSection(3, 60)
        self.tableWidget.horizontalHeader().resizeSection(4, 60)
        # 最后为模板说明，拉伸到最大
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        # 隐藏默认的行号
        self.tableWidget.verticalHeader().setHidden(True)
        self.table_header.select_all_clicked.connect(self.all_clicked)

    def fill_table(self):
        for i, template in enumerate(self.templates):
            self.tableWidget.insertRow(i)
            table_check_item = MyTableWidgetItem(self.tableWidget)
            table_check_item.setCheckState(Qt.Unchecked)
            table_check_item.setText(str(i + 1))
            self.tableWidget.setItem(i, 0, table_check_item)
            self.table_header.all_header_combobox.append(table_check_item)
            n = 1
            for field in template:
                # 模板中的每一个字段
                if field is not None:
                    tp_item = MyTableWidgetItem(self.tableWidget)
                    tp_item.setText(field)
                    self.tableWidget.setItem(i, n, tp_item)
                    n += 1
        self.tableWidget.resizeRowsToContents()

    def all_clicked(self, clicked):
        self.table_header.change_state(clicked)

    def on_checkbox_changed(self, checked, tp_name):
        header_checked = False
        if checked and tp_name not in self.selected_templates:
            self.selected_templates.append(tp_name)
            # 与表头联动
            if len(self.selected_templates) == len(self.table_header.all_header_combobox):
                header_checked = True
        elif not checked and tp_name in self.selected_templates:
            self.selected_templates.remove(tp_name)
        self.table_header.set_header_checked(header_checked)