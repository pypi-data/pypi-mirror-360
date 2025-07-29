from strenum import StrEnum


class Dir(StrEnum):
    # 上
    UP = "01",
    # 下
    DOWN = "02",
    # 前
    FRONT = "03",
    # 后
    BACK = "04",
    # 左
    LEFT = "05",
    # 右
    RIGHT = "06"


class SPED(StrEnum):
    # 1
    ONE = "01",
    # 2
    TWO = "02",
    # 3
    THREE = "03",
    # 4
    FOUR = "04"


class Dir2(StrEnum):
    # 前
    FRONT = "31",
    # 后
    BACK = "32",
    # 左
    LEFT = "33",
    # 右
    RIGHT = "34",
    # 上
    UP = "35",
    # 下
    DOWN = "36"


class Rotate(StrEnum):
    # 顺时针
    CLOCK_WISE = "01",
    # 逆时针
    ANTI_CLOCK_WISE = "02"


class Color(StrEnum):
    # 保持
    NOp = "00",
    # 黑
    BLACK = "01",
    # 白
    WHITE = "02",
    # 红
    RED = "03",
    # 绿
    GREEN = "04",
    # 蓝
    BLUE = "05",
    # 紫
    VIOLET = "06",
    # 青
    CYAN = "07",
    # 黄
    YELLOW = "08"


class State(StrEnum):
    # 常亮
    BRIGHT = "00",
    # 七彩变换
    COLORFUL = "02",
    # 呼吸灯
    BREATHING = "01"


class ATGColor(StrEnum):
    # 颜色
    COLOR = "44",
    # 标签
    LABEL = "43"


class QH(StrEnum):
    # 前
    FRONT = "01",
    # 后
    BACK = "02"


class ZY(StrEnum):
    # 左
    LEFT = "01",
    # 右
    RIGHT = "02"


class SX(StrEnum):
    # 上
    UP = "01",
    # 下
    DOWN = "02"


class Land(StrEnum):
    # 普通
    ORD = "2F"
    # 急停
    STOP = "2E"


class XXFX(StrEnum):
    # 前
    FRONT = "01",
    # 后
    BACK = "02",
    # 左
    LEFT = "03",
    # 右
    RIGHT = "04"


class OFFON(StrEnum):
    # 开
    ON = "01",
    # 关
    OFF = "02"


class MVColor(StrEnum):
    # 红
    RED = "10",
    # 绿
    GREEN = "20",
    # 蓝
    BLUE = "30",
    # 黄
    YELLOW = "40"
    # 黑
    BLACK = "50",


class JXSOF(StrEnum):
    # 张开
    OPEN = "28"
    # 闭合
    CLOSE = "5A"


class FliPpt(StrEnum):
    # 前
    FRONT = "01",
    # 后
    BACK = "02",
    # 左
    LEFT = "03",
    # 右
    RIGHT = "04"


class AllMode(StrEnum):
    # 二维码
    BY_QR_CODE = "01",
    # 颜色定位
    BY_COLOR = "02",
    # 循线
    BY_LINE = "03",
    # 特殊标志
    BY_SPECIAL_FLAG = "05",
    # 常规
    BY_DEFAULT = "04"


class ISRRT(StrEnum):
    # 关
    TURN_OFF = "F7 40 BF",
    # 开
    TURN_ON = "F7 C0 3F",
    # 红
    RED = "F7 20 DF",
    # 绿
    GREEN = "F7 A0 5F",
    # 蓝
    BLUE = "F7 60 9F",
    # 黄
    YELLOW = "F7 28 D7",
    # 锭
    INDIGO = "F7 B0 4F",
    # 紫
    VIOLET = "F7 68 97",
    # 白
    WHITE = "F7 E0 1F",
    # 七彩变换
    COLOR_TRANSFORM = "F7 C8 37",
    # 跳转变换
    JUMP_TRANSFORM = "F7 F0 0F",
    # 亮度增加
    INCREASE_BRIGHTNESS = "F7 00 FF",
    # 亮度减少
    DECREASE_BRIGHTNESS = "F7 80 7F"


class ISRColor(StrEnum):
    # 1.红
    RED = "01",
    # 2.绿
    GREEN = "02",
    # 3.蓝
    BLUE = "03",
    # 4.黄
    YELLOW = "04",
    # 5.锭
    INDIGO = "05",
    # 6.紫
    VIOLET = "06",
    # 7.白
    WHITE = "07"
