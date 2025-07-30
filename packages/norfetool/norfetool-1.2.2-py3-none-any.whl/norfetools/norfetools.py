import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image

import os
import re
import numpy as np
import pickle

import matplotlib as mpl

from contextlib import contextmanager
import warnings


try:
    # plt.style.use(["science", "grid"])
    plt.style.use(["science", ])
except OSError:
    warnings.warn(f"Matplotlib style load failed. Using default style.", UserWarning)


# 设置网格透明度为0.2
mpl.rcParams.update({
    'axes.grid': True,           # 启用主坐标轴网格线
    'grid.alpha': 0.4,           # 网格线透明度
    'grid.linestyle': ':',       # 网格线样式（点状）
    'grid.color': 'black'        # 网格线颜色
})

mpl.rcParams.update({
    'legend.frameon': True,           # 显示图例边框
    'legend.facecolor': 'white',      # 图例背景颜色
    'legend.edgecolor': '#cccccc',      # 图例边框颜色
    'legend.framealpha': 1.0,         # 图例背景不透明度（1为不透明，0为透明）
    'legend.fancybox': True          # 若为True则边框为圆角，False为直角
})

# 默认的DPI设置，用于保存图像
DPI_SAVE = 800


@contextmanager
def Set_style(styles = ["science", "nature", "grid"]):
    with plt.style.context(styles):
        yield


def Save_Fig(flag, path, filepath="figure/"):
    """
    保存绘制的图像到指定路径。

    参数:
    flag (bool 或 int): 决定是否保存图像。如果为 True，则保存图像；
                         如果为 False，则显示图像；
                         如果为 int 且等于 2，则保存多格式和风格图像。
    path (str): 图像文件名，包括扩展名（如 'image.png'）。
    filepath (str): 保存图像的文件夹路径，默认为 'figure/'。

    返回:
    无
    """
    # 提取基本文件名（不含扩展名）和后缀
    base, ext = os.path.splitext(path)
    base_path = os.path.join(filepath, base)

    # 若为True或int类型
    if flag:
        if not os.path.isdir(filepath):
            os.makedirs(filepath)

        if isinstance(flag, int) and flag == 2:
            formats = ['png', 'svg']

            # 原始风格保存
            for fmt in formats:
                filename = f"{base_path}.{fmt}"
                plt.savefig(filename, bbox_inches='tight', dpi=DPI_SAVE)

            # 改变风格后再保存
            with Set_style():
                for fmt in formats:
                    filename = f"{base_path}_altstyle.{fmt}"
                    plt.savefig(filename, bbox_inches='tight', dpi=DPI_SAVE)

            plt.close()
        else:
            # 标准保存流程
            plt.savefig(os.path.join(filepath, path), bbox_inches='tight', dpi=DPI_SAVE)
            plt.close()

    else:
        plt.show()

SaveFig = Save_Fig

def TestColorList(clist):
    """
    显示色卡和颜色在不同图形中的应用示例。
    
    参数:
    clist (list): 色卡列表，包含颜色定义。
    """
    num = len(clist)
    gs = GridSpec(3, num + int(num / 2), figure=plt.figure(figsize=(6, 4)))
    plt.subplots_adjust(wspace=0.3, hspace=0.2)

    # 显示色卡
    for i, color in enumerate(clist):
        if type(color) != str:
            color = tuple([int(i * 255) for i in color])
        img = Image.new('RGB', (10, 10), color)
        ax = plt.subplot(gs[0, i])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis("off")
        ax.imshow(img)

    # 正弦波形
    ax = plt.subplot(gs[1:, :num])
    xvalue = np.arange(0, 2 * np.pi, 0.1)
    for i, color in enumerate(clist):
        ax.plot(xvalue, np.sin((i + 0.5) * xvalue), "-", color=color, label="%d" % i)
    ax.grid(":", alpha=0.3)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.legend(loc=4)

    # 指数波形
    ax = plt.subplot(gs[:, num:])
    xvalue = np.arange(0, 0.5, 0.05)
    for i, color in enumerate(clist):
        ax.plot(xvalue, np.exp((i + 0.5) * xvalue), "s", color=color, markerfacecolor='none', label="%d" % i)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(loc=2)
    plt.show()
    plt.close()


def SetColor(string, num_colors, extract_first_colors=False, ifshow=False):
    """
    根据给定的colormap名称生成颜色列表并显示。可以选择生成均匀分布的颜色列表
    或者提取colormap的前几个颜色。

    参数:
    string (str): colormap的名称。
    num_colors (int): 要生成或提取的颜色数量。
    extract_first_colors (bool): 如果为True，则仅提取colormap的前num_colors个颜色。
                                 如果为False，则根据num_colors在colormap中均匀分布生成颜色列表。

    返回:
    list: 生成的颜色列表。
    """
    if extract_first_colors:
        # 仅提取colormap的前num_colors个颜色
        color_list = [plt.cm.get_cmap(string)(i) for i in range(num_colors)]
    else:
        # 生成均匀分布的颜色列表
        array = np.linspace(0, 1, num_colors)
        color_list = plt.cm.get_cmap(string)(array)

    if ifshow:
        TestColorList(color_list)
    return color_list


