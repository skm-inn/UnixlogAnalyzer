============================================================
  LogAnalyzer — Unix Log Search & AI Analysis Tool
  Version 1.0.0
============================================================

------------------------------------------------------------
  WHAT IS THIS TOOL?
------------------------------------------------------------

LogAnalyzer is a desktop-style application that runs inside
your terminal (command prompt / SSH session). It helps you
search through server log files quickly — no coding needed.

Think of it like a "smart Find & Replace" for your server
logs, but instead of just finding text, it can also:

  • Show you exactly which files and lines contain the issue
  • Save a clean copy of only the relevant files
  • Ask an AI to explain what went wrong and how to fix it

Who is it for?
  - System administrators who need to investigate server errors
  - Developers looking for exceptions or crash details in logs
  - Support teams troubleshooting production issues
  - Anyone who needs to search across many log files at once


------------------------------------------------------------
  WHAT YOU WILL NEED (Prerequisites)
------------------------------------------------------------

1. Python 3.8 or newer
   ─────────────────────
   Check if you already have it by running:

     python --version
       OR
     python3 --version

   If you see "Python 3.8" or higher, you are good.

   If not, download Python from:  https://www.python.org/downloads/
   (Choose the latest version — click "Download Python 3.x.x")

   On Linux/Mac you can also install via:
     sudo apt install python3        (Ubuntu/Debian)
     sudo yum install python3        (CentOS/RHEL)
     brew install python             (macOS with Homebrew)


2. The LogAnalyzer libraries (one-time setup)
   ────────────────────────────────────────────
   Open a terminal in the LogAnalyzer folder and run:

     pip install -r requirements.txt

   This installs four small libraries:
     • textual      — draws the interactive screens
     • rich         — makes colors and tables look nice
     • huggingface_hub — connects to free AI models online
     • requests     — used to talk to a local AI (Ollama)

   If "pip" is not found, try:  pip3 install -r requirements.txt

   You only need to do this ONCE. After that, the app is ready.


------------------------------------------------------------
  OPTIONAL: AI ANALYSIS FEATURE
------------------------------------------------------------

The tool can automatically analyze your logs and suggest
fixes using AI. There are three options (it picks the best
one available automatically):

  Option A — HuggingFace (free, uses internet)
  ─────────────────────────────────────────────
  Sign up free at:  https://huggingface.co
  Go to:  https://huggingface.co/settings/tokens
  Create a token and set it in your terminal:

    Windows:
      set HUGGINGFACE_API_TOKEN=hf_your_token_here

    Linux / Mac:
      export HUGGINGFACE_API_TOKEN=hf_your_token_here

  Option B — Ollama (free, works offline)
  ─────────────────────────────────────────
  Download from:  https://ollama.com
  After installing, run:  ollama pull mistral
  The app will detect Ollama automatically.

  Option C — No AI (always works)
  ─────────────────────────────────
  If neither A nor B is set up, the tool creates a
  ready-to-paste prompt file. You can copy its contents
  into ChatGPT, Claude.ai, or Gemini yourself.

  You do NOT need any AI setup to use the search features.


------------------------------------------------------------
  HOW TO START THE APPLICATION
------------------------------------------------------------

Step 1: Open a terminal (or SSH into your server)

Step 2: Go to the LogAnalyzer folder:

          cd /path/to/LogAnalyzer

Step 3: Run the app:

          python loganalyzer.py

        If that does not work, try:

          python3 loganalyzer.py

Step 4: The application opens on screen. Use your keyboard
        to navigate — no mouse needed (though mouse usually
        works too).

To quit at any time:  press Ctrl + Q


------------------------------------------------------------
  HOW TO USE THE APPLICATION (Step by Step)
------------------------------------------------------------

STEP 1 — Welcome Screen
  Press Enter or click "Start" to begin.


STEP 2 — Enter Log Folder Paths
  Type the full path to the folder(s) where your log files
  are stored. You can add up to 5 folders.

  Examples:
    /var/log/myapp
    /home/ubuntu/logs
    C:\Logs\AppServer        (Windows)

  Path 1 is required. The rest are optional.
  A green ✓ appears when the path is valid.
  Press "Validate & Next" when ready.


STEP 3 — Enter Your Search Term
  Type the word or phrase you are looking for.

  Examples:
    ERROR
    OutOfMemoryError
    connection refused
    NullPointerException

  The search is NOT case-sensitive, so "error" and "ERROR"
  find the same results.

  Optionally, enter a File Name Filter to search only
  certain types of files:
    *.log        — search only .log files
    app_*.log    — search only files starting with "app_"
    (leave blank to search ALL files)

  Press "Search" when ready.


