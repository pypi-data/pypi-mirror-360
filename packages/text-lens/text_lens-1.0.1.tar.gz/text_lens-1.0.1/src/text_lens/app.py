# app.py
import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
import random
import re, math
import tiktoken
from PIL import Image, ImageTk
from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from textstat import flesch_kincaid_grade as fk
from textstat import flesch_reading_ease
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter

sia = SentimentIntensityAnalyzer()
enc = tiktoken.get_encoding("cl100k_base")
graph_canvas = None
stats_lbl = None
closed = False

quotes = [
    '"I think, therefore I am ." - René Descartes',
    '"To be or not to be." - William Shakespeare',
    '"Knowledge is power." - Francis Bacon',
    '"Stay hungry, stay foolish." - Steve Jobs',
    '"Time is money." - Benjamin Franklin',
    '"Simplicity is the ultimate sophistication." - Leonardo da Vinci',
    '"Fortune favors the brave." - Virgil',
    '"Imagination is more important than knowledge." - Albert Einstein',
    '"Power tends to corrupt." - Lord Acton',
    '"The medium is the message." - Marshall McLuhan',
    '"Creativity is intelligence having fun." - Albert Einstein',
    '"Less is more." - Ludwig Mies van der Rohe',
    '"Good artists copy, great artists steal." - Pablo Picasso',
    '"Injustice anywhere is a threat." - Martin Luther King Jr.',
    '"Speak softly and carry a big stick." - Theodore Roosevelt',
    '"Hope is a good breakfast." - Francis Bacon',
    '"Facts are stubborn things." - John Adams'
]

farewells = [
    "See you next writing session",
    "Until next time-keep the words flowing!",
    "Good-bye! May your ideas stay sharp!",
    "Thanks for stopping by-happy typing",
    "Farewell, fellow wordsmith",
    "Catch you later-keep crafting sentences!",
    "Safe travels through the realm of prose",
    "Cheers! Don't forget to save your work",
    "Signing off-may inspirations strike often!",
    "Adiós! Your next story awaits",
    "Good-bye! Keep those commas in line, okay?",
    "Take care, come back with fresh paragraphs!",
    "See you soon, creativity champion!",
    "Bye for now-let the punctuation be with you!",
    "Exciting... but the narrative continues elsewhere"
]

def show_input():
    global graph_canvas, stats_lbl
    input_box.grid()
    scroll.grid()
    analyze.grid()

    # Restore clear button
    clear_btn.config(state="normal")

    # Restore label
    input_lbl.config(text="")
    input_lbl.config(text="📝 Paste your text here for analysis:")

    if graph_canvas is not None:
        graph_canvas.get_tk_widget().grid_remove()
        graph_canvas = None

    # Hide advanced stats
    if stats_lbl is not None:
        stats_lbl.grid_remove()

def show_top_words():
    global graph_canvas
    # Disable clear button
    clear_btn.config(state="disabled")

    # Update label
    input_lbl.config(text="")
    input_lbl.config(text="📊 Top ten word frequencies in your text:")

    # Data
    text = input_box.get("1.0", "end-1c").lower()
    words = re.findall(r"\b\w+\b", text)
    if not words:
        return
    top = Counter(words).most_common(10) or [("none", 0)]
    labels, counts = zip(*reversed(top))

    # Hide widgets
    for w in input_box, scroll, analyze:
        w.grid_remove()

    # Clean up existing graph canvas
    if graph_canvas is not None:
        graph_canvas.get_tk_widget().destroy()
        graph_canvas = None

    # Build new graph
    fig = plt.Figure(figsize=(5, 3))
    graph_canvas = FigureCanvasTkAgg(fig, master=input_frame)

    ax = fig.add_subplot(111)
    ax.barh(labels, counts, color="RoyalBlue")
    ax.set_xlabel("Frequency")
    ax.set_title("Top Words")
    fig.tight_layout()
    graph_canvas.draw()
    plt.close(fig)

    # Place graph
    graph_canvas.get_tk_widget().grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="nsew",
        pady=30
    )

