import tkinter as tk
import math
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from signal_processing import (
    read_signal,
    add_signals,
    multiply_signal,
    subtract_signals,
    shift_signal,
    fold_signal,
    quantize_signal
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


# Plot representation: "Discrete" uses stems; "Continuous-style" connects samples.
plot_style = "Discrete"


def generate_waveform(waveform, amplitude, phase, analog_frequency,
                      sampling_frequency, num_samples):
    """Generate a sampled sine or cosine wave; phase is in radians."""
    values = (amplitude, phase, analog_frequency, sampling_frequency)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("All parameters must be finite numbers.")
    if analog_frequency < 0:
        raise ValueError("Analog frequency cannot be negative.")
    if sampling_frequency <= 0:
        raise ValueError("Sampling frequency must be positive.")
    if sampling_frequency <= 2 * analog_frequency:
        raise ValueError("Sampling frequency must be greater than twice the analog frequency.")
    if num_samples <= 0:
        raise ValueError("Number of samples must be a positive integer.")

    indices = list(range(num_samples))
    function = math.sin if waveform == "Sine" else math.cos
    samples = [
        amplitude * function(2 * math.pi * analog_frequency / sampling_frequency * n + phase)
        for n in indices
    ]
    return indices, samples


def open_signal_generator(waveform):
    """Open a parameter form for generating a sine or cosine signal."""
    dialog = tk.Toplevel(root)
    dialog.title(f"Generate {waveform} Wave")
    dialog.transient(root)
    dialog.resizable(True, True)
    dialog.configure(bg=PANEL_COLOR)
    dialog.minsize(340, 360)

    container = tk.Frame(dialog, bg=PANEL_COLOR, padx=18, pady=16)
    container.pack(fill="both", expand=True)

    tk.Label(container, text=f"{waveform} Wave Parameters",
             font=("Arial", 14, "bold"), bg=PANEL_COLOR,
             fg=TEXT_COLOR).grid(row=0, column=0, columnspan=2,
                                 sticky="w", pady=(0, 12))

    fields = [
        ("Amplitude (A)", "1"),
        ("Phase shift θ (radians)", "0"),
        ("Analog frequency (Hz)", "5"),
        ("Sampling frequency (Hz)", "50"),
        ("Number of samples", "100"),
    ]
    entries = {}
    for row, (label_text, default) in enumerate(fields, start=1):
        tk.Label(container, text=label_text, font=("Segoe UI", 10),
                 bg=PANEL_COLOR, fg=TEXT_COLOR).grid(
                     row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        entry = tk.Entry(container, font=("Segoe UI", 10), width=16)
        entry.insert(0, default)
        entry.grid(row=row, column=1, sticky="ew", pady=6)
        entries[label_text] = entry
    container.columnconfigure(1, weight=1)

    def generate():
        try:
            amplitude = float(entries["Amplitude (A)"].get().strip())
            phase = float(entries["Phase shift θ (radians)"].get().strip())
            analog_frequency = float(entries["Analog frequency (Hz)"].get().strip())
            sampling_frequency = float(entries["Sampling frequency (Hz)"].get().strip())
            raw_count = entries["Number of samples"].get().strip()
            num_samples = int(raw_count)
            if str(num_samples) != raw_count and not raw_count.isdigit():
                raise ValueError("Number of samples must be a positive integer.")
            indices, samples = generate_waveform(
                waveform, amplitude, phase, analog_frequency,
                sampling_frequency, num_samples)
        except ValueError as exc:
            messagebox.showerror("Invalid Parameters", str(exc), parent=dialog)
            return

        signal = (indices, samples)
        name = f"Generated {waveform} (A={amplitude:g}, f={analog_frequency:g}Hz)"
        loaded_signals.append(signal)
        loaded_signal_names.append(name)
        signals_listbox.insert(tk.END, name)
        new_index = len(loaded_signals) - 1
        signals_listbox.selection_clear(0, tk.END)
        signals_listbox.selection_set(new_index)
        signals_listbox.activate(new_index)
        update_signal_count()
        update_selection_count()
        display_signal(indices, samples, name)
        status_label.config(text=f"Generated {waveform.lower()} wave successfully.", fg=SUCCESS_COLOR)
        dialog.destroy()

    button = tk.Button(container, text="Generate Signal", command=generate,
                       bg=PRIMARY_COLOR, fg="white", activebackground=PRIMARY_HOVER,
                       activeforeground="white", relief="flat", cursor="hand2",
                       font=("Arial", 10, "bold"), padx=14, pady=8)
    button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(16, 0))
    entries["Amplitude (A)"].focus_set()
def open_quantization_dialog():
    """Quantize the single selected signal and display encoded values and errors."""
    selected = list(signals_listbox.curselection())
    if len(selected) != 1:
        messagebox.showwarning("Select One Signal", "Please select exactly one signal to quantize.", parent=root)
        return

    source_index = selected[0]
    source_name = loaded_signal_names[source_index]
    source_signal = loaded_signals[source_index]
    dialog = tk.Toplevel(root)
    dialog.title("Task 3 - Signal Quantization")
    dialog.transient(root)
    dialog.configure(bg=PANEL_COLOR)
    dialog.geometry("900x620")
    dialog.minsize(760, 520)

    outer = tk.Frame(dialog, bg=PANEL_COLOR, padx=20, pady=18)
    outer.pack(fill="both", expand=True)
    tk.Label(outer, text="Signal Quantization", font=("Segoe UI", 18, "bold"),
             bg=PANEL_COLOR, fg=TEXT_COLOR).pack(anchor="w")
    tk.Label(outer, text=f"Input signal: {source_name}", font=("Segoe UI", 10),
             bg=PANEL_COLOR, fg=MUTED_COLOR).pack(anchor="w", pady=(3, 12))

    settings = tk.Frame(outer, bg="#F8FAFD", padx=12, pady=10,
                        highlightbackground=BORDER_COLOR, highlightthickness=1)
    settings.pack(fill="x", pady=(0, 12))
    mode_var = tk.StringVar(value="bits")
    tk.Label(settings, text="Quantize by:", font=("Segoe UI", 10, "bold"),
             bg="#F8FAFD", fg=TEXT_COLOR).grid(row=0, column=0, padx=(0, 10))
    ttk.Radiobutton(settings, text="Number of bits", variable=mode_var, value="bits").grid(row=0, column=1, padx=8)
    ttk.Radiobutton(settings, text="Number of levels", variable=mode_var, value="levels").grid(row=0, column=2, padx=8)
    amount_entry = tk.Entry(settings, font=("Segoe UI", 11), width=9, relief="solid", bd=1)
    amount_entry.insert(0, "3")
    amount_entry.grid(row=0, column=3, padx=(8, 0))
    hint = tk.Label(settings, text="3 bits = 8 levels", font=("Segoe UI", 9), bg="#F8FAFD", fg=MUTED_COLOR)
    hint.grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))

    def update_hint(*_):
        try:
            value = int(amount_entry.get())
            if value <= 0:
                raise ValueError
            hint.config(text=(f"{value} bits = {2 ** value} levels" if mode_var.get() == "bits"
                              else f"{value} quantization levels"))
        except ValueError:
            hint.config(text="Enter a positive whole number")
    amount_entry.bind("<KeyRelease>", update_hint)
    mode_var.trace_add("write", update_hint)

    table_frame = tk.Frame(outer, bg=PANEL_COLOR)
    table_frame.pack(fill="both", expand=True)
    columns = ("n", "original", "quantized", "code", "error")
    table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
    headings = {"n": "Sample n", "original": "Original x[n]", "quantized": "Quantized xq[n]",
                "code": "Encoded code", "error": "Error e[n] = x - xq"}
    widths = {"n": 75, "original": 135, "quantized": 145, "code": 130, "error": 180}
    for column in columns:
        table.heading(column, text=headings[column])
        table.column(column, width=widths[column], anchor="center")
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    summary = tk.Label(outer, text="Choose bits or levels, then click Quantize Signal.",
                       font=("Segoe UI", 9), bg=PANEL_COLOR, fg=MUTED_COLOR, anchor="w")
    summary.pack(fill="x", pady=(10, 8))

    def run_quantization():
        try:
            amount = int(amount_entry.get().strip())
            if amount <= 0:
                raise ValueError("Enter a positive whole number.")
            if mode_var.get() == "bits":
                if amount > 16:
                    raise ValueError("Choose between 1 and 16 bits.")
                levels = 2 ** amount
            else:
                levels = amount
                if not 2 <= levels <= 65536:
                    raise ValueError("Choose between 2 and 65536 levels.")
            indices, quantized, codes, errors, step = quantize_signal(source_signal, levels)
        except (ValueError, OverflowError) as exc:
            messagebox.showerror("Invalid Quantization Settings", str(exc), parent=dialog)
            return

        for item in table.get_children():
            table.delete(item)
        bit_width = max(1, math.ceil(math.log2(levels)))
        original_samples = source_signal[1]
        for n, original, q_value, code, error in zip(indices, original_samples, quantized, codes, errors):
            table.insert("", "end", values=(n, f"{original:.6g}", f"{q_value:.6g}",
                                             f"{format(code, f'0{bit_width}b')} (L{code})", f"{error:.6g}"))

        q_name = f"Quantized {source_name} ({levels} levels)"
        e_name = f"Quantization Error {source_name} ({levels} levels)"
        for name in (q_name, e_name):
            if name in loaded_signal_names:
                old_index = loaded_signal_names.index(name)
                loaded_signal_names.pop(old_index)
                loaded_signals.pop(old_index)
        loaded_signals.append((indices.copy(), quantized.copy()))
        loaded_signal_names.append(q_name)
        loaded_signals.append((indices.copy(), errors.copy()))
        loaded_signal_names.append(e_name)
        signals_listbox.delete(0, tk.END)
        for name in loaded_signal_names:
            signals_listbox.insert(tk.END, name)
        q_index = loaded_signal_names.index(q_name)
        signals_listbox.selection_set(q_index)
        signals_listbox.activate(q_index)
        update_signal_count()
        update_selection_count()
        update_signal_summary()
        display_signal(indices, quantized, q_name)
        status_label.config(text=f"Quantized using {levels} levels. Quantized signal and error added to the list.", fg=SUCCESS_COLOR)
        max_error = max((abs(value) for value in errors), default=0.0)
        summary.config(text=f"Levels: {levels}  |  Code width: {bit_width} bits  |  Step Δ: {step:.6g}  |  Max |error|: {max_error:.6g}")

    buttons = tk.Frame(outer, bg=PANEL_COLOR)
    buttons.pack(fill="x")
    tk.Button(buttons, text="Quantize Signal", command=run_quantization, bg=PRIMARY_COLOR,
              fg="white", activebackground=PRIMARY_HOVER, relief="flat", bd=0,
              cursor="hand2", font=("Segoe UI", 10, "bold"), padx=18, pady=9).pack(side="left")
    tk.Button(buttons, text="Close", command=dialog.destroy, bg=SECONDARY_COLOR,
              fg=TEXT_COLOR, relief="flat", bd=0, cursor="hand2",
              font=("Segoe UI", 10), padx=18, pady=9).pack(side="right")


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#EEF3FA"
PANEL_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#2672F3"
PRIMARY_HOVER = "#155ED5"
SECONDARY_COLOR = "#E7EDF6"
TEXT_COLOR = "#142B4D"
MUTED_COLOR = "#64748B"
SUCCESS_COLOR = "#07845A"
ERROR_COLOR = "#C6283D"
INPUT_BG_COLOR = "#F7FAFE"
INPUT_BORDER_COLOR = "#CBD8E8"
HEADER_COLOR = "#17365D"
HEADER_SUBTITLE = "#C6D6EC"
BORDER_COLOR = "#DCE5F0"


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("DSP Signal Processing Lab")

