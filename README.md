# Prodigit - Desktop Productivity Tracking Widget

A sleek, modern floating desktop widget for tracking your daily productivity sessions on Windows.

---

## Features

- **One-Click Start / Stop Timer**:
  - Click **▶ START PRODUCTIVITY** to note down the start time and begin the real-time live elapsed counter.
  - Click **⏹ STOP SESSION** to automatically calculate the duration, log the stop timestamp, and record the session into local storage.
- **Resilient State Management**:
  - If you close or restart the app while a timer is active, the widget automatically detects the running session and resumes counting accurately.
- **Automated Local Storage (`productivity.db`)**:
  - Stores each session's date, start time, end time, total seconds, and converted hours in a local SQLite database.
- **Default Current Day View**:
  - Always defaults to showing **Today's** total productive hours and session timeline on startup.
- **Historical Navigation & Filtering**:
  - **Day Navigator**: Switch to any previous day (`◀`, `▶`) or click the date to open an interactive calendar picker.
  - **Range Filters**: Instantly aggregate total productivity across **Last 7 Days (Week)**, **Last 30 Days (Month)**, or **Last 90 Days (3 Months)**.
- **Desktop Widget Controls**:
  - **Draggable**: Click and drag from anywhere on the header or body to reposition the widget across your monitors.
  - **Always on Top Toggle**: Click `📌` to pin or unpin the widget over other active windows.
  - **Minimize & Close**: Dedicated `─` and `✕` buttons.
  - **Session Management**: Each logged session has a `🗑` button to delete accidental entries.

---

## How to Run

### Option 1: Double-click Launcher
- Double-click `run.bat` (standard console launcher), or
- Double-click `run_silent.vbs` (runs quietly in the background without a command prompt window).

### Option 2: Terminal / PowerShell
```powershell
python main.py
```