def show_sentence_lengths():
    global graph_canvas

    # Disable clear button
    clear_btn.config(state="disabled")

    # Update label
    input_lbl.config(text="📊 Sentence-length distribution (words per sentence)")

    text = input_box.get("1.0", "end-1c")
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return

    lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]

    # Hide widgets
    for w in input_box, scroll, analyze:
        w.grid_remove()

    # Clean up existing graph canvas
    if graph_canvas is not None:
        graph_canvas.get_tk_widget().destroy()
        graph_canvas = None

    # Build new graph
    fig = plt.Figure(figsize=(5, 3))
    graph_canvas = FigureCanvasTkAgg(fig, master=input_frame)

    # Build histogram
    bins = range(1, max(lengths) + 2)
    ax = fig.add_subplot(111)
    ax.hist(lengths, bins=bins, color="RoyalBlue", edgecolor="white")
    ax.set_xlabel("Sentence length (words)")
    ax.set_ylabel("Number of sentences")
    ax.set_title("Sentence-Length Distribution")
    fig.tight_layout()
    graph_canvas.draw()
    plt.close(fig)

    graph_canvas.get_tk_widget().grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="nsew",
        pady=30
    )

def show_punctuation():
    global graph_canvas

    # Disable clear btn
    clear_btn.config(state="disabled")

    # Update label
    input_lbl.config(text="📊 Punctuation breakdown")

    text   = input_box.get("1.0", "end-1c")
    marks  = {".": "Periods", ",": "Commas", "?": "Questions", "!": "Exclamations"}
    pairs  = [(label, text.count(sym)) for sym, label in marks.items() if text.count(sym) > 0]

    if not pairs:                        # nothing to show
        messagebox.showinfo("No punctuation",
                               "The text contains no . , ? or ! marks.")
        return

    labels, counts = zip(*pairs)

    # Hide widgets
    for w in input_box, scroll, analyze:
        w.grid_remove()

    # Clean up existing graph canvas
    if graph_canvas is not None:
        graph_canvas.get_tk_widget().destroy()
        graph_canvas = None

    # Build pie chart
    fig = plt.Figure(figsize=(4.5, 3))
    graph_canvas = FigureCanvasTkAgg(fig, master=input_frame)

    ax = fig.add_subplot(111)
    ax.pie(
        counts,
        labels=labels,
        autopct=lambda pct: f"{pct:.0f}%" if pct > 3 else "",
        startangle=90,
        wedgeprops=dict(edgecolor="white")
    )
    ax.set_title("Punctuation Usage")
    fig.tight_layout()
    graph_canvas.draw()
    plt.close(fig)

    graph_canvas.get_tk_widget().grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="nsew",
        pady=30
    )

def show_sentiment():
    global graph_canvas

    # Disable clear button
    clear_btn.config(state="disabled")

    # Update label
    input_lbl.config(text="📊 Sentiment per sentence")

    # Break text into sentences
    text = input_box.get("1.0", "end-1c")
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return

    scores = [sia.polarity_scores(s)["compound"] for s in sentences]
    xs = list(range(1, len(sentences) + 1))

    # Hide widgets
    for w in (input_box, scroll, analyze):
        w.grid_remove()

    # Destroy previous figure if any
    if graph_canvas is not None:
        graph_canvas.get_tk_widget().destroy()
        graph_canvas = None

    # Build the chart
    fig = plt.Figure(figsize=(5, 3))
    graph_canvas = FigureCanvasTkAgg(fig, master=input_frame)

    ax = fig.add_subplot(111)
    ax.plot(xs, scores, marker="o")
    ax.axhline(0, lw=1, ls="--", color="grey")
    ax.set_xlabel("Sentence #")
    ax.set_ylabel("Sentiment score")
    ax.set_ylim(-1.05, 1.05)
    ax.set_title("Sentiment Trajectory")
    fig.tight_layout()
    graph_canvas.draw()
    plt.close(fig)

    graph_canvas.get_tk_widget().grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="nsew",
        pady=30
    )

