# text-lens
Turn any block of text into clear, insight-packed charts.

<p align="left">
  <img src="text-lens-logo.png"
       alt="text-lens-logo"
       width="200">
</p>

## Demo

Watch a quick preview below (GIF)

### 🔹 Preview (GIF)
![Text Lens - Preview](https://github.com/adrirubio/demo-files/raw/main/text-lens-demo.gif)

## Features

#### Core Features
- Text Analysis Engine: Analyzes word count, sentence count, unique words, and estimated reading time
- Interactive Text Input: Multi-line text box with scrollbar and custom right-click copy/paste menu
- Visual Data Charts: Generate bar charts, histograms, pie charts, and sentiment analysis graphs from text data
- Advanced Statistics: Calculate reading level, complexity scores, lexical diversity, OpenAI token counts, and more
- Dynamic Interface: Switches between input view and various visualization displays with state-aware controls
- Clear Functionality: One-click clearing of both input and output areas

#### Visualization Features
- Top Words Chart: Horizontal bar chart showing 10 most frequent words in text
- Sentence Length Distribution: Histogram displaying words per sentence patterns
- Punctuation Breakdown: Pie chart analyzing usage of periods, commas, questions, exclamations
- Sentiment Analysis: Line chart tracking emotional trajectory across sentences
- Advanced Stats: In-depth metrics including:
  - Readability scores (Flesch-Kincaid, Gunning Fog, SMOG)
    - OpenAI token count with cl100k_base encoding
    - Vocabulary diversity metrics (Type-Token Ratio, rare words)
    - Sentence pattern analysis (most/least common lengths)
    - Word usage statistics (most/least common lengths)
    - Punctuation density per 100 words

## Installation

### Prerequisites
- Python 3.8 or higher

### Install from PyPI
```bash
pip install text-lens
```

Or with uv:
```bash
uv pip install text-lens
```

### Run the application
```bash
python -m text_lens
```

Or after installation:
```bash
text-lens
```

### Install from source

1. **Clone the repository**
   ```bash
   git clone https://github.com/adrirubio/text-lens.git
   cd text-lens
   ```

2. **Install the package**
   ```bash
   pip install .
   ```

3. **Run the application**
   ```bash
   python -m text_lens
   ```

### Optional: Global Hotkey Setup (F5)

To launch Text Lens with the F5 key from anywhere on your system

1. **Start the hotkey daemon**
   ```bash
   python hotkey_daemon.py
   ```

2. **Keep it running in the background**
   - The daemon will listen for F5 key presses
   - Press F5 anytime to launch Text Lens
   - Press Ctrl-C to stop the daemon

3. **Auto-start on boot (Linux)**
   Add to your startup applications or create a systemd service:
   ```bash
   # Create a systemd service file
   sudo nano /etc/systemd/system/text-lens-hotkey.service
   ```
   Add the following content:
   ```ini
   [Unit]
   Description=Text Lens Hotkey Daemon
   After=graphical.target

   [Service]
   Type=simple
   ExecStart=/usr/bin/python3 /path/to/text-lens/hotkey_daemon.py
   Restart=on-failure
   User=YOUR_USERNAME

   [Install]
   WantedBy=default.target
   ```
   Enable and start service:
   ```bash
   sudo systemctl enable text-lens-hotkey
   sudo systemctl start text-lens-hotkey
   ```
## Usage

1. **Launch the app** using either:
    - Direct command: `python -m text_lens` or `text-lens`
    - F5 hotkey (if daemon is running)

2. **Enter your text** in the large text area
   - Type directly or paste from clipboard
   - Right-click for copy/paste menu

3. **Get instant analysis** with the Analyze button
   - Word count and reading time
   - Sentence statistics
   - Unique word count

4. **Explore visualizations** via the dropdown menu:
   - **Top Words**: See your most common words
   - **Sentence Lengths**: Understand your writing rhythm
   - **Punctuation**: Analyze your punctuation patterns
   - **Sentiment**: Track emotional flow across sentences
   - **Advanced Stats**: Deep dive into readability metrics

5. **Clear and start over** with the Clear button

## Screenshots

Home:<br>
![Home](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/home.png)

Copy and Paste:<br>
![Copy and Paste](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/copy-paste.png)

Basic Insights:<br>
![Basic Insights](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/basic-insights.png)

Top Words:<br>
![Top Words](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/top-words.png)

Sentence Length:<br>
![Sentence Length](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/sentence-length.png)

Punctuation:<br>
![Punctuation](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/punctuation.png)

Sentiment:<br>
![Sentiment](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/sentiment.png)

Advanced Stats:<br>
![Advanced Stats](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/advanced-stats.png)

Goodbye:<br>
![Goodbye](https://raw.githubusercontent.com/adrirubio/demo-files/main/text-lens-screenshots/goodbye.png)