root.geometry("1200x750")

root.minsize(
    800,
    520
)

root.configure(
    bg=BG_COLOR
)


# ============================================================
# APPLICATION MENU
# ============================================================

signal_generation_menu = tk.Menu(root, tearoff=0, font=("Segoe UI", 11),
                                 bg=PANEL_COLOR, fg=TEXT_COLOR,
                                 activebackground=PRIMARY_COLOR, activeforeground="white")
signal_generation_menu.add_command(label="〰  Sine Wave", command=lambda: open_signal_generator("Sine"))
signal_generation_menu.add_command(label="〰  Cosine Wave", command=lambda: open_signal_generator("Cosine"))


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

    if len(selected) == 1:
        index = selected[0]
        indices, samples = loaded_signals[index]
        signal_name = loaded_signal_names[index]
        display_signal(indices, samples, signal_name)
        status_text = f"Displaying: {signal_name}"
    else:
        selected_items = [(loaded_signal_names[i], loaded_signals[i]) for i in selected]
        display_multiple_signals(selected_items, "Selected Signals")
        status_text = f"Displaying {len(selected)} selected signals."

    status_label.config(text=status_text, fg=SUCCESS_COLOR)


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

    signal_count_label.config(text=f"{count} signal(s) loaded")
    if "signal_summary_label" in globals():
        update_signal_summary()


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
            pady=8,
            before=apply_button
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
            pady=8,
            before=apply_button
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

