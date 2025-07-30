# fssucaiot/__init__.py
from .core import RecorderTool, SimpleSwitchController, create_label, create_button, create_textbox

# 主动导出 tk 模块（tkinter）
import tkinter as tk

__all__ = ['RecorderTool', 'RecorderTool', 'SimpleSwitchController', 'create_label', 'create_button', 'create_textbox',
           'tk']
