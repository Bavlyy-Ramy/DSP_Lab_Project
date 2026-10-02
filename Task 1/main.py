import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from signal_processing import (
    read_signal,
    add_signals,
    multiply_signal,
    subtract_signals,
    shift_signal,
    fold_signal
)


# ============================================================
# APPLICATION DATA
# ============================================================

loaded_signals = []
loaded_signal_names = []

operations = [
    "Add",
    "Subtract",
    "Multiply",
    "Shift",
    "Fold"
]


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#F5F7FA"
PANEL_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
SECONDARY_COLOR = "#E5E7EB"
TEXT_COLOR = "#1F2937"
MUTED_COLOR = "#6B7280"
SUCCESS_COLOR = "#15803D"
ERROR_COLOR = "#B91C1C"
INPUT_BG_COLOR = "#EFF6FF"
INPUT_BORDER_COLOR = "#BFDBFE"


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("DSP Task 1")

root.geometry("1200x750")

root.minsize(
    1000,
    650
)

root.configure(
    bg=BG_COLOR
)


# ============================================================
# TKINTER STYLE
# ============================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure(
    "TCombobox",
    padding=6,
    font=("Arial", 11)
)


# ============================================================
# LOAD SIGNAL
# ============================================================

def load_signal():
    """
    Load a signal from a .txt file.
    """

    filename = filedialog.askopenfilename(
        title="Select Signal File",
        filetypes=[
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
    )

    if not filename:
        return

    try:

        signal = read_signal(filename)

        loaded_signals.append(signal)

        signal_name = filename.replace("\\", "/").split("/")[-1]

        loaded_signal_names.append(signal_name)

        signals_listbox.insert(
            tk.END,
            signal_name
        )

        update_signal_count()

        status_label.config(
            text=f"Loaded: {signal_name}",
            fg=SUCCESS_COLOR
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not load the signal.\n\n{error}"
        )

        status_label.config(
            text="Failed to load signal.",
            fg=ERROR_COLOR
        )


# ============================================================
# REMOVE SELECTED SIGNAL
# ============================================================

def remove_selected_signal():
    """
    Remove the currently selected signals.
    """

    selected = list(
        signals_listbox.curselection()
    )

    if not selected:

        messagebox.showwarning(
            "No Signal Selected",
            "Please select one or more signals to remove."
        )

        return

    # Delete from the end so indices don't change
    for index in reversed(selected):

        signals_listbox.delete(index)

        del loaded_signals[index]

        del loaded_signal_names[index]

    update_signal_count()
    update_selection_count()

    status_label.config(
        text="Selected signal(s) removed.",
        fg=SUCCESS_COLOR
    )


# ============================================================
# CLEAR ALL SIGNALS
# ============================================================

def clear_all_signals():
    """
    Remove all loaded signals and clear the graph.
    """

    loaded_signals.clear()

    loaded_signal_names.clear()

    signals_listbox.delete(
        0,
        tk.END
    )

    clear_plot()

    update_signal_count()
    update_selection_count()

    status_label.config(
        text="All signals cleared.",
        fg=MUTED_COLOR
    )


# ============================================================
# DISPLAY SELECTED SIGNAL
# ============================================================

def display_selected_signal():
    """
    Display the first selected signal.
    """

    selected = signals_listbox.curselection()

    if not selected:

        messagebox.showwarning(
            "No Signal Selected",
            "Please select a signal first."
        )

        return

    index = selected[0]

    signal = loaded_signals[index]

    indices, samples = signal

    signal_name = loaded_signal_names[index]

    display_signal(
        indices,
        samples,
        signal_name
    )

    status_label.config(
        text=f"Displaying: {signal_name}",
        fg=SUCCESS_COLOR
    )


# ============================================================
# SHOW SIGNAL INFORMATION
# ============================================================

def show_signal_info():
    """
    Display information about the selected signal.
    """

    selected = signals_listbox.curselection()

    if not selected:

        messagebox.showwarning(
            "No Signal Selected",
            "Please select a signal first."
        )

        return

    index = selected[0]

    signal = loaded_signals[index]

    indices, samples = signal

    signal_name = loaded_signal_names[index]

    message = (
        f"Signal: {signal_name}\n\n"
        f"Number of samples: {len(samples)}\n\n"
        f"Indices:\n{indices}\n\n"
        f"Samples:\n{samples}"
    )

    messagebox.showinfo(
        "Signal Information",
        message
    )


# ============================================================
# UPDATE SIGNAL COUNT
# ============================================================

def update_signal_count():
    """
    Update the number of loaded signals.
    """

    count = len(loaded_signals)

    signal_count_label.config(
        text=f"{count} signal(s) loaded"
    )


# ============================================================
# UPDATE SELECTION COUNT
# ============================================================

def update_selection_count(event=None):
    """
    Update the number of selected signals.
    """

    selected_count = len(
        signals_listbox.curselection()
    )

    selection_count_label.config(
        text=f"{selected_count} selected"
    )


# ============================================================
# OPERATION CHANGED
# ============================================================

def operation_changed(event=None):
    """
    Show the appropriate input field for the selected operation.
    """

    operation = operation_var.get()

    # Hide optional input sections first
    constant_frame.pack_forget()
    shift_frame.pack_forget()

    # Clear old values
    constant_var.set("")
    shift_var.set("")

    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    if operation == "Add":

        instruction_label.config(
            text="Select two or more signals to add them."
        )

    # --------------------------------------------------------
    # SUBTRACT
    # --------------------------------------------------------

    elif operation == "Subtract":

        instruction_label.config(
            text="Select exactly two signals.\n"
                 "First selected signal - second selected signal."
        )

    # --------------------------------------------------------
    # MULTIPLY
    # --------------------------------------------------------

    elif operation == "Multiply":

        instruction_label.config(
            text="Select one signal and enter a constant."
        )

        # Show Constant input
        constant_frame.pack(
            fill="x",
            padx=15,
            pady=8
        )

    # --------------------------------------------------------
    # SHIFT
    # --------------------------------------------------------

    elif operation == "Shift":

        instruction_label.config(
            text="Select one signal and enter a shift value.\n"
                 "+3 = advance, -3 = delay."
        )

        # Show Shift input
        shift_frame.pack(
            fill="x",
            padx=15,
            pady=8
        )

    # --------------------------------------------------------
    # FOLD
    # --------------------------------------------------------

    elif operation == "Fold":

        instruction_label.config(
            text="Select one signal to perform x(-n).\n"
                 "No additional value is required."
        )


# ============================================================
# APPLY OPERATION
# ============================================================

def apply_operation():
    """
    Execute the selected DSP operation.
    """

    if not loaded_signals:

        messagebox.showwarning(
            "No Signals",
            "Please load at least one signal first."
        )

        return

    operation = operation_var.get()

    selected = signals_listbox.curselection()

    # ========================================================
    # ADD
    # ========================================================

    if operation == "Add":

        if len(selected) < 2:

            messagebox.showwarning(
                "Invalid Selection",
                "Please select at least two signals to add."
            )

            return

        selected_signals = [
            loaded_signals[index]
            for index in selected
        ]

        result_indices, result_samples = add_signals(
            *selected_signals
        )

        display_signal(
            result_indices,
            result_samples,
            "Addition Result"
        )

        status_label.config(
            text=f"Added {len(selected_signals)} signals successfully.",
            fg=SUCCESS_COLOR
        )

    # ========================================================
    # SUBTRACT
    # ========================================================

    elif operation == "Subtract":

        if len(selected) != 2:

            messagebox.showwarning(
                "Invalid Selection",
                "Please select exactly two signals."
            )

            return

        signal1 = loaded_signals[selected[0]]

        signal2 = loaded_signals[selected[1]]

        result_indices, result_samples = subtract_signals(
            signal1,
            signal2
        )

        display_signal(
            result_indices,
            result_samples,
            "Subtraction Result"
        )

        status_label.config(
            text="Subtraction completed successfully.",
            fg=SUCCESS_COLOR
        )

    # ========================================================
    # MULTIPLY
    # ========================================================

    elif operation == "Multiply":

        if len(selected) != 1:

            messagebox.showwarning(
                "Invalid Selection",
                "Please select exactly one signal."
            )

            return

        constant_text = constant_var.get().strip()

        if not constant_text:

            messagebox.showwarning(
                "Missing Constant",
                "Please enter a multiplication constant."
            )

            # Put cursor directly into the input box
            constant_entry.focus_set()

            return

        try:

            constant = float(constant_text)

        except ValueError:

            messagebox.showerror(
                "Invalid Constant",
                "The constant must be a valid number."
            )

            constant_entry.focus_set()

            return

        signal = loaded_signals[selected[0]]

        result_indices, result_samples = multiply_signal(
            signal,
            constant
        )

        display_signal(
            result_indices,
            result_samples,
            f"Multiplication Result (× {constant})"
        )

        status_label.config(
            text=f"Signal multiplied by {constant}.",
            fg=SUCCESS_COLOR
        )

    # ========================================================
    # SHIFT
    # ========================================================

    elif operation == "Shift":

        if len(selected) != 1:

            messagebox.showwarning(
                "Invalid Selection",
                "Please select exactly one signal."
            )

            return

        shift_text = shift_var.get().strip()

        if not shift_text:

            messagebox.showwarning(
                "Missing Shift Value",
                "Please enter a shift value."
            )

            shift_entry.focus_set()

            return

        try:

            shift = int(shift_text)

        except ValueError:

            messagebox.showerror(
                "Invalid Shift",
                "The shift value must be an integer."
            )

            shift_entry.focus_set()

            return

        signal = loaded_signals[selected[0]]

        result_indices, result_samples = shift_signal(
            signal,
            shift
        )

        if shift > 0:

            title = f"Advanced Signal by {shift}"

            status = f"Signal advanced by {shift}."

        elif shift < 0:

            title = f"Delayed Signal by {abs(shift)}"

            status = f"Signal delayed by {abs(shift)}."

        else:

            title = "Signal - No Shift"

            status = "No shift applied."

        display_signal(
            result_indices,
            result_samples,
            title
        )

        status_label.config(
            text=status,
            fg=SUCCESS_COLOR
        )

    # ========================================================
    # FOLD
    # ========================================================

    elif operation == "Fold":

        if len(selected) != 1:

            messagebox.showwarning(
                "Invalid Selection",
                "Please select exactly one signal."
            )

            return

        signal = loaded_signals[selected[0]]

        result_indices, result_samples = fold_signal(
            signal
        )

        display_signal(
            result_indices,
            result_samples,
            "Folded Signal x(-n)"
        )

        status_label.config(
            text="Signal folded successfully.",
            fg=SUCCESS_COLOR
        )


# ============================================================
# DISPLAY SIGNAL ON MATPLOTLIB
# ============================================================

def display_signal(
    indices,
    samples,
    title="Signal"
):
    """
    Display a discrete-time signal inside the GUI.
    """

    figure.clear()

    ax = figure.add_subplot(111)

    ax.stem(
        indices,
        samples
    )

    ax.set_xlabel(
        "n",
        fontsize=11
    )

    ax.set_ylabel(
        "x[n]",
        fontsize=11
    )

    ax.set_title(
        title,
        fontsize=14,
        fontweight="bold"
    )

    ax.grid(
        True,
        alpha=0.3
    )

    figure.tight_layout()

    canvas.draw()


# ============================================================
# CLEAR PLOT
# ============================================================

def clear_plot():
    """
    Clear the graph.
    """

    figure.clear()

    ax = figure.add_subplot(111)

    ax.set_title(
        "Signal Plot",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel(
        "n"
    )

    ax.set_ylabel(
        "x[n]"
    )

    ax.grid(
        True,
        alpha=0.3
    )

    figure.tight_layout()

    canvas.draw()


# ============================================================
# CLOSE APPLICATION
# ============================================================

def on_closing():
    """
    Properly close the application.
    """

    plt.close("all")

    root.destroy()


# ============================================================
# HEADER
# ============================================================

header_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

header_frame.pack(
    fill="x",
    padx=30,
    pady=(20, 10)
)


title_label = tk.Label(
    header_frame,
    text="DSP Task 1",
    font=("Arial", 26, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

title_label.pack(
    anchor="w"
)


subtitle_label = tk.Label(
    header_frame,
    text="Discrete-Time Signal Processing",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg=MUTED_COLOR
)

subtitle_label.pack(
    anchor="w",
    pady=(2, 0)
)


# ============================================================
# MAIN CONTENT
# ============================================================

main_frame = tk.Frame(
    root,
    bg=BG_COLOR
)

main_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=10
)


# ============================================================
# LEFT CONTROL PANEL
# ============================================================

control_panel = tk.Frame(
    main_frame,
    bg=PANEL_COLOR,
    highlightbackground="#D1D5DB",
    highlightthickness=1
)

control_panel.pack(
    side="left",
    fill="y",
    padx=(0, 15)
)

control_panel.configure(
    width=350
)

control_panel.pack_propagate(
    False
)


# ============================================================
# CONTROL TITLE
# ============================================================

control_title = tk.Label(
    control_panel,
    text="Controls",
    font=("Arial", 16, "bold"),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR
)

control_title.pack(
    anchor="w",
    padx=20,
    pady=(20, 5)
)


control_description = tk.Label(
    control_panel,
    text="Load signals and choose an operation.",
    font=("Arial", 10),
    bg=PANEL_COLOR,
    fg=MUTED_COLOR
)

control_description.pack(
    anchor="w",
    padx=20,
    pady=(0, 15)
)


# ============================================================
# SIGNAL SECTION
# ============================================================

signal_section = tk.LabelFrame(
    control_panel,
    text=" Signals ",
    font=("Arial", 11, "bold"),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    bd=1,
    relief="solid"
)

signal_section.pack(
    fill="x",
    padx=15,
    pady=5
)


# ============================================================
# SIGNAL COUNT
# ============================================================

signal_count_label = tk.Label(
    signal_section,
    text="0 signal(s) loaded",
    font=("Arial", 9),
    bg=PANEL_COLOR,
    fg=MUTED_COLOR
)

signal_count_label.pack(
    anchor="w",
    padx=10,
    pady=(8, 3)
)


# ============================================================
# SIGNAL LIST
# ============================================================

signals_listbox = tk.Listbox(
    signal_section,
    width=35,
    height=8,
    font=("Arial", 10),
    selectmode=tk.EXTENDED,
    activestyle="none",
    bg="#F9FAFB",
    fg=TEXT_COLOR,
    selectbackground=PRIMARY_COLOR,
    selectforeground="white",
    highlightthickness=1,
    highlightbackground="#D1D5DB"
)

signals_listbox.pack(
    fill="x",
    padx=10,
    pady=5
)

signals_listbox.bind(
    "<<ListboxSelect>>",
    update_selection_count
)


# ============================================================
# SELECTION COUNT
# ============================================================

selection_count_label = tk.Label(
    signal_section,
    text="0 selected",
    font=("Arial", 9),
    bg=PANEL_COLOR,
    fg=MUTED_COLOR
)

selection_count_label.pack(
    anchor="w",
    padx=10,
    pady=(0, 5)
)


# ============================================================
# SIGNAL BUTTONS - ROW 1
# ============================================================

signal_buttons_frame = tk.Frame(
    signal_section,
    bg=PANEL_COLOR
)

signal_buttons_frame.pack(
    fill="x",
    padx=10,
    pady=(2, 10)
)


load_button = tk.Button(
    signal_buttons_frame,
    text="Load",
    command=load_signal,
    bg=PRIMARY_COLOR,
    fg="white",
    activebackground=PRIMARY_HOVER,
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    font=("Arial", 10, "bold"),
    padx=12,
    pady=6
)

load_button.pack(
    side="left",
    padx=(0, 5)
)


display_button = tk.Button(
    signal_buttons_frame,
    text="Display",
    command=display_selected_signal,
    bg=SECONDARY_COLOR,
    fg=TEXT_COLOR,
    activebackground="#D1D5DB",
    relief="flat",
    cursor="hand2",
    font=("Arial", 10),
    padx=10,
    pady=6
)

display_button.pack(
    side="left",
    padx=5
)


info_button = tk.Button(
    signal_buttons_frame,
    text="Info",
    command=show_signal_info,
    bg=SECONDARY_COLOR,
    fg=TEXT_COLOR,
    activebackground="#D1D5DB",
    relief="flat",
    cursor="hand2",
    font=("Arial", 10),
    padx=10,
    pady=6
)

info_button.pack(
    side="left",
    padx=5
)


# ============================================================
# SIGNAL BUTTONS - ROW 2
# ============================================================

signal_buttons_frame_2 = tk.Frame(
    signal_section,
    bg=PANEL_COLOR
)

signal_buttons_frame_2.pack(
    fill="x",
    padx=10,
    pady=(0, 10)
)


remove_button = tk.Button(
    signal_buttons_frame_2,
    text="Remove Selected",
    command=remove_selected_signal,
    bg="#FEE2E2",
    fg=ERROR_COLOR,
    activebackground="#FECACA",
    relief="flat",
    cursor="hand2",
    font=("Arial", 9),
    padx=10,
    pady=5
)

remove_button.pack(
    side="left"
)


clear_button = tk.Button(
    signal_buttons_frame_2,
    text="Clear All",
    command=clear_all_signals,
    bg=SECONDARY_COLOR,
    fg=TEXT_COLOR,
    activebackground="#D1D5DB",
    relief="flat",
    cursor="hand2",
    font=("Arial", 9),
    padx=10,
    pady=5
)

clear_button.pack(
    side="right"
)


# ============================================================
# OPERATION SECTION
# ============================================================

operation_section = tk.LabelFrame(
    control_panel,
    text=" Operation ",
    font=("Arial", 11, "bold"),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    bd=1,
    relief="solid"
)

operation_section.pack(
    fill="x",
    padx=15,
    pady=15
)


# ============================================================
# OPERATION DROPDOWN
# ============================================================

operation_var = tk.StringVar(
    value="Add"
)

operation_menu = ttk.Combobox(
    operation_section,
    textvariable=operation_var,
    values=operations,
    state="readonly",
    width=28
)

operation_menu.pack(
    padx=15,
    pady=(12, 8)
)

operation_menu.bind(
    "<<ComboboxSelected>>",
    operation_changed
)


# ============================================================
# OPERATION INSTRUCTIONS
# ============================================================

instruction_label = tk.Label(
    operation_section,
    text="Select two or more signals to add them.",
    font=("Arial", 9),
    bg=PANEL_COLOR,
    fg=MUTED_COLOR,
    justify="left",
    wraplength=280
)

instruction_label.pack(
    anchor="w",
    padx=15,
    pady=(0, 8)
)


# ============================================================
# CONSTANT INPUT
# ============================================================

constant_frame = tk.Frame(
    operation_section,
    bg=INPUT_BG_COLOR,
    highlightbackground=INPUT_BORDER_COLOR,
    highlightthickness=1
)

constant_label = tk.Label(
    constant_frame,
    text="Constant:",
    font=("Arial", 10, "bold"),
    bg=INPUT_BG_COLOR,
    fg=TEXT_COLOR
)

constant_label.pack(
    side="left",
    padx=(10, 5),
    pady=8
)


constant_var = tk.StringVar()

constant_entry = tk.Entry(
    constant_frame,
    textvariable=constant_var,
    width=12,
    font=("Arial", 11),
    relief="solid",
    bd=1
)

constant_entry.pack(
    side="right",
    padx=(5, 10),
    pady=8
)


# ============================================================
# SHIFT INPUT
# ============================================================

shift_frame = tk.Frame(
    operation_section,
    bg=INPUT_BG_COLOR,
    highlightbackground=INPUT_BORDER_COLOR,
    highlightthickness=1
)

shift_label = tk.Label(
    shift_frame,
    text="Shift Value:",
    font=("Arial", 10, "bold"),
    bg=INPUT_BG_COLOR,
    fg=TEXT_COLOR
)

shift_label.pack(
    side="left",
    padx=(10, 5),
    pady=8
)


shift_var = tk.StringVar()

shift_entry = tk.Entry(
    shift_frame,
    textvariable=shift_var,
    width=12,
    font=("Arial", 11),
    relief="solid",
    bd=1
)

shift_entry.pack(
    side="right",
    padx=(5, 10),
    pady=8
)


# ============================================================
# APPLY OPERATION BUTTON
# ============================================================

apply_button = tk.Button(
    operation_section,
    text="Apply Operation",
    command=apply_operation,
    bg=PRIMARY_COLOR,
    fg="white",
    activebackground=PRIMARY_HOVER,
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    font=("Arial", 11, "bold"),
    padx=20,
    pady=8
)

apply_button.pack(
    fill="x",
    padx=15,
    pady=(12, 15)
)


# ============================================================
# STATUS SECTION
# ============================================================

status_frame = tk.Frame(
    control_panel,
    bg=PANEL_COLOR
)

status_frame.pack(
    fill="x",
    padx=20,
    pady=10
)


status_title = tk.Label(
    status_frame,
    text="Status",
    font=("Arial", 9, "bold"),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR
)

status_title.pack(
    anchor="w"
)


status_label = tk.Label(
    status_frame,
    text="Load signals to begin.",
    font=("Arial", 9),
    bg=PANEL_COLOR,
    fg=MUTED_COLOR,
    justify="left",
    wraplength=290
)

status_label.pack(
    anchor="w",
    pady=(3, 0)
)


# ============================================================
# RIGHT PLOT PANEL
# ============================================================

plot_panel = tk.Frame(
    main_frame,
    bg=PANEL_COLOR,
    highlightbackground="#D1D5DB",
    highlightthickness=1
)

plot_panel.pack(
    side="right",
    fill="both",
    expand=True
)


# ============================================================
# PLOT HEADER
# ============================================================

plot_header = tk.Frame(
    plot_panel,
    bg=PANEL_COLOR
)

plot_header.pack(
    fill="x",
    padx=20,
    pady=(15, 5)
)


plot_title = tk.Label(
    plot_header,
    text="Signal Visualization",
    font=("Arial", 16, "bold"),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR
)

plot_title.pack(
    side="left"
)


plot_description = tk.Label(
    plot_header,
    text="Discrete-time signal",
    font=("Arial", 9),
    bg=PANEL_COLOR,
    fg=MUTED_COLOR
)

plot_description.pack(
    side="right"
)


# ============================================================
# PLOT FRAME
# ============================================================

plot_frame = tk.Frame(
    plot_panel,
    bg="white"
)

plot_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


# ============================================================
# MATPLOTLIB FIGURE
# ============================================================

figure = plt.Figure(
    figsize=(7, 5),
    dpi=100
)

ax = figure.add_subplot(
    111
)

ax.set_title(
    "Signal Plot",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel(
    "n"
)

ax.set_ylabel(
    "x[n]"
)

ax.grid(
    True,
    alpha=0.3
)

figure.tight_layout()


# ============================================================
# MATPLOTLIB CANVAS
# ============================================================

canvas = FigureCanvasTkAgg(
    figure,
    master=plot_frame
)

canvas.draw()

canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)


# ============================================================
# FOOTER
# ============================================================

footer_label = tk.Label(
    root,
    text="DSP Task 1 • Signal Processing GUI",
    font=("Arial", 9),
    bg=BG_COLOR,
    fg=MUTED_COLOR
)

footer_label.pack(
    pady=(0, 10)
)


# ============================================================
# CLOSE EVENT
# ============================================================

root.protocol(
    "WM_DELETE_WINDOW",
    on_closing
)


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()