def display_signal(indices, samples, title="Signal"):
    """Display one signal using the currently selected plot representation."""
    display_multiple_signals([(title, (indices, samples))], title)


def display_multiple_signals(named_signals, title="Signals"):
    """Display one or more signals together in the plot."""
    figure.clear()
    ax = figure.add_subplot(111)

    for name, signal in named_signals:
        indices, samples = signal
        if plot_style == "Discrete":
            markerline, stemlines, baseline = ax.stem(indices, samples, label=name)
            try:
                markerline.set_markersize(4)
                stemlines.set_linewidth(1)
            except AttributeError:
                pass
        else:
            ax.plot(indices, samples, marker="o", markersize=3, linewidth=1.5, label=name)

    ax.set_xlabel("n", fontsize=11)
    ax.set_ylabel("x[n]", fontsize=11)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    if len(named_signals) > 1:
        ax.legend(fontsize=8, loc="best")
    figure.tight_layout()
    canvas.draw_idle()


def plot_style_changed(event=None):
    """Update representation and redraw the currently selected signals."""
    global plot_style
    plot_style = plot_style_var.get()
    selected = signals_listbox.curselection()
    if selected:
        items = [(loaded_signal_names[i], loaded_signals[i]) for i in selected]
        display_multiple_signals(items, "Selected Signals" if len(items) > 1 else items[0][0])
        plot_description.config(text=plot_style + " representation")
    else:
        clear_plot()
        plot_description.config(text=plot_style + " representation")


