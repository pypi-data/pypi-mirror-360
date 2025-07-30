# norfetools/__init__.py


from .Bibcleaner import Bib
from .FileTools import Sl


# === 引入工具函数 ===
from .norfetools import (
    Set_colorbar_ticks_inward,
    Set_colorbar_ticks_outward,
    Set_axis_formatting,
    SetColor,
    TestColorList,
    Save_Fig,
    SaveFig,
    Set_style,
    Save_data,
    Load_data,
    SaveData,
    LoadData,
    Ensure_directory_exists
)


__all__ = ['Bib', 
            'Sl',
            "Set_colorbar_ticks_inward",
            "Set_colorbar_ticks_outward",
            "Set_axis_formatting",
            "SetColor",
            "TestColorList",
            "Save_Fig",
            "SaveFig",
            "Set_style",
            "Save_data",
            "Load_data",
            "SaveData",
            "LoadData",
            "Ensure_directory_exists",
            ]



import matplotlib.pyplot as plt

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