def show_advanced_stats():
    global stats_lbl, graph_canvas

    # Disable clear btn
    clear_btn.config(state="disabled")

    # Hide widgets
    for w in input_box, scroll, analyze:
        w.grid_remove()

    # Clean up existing graph canvas
    if graph_canvas is not None:
        graph_canvas.get_tk_widget().destroy()
        graph_canvas = None

    # Get text
    text = input_box.get("1.0", "end-1c")

    # Reading level
    level = fk(text)

    # Test complexity
    complexity = 100 - flesch_reading_ease(text)

    # Most/least common sentence lengths
    freq = Counter(
        len(re.findall(r'\w+', s))
        for s in re.split(r'[.!?]+', text) if s.strip()
    )

    most_common = [k for k, v in freq.items() if v == max(freq.values())]
    least_common = [k for k, v in freq.items() if v == min(freq.values())]

    # Average words per sentences vs 'ideal'
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    avg = (sum(len(re.findall(r'\w+', s)) for s in sentences) / len(sentences)) if sentences else 0
    verdict = 'below' if avg < 12 else 'above' if avg > 18 else 'ideal'

    # Punctuation density
    punct = len(re.findall(r'[.,!?;:]', text))
    words = len(re.findall(r'\w+', text))

    density = (punct / words * 100) if words else 0

    # Word length distribution
    dist = Counter(len(w) for w in re.findall(r'\w+', text))
    total = sum(dist.values()) or 1
    percentage = {k: round(v / total * 100, 1) for k, v in dist.items()}

    # Lexical diversity
    tokens = re.findall(r'\w+', text.lower())
    ttr = (len(set(tokens)) / len(tokens)) if tokens else 0

    # Overused words
    words = re.findall(r'\w+', text.lower())
    total = len(words) or 1
    overused = sorted(
        (w for w, c in Counter(words).items()
         if c / total > 0.02),
        key=lambda w: -words.count(w)
    )

    # Rare words
    words = re.findall(r"\w+", text.lower())
    rare_count = sum(1 for c in Counter(words).values() if c == 1)

    # Get OPEN AI token count
    openai_tokens = len(enc.encode(text))
    avg_tok_per_sentence = openai_tokens / len(sentences) if sentences else 0

    stats_text = (
        f"Reading level : {level:.1f}\n"
        f"Text complexity score : {complexity:.1f}\n"
        f"Average words/sentence : {avg:.1f} ({verdict})\n"
        f"Most-common sentence len. : {', '.join(map(str, most_common))}\n"
        f"Least-common sentence len. : {', '.join(map(str, least_common))}\n"
        f"Punctuation density : {density:.1f} per 100 words\n"
        f"Lexical diversity : {ttr:.3f}\n"
        f"Rare words : {rare_count}\n"
        f"Overused words : {', '.join(overused)}\n"
        f"Word-length distribution (%):"
        + ', '.join(f" {v}%" for k, v in sorted(percentage.items()))
        + "\n"
        f"OpenAI tokens : {openai_tokens:,} "
        f"(avg {avg_tok_per_sentence:.1f}/sentence)"
    )

    if stats_lbl is None:
        stats_lbl = tk.Label(
            input_frame,
            bg="grey63",
            fg="black",
            font=text_font,
            justify="left",
            anchor="nw",
            wraplength=820,
            bd=7,
            relief="groove"
        )
    stats_lbl.config(text=stats_text)
    stats_lbl.grid(row=1, column=0, columnspan=2, sticky="ew", pady=40)

def on_analyze(input_box, response_box, wpm=200):
    text = input_box.get("1.0", "end-1c")

    tokens = re.findall(r"\b\w+\b", text.lower())
    words  = len(tokens)
    unique = len(set(tokens))
    ttr    = unique / words if words else 0
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    avg_len   = words / len(sentences) if sentences else 0
    m, s      = divmod(math.ceil(words / wpm * 60), 60)

    response_box.delete("1.0", "end")
    response_box.insert("end", f"Words: {words:,}    Sentences: {len(sentences)}\n")
    response_box.insert("end", f"Avg. sentence length: {avg_len:.1f} words\n")
    response_box.insert("end", f"Unique words: {unique:,} \n")
    response_box.insert("end", f"Est. reading time: {m} min {s:02d} sec\n")

def on_right_click(event):
    w, h = 200, 100
    cur_x, cur_y = event.x_root, event.y_root
    x = cur_x
    y = cur_y + 20

    # Keep pop up on screen
    scr_w = window.winfo_screenwidth()
    scr_h = window.winfo_screenheight()
    x = max(0 , x)
    y = min(scr_h - h, y)

    click_win = tk.Toplevel(window)
    click_win.title("Right click")
    click_win.geometry(f"{w}x{h}+{x}+{y}")
    click_win.configure(bg="#2E2E2E")
    click_win.resizable(False, False)

    # Grid
    click_win.grid_columnconfigure(0, weight=1)
    click_win.grid_columnconfigure(1, weight=1)

    # Copy button
    copy_btn = tk.Button(
        click_win,
        text="Copy",
        font=button_font,
        bg="white",
        fg="black",
        activebackground="black",
        activeforeground="white",
        width=3,
        height=1,
        relief="raised",
        bd=7,
        command=lambda: on_copy(click_win)
    )
    copy_btn.grid(row=0, column=0, pady=30)

    # Paste button
    paste_btn = tk.Button(
        click_win,
        text="Paste",
        font=button_font,
        bg="white",
        fg="black",
        activebackground="black",
        activeforeground="white",
        width=3,
        height=1,
        relief="raised",
        bd=7,
        cursor="hand2",
        command=lambda: on_paste(click_win)
    )
    paste_btn.grid(row=0, column=1, pady=30)