# ============================================================
# CLEAR PLOT
# ============================================================

def clear_plot():
    """
    Clear the graph.
    """

    figure.clear()

    ax = figure.add_subplot(111)
    ax.set_facecolor("#FFFFFF")

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

header_frame = tk.Frame(root, bg=HEADER_COLOR, height=86)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

brand_mark = tk.Label(header_frame, text="∿", font=("Segoe UI", 36, "bold"),
                      bg=HEADER_COLOR, fg="#8AB7FF")
brand_mark.pack(side="left", padx=(24, 14))

header_text_frame = tk.Frame(header_frame, bg=HEADER_COLOR)
header_text_frame.pack(side="left", fill="y", pady=12)

title_label = tk.Label(header_text_frame, text="DSP Signal Processing Lab",
                       font=("Segoe UI", 22, "bold"), bg=HEADER_COLOR, fg="white")
title_label.pack(anchor="w")

subtitle_label = tk.Label(header_text_frame,
                          text="Load, generate and process discrete-time signals",
                          font=("Segoe UI", 10), bg=HEADER_COLOR, fg=HEADER_SUBTITLE)
subtitle_label.pack(anchor="w", pady=(1, 0))

# Large, visible toolbar replaces the tiny menu in the window corner.
toolbar = tk.Frame(root, bg="#F8FAFD", highlightbackground=BORDER_COLOR, highlightthickness=1)
toolbar.pack(fill="x", padx=0, pady=(0, 8))

