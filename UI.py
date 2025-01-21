import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import fitz

class PlaceholderText(tk.Text):
    def __init__(self, container, placeholder="", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = 'black'

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self.get("1.0", "end-1c") == self.placeholder:
            self.delete("1.0", "end")
            self.configure(fg=self.default_fg_color)

    def _add_placeholder(self, event=None):
        if not self.get("1.0", "end-1c").strip():
            self.delete("1.0", "end")
            self.configure(fg=self.placeholder_color)
            self.insert("1.0", self.placeholder)

    def get_text(self):
        """Get the actual text, ignoring placeholder"""
        current_text = self.get("1.0", "end-1c").strip()
        return "" if current_text == self.placeholder else current_text

class SimplifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simplify")
        self.root.geometry("1200x800")

        self.previous_results = []
        self.previous_result_names = []
        self.current_original_text = ""

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.show_start_screen()

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="#f0f0f0", width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_propagate(False)

        title = tk.Label(self.sidebar, text="Simplify", font=("Arial", 24, "bold"), bg="#f0f0f0")
        title.pack(pady=(20,30), anchor="w")

        tk.Label(self.sidebar, text="Previous", font=("Arial", 12, "bold"),
                bg="#f0f0f0").pack(anchor="w")

        self.result_list = tk.Listbox(self.sidebar, height=15, width=25)
        self.result_list.pack(padx=10, pady=5)
        self.result_list.bind("<ButtonRelease-1>", self.select_previous_result)

        new_page_btn = tk.Button(self.sidebar, text="+ New Page",
                               command=self.show_start_screen,
                               bg="#e0e0e0", relief="flat", width=25)
        new_page_btn.pack(pady=(30,10), anchor="w")

    def show_result_screen(self, result, original_text):
        for widget in self.root.grid_slaves(row=0, column=1):
            widget.destroy()

        result_frame = tk.Frame(self.root, bg="white")
        result_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        result_frame.grid_columnconfigure(0, weight=1)

        result_label = tk.Label(result_frame, text="Processed Result",
                              font=("Arial", 16, "bold"), bg="white")
        result_label.pack(pady=(20,10))

        self.result_output = tk.Text(result_frame, height=15, width=70,
                                   font=("Arial", 12), wrap=tk.WORD)
        self.result_output.pack(padx=20, pady=(0,20), fill=tk.BOTH, expand=True)
        self.result_output.insert("1.0", result)
        self.result_output.config(state=tk.DISABLED)

        original_label = tk.Label(result_frame, text="Original Text",
                                font=("Arial", 14), bg="white")
        original_label.pack(pady=(10,5))

        original_output = tk.Text(result_frame, height=8, width=70,
                                font=("Arial", 11), wrap=tk.WORD)
        original_output.pack(padx=20, pady=(0,20), fill=tk.X)
        original_output.insert("1.0", original_text)
        original_output.config(state=tk.DISABLED)

        button_frame = tk.Frame(result_frame, bg="white")
        button_frame.pack(pady=20)

        download_btn_og = tk.Button(button_frame, text="Download Original",
                               command=lambda: self.download_result(original_text),
                               font=("Arial", 11))
        download_btn_og.pack(side=tk.LEFT, padx=10)

        download_btn_result = tk.Button(button_frame, text="Download Result",
                               command=lambda: self.download_result(result),
                               font=("Arial", 11))
        download_btn_result.pack(side=tk.LEFT, padx=10)

    def process_text(self, text):
        import json
        import nbformat
        from nbconvert.preprocessors import ExecutePreprocessor
        import os

        # Save text var to file to load in notebook
        with open('text_var.json', 'w') as f:
            json.dump({'text_var': text}, f)

        # Open notebook
        notebook_path = 'KG.ipynb'
        with open(notebook_path) as f:
            notebook = nbformat.read(f, as_version=4)

        # Execute notebook
        ep = ExecutePreprocessor(timeout=1200, kernel_name='python3')
        ep.preprocess(notebook, {'metadata': {'path': os.getcwd()}})
        print("notebook executed")

        output = None
        for cell in notebook.cells:
            if cell.cell_type == 'code' and 'final_summary' in cell.source:
                    output = cell.outputs[0]['text']

        # Delete text var file
        os.remove('text_var.json')

        return output

    def handle_text_input(self):
        text = self.text_input.get_text()
        if text:
            result = self.process_text(text)
            name = self.ask_for_name()
            if name:
                self.store_result(result, name)
                self.update_result_list()
                self.show_result_screen(result, text)
        else:
            messagebox.showwarning("Input Required", "Please enter text or upload a file.")

    def handle_file_input(self):
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")]
        )
        if file_path:
            result, name = self.process_file(file_path)
            if name:
                self.store_result(result, name)
                self.update_result_list()
                self.show_result_screen(result, self.current_original_text)

    def process_file(self, file_path):
        try:
            if file_path.endswith(".txt"):
                with open(file_path, 'r') as file:
                    content = file.read()
            elif file_path.endswith(".pdf"):
                content = self.extract_text_from_pdf(file_path)
            else:
                messagebox.showerror("Unsupported File", "Only .txt and .pdf files are supported.")
                return "", None
            self.current_original_text = content
            return self.process_text(content), os.path.basename(file_path).split('.')[0]
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            return "", None

    def select_previous_result(self, event):
        try:
            selected_index = self.result_list.curselection()[0]
            selected_result = self.previous_results[selected_index]
            self.show_result_screen(selected_result, "Original text not available for previous results")
        except IndexError:
            pass

    def download_result(self, result):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if save_path:
            try:
                with open(save_path, 'w') as file:
                    file.write(result)
                messagebox.showinfo("Success", f"Result saved to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def show_start_screen(self):
        for widget in self.root.grid_slaves(row=0, column=1):
            widget.destroy()

        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)

        logo_frame = tk.Frame(self.main_frame, bg="white")
        logo_frame.pack(pady=(50,20))
        logo_label = tk.Label(logo_frame, text="S", font=("Arial", 40, "bold"), bg="white")
        logo_label.pack()

        header = tk.Label(self.main_frame,
                         text="Header to give main information",
                         font=("Arial", 24, "bold"),
                         bg="white")
        header.pack(pady=(0,20))

        description = tk.Label(self.main_frame,
                             text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do\n" +
                                  "eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                             font=("Arial", 12),
                             bg="white")
        description.pack(pady=(0,40))

        input_frame = tk.Frame(self.main_frame, bg="#f5f5f5", padx=20, pady=20)
        input_frame.pack(fill="x", padx=200)

        self.text_input = PlaceholderText(
            input_frame,
            placeholder="Insert your text here or upload a file",
            height=3,
            width=50,
            font=("Arial", 11)
        )
        self.text_input.pack(fill="x", pady=(0,10))

        button_frame = tk.Frame(input_frame, bg="#f5f5f5")
        button_frame.pack(fill="x")

        upload_btn = tk.Button(button_frame, text="📎", command=self.handle_file_input, width=3)
        upload_btn.pack(side="left")

        process_btn = tk.Button(button_frame, text="⬆", command=self.handle_text_input, width=3)
        process_btn.pack(side="right")

    def extract_text_from_pdf(self, file_path):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def store_result(self, result, name):
        self.previous_results.append(result)
        self.previous_result_names.append(name)

    def update_result_list(self):
        self.result_list.delete(0, tk.END)
        for name in self.previous_result_names:
            self.result_list.insert(tk.END, name)

    def ask_for_name(self):
        name = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if name:
            return os.path.basename(name).split('.')[0]
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = SimplifyApp(root)
    root.mainloop()