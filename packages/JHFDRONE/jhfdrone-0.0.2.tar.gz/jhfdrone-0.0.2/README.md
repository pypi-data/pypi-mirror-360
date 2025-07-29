# Description 
A python package for UAV control designed by JHFDRONE
# Function list of JHFDRONE
# 打开串口
> start() 
# 关闭串口
> stop()
# 颜色判断 
> get_current_color()
# 获取电压 
> get_current_vcc()
# 获取高度 
> get_current_height()
# 获取二维码编号 
> get_id_qr_code()
# 获取版本号 
> get_version()
# 获取信号强度 
> get_wifi_strength()
# 获取openmv模式
> get_mode_open_mv()
# 获取前方距离 TOF测距（前）cm
> get_data_ultrason_front()
# 获取后方距离 TOF测距（后）cm
> get_data_ultrason_back()
# 获取左方距离 TOF测距（左）cm
> get_data_ultrason_left()
# 获取右方距离 TOF测距（右）cm
> get_data_ultrason_right()
# 获取下方距离 TOF测距（下）cm
> get_data_ultrason_down()
# 相对于[distance]号标签清除误差
> current_location(distance)
# 解锁怠速
> Unlock_uav() 
# 初始化 
> init_uav()  
# 起飞[distance]cm
> take_off(distance) 

# 设置飞行速度[speed]
> set_speed(speed) 

# 移动 --- 向 [direction] 飞[distance]cm
>move_Ctrl_cm(direction, distance) 

# 时间移动 --- 向 [direction] 飞[time]*0.01(秒)
>move_Ctrl_time(direction, time) 

# 斜线移动 --- 向[QH][qh_num][ZY][zy_num][SX][sx_num](厘米)
>move_slash(qh, qh_num, zy, zy_num, sx, sx_num) 

# 旋转 --- [rotate]旋转[degree]度
> rotate(rotate, degree) 

# 环绕 ---  以无人机[QH][distance]cm  [ZY][distance2]cm为中心 [rotate_direction]环绕[degree]°  用时[time]秒
> fly_surround(qh, distance, zy, distance2, rotate_direction, degree,  time) 

# 灯光控制 --- 设置飞机大灯[color]色[mode]
> set_light(color, mode) 
# 4D翻滚[direction]
>flip(direction)
# [mode]降落——[speed]速度
> landing(mode, speed) 

# 拍一张照片照
> take_photo()
# 激光定高[status]
> set_laser(status)
# 定位模式[status]
> set_relocation(status)
# 红外发射 --- 发射红外数据[status]
> emit_appoint_data(status)

# 红外发射 --- 发射红外数据[data]
> emit_data(data)

# 发射红外点阵 --- 红外点阵显示[color]色单个字符[nb_characters]
> display_lattice(color, nb_characters) 

# 数据回传[status]
> DATA_return(status)
# 电磁铁[status]
> set_BM(status) 

# 舵机[degree]°
> set_Servo(degree) 

# 机械手[degree]°
> set_hand(degree)

# 激光 --- 发射激光
> emit_laser()

# 循线方向 --- 向[direction]循线飞行
> Traverse_uav(direction)

# 颜色定位 --- 定位颜色[color]
> point_color(color)
# 二维码模式 --- 切换为[mode]模式
>change_mode(mode):

# 标签间距，根据实际场地调整，单位cm --- 二维码标签间距[distance]cm
> set_spacing(distance)

# 期望标签 --- 飞向[distance]标签，高度[height]
> fly_ID(distance, height) 

# 定点当前标签，高度[height]cm
> fly_now_id(height)

# 定点当前颜色块，高度[height]cm
> fly_now_color(height) 

# 颜色偏差---默认定位在[color][qh]方[nb_pixels]像素
>point_location(color, qh, nb_pixels) 

# 角度校准---飞机航向校准
>calibration() 

# Example
```
# get all avilable serial port
port_name = find_serial_port()
if len(port_name) > 0:
    # creat a peripheral linking to the first available serial port
    peripheral = Peripheral(port_name[0])
    # creat a JHFDRONE object 
    drone = JHFDRONE(peripheral)
    # open the serial port
    drone.start()
    # send the instruction to initialize the tuxing uav
    drone.init_uav()
    # close the serial port
    drone.stop()
```