def toolbar_button(parent, text, command, primary=False):
    return tk.Button(parent, text=text, command=command,
                     bg=PRIMARY_COLOR if primary else "#E8EEF7",
                     fg="white" if primary else TEXT_COLOR,
                     activebackground=PRIMARY_HOVER if primary else "#D8E3F1",
                     activeforeground="white" if primary else TEXT_COLOR,
                     relief="flat", bd=0, cursor="hand2",
                     font=("Segoe UI", 10, "bold"), padx=18, pady=11)

def show_generation_menu(event=None):
    try:
        signal_generation_menu.tk_popup(generation_button.winfo_rootx(),
                                        generation_button.winfo_rooty() + generation_button.winfo_height())
    finally:
        signal_generation_menu.grab_release()

toolbar_button(toolbar, "⌂   Home", lambda: clear_plot(), primary=True).pack(side="left", padx=(18, 8), pady=9)
toolbar_button(toolbar, "📂   Load Signal", load_signal).pack(side="left", padx=7, pady=9)
generation_button = toolbar_button(toolbar, "∿   Signal Generation   ▾", show_generation_menu)
generation_button.pack(side="left", padx=7, pady=9)
toolbar_button(toolbar, "▦   Quantization", open_quantization_dialog, primary=True).pack(side="left", padx=7, pady=9)
toolbar_button(toolbar, "⚙   Operations", lambda: operation_menu.focus_set()).pack(side="left", padx=7, pady=9)
tk.Label(toolbar, text="TASK 1 + TASK 2 + TASK 3", font=("Segoe UI", 9, "bold"),
         bg="#F8FAFD", fg=MUTED_COLOR).pack(side="right", padx=22)

# ============================================================
# MAIN CONTENT
# ============================================================

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True, padx=14, pady=(0, 10))


# ============================================================
# LEFT CONTROL PANEL - RESPONSIVE / SCROLLABLE
# ============================================================

control_container = tk.Frame(
    main_frame,
    bg=BG_COLOR,
    width=380
)

control_container.pack(
    side="left",
    fill="y",
    padx=(0, 15)
)

# Keep the left panel at a predictable width
control_container.pack_propagate(False)

# Canvas allows the controls to scroll vertically
control_canvas = tk.Canvas(
    control_container,
    bg=PANEL_COLOR,
    highlightthickness=0,
    width=350
)

control_scrollbar = ttk.Scrollbar(
    control_container,
    orient="vertical",
    command=control_canvas.yview
)

control_canvas.configure(
    yscrollcommand=control_scrollbar.set
)

control_scrollbar.pack(
    side="right",
    fill="y"
)

control_canvas.pack(
    side="left",
    fill="both",
    expand=True
)

# This is the frame that holds all your existing controls
control_panel = tk.Frame(control_canvas, bg=PANEL_COLOR,
                          highlightbackground=BORDER_COLOR, highlightthickness=1)

control_window = control_canvas.create_window(
    (0, 0),
    window=control_panel,
    anchor="nw"
)


def update_control_scroll_region(event=None):
    # Update after Tk has completed geometry calculations.
    control_canvas.after_idle(
        lambda: control_canvas.configure(
            scrollregion=control_canvas.bbox("all") or (0, 0, 0, 0)
        )
    )


