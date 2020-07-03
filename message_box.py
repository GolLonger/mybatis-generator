﻿# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from constant import *
_author_ = 'luwt'
_date_ = '2020/6/21 16:08'


def pop_msg(title, msg):
    """弹出普通信息框"""
    msg_box = QMessageBox(QMessageBox.Information, title, msg)
    msg_box.addButton(OK_BUTTON, QMessageBox.AcceptRole)
    msg_box.exec()


def pop_ok(title, msg):
    """弹出执行成功消息框"""
    msg_box = QMessageBox(QMessageBox.NoIcon, title, msg)
    pix = QPixmap("right.jpg").scaled(30, 30, Qt.IgnoreAspectRatio,
                                      Qt.SmoothTransformation)
    msg_box.setIconPixmap(pix)
    msg_box.addButton(OK_BUTTON, QMessageBox.AcceptRole)
    msg_box.exec()


def pop_fail(title, msg):
    """弹出失败消息框"""
    msg_box = QMessageBox(QMessageBox.Critical, title, msg)
    msg_box.addButton(OK_BUTTON, QMessageBox.AcceptRole)
    msg_box.exec()


def pop_question(title, msg):
    """弹出询问消息框"""
    msg_box = QMessageBox(QMessageBox.Question, title, msg)
    msg_box.addButton(ACCEPT_BUTTON, QMessageBox.AcceptRole)
    msg_box.addButton(REJECT_BUTTON, QMessageBox.RejectRole)
    reply = msg_box.exec()
    return True if reply == QMessageBox.AcceptRole else False