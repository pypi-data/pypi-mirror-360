#!/usr/bin/env python
# -*-coding:utf-8-*-


"""
matplotlib plot utils

pandas虽然也有绘图功能，但感觉让事情变得复杂了。就算是已经转成pandas那边的数据类型了，要绘图提出指定的数据也是很方便的。

约定都统一到matplotlib这边的绘图接口上。

约定本脚本所有绘图函数都需要指定ax
"""

import numpy as np


def _process_ax_args(ax, title='', x_label='', y_label='', x_lim=None, y_lim=None):
    # 标题
    if title:
        ax.set_title(title)

    # 设置x标签
    if x_label:
        ax.set_xlabel(x_label)

    # 设置y标签
    if y_label:
        ax.set_ylabel(y_label)

    # 设置x轴范围
    if x_lim is not None:
        ax.set_xlim(x_lim)

    # 设置y轴范围
    if y_lim is not None:
        ax.set_ylim(y_lim)


def line_plot(ax, x_values=None, y_values=None, title='', x_label='', y_label='', x_tick_labels=None, x_lim=None,
              y_lim=None, **kwargs):
    """
    kwargs 各个参数参见 `matplotlib.lines.Line2D` 文档

    https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D

    matplotlib 推荐的风格
    A helper function to make a graph.
    """
    if x_values is None and y_values is None:
        raise Exception(f'x_values, y_values, 至少要给定一个')

    if x_values is None:
        x_values = np.arange(len(y_values))

    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    # 设置x标签
    if x_tick_labels is not None:
        ax.set_xticks(x_values)
        ax.set_xticklabels(x_tick_labels)

    ax.plot(x_values, y_values, **kwargs)


def scatter_plot(ax, x_values, y_values, title='', x_label='', y_label='', x_lim=None, y_lim=None, **kwargs):
    """
    散点图
    """
    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    ax.scatter(x_values, y_values, **kwargs)


def image_plot(ax, image_data, cmap=None, interpolation=None, vmin=None, vmax=None, title='', x_label='', y_label='',
               x_lim=None, y_lim=None, **kwargs):
    """
    显示图片
    """
    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    ax.imshow(image_data, interpolation=interpolation, cmap=cmap, vmin=vmin, vmax=vmax, **kwargs)


def pie_plot(ax, values, title='', x_label='', y_label='', x_lim=None, y_lim=None, **kwargs):
    """
    绘制饼状图
    :return:
    """
    _process_ax_args(ax, title=title, x_label=x_label, y_label=y_label, x_lim=x_lim, y_lim=y_lim)

    ax.pie(values, autopct='%2.0f%%', startangle=90, **kwargs)


def set_matplotlib_support_chinese(font='SimHei'):
    """
    设置matplotlib支持中文
    :param font:
    :return:
    """
    from matplotlib import rcParams

    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'].insert_child(0, font)  # 插入中文字体
