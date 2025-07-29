from .enumHelper import ATGColor, QH, AllMode, MVColor, XXFX, JXSOF, OFFON, ISRColor, ISRRT, Land, FliPpt, Color, State, ZY, Rotate, SX, Dir2, Dir, SPED
from .peripheral import Peripheral
from .serialHelper import hex_str


#2023-5-22 名称修改完毕

# 红外灯
# 红外灯[ISR_RT]
def get_infrared_hex_code(code: ISRRT):
    return code.value


class JHFDRONE:
    def __init__(self, peripheral: Peripheral):
        self.__peripheral = peripheral

    def start(self):
        self.__peripheral.start()

    def stop(self):
        self.__peripheral.stop()

    # 颜色判断
    # 前方颜色
    def get_current_color(self):
        color = self.__peripheral.parse_data("DDAA", "FEFE", 40, 42)
        if color == "10":
            return "红"
        elif color == "20":
            return "蓝"
        elif color == "30":
            return "黄"
        else:
            return "无"

    # 获取电压
    # 飞机电压
    def get_current_vcc(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 8, 12), 16)

    # 获取高度
    # 当前高度
    def get_current_height(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 12, 16), 16)

    # 获取二维码编号
    # 二维码ID
    def get_id_qr_code(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 44, 48), 16)

    # 获取版本号
    # 固件版本
    def get_version(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 16, 22), 16) / 100.0

    # 获取信号强度
    # 无线信号强度
    def get_wifi_strength(self):
        return str(int(self.__peripheral.parse_data("DDAA", "FEFE", 34, 36), 16)) + "%"

    # 循线路口
    # 循线路口
    def air_HIGH(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 40, 42), 16)

    # # 获取openmv模式
    # # 视觉模式
    # def get_mode_open_mv(self):
    #     open_mv_mode = self.__peripheral.parse_data("DDAA", "FEFE", 42, 44)
    #     if open_mv_mode == "F3":
    #         return "循线模式"
    #     elif open_mv_mode == "F6":
    #         return "二维码模式"
    #     elif open_mv_mode == "F7":
    #         return "色块定位模式"
    #     else:
    #         return "常规模式"

    # 获取前方距离
    # TOF测距（前）cm
    def get_data_ultrason_front(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 38, 40), 16)

    # 获取后方距离
    # TOF测距（后）cm
    def get_data_ultrason_back(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 30, 32), 16)

    # 获取左方距离
    # TOF测距（左）cm
    def get_data_ultrason_left(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 32, 34), 16)

    # 获取右方距离
    # TOF测距（右）cm
    def get_data_ultrason_right(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 36, 38), 16)

    # 获取下方距离
    # TOF测距（下）cm
    def get_data_ultrason_down(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 28, 30), 16)



    # 获取长
    # 获取长
    def parsedotx(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 48, 50), 16)



    # 获取宽
    # 获取宽
    def parsedoty(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 50, 52), 16)


    # 获取面积
    # 获取面积
    def parsedot_MJ(self):
        return int(self.__peripheral.parse_data("DDAA", "FEFE", 52, 56), 16)


    # 位置值清零
    # 相对于[distance]号标签清除误差
    def current_location(self, distance: int):
        msg = " ".join(["AA FA 45", hex_str("%04X" % distance, 4), "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 解锁怠速
    # 无人机怠速
    def Unlock_uav(self):
        msg = "AA FA 2B 00 00 00 00 00 00 00 00 00 FE"
        self.__peripheral.write(msg)

    # 初始化
    # 无人机初-始化
    def init_uav(self):
        msg = "AA FA 21 00 00 00 00 00 00 00 00 00 FE"
        self.__peripheral.write(msg)

    # 起飞
    # 起飞[distance]cm
    def take_off(self, distance: int):
        msg = " ".join(["AA FA 22", hex_str("%04X" % distance, 4), "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 飞行速度
    # 设置飞行速度[distance]
    def set_speed(self, distance: int):
        msg = " ".join(["AA FA 28", hex_str("%04X" % distance, 4), "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 移动
    # 向 [direction] 飞[distance]cm
    def move_Ctrl_cm(self, direction: Dir, distance: int):
        msg = " ".join(["AA FA 23", direction.value, hex_str("%04X" % distance, 4), "00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 时间移动
    # 向 [mangtion] 飞[distance]*0.01(秒)
    def move_Ctrl_time(self, direction: Dir2, distance: int):
        msg = " ".join(["AA FA 51", direction.value, hex_str("%04X" % distance, 4), "00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)


    # 时间移动
    # 向 [mangtion] 飞[distance]*0.01(秒)，速度[direction2]---------------------------------------------------------------------------------------------------------------------------------------
    def move_Ctrl_time_speed(self, direction: Dir2, direction2: SPED, distance: int):
        msg = " ".join(["AA FA 41", direction.value, hex_str("%04X" % distance, 4), "00", direction2.value ,"00 00 00 00 FE"])
        self.__peripheral.write(msg)



    # 斜线移动
    # 向[QH][qh_num][ZY][zy_num][SX][sx_num](厘米)
    def move_slash(self, qh: QH, qh_num: int, zy: ZY, zy_num: int, sx: SX, sx_num: int):
        msg = " ".join(
            ["AA FA 24", qh.value, hex_str("%04X" % qh_num, 4), zy.value, hex_str("%04X" % zy_num, 4), sx.value,
             hex_str("%04X" % sx_num, 4), "FE"])
        self.__peripheral.write(msg)

    # 旋转
    # [Rotate]旋转[distance]度
    def rotate(self, rotate: Rotate, distance: int):
        msg = " ".join(["AA FA 25", rotate.value, hex_str("%04X" % distance, 4), "00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 环绕
    # 以无人机[QH][distance]cm  [ZY][distance2]cm为中心 [Rotate]环绕[distance3]°  用时[distance4]秒
    def fly_surround(self, qh: QH, distance: int, zy: ZY, distance2: int, rotate_direction: Rotate, distance3: int,
                     distance4: int):
        msg = " ".join(["AA FA 52", qh.value, hex_str("%02X" % distance), zy.value, hex_str("%02X" % distance2),
                        hex_str("%04X" % distance3, 4), rotate_direction.value, hex_str("%02X" % distance4), "00 FE"])
        self.__peripheral.write(msg)

    # 灯光控制
    # 设置飞机大灯[clour]色[state]
    def set_light(self, color: Color = Color.BLACK, mode: State = State.BRIGHT):
        msg = " ".join(["AA FA 26", color.value, mode.value, "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 翻滚
    # 4D翻滚[flippt]
    def flip(self, direction: FliPpt):
        msg = " ".join(["AA FA 29", direction.value, "00 00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 降落
    # [land_stop]降落——[distance]速度
    def landing(self, mode: Land, distance: int):
        msg = " ".join(["AA FA", mode.value, hex_str("%04X" % distance, 4), "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 拍照
    # 拍一张照片照
    def take_photo(self):
        msg = "AA FA 2C 00 00 00 00 00 00 00 00 00 FE"
        self.__peripheral.write(msg)

    # 激光定高
    # 激光定高[OFFON]
    def set_laser(self, status: OFFON):
        msg = " ".join(["AA FA 40 00 00 00", status.value, "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 定位模式
    # 定位模式[OFFON]
    def set_relocation(self, status: OFFON):
        msg = " ".join(["AA FA 47 00 00 00", status.value, "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)


    # 红外发射
    # 发射红外数据[ISR_RT]
    def emit_appoint_data(self, status: ISRRT):
        msg = " ".join(["AA FA 30 00", status.value, "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 红外发射
    # 发射红外数据[NUMT1]
    def emit_data(self, data: str):
        msg = " ".join(["AA FA 30 00", data, "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 发射红外点阵
    # 红外点阵显示[ISR_col]色单个字符[distance]
    def display_lattice(self, color: ISRColor, nb_characters: int):
        msg = " ".join(["AA FA 30 00 FF", color.value, hex_str("%02X" % nb_characters), "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 数据回传
    # 数据回传[OFFON]
    def DATA_return(self, status: OFFON = OFFON.ON):
        msg = " ".join(["AA FA D0", status.value, "00 00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 磁吸
    # 电磁铁[OFFON]
    def set_BM(self, status: OFFON = OFFON.ON):
        msg = " ".join(["AA FA 31 00 FF FF", status.value, "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 舵机
    # 舵机[distance]°
    def set_Servo(self, distance: int):
        msg = " ".join(["AA FA 33", hex_str("%02X" % distance), "00 00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)



    # 机械手
    # 机械手[distance]°
    def set_hand(self, distance: int):
        msg = " ".join(["AA FA 34", hex_str("%02X" % distance), "00 00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 激光
    # 发射激光
    def emit_laser(self):
        msg = "AA FA 35 00 00 00 00 00 00 00 00 00 FE"
        self.__peripheral.write(msg)

    # 循线方向
    # 向[XXFX]循线飞行
    def Traverse_uav(self, direction: XXFX = XXFX.FRONT):
        msg = " ".join(["AA FA 41 00 00 00", direction.value, "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 颜色定位
    # 定位颜色[MV_COLOUR]
    def point_color(self, color: MVColor = MVColor.RED):
        msg = " ".join(["AA FA 42 00 00 00", color.value, "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 二维码模式
    # 切换为[ALL_mode]模式
    def change_mode(self, mode: AllMode = AllMode.BY_DEFAULT):
        msg = " ".join(["AA FA A0", mode.value, "00 00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)


    # 标签间距，根据实际场地调整，单位cm
    # 二维码标签间距[distance]cm
    def set_spacing(self, distance: int):
        msg = " ".join(["AA FA A2", hex_str("%02X" % distance), "00 00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 期望标签
    # 飞向[distance]标签，高度[distance2]
    def fly_ID(self, distance: int, distance2: int):
        msg = " ".join(["AA FA A7", hex_str("%04X" % distance, 4), hex_str("%02X" % distance2), "00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 定点当前标签
    # 定点当前标签，高度[distance]
    def fly_now_id(self, distance: int):
        msg = " ".join(["AA FA A6", hex_str("%04X" % distance, 4), "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 定点当前颜色
    # 定点当前颜色块，高度[distance]cm
    def fly_now_color(self, distance: int):
        msg = " ".join(["AA FA A5 00", hex_str("%02X" % distance), "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 颜色偏差
    # 默认定位在[ATG_COLOUR][QH]方[distance]像素
    def point_location(self, color: ATGColor, qh: QH, distance: int):
        msg = " ".join(["AA FA", color.value, "00 00", qh.value, hex_str("%02X" % distance), "00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

    # 角度校准
    # 飞机航向校准
    def calibration(self):
        msg = "AA FA 2A 00 00 00 00 00 00 00 00 00 FE"
        self.__peripheral.write(msg)

    # ********************************************************************************************************
    # 编队怠速
    # TX230[direction]怠速
    def BD_Unlock_uav(self, distance: int):
        msg = " ".join(["AA FA C5", hex_str("%02X" % distance), "00 00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)


    # 环绕速度
    # 环绕速度[distance]cm/s
    def BD_around_SPEED(self, distance: int):
        msg = " ".join(["AA FA A3", hex_str("%04X" % distance, 4),  "00 00 00 00 00 00 00 FE"])
        self.__peripheral.write(msg)

        # 编队起飞..................................................................................
        # "[distance]无人机起飞[distance2]厘米",

    def BD_take_off(self, distance: int, distance2: int):
        msg = " ".join(
            ["AA FA 22", hex_str("%04X" % distance2, 4), "00 00 00 00 00 00", hex_str("%02X" % distance), "FE"])
        self.__peripheral.write(msg)

        # 旋转..................................................................................
        # [distance]无人机,[Rotate]旋转[distance2]度

    def BD_rotate(self, distance: int, rotate: Rotate, distance2: int):
        msg = " ".join(
            ["AA FA 25", rotate.value, hex_str("%04X" % distance2, 4), "00 00 00 00 00", hex_str("%02X" % distance),
             "FE"])
        self.__peripheral.write(msg)

        # 灯光控制
        # [distance]无人机灯光[clour]色[state]........................................................

    def BD_set_light(self, distance: int, color: Color = Color.BLACK, mode: State = State.BRIGHT):
        msg = " ".join(["AA FA 26", color.value, mode.value, "00 00 00 00 00 00", hex_str("%02X" % distance), "FE"])
        self.__peripheral.write(msg)

        # 斜线移动
        # ..........................................................................................
        # [direction]无人机向[QH][qh_num][ZY][zy_num][SX][sx_num](厘米)

    def BD_move_slash(self, distance: int, qh: QH, qh_num: int, zy: ZY, zy_num: int, sx: SX, sx_num: int):
        msg = " ".join(
            ["AA FA 56", qh.value, hex_str("%04X" % qh_num, 4), zy.value, hex_str("%04X" % zy_num, 4), sx.value,
             hex_str("%02X" % sx_num), hex_str("%02X" % distance), "FE"])
        self.__peripheral.write(msg)

        # 匀速斜线移动
        # [distance]无人机匀速向[QH][qh_num][ZY][zy_num](厘米)用时[distance4]秒

    def BD_move_slash2(self, distance: int, qh: QH, qh_num: int, zy: ZY, zy_num: int, distance4: int):
        msg = " ".join(
            ["AA FA 57", qh.value, hex_str("%04X" % qh_num, 4), zy.value, hex_str("%04X" % zy_num, 4), "00",
             hex_str("%02X" % distance4), hex_str("%02X" % distance), "FE"])
        self.__peripheral.write(msg)

        # 环绕
        # [distance]号无人机以自身[QH][distance5]cm  [ZY][distance2]cm为中心 [Rotate]环绕[distance3]°  用时[distance4]秒

    def BD_fly_surround(self, distance: int, qh: QH, distance5: int, zy: ZY, distance2: int, rotate_direction: Rotate,
                        distance3: int,
                        distance4: int):
        msg = " ".join(["AA FA 52", qh.value, hex_str("%02X" % distance5), zy.value, hex_str("%02X" % distance2),
                        hex_str("%04X" % distance3, 4), rotate_direction.value, hex_str("%02X" % distance4),
                        hex_str("%02X" % distance), "FE"])
        self.__peripheral.write(msg)

        # 环绕
        # [distance]号无人机以自身[SX][distance5]cm  [ZY][distance2]cm为中心 [Rotate]环绕[distance3]°  用时[distance4]秒

    def BD_fly_surround2(self, distance: int, sx: SX, distance5: int, zy: ZY, distance2: int, rotate_direction: Rotate,
                         distance3: int,
                         distance4: int):
        msg = " ".join(["AA FA 54", sx.value, hex_str("%02X" % distance5), zy.value, hex_str("%02X" % distance2),
                        hex_str("%04X" % distance3, 4), rotate_direction.value, hex_str("%02X" % distance4),
                        hex_str("%02X" % distance), "FE"])
        self.__peripheral.write(msg)

        # 编队降落...........................................................................................................
        # "TX230[direction]降落",

    def BD_landing(self, distance: int, mode: Land, distance2: int):
        msg = " ".join(
            ["AA FA", mode.value, hex_str("%04X" % distance2, 4), "00 00 00 00 00 00", hex_str("%02X" % distance),
             "FE"])
        self.__peripheral.write(msg)

        # 期望标签
        # "TX230[distance]飞到[distance2]标签，高度[distance3]厘米[clour]",

    def BD_fly_ID(self, distance: int, distance2: int, distance3: int, color: Color):
        msg = " ".join(
            ["AA FA c2", hex_str("%02X" % distance), hex_str("%04X" % distance2, 4), hex_str("%04X" % distance3, 4),
             "00 00 00", color.value, "FE"])
        self.__peripheral.write(msg)

        # 编队起飞
        # "所有无人机以 X[distance]Y[distance2]为中心 [Rotate]环绕[distance3]°[clour]",

    def BD_around(self, distance: int, distance2: int, distance3: int, rotate: Rotate, color: Color):
        msg = " ".join(["AA FA C7 FF", hex_str("%04X" % distance, 4), hex_str("%04X" % distance2, 4),
                        hex_str("%04X" % distance3, 4), rotate.value, color.value, "FE"])
        self.__peripheral.write(msg)

        # 编队结束

    def BD_end(self):
        msg = "AA FA CE 00 00 00 00 00 00 00 00 00 FE"
        self.__peripheral.write(msg)







