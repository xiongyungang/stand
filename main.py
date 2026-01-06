import tkinter as tk
import threading
import time
import pystray
from PIL import Image, ImageDraw
import sys


class ReminderApp:
    def __init__(self, root, interval_seconds=1800, message="时间到啦！休息一下~"):
        self.root = root
        self.root.title("周期提醒器")
        self.root.geometry("300x230")
        self.root.resizable(False, False)

        self.interval = interval_seconds
        self.message = message
        self.running = False
        self.remaining = interval_seconds
        self.is_waiting_for_input = False

        self.tray_icon = None  # 系统托盘图标对象

        # 绑定窗口最小化事件
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.bind("<Unmap>", self.on_minimize)

        # 标题
        tk.Label(root, text="周期提醒器", font=("微软雅黑", 14)).pack(pady=5)

        # 时间设置
        tk.Label(root, text="间隔时间（秒）:").pack()
        self.interval_var = tk.StringVar(value=str(interval_seconds))
        tk.Entry(root, textvariable=self.interval_var).pack()

        # 提醒内容
        tk.Label(root, text="提醒内容:").pack()
        self.msg_var = tk.StringVar(value=message)
        tk.Entry(root, textvariable=self.msg_var).pack()

        # 倒计时
        self.countdown_label = tk.Label(root, text="剩余: -- 秒", font=("微软雅黑", 12), fg="blue")
        self.countdown_label.pack(pady=5)

        # 提示信息
        self.reminder_label = tk.Label(root, text="", font=("微软雅黑", 12), fg="red")
        self.reminder_label.pack(pady=5)

        # 控制按钮框
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)
        tk.Button(control_frame, text="开始提醒", command=self.start, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="停止提醒", command=self.stop, width=10).pack(side=tk.LEFT, padx=5)

        # 提醒阶段按钮框
        self.action_frame = tk.Frame(root)
        self.action_frame.pack(pady=5)

    def create_tray_icon(self):
        """创建托盘图标"""
        if self.tray_icon is not None:
            return  # 已经有图标了

        # 创建一个简单的图标
        img = Image.new('RGB', (64, 64), color=(0, 128, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 0))

        menu = pystray.Menu(
            pystray.MenuItem("显示", self.show_window),
            pystray.MenuItem("退出", self.quit_app)
        )
        self.tray_icon = pystray.Icon("reminder", img, "周期提醒器", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def on_minimize(self, event):
        """最小化时隐藏窗口"""
        if self.root.state() == "iconic":
            self.hide_window()

    def hide_window(self):
        """隐藏主窗口并创建托盘图标"""
        self.root.withdraw()
        self.create_tray_icon()

    def show_window(self, icon=None, item=None):
        """恢复主窗口"""
        self.root.deiconify()
        self.root.state("normal")
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def quit_app(self, icon=None, item=None):
        """退出程序"""
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit()

    def reminder_loop(self):
        self.remaining = self.interval
        while self.running:
            if not self.is_waiting_for_input:  # 倒计时阶段
                self.countdown_label.config(text=f"剩余: {self.remaining} 秒")
                if self.remaining <= 0:
                    self.show_reminder()
                time.sleep(1)
                self.remaining -= 1
            else:
                time.sleep(0.1)  # 等待用户点击继续/停止

    def show_reminder(self):
        self.is_waiting_for_input = True
        self.reminder_label.config(text=self.message, fg="red")
        self.countdown_label.config(text="剩余: 0 秒")

        # 清空并添加“继续/停止”按钮
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        tk.Button(self.action_frame, text="继续", width=10, command=self.continue_cycle).pack(side=tk.LEFT, padx=10)
        tk.Button(self.action_frame, text="停止", width=10, command=self.stop).pack(side=tk.LEFT, padx=10)

        # 窗口置顶
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(500, lambda: self.root.attributes('-topmost', False))

    def continue_cycle(self):
        self.is_waiting_for_input = False
        self.remaining = self.interval
        self.reminder_label.config(text="")
        for widget in self.action_frame.winfo_children():
            widget.destroy()

    def start(self):
        try:
            self.interval = int(self.interval_var.get())
            self.message = self.msg_var.get()
            self.hide_window()
        except ValueError:
            self.reminder_label.config(text="请输入正确的数字！", fg="red")
            return

        if not self.running:
            self.running = True
            self.is_waiting_for_input = False
            threading.Thread(target=self.reminder_loop, daemon=True).start()
            self.reminder_label.config(text="提醒已开始", fg="green")
        else:
            if self.is_waiting_for_input:
                self.continue_cycle()

    def stop(self):
        self.running = False
        self.reminder_label.config(text="提醒已停止", fg="gray")
        self.countdown_label.config(text="剩余: -- 秒")


if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root, interval_seconds=1800)
    root.mainloop()
