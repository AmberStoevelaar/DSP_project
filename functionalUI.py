import tkinter as tk
from tkinter import filedialog, messagebox
import os
import fitz  # PyMuPDF for handling PDF files

# Store previous results for selection from the sidebar
previous_results = []
previous_result_names = []

def process_text(text):
    # Example: reverse the input text
    return text[::-1]

def process_file(file_path):
    try:
        if file_path.endswith(".txt"):
            with open(file_path, 'r') as file:
                content = file.read()
        elif file_path.endswith(".pdf"):
            content = extract_text_from_pdf(file_path)
        else:
            messagebox.showerror("Unsupported File", "Only .txt and .pdf files are supported.")
            return "", None  # Return empty result and None for name
        return process_text(content), os.path.basename(file_path).split('.')[0]
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file: {e}")
        return "", None  # Return empty result and None for name

def extract_text_from_pdf(file_path):
    # Extract text from a PDF using PyMuPDF (fitz)
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def handle_text_input():
    input_text = text_input.get("1.0", tk.END).strip()
    if input_text:
        result = process_text(input_text)
        name = ask_for_name()
        if name:
            store_result(result, name)  # Store the result in previous_results with name
            update_result_list()  # Update the sidebar with previous results
            display_result(result)
    else:
        messagebox.showwarning("Input Error", "Please enter some text.")

def handle_file_input():
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")])
    if file_path:
        result, name = process_file(file_path)
        if name:  # If the result is valid
            store_result(result, name)  # Store the result in previous_results with name
            update_result_list()  # Update the sidebar with previous results
            display_result(result)
        else:
            messagebox.showwarning("Invalid File", "The file type is not supported.")

def display_result(result):
    result_output.config(state=tk.NORMAL)  # Enable to modify the output
    result_output.delete("1.0", tk.END)
    result_output.insert(tk.END, result)
    result_output.config(state=tk.DISABLED)  # Disable editing

def store_result(result, name):
    previous_results.append(result)
    previous_result_names.append(name)

def update_result_list():
    result_list.delete(0, tk.END)
    for name in previous_result_names:
        result_list.insert(tk.END, name)

def select_previous_result(event):
    try:
        selected_index = result_list.curselection()[0]
        selected_result = previous_results[selected_index]
        display_result(selected_result)
    except IndexError:
        pass  # No result selected

def ask_for_name():
    # Ask the user to provide a name for the result if it's text-based input
    name = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if name:
        return os.path.basename(name).split('.')[0]  # Return the name without the extension
    return None

def download_result():
    result = result_output.get("1.0", tk.END).strip()
    if result:
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if save_path:
            try:
                with open(save_path, 'w') as file:
                    file.write(result)
                messagebox.showinfo("Saved", f"Result saved as {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the file: {e}")
    else:
        messagebox.showwarning("No Result", "There is no result to download.")

# Main GUI setup
root = tk.Tk()
root.title("Text/File Processor")

# Layout: Split the window into two parts: the sidebar and main area
main_frame = tk.Frame(root)
main_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Sidebar (Result history list)
sidebar_frame = tk.Frame(root, width=200, height=400, bg="lightgrey")
sidebar_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Sidebar components
result_list_label = tk.Label(sidebar_frame, text="Previous Results:", anchor="w")
result_list_label.pack(padx=10, pady=5)
result_list = tk.Listbox(sidebar_frame, height=15, width=25)
result_list.pack(padx=10, pady=5)
result_list.bind("<ButtonRelease-1>", select_previous_result)

# Text Input Area
text_input_label = tk.Label(main_frame, text="Enter Text:")
text_input_label.pack(padx=10, pady=5)
text_input = tk.Text(main_frame, height=5, width=50)
text_input.pack(padx=10, pady=5)

# File Input Button
file_input_button = tk.Button(main_frame, text="Open File", command=handle_file_input)
file_input_button.pack(pady=10)

# Process Button
process_button = tk.Button(main_frame, text="Process Text", command=handle_text_input)
process_button.pack(pady=10)

# Output Area
result_label = tk.Label(main_frame, text="Processed Result:")
result_label.pack(padx=10, pady=5)
result_output = tk.Text(main_frame, height=10, width=50, state=tk.DISABLED)
result_output.pack(padx=10, pady=5)

# Download Button
download_button = tk.Button(main_frame, text="Download Result", command=download_result)
download_button.pack(pady=10)

# Run the application
root.mainloop()