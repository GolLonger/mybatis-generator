﻿# -*- coding: utf-8 -*-
"""
处理所有关于树节点的操作
    双击节点事件
    右键菜单
    列表复选框
"""
from gui_function import *
from menu import *
from sys_info_storage.sqlite import *
from message_box import *
from conn_dialog import test_connection
from PyQt5.QtCore import Qt
from abc import ABC, abstractmethod
_author_ = 'luwt'
_date_ = '2020/6/23 16:21'


def tree_node_factory(item):
    """
    获取树节点对应的实例化对象。
    树结构：
        树的根：树的顶层
            连接：第一级，父节点为根
                数据库：第二级，父节点为连接
                    表：第三级，父节点为库
    目前树的根节点为空，所以可以根据这一特性发现当前节点的层级，
    从而返回相应的实例
    """
    # 如果父级为空，那么则为连接
    if item.parent() is None:
        return TreeNodeConn()
    elif item.parent().parent() is None:
        return TreeNodeDB()
    elif item.parent().parent().parent() is None:
        return TreeNodeTable()


class Context:

    def __init__(self, tree_node):
        self.tree_node = tree_node

    def open_item(self, item, gui):
        return self.tree_node.open_item(item, gui)

    def change_check_box(self, item, gui):
        return self.tree_node.change_check_box(item, gui)

    def get_menu_names(self, item, gui):
        return self.tree_node.get_menu_names(item, gui)

    def handle_menu_func(self, item, func, gui):
        return self.tree_node.handle_menu_func(item, func, gui)


class TreeNodeAbstract(ABC):

    @abstractmethod
    def open_item(self, item, gui): ...

    @abstractmethod
    def change_check_box(self, item, gui): ...

    @abstractmethod
    def get_menu_names(self, item, gui): ...

    @abstractmethod
    def handle_menu_func(self, item, func, gui): ...


class TreeNodeConn(TreeNodeAbstract, ABC):

    def open_item(self, item, gui):
        """
        打开连接，展示连接下的所有库列表
        :param item 当前点击元素
        :param gui 启动的主窗口界面对象
        """
        # 仅当子元素不存在时，获取子元素并填充
        if item.childCount() == 0:
            # 连接的id，存在于元素的第一列
            conn_id = int(item.text(1))
            dbs = open_connection(gui, conn_id).get_dbs()
            for db in dbs:
                make_tree_item(gui, item, db)

    def change_check_box(self, item, gui): ...

    def get_menu_names(self, item, gui):
        """
        获取树中，第一级连接项的右键菜单名字列表
        :param item 当前点击元素
        :param gui 启动的主窗口界面对象
        """
        return get_conn_menu_names(item)

    def handle_menu_func(self, item, func, gui):
        """右键菜单中关于连接的处理"""
        # 获取当前选中的连接id
        conn_id = int(item.text(1))
        # 打开连接
        if func == OPEN_CONN_MENU:
            self.open_item(item, gui)
            item.setExpanded(True)
            gui.treeWidget.repaint()
        # 关闭连接
        elif func == CLOSE_CONN_MENU:
            # 关闭数据连接，关闭特定连接，id为标识
            close_connection(gui, conn_id)
            item.takeChildren()
            close_table(gui)
        # 测试连接
        elif func == TEST_CONN_MENU:
            test_connection(gui.conns_dict.get(conn_id))
        # 添加连接
        elif func == ADD_CONN_MENU:
            add_conn_func(gui)
        # 编辑连接
        elif func == EDIT_CONN_MENU:
            # 先弹关闭连接确认框
            reply = pop_question(func, EDIT_CONN_PROMPT)
            if reply:
                # 关闭连接
                close_connection(gui, conn_id)
                close_tree_item(gui, item)
                conn_info = gui.conns_dict.get(conn_id)
                show_conn_dialog(gui, conn_info, func)
                # 在子窗口更新完数据库和页面后，将页面的存储数据也更新
                gui.conns_dict[conn_id] = open_connection(gui, conn_id)
        # 删除连接
        elif func == DEL_CONN_MENU:
            # 弹出关闭连接确认框
            reply = pop_question(func, DEL_CONN_PROMPT)
            if reply:
                # 关闭连接
                close_connection(gui, conn_id)
                conn_info = gui.conns_dict[conn_id]
                delete_conn(conn_info.id)
                del gui.conns_dict[conn_id]
                # 删除树元素
                # 树型部件的takeTopLevelItem方法可以从树型部件中删除对应项的节点并返回该项，语法：takeTopLevelItem(index)
                # 通过调用树型部件的indexOfTopLevelItem方法可以获得对应项在顶层项的位置，语法：indexOfTopLevelItem
                #
                # self.treeWidget.removeItemWidget，它从一个项中移除一个小部件，而不是QTreeWidgetItem。它对应于setItemWidget方法
            gui.treeWidget.takeTopLevelItem(gui.treeWidget.indexOfTopLevelItem(item))


