import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import subprocess
import os
import shutil
class DriizzyyCompilerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Driizzyy's Python Compiler")
        self.root.geometry("700x500")
        self.file_list = []
        self.onefile = tk.BooleanVar(value=True)
        self.noconsole = tk.BooleanVar(value=False)
        self.output_dir = tk.StringVar(value=os.path.abspath("dist"))
        self.icon_path = tk.StringVar(value="")
        self.exe_name = tk.StringVar(value="output")
        self.build_ui()
    def build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill='both', expand=True)
        ttk.Label(frm, text="Selected Python Files:").pack(anchor='w')
        self.filebox = tk.Listbox(frm, height=5)
        self.filebox.pack(fill='x')
        btns = ttk.Frame(frm)
        btns.pack(fill='x', pady=4)
        ttk.Button(btns, text="Add .py File", command=self.add_file).pack(side='left', padx=2)
        ttk.Button(btns, text="Clear Files", command=self.clear_files).pack(side='left', padx=2)
        ttk.Checkbutton(frm, text="Bundle into One File (--onefile)", variable=self.onefile).pack(anchor='w')
        ttk.Checkbutton(frm, text="Hide Console Window (--noconsole)", variable=self.noconsole).pack(anchor='w')
        adv = ttk.LabelFrame(frm, text="Advanced")
        adv.pack(fill='x', pady=10)
        out_frame = ttk.Frame(adv)
        out_frame.pack(fill='x', pady=3)
        ttk.Label(out_frame, text="Output Folder:").pack(anchor='w')
        ttk.Entry(out_frame, textvariable=self.output_dir, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(out_frame, text="Browse", command=self.choose_output_dir).pack(side='right')
        icon_frame = ttk.Frame(adv)
        icon_frame.pack(fill='x', pady=3)
        ttk.Label(icon_frame, text="EXE Icon (optional):").pack(anchor='w')
        ttk.Entry(icon_frame, textvariable=self.icon_path, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(icon_frame, text="Browse", command=self.choose_icon).pack(side='right')
        name_frame = ttk.Frame(adv)
        name_frame.pack(fill='x', pady=3)
        ttk.Label(name_frame, text="EXE Name:").pack(anchor='w')
        ttk.Entry(name_frame, textvariable=self.exe_name).pack(fill='x')
        ttk.Button(frm, text="Compile", command=self.compile).pack(pady=8)
        ttk.Label(frm, text="Build Log:").pack(anchor='w', pady=(8, 0))
        self.log = scrolledtext.ScrolledText(frm, height=10, state='disabled')
        self.log.pack(fill='both', expand=True)
    def add_file(self):
        files = filedialog.askopenfilenames(filetypes=[("Python files", "*.py")])
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self.filebox.insert(tk.END, f)
    def clear_files(self):
        self.file_list = []
        self.filebox.delete(0, tk.END)
    def choose_output_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir.set(folder)
    def choose_icon(self):
        icon = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
        if icon:
            self.icon_path.set(icon)
    def log_output(self, text):
        self.log.configure(state='normal')
        self.log.insert(tk.END, text + "\n")
        self.log.configure(state='disabled')
        self.log.see(tk.END)
    def compile(self):
        if not self.file_list:
            messagebox.showerror("Error", "No Python files selected.")
            return
        if len(self.file_list) > 1:
            messagebox.showwarning("Note", "Only the first file will be compiled as entry point.")
        pyinstaller = shutil.which("pyinstaller")
        if not pyinstaller:
            messagebox.showerror("Missing PyInstaller", "Please install pyinstaller using pip.")
            return
        entry = self.file_list[0]
        output_name = self.exe_name.get().strip()
        if not output_name:
            messagebox.showerror("Invalid Name", "EXE name cannot be empty.")
            return
        cmd = [
            pyinstaller,
            "--name", output_name,
            "--distpath", self.output_dir.get(),
            "--workpath", "build",
            "--specpath", "specs"
        ]
        if self.onefile.get():
            cmd.append("--onefile")
        if self.noconsole.get():
            cmd.append("--noconsole")
        if self.icon_path.get():
            cmd.extend(["--icon", self.icon_path.get()])
        cmd.append(entry)
        self.log_output(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=False)
            self.log_output("✅ Build completed.")
            messagebox.showinfo("Success", f"Build completed.\nOutput: {self.output_dir.get()}")
        except subprocess.CalledProcessError as e:
            self.log_output("❌ Build failed.")
            messagebox.showerror("Error", f"Build failed.\n\n{e}")
def launch_gui():
    gui = DriizzyyCompilerGUI()
    gui.root.mainloop()