def resize_control_content(event):
    # Make the controls frame fit the available canvas width.
    if event.width > 1:
        control_canvas.itemconfigure(
            control_window,
            width=event.width
        )


control_panel.bind(
    "<Configure>",
    update_control_scroll_region
)

control_canvas.bind(
    "<Configure>",
    resize_control_content
)


# Mouse-wheel scrolling for the left panel (Windows and Linux).
# The handler only scrolls when the mouse is actually over the controls panel.
def scroll_controls(event):
    widget = root.winfo_containing(event.x_root, event.y_root)

    while widget is not None:
        if widget == control_container:
            if getattr(event, "num", None) == 4:       # Linux: wheel up
                control_canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:     # Linux: wheel down
                control_canvas.yview_scroll(1, "units")
            else:                                       # Windows
                delta = getattr(event, "delta", 0)
                if delta:
                    control_canvas.yview_scroll(
                        -1 if delta > 0 else 1,
                        "units"
                    )
            return "break"
        widget = getattr(widget, "master", None)

    return None


root.bind_all("<MouseWheel>", scroll_controls)
root.bind_all("<Button-4>", scroll_controls)
root.bind_all("<Button-5>", scroll_controls)


# ============================================================
# CONTROL TITLE
# ============================================================

control_title = tk.Label(
    control_panel,
    text="Controls",
    font=("Segoe UI", 15, "bold"),
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
    font=("Segoe UI", 10),
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
    font=("Segoe UI", 10, "bold"),
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
    font=("Segoe UI", 9),
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
    font=("Segoe UI", 10),
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
    font=("Segoe UI", 9),
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
    font=("Segoe UI", 10),
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
    font=("Segoe UI", 10),
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
    font=("Segoe UI", 9),
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
    font=("Segoe UI", 9),
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
    font=("Segoe UI", 10, "bold"),
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
    font=("Segoe UI", 9),
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
    font=("Segoe UI", 10, "bold"),
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
    font=("Segoe UI", 9),
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

plot_panel = tk.Frame(main_frame, bg=PANEL_COLOR,
                       highlightbackground=BORDER_COLOR, highlightthickness=1)

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
    text="▥  Signal Visualization",
    font=("Segoe UI", 15, "bold"),
    bg=PANEL_COLOR,
    fg=TEXT_COLOR
)

plot_title.pack(
    side="left"
)


plot_description = tk.Label(
    plot_header,
    text="Discrete-time signal",
    font=("Segoe UI", 9),
    bg=PANEL_COLOR,
    fg=MUTED_COLOR
)

plot_description.pack(
    side="right"
)


plot_style_var = tk.StringVar(value="Discrete")
plot_style_menu = ttk.Combobox(
    plot_header,
    textvariable=plot_style_var,
    values=["Discrete", "Continuous-style"],
    state="readonly",
    width=18
)
plot_style_menu.pack(side="right", padx=(8, 12))
plot_style_menu.bind("<<ComboboxSelected>>", plot_style_changed)


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
    pady=(12, 8)
)

# Compact information and quick-action cards inspired by the approved mockup.
bottom_tools = tk.Frame(plot_panel, bg=PANEL_COLOR)
bottom_tools.pack(fill="x", padx=15, pady=(0, 14))
bottom_tools.columnconfigure(0, weight=3)
bottom_tools.columnconfigure(1, weight=2)

info_card = tk.Frame(bottom_tools, bg="#F8FAFD", highlightbackground=BORDER_COLOR, highlightthickness=1)
info_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
info_heading = tk.Label(info_card, text="▥  Signal Information", font=("Segoe UI", 11, "bold"),
                        bg="#F8FAFD", fg=TEXT_COLOR)
info_heading.pack(anchor="w", padx=12, pady=(9, 3))
signal_summary_label = tk.Label(info_card, text="Select a signal to view its sample count and value range.",
                               font=("Segoe UI", 9), bg="#F8FAFD", fg=MUTED_COLOR,
                               anchor="w", justify="left", wraplength=460)
