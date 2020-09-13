# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout

from src.constant.constant import TREE_HEADER_LABELS, WRONG_TITLE, WRONG_UNSELECT_DATA, UNSELECT_FIELD_MENU, \
    SELECT_ALL_FIELD_MENU
from src.dialog.generate_dialog.generate_dialog import DisplaySelectedDialog
from src.func.connection_function import close_connection
from src.func.refresh_thread import Refresh
from src.func.select_table_thread import AsyncSelectTable
from src.func.selected_data import SelectedData
from src.func.table_func import get_node
from src.func.tree_function import make_tree_item
from src.func.tree_strategy import tree_node_factory, Context, TreeNodeTable
from src.little_widget.about_ui import AboutUI
from src.little_widget.help_ui import HelpUI
from src.little_widget.menu_bar_func import fill_menu_bar
from src.little_widget.message_box import pop_fail
from src.little_widget.title_bar import TitleBar
from src.little_widget.tool_bar import fill_tool_bar
from src.scrollable_widget.scrollable_widget import MyTreeWidget
from src.sys.sys_info_storage.sqlite import get_conns


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, screen_rect):
        super().__init__()
        # 已经连接数据库的连接，key为连接名，value为DBExecutor对象
        self.connected_dict = dict()
        self._translate = QtCore.QCoreApplication.translate
        # 页面展示的连接（从系统库中获取的连接信息），key为id，value为connection对象，
        # 因为在编辑连接后，连接名称可能会变化，无法作为唯一标识
        self.display_conn_dict = dict()
        # 保存在页面已经打开的项，字典键为连接名，值为字典，字典包含两个键，一个为expanded记录展开状态，
        # 一个为opened_db 记录打开的库信息。opened_db对应的值为字典，该字典包含多个打开的库名键，
        # 值为字典，包含两个键值对，一个为expanded记录节点展开状态，一个为table，表名，table对应值为字典，
        # 字典包含多个表名键，值为是否选中
        # {
        #      conn:{
        #          'opened_db':{
        #              db:{
        #                  'table':{tb: Qt.Checked},
        #                  'expanded': True,
        #              }
        #          },
        #          'expanded': True
        #      }
        # }
        self.open_item_dict = dict()
        # opened_table: (conn_name, db_name, tb_name)
        self.opened_table = tuple()
        # 当前屏幕的分辨率大小
        self.desktop_screen_rect = screen_rect
        self.refresh_finished = True

        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 按当前分辨率计算窗口大小
        self.resize(self.desktop_screen_rect.width() * 0.6, self.desktop_screen_rect.height() * 0.75)
        # 当前窗口的分辨率大小，其他窗口以此为参考
        self.screen_rect = self.geometry()
        # 创建主控件，用以包含所有内容
        self.main_widget = QtWidgets.QWidget()
        # 主控件中的布局
        self.main_layout = QVBoxLayout()
        # 设置所有间距为0
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tree_frame = QtWidgets.QFrame(self.centralwidget)
        self.tree_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tree_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tree_frame.setObjectName("tree_frame")
        self.tree_verticalLayout = QtWidgets.QVBoxLayout(self.tree_frame)
        self.tree_verticalLayout.setObjectName("verticalLayout")
        self.tree_header_label = QtWidgets.QLabel(self.tree_frame)
        self.tree_header_label.setObjectName("tree_header_label")
        self.tree_verticalLayout.addWidget(self.tree_header_label)
        self.treeWidget = MyTreeWidget(self.tree_frame)

        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setHidden(True)
        # 统一设置图标大小
        self.treeWidget.setIconSize(QSize(40, 30))
        self.tree_verticalLayout.addWidget(self.treeWidget)
        self.horizontalLayout.addWidget(self.tree_frame)

        # 菜单栏
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        fill_menu_bar(self)

        # 创建标题栏
        self.title_bar = TitleBar(30, self, self.menubar)
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedWidth(self.width())

        # 工具栏
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        # 设置名称显示在图标下面（默认本来是只显示图标）
        fill_tool_bar(self)
        self.toolBar.setIconSize(QSize(50, 40))
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # 主布局添加所有部件，依次为标题栏、菜单栏、工具栏、承载了实际窗口内容的主控件，将窗口中央控件设置为包含所有的控件
        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.toolBar)
        self.main_layout.addWidget(self.centralwidget)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        # 任务栏图标
        self.setWindowIcon(QIcon(":/icon/exec.png"))

        # 初始化树：初始化获取树结构的第一层元素，为数据库连接列表
        self.get_saved_conns()

        # 双击树节点事件
        self.treeWidget.doubleClicked.connect(self.get_tree_list)
        # 树结构中，第三层表格的复选框点击事件
        self.treeWidget.item_checkbox_clicked.connect(self.table_check_box)
        # 右击事件
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.right_click_menu)
        # 树控件背景透明
        self.treeWidget.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        # 不透明度
        self.setWindowOpacity(0.95)

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self._translate("MainWindow", "MainWindow"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.set_tree_header_label()

    def set_tree_header_label(self):
        self.tree_header_label.setText(TREE_HEADER_LABELS)

    def get_saved_conns(self):
        """获取所有已存储的连接，生成页面树结构第一层"""
        conns = get_conns()
        icon = QIcon(":/icon/mysql_conn_icon.png")
        for item in conns:
            # item属性：id name host port user pwd
            # 根节点，展示连接的列表
            make_tree_item(self, self.treeWidget, item.name, icon, item.id)
            self.display_conn_dict[item.id] = item

    def get_tree_list(self):
        """获取树的子节点，双击触发，将连接 -> 数据库 -> 数据表，按顺序读取出来"""
        item = self.treeWidget.currentItem()
        node = tree_node_factory(item)
        Context(node).open_item(item, self)

    def table_check_box(self, item, check_state):
        """
        处理树结构中，表的复选框，实现表的复选框与表格控件中复选框联动效果
        :param item: 当前点击树节点元素
        :param check_state: 选中状态：全部选择、部分选、未选择
        """
        node = tree_node_factory(item)
        # 只处理表
        Context(node).change_check_box(item, check_state, self)

    def update_tree_item_name(self, item, name, col=0):
        """
        更新树的节点项名称
        :param item: 当前树节点元素
        :param name: 要更新的名字
        :param col: 写入在哪一列，默认名字写在第一列，第二列为隐藏列，可写id作为隐藏属性
        """
        item.setText(col, self._translate("MainWindow", name))

    def update_table_item(self, item, field):
        """
        更新表格控件中表格的值
        :param item: 当前表格元素
        :param field: 要填写的值
        """
        item.setText(self._translate("MainWindow", field))

    def close_conn(self, conn_name=None):
        """
        关闭连接
        :param conn_name: 要关闭的连接名称，若无，则关闭所有
        """
        close_connection(self, conn_name)

    def right_click_menu(self, pos):
        """
        右键菜单功能，实现右键弹出菜单功能
        :param pos:右键的坐标位置
        """
        # 获取当前元素，只有在元素上才显示菜单
        item = self.treeWidget.itemAt(pos)
        if item:
            # 生成右键菜单
            menu = QtWidgets.QMenu()
            node = tree_node_factory(item)
            menu_names = Context(node).get_menu_names(item, self)
            [menu.addAction(QtWidgets.QAction(option, menu)) for option in menu_names]
            # 右键菜单点击事件
            menu.triggered.connect(self.menu_slot)
            # 右键菜单弹出位置跟随焦点位置
            menu.exec_(QtGui.QCursor.pos())

    def menu_slot(self, act):
        """
        点击右键菜单选项后触发事件
        :param act: 右键菜单中的动作
        """
        # 获取右键点击的项
        item = self.treeWidget.currentItem()
        func = act.text()
        node = tree_node_factory(item)
        Context(node).handle_menu_func(item, func, self)

    def generate(self):
        selected_data = SelectedData().conn_dict
        if selected_data:
            generate_dialog = DisplaySelectedDialog(self, selected_data, self.screen_rect)
            generate_dialog.exec()
        else:
            pop_fail(WRONG_TITLE, WRONG_UNSELECT_DATA)

    def help(self):
        self.help_ui = HelpUI(self.screen_rect)
        self.help_ui.show()

    def about(self):
        self.about_ui = AboutUI(self.screen_rect)
        self.about_ui.show()

    def refresh(self):
        if self.refresh_finished:
            # 先将标志位修改
            self.refresh_finished = False
            refresh = Refresh(self, self.opened_table)
            refresh.collect_data_before_refresh()
            # 关闭右侧表格
            if hasattr(self, 'table_frame'):
                TreeNodeTable().close_item(self.current_table, self)
            # 清空当前树
            self.treeWidget.clear()
            # 重新获取页面连接
            self.get_saved_conns()
            refresh.refresh_finished.connect(lambda: self.refresh_finish())
            # 刷新数据
            refresh.refresh_data()

    def refresh_finish(self):
        # 复原标志位为已刷新完毕
        self.refresh_finished = True
        # 清空存储的打开项
        self.open_item_dict.clear()

    def all_selected_table_cols(self, checked):
        """作为表格表头复选框点击事件的槽函数，保持与右键树节点相同处理"""
        func = SELECT_ALL_FIELD_MENU if checked else UNSELECT_FIELD_MENU
        TreeNodeTable().handle_menu_func(self.current_table, func, self)

    def on_table_check_changed(self, checked, field):
        """
        表格第一列checkbox状态改变时触发
        :param checked: 复选框是否选中
        :param field: 表格中当前行字段值
        """
        # 获取当前打开表对应的树控件中的信息
        conn_id, conn_name, db_name, tb_name = get_node(self.current_table)
        # 如果是选择字段
        if checked:
            select_table = AsyncSelectTable(self,
                                            self.current_table,
                                            conn_id,
                                            conn_name,
                                            db_name,
                                            tb_name,
                                            field)
            select_table.select_table()
        else:
            # 设置表头复选框按钮状态为未选中
            self.table_header.set_header_checked(False)
            # 删除字段
            SelectedData().unset_cols(self, conn_name, db_name, tb_name, field)
            checked_list = SelectedData().get_col_list(conn_name, db_name, tb_name, True)
            # 设置左侧树部件中，对应表为未选中状态
            if checked_list is None:
                check_state = Qt.Unchecked
            else:
                check_state = Qt.PartiallyChecked
            self.current_table.setCheckState(0, check_state)



