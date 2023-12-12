import configparser
import datetime
import re
import sys, os
from dataclasses import dataclass, asdict
from enum import Enum
from tkinter import messagebox
from typing import List

import customtkinter
from PIL import Image


class UT(Enum):
    H = "小时"
    M = "分钟"
    S = "秒"


@dataclass
class TimeItem:
    units: UT
    input_n: int
    desc: str
    is_fullscreen: bool = False

    def __post_init__(self):
        self.input_n = int(self.input_n)
        match self.units:
            case UT.H | "UT.H":
                self.second = self.input_n * 60 * 60
                self.units = UT.H
            case UT.M | "UT.M":
                self.second = self.input_n * 60
                self.units = UT.M
            case UT.S | "UT.S":
                self.second = self.input_n
                self.units = UT.S


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

clock_list: List[TimeItem] = []

config = configparser.ConfigParser()


def resource(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class ConfigFrame(customtkinter.CTkFrame):
    """
    配置窗口
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.name = customtkinter.CTkLabel(self, text="配置向导", font=("", 32))
        self.name.grid(column=0, row=0, columnspan=4, padx=20, pady=20, sticky="nsew")
        # 表头
        self.table_title = customtkinter.CTkLabel(self, text="标签")
        self.table_title.grid(column=0, row=2, padx=20, pady=20, sticky="nsew")
        self.table_num = customtkinter.CTkLabel(self, text="时间")
        self.table_num.grid(column=1, row=2, padx=20, pady=20, sticky="nsew")
        self.table_unit = customtkinter.CTkLabel(self, text="单位")
        self.table_unit.grid(column=2, row=2, padx=20, pady=20, sticky="nsew")
        self.table_fullscreen = customtkinter.CTkLabel(self, text="模式")
        self.table_fullscreen.grid(column=3, row=2, padx=20, pady=20, sticky="nsew")
        self.add_button = customtkinter.CTkButton(master=self, text="添加", fg_color="transparent", border_width=2,
                                                  text_color=("gray10", "#DCE4EE"), command=self.add_column)
        self.add_button.grid(column=0, row=1000, columnspan=2, pady=20)
        self.save_button = customtkinter.CTkButton(master=self, text="保存", fg_color="transparent", border_width=2,
                                                   text_color=("gray10", "#DCE4EE"), command=self.save_config)
        self.save_button.grid(column=2, row=1000, columnspan=2, pady=20)

        self.list_show()

    def list_show(self):
        for i, v in enumerate(clock_list):
            entry = customtkinter.CTkLabel(self, text=v.desc)
            entry.grid(column=0, row=3 + i, padx=10, pady=(0, 20))
            entry = customtkinter.CTkLabel(self, text=v.input_n)
            entry.grid(column=1, row=3 + i, padx=10, pady=(0, 20))
            units = customtkinter.CTkLabel(self, text=v.units.value)
            units.grid(column=2, row=3 + i, padx=10, pady=(0, 20))
            is_fullscreen = customtkinter.CTkLabel(self, text="全屏" if v.is_fullscreen else "窗口")
            is_fullscreen.grid(column=3, row=3 + i, padx=10, pady=(0, 20))

    def save_config(self):
        user_dir = os.path.expanduser('~')

        if not os.path.exists(os.path.join(user_dir, '.config')):
            os.mkdir(os.path.join(user_dir, '.config'))
        if len(clock_list) == 0:
            messagebox.showerror(message="没有任何配置")
            return
        for i, v in enumerate(clock_list):
            config[f'default{i}'] = asdict(v)
        with open(os.path.join(user_dir, '.config', 'time_loop_lconfig.ini'), 'w') as f:
            config.write(f)
        messagebox.showinfo("保存成功")

    def add_column(self):
        """
        添加计时
        :return:
        """

        def save():
            clock_list.append(TimeItem(desc=entry.get(), input_n=num.get(), units=UT(unit.get()),
                                       is_fullscreen=bool(is_fullscreen.get())))
            dialog.destroy()
            self.list_show()
            self.master.refresh_control(0)

        dialog = customtkinter.CTkToplevel()
        dialog.geometry("300x200")
        dialog.wm_attributes('-topmost', True)
        label_entry = customtkinter.CTkLabel(dialog, text="标签")
        label_entry.grid(column=0, row=5)
        entry = customtkinter.CTkEntry(dialog, placeholder_text="")
        entry.grid(column=1, row=5)
        label_num = customtkinter.CTkLabel(dialog, text="时间")
        label_num.grid(column=0, row=10)
        num = customtkinter.CTkEntry(dialog, validate='all',
                                     validatecommand=(self.master.register(self.check_num), '%P'))
        num.grid(column=1, row=10)

        label_unit = customtkinter.CTkLabel(dialog, text="单位")
        label_unit.grid(column=0, row=15)
        unit = customtkinter.CTkComboBox(dialog, values=[UT.S.value, UT.M.value, UT.H.value])
        unit.grid(column=1, row=15)

        label_fullscreen = customtkinter.CTkLabel(dialog, text="全屏")
        label_fullscreen.grid(column=0, row=20)
        is_fullscreen = customtkinter.CTkCheckBox(dialog, text="", )
        is_fullscreen.grid(column=1, row=20)

        ok = customtkinter.CTkButton(dialog, text="保存", command=save)
        ok.grid(column=0, row=25)
        cancel = customtkinter.CTkButton(dialog, text="取消", command=dialog.destroy)
        cancel.grid(column=1, row=25)

    @staticmethod
    def check_num(num):
        return re.match('^[0-9]*$', num) is not None and len(num) <= 5


class TimerFrame(customtkinter.CTkFrame):
    """
    倒计时窗口
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # self.time_area = customtkinter.CTkFrame(self)
        # self.time_area.pack()

        self.time_label = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.time_label.grid(row=0, column=0)
        self.end_time = None
        # 计时次数
        self.clock_num = None
        # 处理时序的索引
        self.clock_list_index = 0
        self.update_clock()

    def update_clock(self):
        end_time = self.get_end_time()
        if clock_list[self.clock_list_index].is_fullscreen:
            self.master.wm_attributes('-fullscreen', True)
            self.time_label.configure(font=customtkinter.CTkFont(size=250, weight="bold"))
        else:
            self.master.wm_attributes('-fullscreen', False)
            self.time_label.configure(font=customtkinter.CTkFont(size=20, weight="bold"))
        if end_time < datetime.datetime.now():
            s = messagebox.askokcancel(message=f"{clock_list[self.clock_list_index].desc} stopped",
                                       parent=self)
            self.end_time = None
            if not s:
                self.master.refresh_control(0)
                return

        remaining_time = datetime.datetime.utcfromtimestamp((end_time - datetime.datetime.now()).seconds)
        self.time_label.configure(text=remaining_time.strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def get_end_time(self) -> datetime:
        if not self.end_time:
            self.get_clock_index()
            self.end_time = datetime.datetime.now() + datetime.timedelta(
                seconds=clock_list[self.clock_list_index].second)
            return self.end_time
        return self.end_time

    def get_clock_index(self):
        len_clock = len(clock_list)
        if len_clock <= 0:
            raise Exception("没有时间")
        if self.clock_num is None:
            self.clock_num = 0
        else:
            self.clock_num += 1
            self.clock_list_index = self.clock_num if self.clock_num < len_clock else self.clock_num % len_clock


class ControlFrame(customtkinter.CTkFrame):
    """
    控制
    """

    def __init__(self, master, state: int, **kwargs):
        super().__init__(master, **kwargs)

        self.ff = customtkinter.CTkFrame(self)
        self.ff.pack()

        self.state = state  # 0未开始 1正在运行
        self.time_frame = None

        self.img_play = customtkinter.CTkImage(light_image=Image.open(resource("static/play.png")).resize((18, 18)),
                                               dark_image=Image.open(resource("static/play.png")).resize((18, 18)),
                                               size=(18, 18))
        self.img_stop = customtkinter.CTkImage(light_image=Image.open(resource("static/stop.png")).resize((18, 18)),
                                               dark_image=Image.open(resource("static/stop.png")).resize((18, 18)),
                                               size=(18, 18))
        self.img_pause = customtkinter.CTkImage(light_image=Image.open(resource("static/pause.png")).resize((18, 18)),
                                                dark_image=Image.open(resource("static/pause.png")).resize((18, 18)),
                                                size=(18, 18))
        if state == 0 and len(clock_list) != 0:
            self.start_button = customtkinter.CTkButton(self.ff, text="", width=18, height=18, image=self.img_play,
                                                        fg_color="transparent", hover_color="green",
                                                        command=self.start)
            self.start_button.grid(row=0, column=0)
        else:
            # self.pause_button = customtkinter.CTkButton(self.ff, text="", width=18, height=18, image=self.img_pause,
            #                                             fg_color="transparent", hover_color="orange",
            #                                             command=self.pause)
            # self.pause_button.grid(row=0, column=0, padx=20, pady=20, sticky="nsew", )
            self.end_button = customtkinter.CTkButton(self.ff, text="", width=18, height=18, image=self.img_stop,
                                                      fg_color="transparent", hover_color="red", command=self.stop)
            self.end_button.grid(row=0, column=1)

    def start(self):
        assert self.state == 0
        if len(clock_list) == 0:
            messagebox.showerror(message="未填写配置")
        else:
            self.master.refresh_control(1)

    def pause(self):
        pass

    def stop(self):
        assert self.state == 1
        r = messagebox.askokcancel(message="停止后将无法继续，是否停止")
        if r:
            self.master.refresh_control(0)
            self.master.wm_attributes('-fullscreen', False)
        else:
            pass


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.title("Time Loop")
        self.iconbitmap(resource("static/icon.ico"))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.control_frame = None
        self.time_frame = None
        self.config_frame = None

        self.read_config()
        self.init_frame()
        self.refresh_control(0)

    def read_config(self):
        return
        # user_dir = os.path.expanduser('~')
        #
        # if not os.path.exists(os.path.join(user_dir, '.config')):
        #     return
        #
        # config.read(os.path.join(user_dir, '.config', 'time_loop_lconfig.ini'))
        # for c in config.sections():
        #     clock_list.append(TimeItem(units=config[c].get("units"), input_n=config[c].getint("input_n"),
        #                                desc=config[c]["desc"],
        #                                is_fullscreen=config[c].getboolean("is_fullscreen")))

    def init_frame(self):
        self.config_frame = ConfigFrame(master=self)
        self.config_frame.grid(row=0, column=0)

    def refresh_control(self, state: int):
        """
        :param state:0 未开始 1 运行中
        :return:
        """
        if len(clock_list) != 0:
            self.control_frame = ControlFrame(master=self, state=state)
            self.control_frame.grid(row=6, sticky="s")
        if state == 1:
            # 运行中 开始计时 ，并变化按钮
            self.control_frame = ControlFrame(master=self, state=state)
            self.control_frame.grid(row=6, sticky="s")

            self.config_frame.destroy()
            self.control_frame = None
            self.time_frame = TimerFrame(master=self.master, fg_color="transparent")
            self.time_frame.grid(row=0, column=0)

        elif self.time_frame and state == 0:
            self.init_frame()
            self.time_frame.destroy()
            self.time_frame = None
        else:
            pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
