# 允许用户从 fssucatools 直接导入 RecorderTool 和控件函数
from .fssucatools import RecorderTool, create_label, create_button, create_entry

# 主动导出 tk 模块（tkinter）
import tkinter as tk

__all__ = ['RecorderTool', 'create_label', 'create_button', 'create_entry', 'tk']
