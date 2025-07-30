import tkinter as tk
from functools import wraps
from tkinter import filedialog, messagebox, ttk


def gui(title="", width=600, height=400, input_filter=None, output_filter=None):
    """
    input_filter: 输入文件类型过滤器，默认为 [("Excel files", "*.xls *.xlsx")]
    output_filter: 输出文件类型过滤器，默认为 [("Excel files", "*.xlsx")]
    """

    if input_filter is None:
        input_filter = [("Excel files", "*.xls *.xlsx")]
    if output_filter is None:
        output_filter = [("Excel files", "*.xlsx")]

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            class GUIAPP:
                def __init__(self, root):
                    self.root = root
                    self.root.title(title)
                    self.root.geometry(f"{width}x{height}")
                    self.root.resizable(True, True)

                    self.style = ttk.Style()
                    self.style.configure("TLabel", font=("SimHei", 10))
                    self.style.configure("TButton", font=("SimHei", 10))

                    self.input_path = tk.StringVar()
                    self.output_path = tk.StringVar()
                    self.status = tk.StringVar(value="就绪")

                    self.create_widgets()

                def create_widgets(self):
                    main_frame = ttk.Frame(self.root, padding="20")
                    main_frame.pack(fill=tk.BOTH, expand=True)

                    ttk.Label(main_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
                    input_frame = ttk.Frame(main_frame)
                    input_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
                    ttk.Entry(input_frame, textvariable=self.input_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
                    ttk.Button(
                        input_frame,
                        text="浏览...",
                        command=self.browse_input_file,
                    ).pack(side=tk.LEFT, padx=5)

                    ttk.Label(main_frame, text="输出文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
                    output_frame = ttk.Frame(main_frame)
                    output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
                    ttk.Entry(output_frame, textvariable=self.output_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
                    ttk.Button(
                        output_frame,
                        text="浏览...",
                        command=self.browse_output_file,
                    ).pack(side=tk.LEFT, padx=5)

                    button_frame = ttk.Frame(main_frame)
                    button_frame.grid(row=2, column=0, columnspan=2, pady=20)
                    ttk.Button(
                        button_frame,
                        text="开始处理",
                        command=self.process_excel,
                        style="Accent.TButton",
                    ).pack(padx=5, pady=5)

                    ttk.Label(main_frame, text="状态:").grid(row=3, column=0, sticky=tk.W, pady=5)
                    ttk.Label(main_frame, textvariable=self.status).grid(row=3, column=1, sticky=tk.W, pady=5)

                    ttk.Label(main_frame, text="处理日志:").grid(row=5, column=0, sticky=tk.NW, pady=5)
                    log_frame = ttk.Frame(main_frame)
                    log_frame.grid(row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
                    self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10, width=50)
                    self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    self.log_text.config(yscrollcommand=scrollbar.set)

                    # 设置列权重，使界面更美观
                    main_frame.columnconfigure(1, weight=1)
                    main_frame.rowconfigure(5, weight=1)

                def browse_input_file(self):
                    filename = filedialog.askopenfilename(
                        title="选择输入文件",
                        filetypes=input_filter,
                    )
                    if filename:
                        self.input_path.set(filename)

                def browse_output_file(self):
                    filename = filedialog.asksaveasfilename(
                        title="选择输出文件",
                        defaultextension=".xlsx",
                        filetypes=output_filter,
                    )
                    if filename:
                        self.output_path.set(filename)

                def log(self, message):
                    if message is None:
                        return
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, message + "\n")
                    self.log_text.see(tk.END)
                    self.root.update_idletasks()
                    self.log_text.config(state=tk.DISABLED)

                def process_excel(self):
                    self.log_text.delete(1.0, tk.END)
                    input_file = self.input_path.get()
                    output_file = self.output_path.get()

                    if not input_file:
                        messagebox.showerror("错误", "请选择输入文件")
                        return
                    if not output_file:
                        messagebox.showerror("错误", "请选择输出文件")
                        return

                    try:
                        self.log("开始处理Excel文件...")

                        process_gen = f(input_file, output_file)
                        for log_msg in process_gen:
                            self.log(log_msg)

                        self.log(f"处理完成！文件已保存至 {output_file}")
                        messagebox.showinfo("成功", f"Excel文件处理完成！\n保存路径: {output_file}")
                    except Exception as e:
                        self.log(f"错误: {e!s}")
                        messagebox.showerror("处理失败", f"发生错误: {e!s}")

            root = tk.Tk()
            _ = GUIAPP(root)
            root.mainloop()

        return wrapper

    return decorator


if __name__ == "__main__":

    @gui(title="The Title")
    def run(input_file=None, output_file=None):
        yield input_file
        yield output_file

    run()
