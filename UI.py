# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# from datetime import datetime
# import os
# import fitz  # PyMuPDF for PDF files

# class SimplifyApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Simplify")
#         self.root.geometry("1200x800")
        
#         # Configure grid weight
#         root.grid_columnconfigure(1, weight=1)
#         root.grid_rowconfigure(0, weight=1)
        
#         self.create_sidebar()
#         self.show_start_screen()
        
#     def create_sidebar(self):
#         sidebar = tk.Frame(self.root, bg="#f0f0f0", width=250)
#         sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
#         sidebar.grid_propagate(False)
        
#         # App title
#         title = tk.Label(sidebar, text="Simplify", font=("Arial", 24, "bold"), bg="#f0f0f0")
#         title.pack(pady=(20,30), anchor="w")
        
#         # Today section
#         tk.Label(sidebar, text="Today", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w")
        
#         # Previous 7 days section
#         tk.Label(sidebar, text="Previous 7 days", font=("Arial", 12, "bold"), 
#                 bg="#f0f0f0").pack(pady=(20,5), anchor="w")
        
#         # Previous 30 days section
#         tk.Label(sidebar, text="Previous 30 days", font=("Arial", 12, "bold"), 
#                 bg="#f0f0f0").pack(pady=(20,5), anchor="w")
        
#         # New Page Button
#         new_page_btn = tk.Button(sidebar, text="+ New Page", 
#                                command=self.show_start_screen,
#                                bg="#e0e0e0", relief="flat", width=25)
#         new_page_btn.pack(pady=(30,10), anchor="w")

#     def show_start_screen(self):
#         # Clear any existing content in main area
#         for widget in self.root.grid_slaves(row=0, column=1):
#             widget.destroy()
            
#         main_frame = tk.Frame(self.root, bg="white")
#         main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
#         main_frame.grid_columnconfigure(0, weight=1)
#         main_frame.grid_rowconfigure(1, weight=1)
        
#         # Logo/Header section
#         logo_frame = tk.Frame(main_frame, bg="white")
#         logo_frame.grid(row=0, column=0, pady=(100,20))
        
#         # Replace with actual logo if available
#         logo_label = tk.Label(logo_frame, text="S", font=("Arial", 40, "bold"), bg="white")
#         logo_label.pack()
        
#         # Header
#         header = tk.Label(main_frame, 
#                          text="Header to give main information",
#                          font=("Arial", 24, "bold"),
#                          bg="white")
#         header.grid(row=1, column=0, pady=(0,20))
        
#         # Description
#         description = tk.Label(main_frame,
#                              text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do\n" +
#                                   "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut\n" +
#                                   "enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi",
#                              font=("Arial", 12),
#                              bg="white")
#         description.grid(row=2, column=0, pady=(0,40))
        
#         # Input frame
#         input_frame = tk.Frame(main_frame, bg="#f5f5f5", padx=20, pady=20)
#         input_frame.grid(row=3, column=0, sticky="ew", padx=200)
        
#         # Text area
#         self.text_input = tk.Text(input_frame, height=3, width=50,
#                                  font=("Arial", 11))
#         self.text_input.pack(fill="x", pady=(0,10))
#         self.text_input.insert("1.0", "Insert your text here or upload a file")
        
#         # Buttons frame
#         button_frame = tk.Frame(input_frame, bg="#f5f5f5")
#         button_frame.pack(fill="x")
        
#         # File upload button
#         upload_btn = tk.Button(button_frame, text="📎", 
#                              command=self.upload_file,
#                              width=3)
#         upload_btn.pack(side="left")
        
#         # Process button
#         process_btn = tk.Button(button_frame, text="⬆", 
#                               command=self.process_input,
#                               width=3)
#         process_btn.pack(side="right")

#     def upload_file(self):
#         file_path = filedialog.askopenfilename(
#             filetypes=[("Text/PDF files", "*.txt *.pdf")]
#         )
#         if file_path:
#             try:
#                 if file_path.endswith('.pdf'):
#                     # Handle PDF
#                     doc = fitz.open(file_path)
#                     text = ""
#                     for page in doc:
#                         text += page.get_text()
#                     self.text_input.delete("1.0", tk.END)
#                     self.text_input.insert("1.0", text)
#                 else:
#                     # Handle TXT
#                     with open(file_path, 'r') as file:
#                         content = file.read()
#                         self.text_input.delete("1.0", tk.END)
#                         self.text_input.insert("1.0", content)
#             except Exception as e:
#                 messagebox.showerror("Error", f"Could not read file: {e}")

#     def process_input(self):
#         # Get text from input
#         text = self.text_input.get("1.0", tk.END).strip()
#         if text and text != "Insert your text here or upload a file":
#             # Process the text (implement your processing logic here)
#             messagebox.showinfo("Success", "Text processed successfully!")
#         else:
#             messagebox.showwarning("Input Required", "Please enter text or upload a file.")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = SimplifyApp(root)
#     root.mainloop()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import os

class SimplifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simplify")
        self.root.geometry("1200x800")
        
        # Configure grid weight
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        
        # Create frames
        self.create_sidebar()
        self.create_main_content()
        
        # Store entries
        self.entries = []
        
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#f0f0f0", width=250)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        sidebar.grid_propagate(False)
        
        # App title
        title = tk.Label(sidebar, text="Simplify", font=("Arial", 24, "bold"), bg="#f0f0f0")
        title.pack(pady=(20,30), anchor="w")
        
        # Today section
        tk.Label(sidebar, text="Today", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w")
        # Example entry button
        today_entry = tk.Button(sidebar, text="Title here (autogenerated)", 
                              bg="#e0e0e0", relief="flat", width=25)
        today_entry.pack(pady=(5,15), anchor="w")
        
        # Previous 7 days section
        tk.Label(sidebar, text="Previous 7 days", font=("Arial", 12, "bold"), 
                bg="#f0f0f0").pack(anchor="w")
        for _ in range(3):
            entry = tk.Button(sidebar, text="Title here (autogenerated)", 
                            bg="#e0e0e0", relief="flat", width=25)
            entry.pack(pady=5, anchor="w")
            
        # Previous 30 days section
        tk.Label(sidebar, text="Previous 30 days", font=("Arial", 12, "bold"), 
                bg="#f0f0f0").pack(pady=(15,5), anchor="w")
        
    def create_main_content(self):
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Entry name frame
        name_frame = tk.Frame(main_frame, bg="#f0f0f0", height=50)
        name_frame.pack(fill="x", pady=(0,20))
        entry_name = tk.Label(name_frame, text="Name of entry (auto gen)", 
                            bg="#f0f0f0", font=("Arial", 14))
        entry_name.pack(pady=10, padx=20)
        
        # Original input frame
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill="x", pady=(0,20))
        
        # Header with download button
        header_frame = tk.Frame(input_frame, bg="#f0f0f0")
        header_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header_frame, text="Title of original input", 
                font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side="left")
        
        download_btn = tk.Button(header_frame, text="⬇ Download input", 
                               command=self.download_input)
        download_btn.pack(side="right")
        
        # Input summary
        tk.Label(input_frame, text="Here a quick summary of original input/more headlines",
                bg="#f0f0f0").pack(padx=20, pady=(0,10), anchor="w")
        
        # Simplification frame
        simpl_frame = tk.Frame(main_frame, bg="#f0f0f0")
        simpl_frame.pack(fill="both", expand=True)
        
        # Header with download button
        simpl_header = tk.Frame(simpl_frame, bg="#f0f0f0")
        simpl_header.pack(fill="x", padx=20, pady=10)
        
        tk.Label(simpl_header, text="Simplification", 
                font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side="left")
        
        download_simpl = tk.Button(simpl_header, text="⬇ Download Simplified output",
                                 command=self.download_output)
        download_simpl.pack(side="right")
        
        # Simplified content
        self.simplified_text = tk.Text(simpl_frame, wrap="word", 
                                     font=("Arial", 11), padx=20, pady=10)
        self.simplified_text.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        # Add example content
        self.add_example_content()
        
        # Feedback buttons
        feedback_frame = tk.Frame(simpl_frame, bg="#f0f0f0")
        feedback_frame.pack(fill="x", padx=20, pady=10)
        
        like_btn = tk.Button(feedback_frame, text="👍", width=3, command=self.like)
        like_btn.pack(side="left", padx=5)
        
        dislike_btn = tk.Button(feedback_frame, text="👎", width=3, command=self.dislike)
        dislike_btn.pack(side="left", padx=5)
        
    def add_example_content(self):
        content = """Challenges and Conflicts:
• Cum asperiores asperiores aut nobis molestiae cum maxime animi.
• Nam explicabo laudantium ut provident ipsa in voluptas nihil non veniam sint quo porro beatae eos incidunt dolore.

Themes of Growth:
• Et inventore laboriosam eum fugit exercitationem aut earum galisum.
• Ab quasi provident est possimus natus a possimus sunt.

Interpersonal Dynamics:
• Ad harum libero ut quod suscipit quo nesciunt Quis et repellendus exercitationem et eius tenetur ut neque quos.

Underlying Tensions:
• In quisquam doloribus et cumque tenetur qui quis voluptate.
• Eos voluptate consequatur sed omnis sint et quia animi ea distinctio autem et itaque voluptatum.

Broader Reflections:
• Vel numquam necessitatibus et quaerat ducimus At tempore atque aut maxime illo qui assumenda animi.
• Ea laboriosam sint aut libero magni id eveniet dignissimos nam inventore perferendis et consequuntur facilis et recusandae laborum rem nobis animi."""
        
        self.simplified_text.insert("1.0", content)
        
    def download_input(self):
        messagebox.showinfo("Download", "Original input downloaded")
        
    def download_output(self):
        messagebox.showinfo("Download", "Simplified output downloaded")
        
    def like(self):
        messagebox.showinfo("Feedback", "Thanks for the positive feedback!")
        
    def dislike(self):
        messagebox.showinfo("Feedback", "Thanks for the feedback! We'll work on improving.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimplifyApp(root)
    root.mainloop()