signal_summary_label.pack(fill="x", padx=12, pady=(0, 10))

quick_card = tk.Frame(bottom_tools, bg="#F8FAFD", highlightbackground=BORDER_COLOR, highlightthickness=1)
quick_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
quick_heading = tk.Label(quick_card, text="⚡  Quick Actions", font=("Segoe UI", 11, "bold"),
                         bg="#F8FAFD", fg=TEXT_COLOR)
quick_heading.pack(anchor="w", padx=12, pady=(9, 5))
quick_buttons = tk.Frame(quick_card, bg="#F8FAFD")
quick_buttons.pack(fill="x", padx=8, pady=(0, 9))

def quick_button(parent, label, command, color=PRIMARY_COLOR, foreground="white"):
    return tk.Button(parent, text=label, command=command, bg=color, fg=foreground,
                     activebackground=PRIMARY_HOVER if color == PRIMARY_COLOR else "#DCE6F3",
                     activeforeground="white" if foreground == "white" else TEXT_COLOR,
                     relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"),
                     padx=8, pady=7)

quick_button(quick_buttons, "Display Selected", display_selected_signal).pack(side="left", fill="x", expand=True, padx=3)
quick_button(quick_buttons, "Show Info", show_signal_info, "#E8E5FF", "#5544B7").pack(side="left", fill="x", expand=True, padx=3)
quick_button(quick_buttons, "Clear Plot", clear_plot, "#FCE7EA", ERROR_COLOR).pack(side="left", fill="x", expand=True, padx=3)


def update_signal_summary(event=None):
    selected = list(signals_listbox.curselection())
    if not selected:
        signal_summary_label.config(text=f"{len(loaded_signals)} signal(s) loaded. Select a signal to see its details.")
        return
    summaries = []
    for i in selected[:3]:
        indices, samples = loaded_signals[i]
        if samples:
            summaries.append(f"{loaded_signal_names[i]}  ·  {len(samples)} samples  ·  min {min(samples):.3g}  ·  max {max(samples):.3g}")
    if len(selected) > 3:
        summaries.append(f"and {len(selected) - 3} more selected…")
    signal_summary_label.config(text="\n".join(summaries) or "Selected signal has no samples.")

signals_listbox.bind("<<ListboxSelect>>", lambda event: (update_selection_count(event), update_signal_summary(event)))


# ============================================================
# MATPLOTLIB FIGURE
# ============================================================

figure = plt.Figure(figsize=(7, 5), dpi=100, facecolor="#FFFFFF")

ax = figure.add_subplot(111)
ax.set_facecolor("#FFFFFF")

ax.set_title("Selected Signals", fontsize=14, fontweight="bold", color=TEXT_COLOR)

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

canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(
    fill="both",
    expand=True
)


def resize_plot(event):
    """Resize the figure to the available plot frame without a resize loop."""
    # Bind this handler to plot_frame (the parent), not the canvas widget.
    # Resizing the figure from the canvas widget's own Configure event can
    # create a feedback loop and cause layout glitches when maximizing.
    if event.width <= 1 or event.height <= 1:
        return

    dpi = figure.get_dpi()
    available_width = max(2, event.width - 30)
    available_height = max(2, event.height - 30)

    new_width = available_width / dpi
    new_height = available_height / dpi

    current_width, current_height = figure.get_size_inches()
    if (abs(current_width - new_width) > 0.05 or
            abs(current_height - new_height) > 0.05):
        figure.set_size_inches(new_width, new_height, forward=False)
        canvas.draw_idle()


plot_frame.bind("<Configure>", resize_plot)


# ============================================================
# FOOTER
# ============================================================

footer_label = tk.Label(root, text="DSP Signal Processing Lab  •  Signal Processing & Generation",
                         font=("Segoe UI", 8), bg=BG_COLOR, fg=MUTED_COLOR)
footer_label.pack(pady=(0, 5))


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