STEP 4 — Search Progress
  Watch as the tool scans your files. You will see:
    • How many files have been scanned
    • How many matches found so far
    • Which file is currently being read

  Press "Cancel" at any time to stop early.


STEP 5 — View Results
  A table shows every line that matched your search term:
    • File Path  — which file it was found in
    • Line       — the exact line number
    • Matched Text — the content of that line

  From here you can:

    [ Export TXT ]   — saves a plain text report of all
                       matches to the "lookup" folder

    [ Copy Files ► ] — copies ONLY the matched files into
                       a new folder so you can safely work
                       with them (your originals are never
                       touched or changed)

    [ ◄ New Search ] — start a fresh search


STEP 6 — Copy Confirmation
  The tool shows you how many files will be copied and
  where they will go:

    lookup/ERROR_20260319_143022/   (folder name = your
                                     search term + date/time)

  Press "Start Copy" to proceed.
  When done, you will see a green "Done!" message.

  Then press "Analyze & Recommend ►" to use AI analysis,
  or go back to results.


STEP 7 — AI Context (optional)
  You can describe your server/application in plain English
  to help the AI give better advice. For example:

    "This is a Java web application running on Ubuntu with
     PostgreSQL database and Nginx reverse proxy."

  This is optional — you can leave it blank and press
  "Analyze ►" and the AI will figure it out from the logs.

  The screen also shows which AI engine will be used.


STEP 8 — AI Analysis
  The AI reads the copied log files and streams its analysis
  live on screen. You will see it "typing" the report in
  real time. This usually takes 30–120 seconds.

  When done, press "View Report ►".


STEP 9 — AI Report
  The final report contains:
    • Errors Identified — what exactly went wrong
    • Root Cause Analysis — why it happened
    • Recommendations — how to fix it
    • Prevention — how to stop it happening again

  The report is also saved automatically as a Markdown file
  inside your lookup folder so you can share it later.

  Press "◄ Back" or "▶ New Search" when done.


------------------------------------------------------------
  WHERE ARE MY OUTPUT FILES SAVED?
------------------------------------------------------------

All output goes into the  "lookup"  folder inside LogAnalyzer.
Your original log files are NEVER modified or deleted.

  lookup/
    ERROR_20260319_143022/       ← one folder per search run
      app/
        application.log          ← copy of matched files
      web/
        error.log
      search_report_*.txt        ← plain text match list
      analysis_report_*.md       ← AI analysis report
      analysis_prompt_*.md       ← (if no AI) paste-ready prompt


------------------------------------------------------------
  KEYBOARD SHORTCUTS
------------------------------------------------------------

  Tab          Move to the next field or button
  Shift+Tab    Move to the previous field or button
  Enter        Press the focused button / confirm
  ↑ ↓          Scroll through results table
  Ctrl+Q       Quit the application at any time
  F1           Show a quick help reminder


------------------------------------------------------------
  TROUBLESHOOTING
------------------------------------------------------------

Problem:  "python: command not found"
Solution: Try "python3" instead. Or install Python from
          https://www.python.org/downloads/

Problem:  "No module named textual" (or similar)
Solution: Run:  pip install -r requirements.txt
          from inside the LogAnalyzer folder.

Problem:  "Permission denied" on a log path
Solution: The path exists but your user account does not
          have read access. Ask your administrator for
          read permission on that folder.

Problem:  The screen looks broken / garbled
Solution: Make your terminal window wider (at least 100
          characters wide). The app works best in a
          full-screen or maximized terminal window.

Problem:  AI analysis says "No AI engine detected"
Solution: This is normal if you have not set up HuggingFace
          or Ollama. The app will still export a prompt file
          you can paste into any AI chatbot manually.


------------------------------------------------------------
  QUICK START (summary)
------------------------------------------------------------

  1.  pip install -r requirements.txt      (first time only)
  2.  python loganalyzer.py
  3.  Enter your log folder path(s)
  4.  Enter a search word (e.g. ERROR)
  5.  Browse results → Copy files → Analyze with AI

That's it!


------------------------------------------------------------
  PROJECT LINKS
------------------------------------------------------------

  GitHub:   https://github.com/skm-inn/UnixlogAnalyzer
  Issues:   https://github.com/skm-inn/UnixlogAnalyzer/issues

============================================================