def update_clear_state(event=None):
    text_present = bool(input_box.get("1.0", "end-1c").strip())

    chart_dd.config(state="normal" if text_present else "disabled")

def on_chart_select(choice):
    if choice != "Home":
        print("User selected:", choice)
    else:
        print("Back on Home")

    if choice == "Home":
        show_input()
    elif choice == "Top Words":
        show_top_words()
    elif choice == "Sentences":
        show_sentence_lengths()
    elif choice == "Punctuation":
        show_punctuation()
    elif choice == "Advanced Stats":
        show_advanced_stats()
    elif choice == "Sentiment":
        show_sentiment()

def on_clear(input_box, output_box):
    # Remove text inside of input box
    input_box.delete("1.0", tk.END)

    # Remove text inside of ouput_box
    output_box.delete("1.0", tk.END)

    # Disable chart_dd
    chart_dd.config(state="disabled")

def on_copy(window):
    text = input_box.get("1.0", "end-1c")
    window.clipboard_clear()
    window.clipboard_append(text)
    window.destroy()

def on_paste(window):
    clipboard = window.clipboard_get()
    input_box.insert("insert", clipboard)
    window.destroy()
    update_clear_state()

def fade_in_label(label, text, delay=40):
    for i in range(len(text)):
        window.after(i * delay, lambda i=i: label.config(text=text[:i+1]))

def on_close():
    global closed
    closed = True
    plt.close("all")
    window.destroy()

# Main window setup
window = tk.Tk()
window.title("Text Lens")
window.geometry("900x700")
window.configure(bg="grey20")
window.resizable(False, False)

# Fonts
quote_font = tkFont.Font(family="Crimson Text", size=23, slant="italic")
author_font = tkFont.Font(family="Times", size=17, weight="bold")
title_font = tkFont.Font(family="Times", size=27, weight="bold")
text_font = tkFont.Font(family="Helvetica", size=14)
button_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

# One stretching column
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(2, weight=1)

quote_frame = tk.Frame(window, bg="RoyalBlue2")
quote_frame.grid(row=0, column=0, sticky="ew")
quote_frame.grid_columnconfigure(0, weight=1)

# Quote
random_quote = random.choice(quotes)

before_dash, dash, after_dash = random_quote.partition('-')
quote_text = before_dash
author = after_dash
author_text = f"- {author}"

row_quote = tk.Frame(quote_frame, bg="RoyalBlue2")
row_quote.grid(row=0, column=0, sticky="ew")
row_quote.grid_columnconfigure(0, weight=1)

# Quote label
quote = tk.Label(
    row_quote,
    text=quote_text,
    fg="white",
    bg="RoyalBlue2",
    font=quote_font,
    wraplength=840,
    justify="center"
)
quote.grid(row=0, column=0, sticky="n", pady=10)
fade_in_label(quote, quote_text)

# Author label
author = tk.Label(
    row_quote,
    text=author_text,
    fg="white",
    bg="RoyalBlue2",
    font=author_font
)
author.grid(row=1, column=0, sticky="n", padx=5, pady=(0, 15))
fade_in_label(author, author_text)

# Text input box
input_frame = tk.Frame(window, bg="grey20")
input_frame.grid(row=1, column=0, sticky="new", padx=20)
input_frame.grid_columnconfigure(0, weight=1)
input_frame.grid_rowconfigure(1, weight=1)

input_lbl = tk.Label(
    input_frame,
    text="📝 Paste your text here for analysis:",
    fg="white",
    bg="grey20",
    font=text_font
)
input_lbl.grid(row=0, column=0, columnspan=2, sticky="n", pady=15)

input_box = tk.Text(
    input_frame,
    font=text_font,
    wrap="word",
    bd=7,
    relief="groove",
    bg="grey63",
    fg="black",
    height=15
)
input_box.grid(row=1, column=0, sticky="ew")
input_box.bind("<Button-3>", on_right_click)

scroll = tk.Scrollbar(
    input_frame,
    orient="vertical",
    command=input_box.yview
)
scroll.grid(row=1, column=1, sticky="ns")
input_box.config(yscrollcommand=scroll.set)
input_box.bind("<KeyRelease>", update_clear_state)
input_box.bind("<<Paste>>", update_clear_state)
input_box.bind("<<Cut>>", update_clear_state)

