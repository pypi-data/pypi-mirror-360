import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import threading
from functools import wraps
from robot.libdocpkg import LibraryDocumentation
from robot.libraries.BuiltIn import BuiltIn
import tkinter as tk
from tkinter import ttk




class SimpleRetryGUI:
    def __init__(self, core):
        self.core = core
        core.gui_controller = self
        self._lock = threading.Lock()
        self.root = tk.Tk()
        self.root.title("Robot Framework Debugger")
        self.root.geometry("900x700")
        self.root.minsize(850, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.libraries = {}
        self.library_names = []
        self._setup_ui()
        self.root.withdraw()

    def _thread_safe(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self._lock:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: func(self, *args, **kwargs))
        return wrapper

    def _setup_ui(self):
        # === Failure Info Panel ===
        self.failure_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10)
        self.failure_text.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.failure_text.config(state=tk.DISABLED)

        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.grid(row=1, column=0, sticky="ew", padx=10)

        # === Sub-tabs for Retry and Custom Keyword ===
        self.sub_tabs = tk.ttk.Notebook(self.root)
        self.sub_tabs.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.root.rowconfigure(2, weight=1)

        self.retry_tab = tk.Frame(self.sub_tabs)
        self.custom_tab = tk.Frame(self.sub_tabs)
        self.sub_tabs.add(self.retry_tab, text="Retry Failed Keyword")
        self.sub_tabs.add(self.custom_tab, text="Run Custom Keyword")

        self._setup_retry_tab()
        self._setup_custom_tab()

    # === RETRY TAB ===
    def _setup_retry_tab(self):
        self.args_frame = tk.LabelFrame(self.retry_tab, text="Edit Keyword Arguments", padx=5, pady=5)
        self.args_frame.pack(fill=tk.X, padx=5, pady=5)

        buttons_frame = tk.Frame(self.retry_tab)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        self.retry_btn = tk.Button(buttons_frame, text="Retry and Continue", command=self._on_retry_and_continue)
        self.retry_btn.pack(side=tk.LEFT, padx=5)

        self.add_arg_btn = tk.Button(buttons_frame, text="+ Add Arg", command=self._on_add_argument)
        self.add_arg_btn.pack(side=tk.LEFT, padx=5)

        self.skip_btn = tk.Button(buttons_frame, text="Skip Test", command=self._on_skip_test, bg="#FFA500")
        self.skip_btn.pack(side=tk.LEFT, padx=5)

        self.abort_btn = tk.Button(buttons_frame, text="Abort Suite", command=self._on_abort_suite, bg="#FF6347")
        self.abort_btn.pack(side=tk.RIGHT, padx=5)

    # === CUSTOM EXECUTOR TAB ===
    def _setup_custom_tab(self):
        self.library_var = tk.StringVar()
        self.keyword_var = tk.StringVar()
        self.command_var = tk.StringVar()
        # self.result_var = tk.StringVar()

        selector_frame = tk.Frame(self.custom_tab)
        selector_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(selector_frame, text="Library:").pack(side=tk.LEFT)
        self.library_dropdown = ttk.Combobox(selector_frame, textvariable=self.library_var, state="readonly")
        self.library_dropdown.pack(side=tk.LEFT, padx=5)

        tk.Label(selector_frame, text="Keyword:").pack(side=tk.LEFT)
        self.keyword_dropdown = ttk.Combobox(selector_frame, textvariable=self.keyword_var, state="readonly")
        self.keyword_dropdown.pack(side=tk.LEFT, padx=5)

        self.library_dropdown.bind("<<ComboboxSelected>>", self._on_library_selected)
        self.keyword_dropdown.bind("<<ComboboxSelected>>", self._on_keyword_selected)

        self.custom_args_frame = tk.LabelFrame(self.custom_tab, text="Keyword Arguments")
        self.custom_args_frame.pack(fill=tk.X, padx=10, pady=5)

        btn_frame = tk.Frame(self.custom_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Execute", command=self._execute_command).pack(side=tk.LEFT)
        # self.result_display = tk.Label(btn_frame, textvariable=self.result_var, fg='green')

        # self.result_display.pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="+ Add Arg", command=self._add_custom_argument_field).pack(side=tk.LEFT, padx=5)

        doc_frame = tk.LabelFrame(self.custom_tab, text="Keyword Documentation", padx=5, pady=5)
        doc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.doc_display = scrolledtext.ScrolledText(doc_frame, wrap=tk.WORD)
        self.doc_display.pack(fill=tk.BOTH, expand=True)
        self.doc_display.config(state=tk.DISABLED)

    def _on_library_selected(self, event=None):
        lib = self.library_var.get()
        if lib not in self.libraries:
            return
        self.keyword_dropdown['values'] = [kw['name'] for kw in self.libraries[lib]]
        if self.keyword_dropdown['values']:
            self.keyword_var.set(self.keyword_dropdown['values'][0])
            self._on_keyword_selected()

    def _on_keyword_selected(self, event=None):
        lib = self.library_var.get()
        kw_name = self.keyword_var.get()

        if not lib or not kw_name:
            return

        if lib in self.libraries:
            for kw in self.libraries[lib]:
                if kw['name'] == kw_name:
                    self._populate_custom_args_editor(kw['args'])

                    # ✅ Show signature
                    args_text = ", ".join(
                        a.name if hasattr(a, "name") else str(a)
                        for a in kw['args']
                    )
                    signature = f"{kw_name}({args_text})"
                    self.command_var.set(signature)

                    # ✅ Show doc
                    self.doc_display.config(state=tk.NORMAL)
                    self.doc_display.delete("1.0", tk.END)
                    self.doc_display.insert(tk.END, f"{kw_name}\n\nSignature:\n{signature}\n\nDoc:\n{kw['doc']}")
                    self.doc_display.config(state=tk.DISABLED)
                    break

    def _populate_custom_args_editor(self, args):
        for widget in self.custom_args_frame.winfo_children():
            widget.destroy()
        self.custom_arg_vars = []

        for i, arg in enumerate(args or []):
            if hasattr(arg, "name"):
                name = arg.name
                default = getattr(arg, "default", None)
            else:
                name = str(arg)
                default = None

            label = f"{name}" if default is None else f"{name} (default={default})"
            var = tk.StringVar(value=str(default) if default is not None else "")

            frame = tk.Frame(self.custom_args_frame)
            frame.pack(anchor='w', pady=2, fill='x')

            tk.Label(frame, text=f"{label}:").pack(side='left')
            entry = tk.Entry(frame, textvariable=var, width=60)
            entry.pack(side='left', padx=5)
            tk.Button(frame, text="–", command=lambda f=frame: self._remove_custom_argument_field(f)).pack(side='left')

            # Optional tooltip for extra polish
            def create_tooltip(widget, text):
                tip = None

                def on_enter(event):
                    nonlocal tip
                    tip = tk.Toplevel(widget)
                    tip.wm_overrideredirect(True)
                    x = widget.winfo_rootx() + 20
                    y = widget.winfo_rooty() + 20
                    tip.geometry(f"+{x}+{y}")
                    tk.Label(tip, text=text, background="lightyellow", relief='solid', borderwidth=1).pack()

                def on_leave(event):
                    nonlocal tip
                    if tip:
                        tip.destroy()

                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

            create_tooltip(entry, label)
            self.custom_arg_vars.append(var)

        # self._add_custom_argument_field()  # start with one empty field

    def _add_custom_argument_field(self, value=""):
        var = tk.StringVar(value=str(value))
        frame = tk.Frame(self.custom_args_frame)
        frame.pack(anchor='w', pady=2, fill='x')
        tk.Label(frame, text=f"Arg {len(self.custom_arg_vars) + 1}:").pack(side='left')
        tk.Entry(frame, textvariable=var, width=60).pack(side='left', padx=2)
        tk.Button(frame, text="–", command=lambda f=frame: self._remove_custom_argument_field(f)).pack(side='left')
        self.custom_arg_vars.append(var)

    def _remove_custom_argument_field(self, frame):
        idx = list(self.custom_args_frame.children.values()).index(frame)
        frame.destroy()
        del self.custom_arg_vars[idx]

    def _execute_command(self):
        lib = self.library_var.get()
        kw = self.keyword_var.get()

        if not lib or not kw:
            self._update_failure_display("Cannot execute. Please select both library and keyword.",
                                         "[Custom] Execution Blocked", "fail")
            return

        args = [self.core.parse_arg(var.get()) for var in getattr(self, 'custom_arg_vars', [])]

        try:
            result = BuiltIn().run_keyword(f"{lib}.{kw}", *args)
            BuiltIn().set_test_variable("${RETURN_VALUE}", result)
            self._update_failure_display(
                f"Executed: {lib}.{kw}\nArgs: {args}\n\n${{RETURN_VALUE}} = {result}",
                f"[Custom] {lib}.{kw} ✅",
                "pass"
            )
        except Exception as e:
            self._update_failure_display(
                f"Executed: {lib}.{kw}\nArgs: {args}\n\nError: {e}",
                f"[Custom] {lib}.{kw} ❌",
                "fail"
            )

    def _update_keywords(self):
        lib = self.library_var.get()
        menu = self.keyword_dropdown["menu"]
        menu.delete(0, "end")

        if lib not in self.libraries:
            return

        keywords = self.libraries[lib]
        for kw in keywords:
            menu.add_command(label=kw['name'], command=lambda name=kw['name']: self.keyword_var.set(name))

    def _update_command_from_keyword(self):
        lib = self.library_var.get()
        kw_name = self.keyword_var.get()
        if lib in self.libraries:
            for kw in self.libraries[lib]:
                if kw['name'] == kw_name:
                    args = [arg for arg in kw['args'] if '=' not in arg]
                    self.command_var.set(f"{lib}.{kw_name}    {'    '.join(args)}")

                    self.doc_display.config(state=tk.NORMAL)
                    self.doc_display.delete("1.0", tk.END)
                    self.doc_display.insert(tk.END, f"{kw_name}\n\nArgs:\n{kw['args']}\n\nDoc:\n{kw['doc']}")
                    self.doc_display.config(state=tk.DISABLED)
                    break

    # def _execute_command(self):
    #     parts = [p.strip() for p in self.command_var.get().split("    ") if p.strip()]
    #     try:
    #         result = BuiltIn().run_keyword(*parts)
    #         BuiltIn().set_test_variable("${RETURN_VALUE}", result)
    #         self.result_var.set(f"✅ RETURN = {result}")
    #     except Exception as e:
    #         self.result_var.set(f"❌ {e}")
    def _execute_command(self):
        if self.execution_in_progress:
            self._update_failure_display("Execution in progress. Please wait.", "[Custom] Busy", "fail")
            return

        lib = self.library_var.get()
        kw = self.keyword_var.get()

        if not lib or not kw:
            self._update_failure_display("Cannot execute. Please select both library and keyword.",
                                         "[Custom] Execution Blocked", "fail")
            return

        args = [self.core.parse_arg(var.get()) for var in getattr(self, 'custom_arg_vars', [])]
        self.execution_in_progress = True

        def _run():
            try:
                result = BuiltIn().run_keyword(f"{lib}.{kw}", *args)
                BuiltIn().set_test_variable("${RETURN_VALUE}", result)
                self._update_failure_display(
                    f"Executed: {lib}.{kw}\nArgs: {args}\n\n${{RETURN_VALUE}} = {result}",
                    f"[Custom] {lib}.{kw} ✅",
                    "pass"
                )
            except Exception as e:
                self._update_failure_display(
                    f"Executed: {lib}.{kw}\nArgs: {args}\n\nError: {e}",
                    f"[Custom] {lib}.{kw} ❌",
                    "fail"
                )
            finally:
                self.execution_in_progress = False

        threading.Thread(target=_run, daemon=True).start()

    @_thread_safe
    def show_failure(self, suite, test, keyword, message, args):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_text = f"[{timestamp}] 🕓 [{test}] {keyword} failed\n\n{message}\n{'-'*60}\n"

        self.failure_text.config(state=tk.NORMAL)
        self.failure_text.insert(tk.END, full_text)
        self.failure_text.see(tk.END)
        self.failure_text.config(state=tk.DISABLED)

        self._build_args_editor(args)
        self._show_window()

    def _build_args_editor(self, args):
        for widget in self.args_frame.winfo_children():
            widget.destroy()
        self.arg_vars = []
        for val in args or []:
            self._add_argument_field(val)

    def _add_argument_field(self, value=""):
        index = len(self.arg_vars)
        var = tk.StringVar(value=str(value))
        frame = tk.Frame(self.args_frame)
        frame.pack(anchor='w', pady=2, fill='x')
        tk.Label(frame, text=f"Arg {index + 1}:").pack(side='left')
        tk.Entry(frame, textvariable=var, width=70).pack(side='left', padx=2)
        tk.Button(frame, text="–", command=lambda f=frame: self._remove_argument_field(f)).pack(side='left')
        self.arg_vars.append(var)

    def _remove_argument_field(self, frame):
        idx = list(self.args_frame.children.values()).index(frame)
        frame.destroy()
        del self.arg_vars[idx]

    def _on_add_argument(self):
        self._add_argument_field()

    def _on_retry_and_continue(self):
        if not self.core.failed_keyword:
            messagebox.showerror("Error", "No failed keyword to retry.")
            return
        kw_name = self.core.failed_keyword.name
        args = [self.core.parse_arg(var.get()) for var in self.arg_vars]
        self.update_status("Retrying...", "blue")
        status, message = self.core.retry_keyword(kw_name, args)
        if status == 'PASS':
            self.core.retry_success = True
            self.core.continue_event.set()
        else:
            self._update_failure_display(
                f"Retry failed: {kw_name}\nArgs: {args}\nError: {message}",
                f"[{self.core.current_test}] Retry failed",
                "fail"
            )

    def _update_failure_display(self, text, prefix, status):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"pass": "✅", "fail": "❌", "pending": "🕓"}
        full_text = f"[{timestamp}] {icons[status]} {prefix}\n{text}\n{'-' * 60}\n"
        self.failure_text.config(state=tk.NORMAL)
        self.failure_text.insert(tk.END, full_text)
        self.failure_text.see(tk.END)
        self.failure_text.config(state=tk.DISABLED)
        self._trim_failure_log()

    def _trim_failure_log(self, max_lines=500):
        lines = self.failure_text.get("1.0", tk.END).splitlines()
        if len(lines) > max_lines:
            trimmed = "\n".join(lines[-max_lines:])
            self.failure_text.config(state=tk.NORMAL)
            self.failure_text.delete("1.0", tk.END)
            self.failure_text.insert(tk.END, trimmed)
            self.failure_text.config(state=tk.DISABLED)

    def update_status(self, text, color="black"):
        self.status_label.config(text=text, fg=color)

    def _on_skip_test(self):
        self.update_status("⚠️ Test skipped", "orange")
        self.core.skip_test = True
        self.core.continue_event.set()

    def _on_abort_suite(self):
        if messagebox.askyesno("Abort Suite", "Really abort entire test suite?"):
            self.update_status("❌ Suite aborted", "red")
            self.core.abort_suite = True
            self.core.continue_event.set()

    def _on_window_close(self):
        self.root.withdraw()

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def library_imported(self, name):
        try:
            libdoc = LibraryDocumentation(name)
            keywords = [{'name': kw.name, 'args': kw.args, 'doc': kw.doc} for kw in libdoc.keywords]
            self.libraries[libdoc.name] = keywords
            self._refresh_library_dropdown()
        except Exception as e:
            print(f"[!] Failed to load library: {name} -> {e}")

    def _refresh_library_dropdown(self):
        self.library_names = sorted(self.libraries.keys())
        self.library_dropdown['values'] = self.library_names
        if self.library_names:
            self.library_var.set(self.library_names[0])
            self._on_library_selected()

    def start(self):
        self.root.mainloop()