def Set_axis_formatting(axis, nbins, decimals):
    from matplotlib.ticker import MaxNLocator, FormatStrFormatter
    """
    设置图表的轴格式。

    参数:
    axis (str): 指定要设置的轴。'x' 设置x轴，'y' 设置y轴，'both' 设置两者。
    nbins (int): 轴的主要刻度的数量。
    decimals (int): 轴刻度标签的小数位数。
    """
    formatter = FormatStrFormatter(f'%.{decimals}f')

    if axis == 'x' or axis == 'both':
        plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=nbins))
        plt.gca().xaxis.set_major_formatter(formatter)

    if axis == 'y' or axis == 'both':
        plt.gca().yaxis.set_major_locator(MaxNLocator(nbins=nbins))
        plt.gca().yaxis.set_major_formatter(formatter)


def Set_colorbar_ticks_outward(cbar, 
                                major_len=None, minor_len=None, 
                                major_width=None, minor_width=None):
    """
    设置 colorbar 主/子刻度线朝外，支持默认或自定义长度和粗细。

    参数：
        cbar : matplotlib.colorbar.Colorbar
        major_len, minor_len : int or None
            刻度线长度；若为 None，则使用默认值。
        major_width, minor_width : float or None
            刻度线宽度；若为 None，则使用默认值。
    """
    # 获取默认参数
    default_major_len = mpl.rcParams['xtick.major.size']
    default_minor_len = mpl.rcParams['xtick.minor.size']
    default_major_width = mpl.rcParams['xtick.major.width']
    default_minor_width = mpl.rcParams['xtick.minor.width']

    # 使用默认值或用户值
    major_len = major_len if major_len is not None else default_major_len
    minor_len = minor_len if minor_len is not None else default_minor_len
    major_width = major_width if major_width is not None else default_major_width
    minor_width = minor_width if minor_width is not None else default_minor_width

    # 应用设置
    cbar.ax.tick_params(which='major', direction='out', length=major_len, width=major_width)
    cbar.ax.minorticks_on()
    cbar.ax.tick_params(which='minor', direction='out', length=minor_len, width=minor_width)


def Set_colorbar_ticks_inward(cbar, 
                              major_len=None, minor_len=None, 
                              major_width=None, minor_width=None):
    """
    设置 colorbar 主/子刻度线朝内，支持默认或自定义长度和粗细。

    参数：
        cbar : matplotlib.colorbar.Colorbar
        major_len, minor_len : int or None
            刻度线长度；若为 None，则使用默认值。
        major_width, minor_width : float or None
            刻度线宽度；若为 None，则使用默认值。
    """
    # 获取默认参数
    default_major_len = mpl.rcParams['xtick.major.size']
    default_minor_len = mpl.rcParams['xtick.minor.size']
    default_major_width = mpl.rcParams['xtick.major.width']
    default_minor_width = mpl.rcParams['xtick.minor.width']

    # 使用默认值或用户值
    major_len = major_len if major_len is not None else default_major_len
    minor_len = minor_len if minor_len is not None else default_minor_len
    major_width = major_width if major_width is not None else default_major_width
    minor_width = minor_width if minor_width is not None else default_minor_width

    # 应用设置，设置刻度线朝内
    cbar.ax.tick_params(which='major', direction='in', length=major_len, width=major_width)
    cbar.ax.minorticks_on()
    cbar.ax.tick_params(which='minor', direction='in', length=minor_len, width=minor_width)

#############################################
##################文件处理####################
#############################################


def Ensure_directory_exists(filename):
    """
    检查文件的目录是否存在，如果不存在，则创建。
    :param filename: 要检查的文件名或路径。
    """
    directory = os.path.dirname(filename)
    
    # 如果目录名不为空且目录不存在，则创建
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def Save_data(temp_data_list, filename='temp_data_list.pkl'):
    """
    保存 temp_data_list 到一个文件中。
    :param temp_data_list: 要保存的数据列表。
    :param filename: 保存数据的文件名，默认为 'temp_data_list.pkl'。
    """
    Ensure_directory_exists(filename)
    with open(filename, 'wb') as file:
        pickle.dump(temp_data_list, file)


def Load_data(filename='temp_data_list.pkl'):
    """
    从文件中加载 temp_data_list。
    :param filename: 包含数据的文件名，默认为 'temp_data_list.pkl'。
    :return: 返回加载的数据列表。
    """
    with open(filename, 'rb') as file:
        return pickle.load(file)

SaveData = Save_data
LoadData = Load_data