# Analyze button
analyze = tk.Button(
    input_frame,
    text="Analyze",
    bg="RoyalBlue2",
    fg="white",
    activebackground="RoyalBlue3",
    activeforeground="#2E2E2E",
    width=14,
    height=1,
    relief="raised",
    bd=7,
    cursor="hand2",
    font=button_font,
    command=lambda: on_analyze(input_box, results_box)
)
analyze.grid(row=2, column=0, pady=15)

# output frame
output_frame = tk.Frame(window, bg="RoyalBlue2")
output_frame.grid(row=2, column=0, sticky="nsew")

# make the column expand
output_frame.grid_columnconfigure(0, weight=1)
output_frame.grid_rowconfigure(1,  weight=1)

result_lbl = tk.Label(
    output_frame,
    text="Basic insights on your text will appear here:",
    fg="white",
    bg="RoyalBlue2",
    font=text_font
)
result_lbl.grid(row=0, column=0, sticky="w", pady=10, padx=20)

results_box = tk.Text(
    output_frame,
    font=text_font,
    wrap="word",
    bd=7,
    relief="groove",
    bg="grey63",
    fg="black",
    width=45,
    height=10
)
results_box.grid(row=1, column=0, sticky="w", pady=(0, 5), padx=5)

# Clear button
clear_btn = tk.Button(
    output_frame,
    text="Clear",
    bg="RoyalBlue2",
    fg="white",
    activebackground="RoyalBlue3",
    activeforeground="#2E2E2e",
    width=10,
    height=1,
    relief="raised",
    bd=7,
    cursor="hand2",
    font=button_font,
    command=lambda: on_clear(input_box, results_box)
)
clear_btn.grid(row=1, column=0, sticky="e", padx=220)

# Graph dropdown
chart_var = tk.StringVar(value="Home")

chart_dd = tk.OptionMenu(
    output_frame,
    chart_var,
    "Home",
    "Top Words",
    "Sentences",
    "Punctuation",
    "Sentiment",
    "Advanced Stats",
    command=on_chart_select
)
chart_dd.config(
    bg="RoyalBlue2",
    fg="white",
    activebackground="RoyalBlue3",
    activeforeground="#2E2E2E",
    font=button_font,
    width=12,
    relief="raised",
    bd=7
)
chart_dd["menu"].config(
    bg="RoyalBlue2",
    fg="white",
    activebackground="RoyalBlue3",
    activeforeground="white",
    font=button_font
)
chart_dd.grid(row=1, column=0, sticky="e", padx=30)
chart_dd.config(state="disabled")

window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()

if closed:
    farewell = tk.Tk()
    farewell.title("Farewell")
    farewell.geometry("900x700")
    farewell.configure(bg="RoyalBlue")
    farewell.resizable(False, False)

    # Fonts
    text_font = tkFont.Font(family="Helvetica", size=14)
    title_font = tkFont.Font(family="Times", size=22, weight="bold")

    message = random.choice(farewells)

    # Farewell label
    farewell_lbl = tk.Label(
        farewell,
        text=message,
        fg="white",
        bg="RoyalBlue",
        font=title_font
    )
    farewell_lbl.pack(pady=20)

    logo_path = Path(__file__).parent / "text-lens-logo.png"

    pil_image = Image.open(logo_path).convert("RGBA")

    target_height = 500
    scale = target_height / pil_image.height
    target_width = int(pil_image.width * scale)

    resized_image = pil_image.resize((target_width, target_height),
                                     Image.Resampling.LANCZOS)
    logo_image = ImageTk.PhotoImage(resized_image)

    logo_label = tk.Label(
        farewell,
        image=logo_image,
        bg="RoyalBlue"
    )
    logo_label.image = logo_image
    logo_label.pack(pady=20)

    # Label
    label = tk.Label(
        farewell,
        bg="RoyalBlue",
        fg="white",
        font=text_font
    )
    label.pack(pady=20)

    # Countdown
    def countdown(n):
        if n > 0:
            label.config(text = f"{n} second{'s' if n != 1 else ''}")
            farewell.after(1000, lambda: countdown(n - 1))
        else:
            label.config(text="Goodbye")
            farewell.after(1500, farewell.destroy)

    countdown(3)

    farewell.mainloop()

def main():
    """Entry point for the text-lens command."""
    pass  # The app runs when the module is imported