class TreeNodeDB(TreeNodeAbstract, ABC):

    def open_item(self, item, gui):
        """
        打开数据库，展示数据库下的所有表，
        并将表的复选框置为未选中
        :param item 当前点击元素
        :param gui 启动的主窗口界面对象
        """
        # 仅当子元素不存在时，获取子元素并填充
        if item.childCount() == 0:
            # 获取连接id，从而获取该连接的数据库操作对象
            conn_id = int(item.parent().text(1))
            executor = open_connection(gui, conn_id)
            # 首先需要切换库
            executor.switch_db(item.text(0))
            tables = executor.get_tables()
            for table in tables:
                make_tree_item(gui, item, table, checkbox=Qt.Unchecked)

    def change_check_box(self, item, gui): ...

    def get_menu_names(self, item, gui):
        """
        获取树中，数据库项的右键菜单名字列表
        :param item 当前点击元素
        :param gui 启动的主窗口界面对象
        """
        # 检查表的复选框状态
        check_state = check_table_status(item)
        return get_db_menu_names(item, check_state)

    def handle_menu_func(self, item, func, gui):
        """右键菜单中关于数据库的处理"""
        # 打开数据库
        if func == OPEN_DB_MENU:
            self.open_item(item, gui)
            item.setExpanded(True)
            gui.treeWidget.repaint()
        # 关闭数据库
        elif func == CLOSE_DB_MENU:
            close_tree_item(gui, item)
        # 全选所有表
        elif func == SELECT_ALL_TB_MENU:
            set_children_check_state(item, Qt.Checked)
        # 取消全选表
        elif func == UNSELECT_TB_MENU:
            set_children_check_state(item, Qt.Unchecked)


class TreeNodeTable(TreeNodeAbstract, ABC):

    def open_item(self, item, gui):
        """
        打开表，可获取表中所有列名信息，然后展示在表格控件中，
        列的复选框与表格的复选框联动
        :param item 当前点击元素
        :param gui 启动的主窗口界面对象
        """
        # 获取连接id，从而获取该连接的数据库操作对象
        conn_id = int(item.parent().parent().text(1))
        executor = open_connection(gui, conn_id)
        # 获取当前表下所有的列名
        cols = executor.get_cols(item.text(0))
        # 当前表复选框的状态，赋予表格中复选框的状态
        fill_table(gui, cols, item.checkState(0))
        # 如果表格复选框为选中，那么将表头的复选框也选中，默认表头复选框未选中
        if item.checkState(0) == Qt.Checked:
            gui.header.set_header_checked(True)
        # 表格复选框改变事件
        gui.tableWidget.cellChanged.connect(gui.on_cell_changed)
        gui.current_table = item

    def change_check_box(self, item, gui):
        """
        修改复选框状态，当前元素复选框状态应与表格控件中的复选框联动
        :param item 当前点击元素
        :param gui 启动的主窗口界面对象
        """
        check_state = item.checkState(0)
        # 如果表已经选中，那么右侧表格需全选字段
        if check_state == Qt.Checked:
            change_table_checkbox(gui, True)
        # 如果表未选中，那么右侧表格需清空选择
        elif check_state == Qt.Unchecked:
            change_table_checkbox(gui, False)

    def get_menu_names(self, item, gui):
        """
        :param item 当前点击元素
        :param gui 启动的主窗口界面对象
        """
        # 检查表格中字段复选框状态
        check_state = check_field_status(gui, item)
        # 检查表是否展示：表头如果展示，当前表对象就是当前点击元素，
        # 那么证明表格已经展示。否则可能展示的是其他表
        table_opened = gui.tableWidget.horizontalHeader().isVisible() \
            and gui.current_table is item
        return get_table_menu_names(table_opened, check_state)

    def handle_menu_func(self, item, func, gui):
        """右键菜单关于表的处理"""
        # 打开表
        if func == OPEN_TABLE_MENU:
            gui.get_tree_list()
        # 关闭表
        elif func == CLOSE_TABLE_MENU:
            close_table(gui)
        # 全选字段
        elif func == SELECT_ALL_FIELD_MENU:
            change_table_checkbox(gui, True)
        # 取消选择字段
        elif func == UNSELECT_FIELD_MENU:
            change_table_checkbox(gui, False)
        # 生成
        elif func == GENERATE_MENU:
            pass

