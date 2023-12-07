import datetime
import re
from dataclasses import dataclass
from enum import Enum
from tkinter import messagebox
from typing import List

import customtkinter


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
            case UT.H:
                self.second = self.input_n * 60 * 60
            case UT.M:
                self.second = self.input_n * 60
            case UT.S:
                self.second = self.input_n


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

clock_list: List[TimeItem] = []


class ConfigFrame(customtkinter.CTkFrame):
    """
    配置窗口
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.name = customtkinter.CTkLabel(self, text="配置向导")
        self.name.grid(column=0, row=0)
        # 表头
        self.add_button = customtkinter.CTkButton(master=self, text="+", fg_color="transparent", border_width=2,
                                                  text_color=("gray10", "#DCE4EE"), command=self.add_column)
        self.add_button.grid(column=0, row=1, padx=10, pady=(0, 20))

        self.table_title = customtkinter.CTkLabel(self, text="标签")
        self.table_title.grid(column=0, row=2, padx=10, pady=(0, 20))
        self.table_num = customtkinter.CTkLabel(self, text="时间")
        self.table_num.grid(column=1, row=2, padx=10, pady=(0, 20))
        self.table_unit = customtkinter.CTkLabel(self, text="单位")
        self.table_unit.grid(column=2, row=2, padx=10, pady=(0, 20))
        self.table_fullscreen = customtkinter.CTkLabel(self, text="全屏")
        self.table_fullscreen.grid(column=3, row=2, padx=10, pady=(0, 20))
        # 长亮
        self.ok = customtkinter.CTkButton(self, text="创建计时", command=self.submit)
        self.ok.grid(column=100, row=100)

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

    def submit(self):
        if len(clock_list) == 0:
            messagebox.showerror(message="")
        else:
            time_frame = TimerFrame(master=self.master)
            time_frame.grid(row=0, column=0, sticky="nsew")


class TimerFrame(customtkinter.CTkFrame):
    """
    倒计时窗口
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.time_label = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.time_label.grid(row=1, column=1, padx=20, pady=(20, 20))
        self.end_time = None
        # 计时次数
        self.clock_num = None
        # 处理时序的索引
        self.clock_list_index = 0
        self.stop_button = customtkinter.CTkButton(self, text="stop", command=self.stop_time)
        self.stop_button.grid(row=2, column=1, padx=20, pady=(20, 20))
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

    def stop_time(self):
        """
        停止时间
        :return:
        """
        r = messagebox.askokcancel(message="停止后将无法继续，是否停止")
        if r:
            self.destroy()
        else:
            pass


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.config_frame = ConfigFrame(master=self)
        self.config_frame.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
