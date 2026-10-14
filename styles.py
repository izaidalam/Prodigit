# Exact Vector Match for Prodigit Design (Left Concept)
DARK_THEME = """
QWidget {
    background-color: transparent;
    color: #F1F5F9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}

#mainFrame {
    background-color: #000000;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.16);
}

/* Header Bar */
#headerBar {
    background-color: transparent;
    padding: 0px;
}

#appTitle {
    font-size: 13px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.8px;
}

#statusBadgeIdle {
    background-color: transparent;
    color: #94A3B8;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 10px;
    padding: 1px 7px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

#statusBadgeActive {
    background-color: rgba(16, 185, 129, 0.12);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.45);
    border-radius: 10px;
    padding: 1px 7px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

#headerIconBtn {
    background-color: rgba(255, 255, 255, 0.06);
    color: #94A3B8;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: bold;
}

#headerIconBtn:hover {
    background-color: rgba(255, 255, 255, 0.15);
    color: #FFFFFF;
    border-color: rgba(255, 255, 255, 0.2);
}

#headerCloseBtn {
    background-color: rgba(255, 255, 255, 0.06);
    color: #94A3B8;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: bold;
}

#headerCloseBtn:hover {
    background-color: #EF4444;
    color: #FFFFFF;
    border-color: #EF4444;
}

/* Timer Inset Card */
#timerCard {
    background-color: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

#timerTopLabel {
    font-size: 11px;
    color: #94A3B8;
    font-weight: 500;
}

#timerLabel {
    font-size: 34px;
    font-weight: 800;
    color: #FFFFFF;
    font-family: 'Consolas', 'Courier New', monospace;
    letter-spacing: 0.5px;
    margin: 2px 0px;
}

#timerSubtext {
    font-size: 11px;
    color: #94A3B8;
}

/* Big Action Button (Exact rounded pill match for both Start & Stop) */
#startBtn, #stopBtn {
    background-color: #FFFFFF;
    color: #000000;
    border: none;
    border-radius: 18px;
    padding: 9px 16px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

#startBtn:hover, #stopBtn:hover {
    background-color: #E2E8F0;
    color: #000000;
}

#startBtn:pressed, #stopBtn:pressed {
    background-color: #CBD5E1;
    color: #000000;
}

/* Summary Card */
#summaryCard {
    background-color: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

#summaryNumberBlue {
    font-size: 18px;
    font-weight: 800;
    color: #60A5FA;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

#summaryNumberWhite {
    font-size: 16px;
    font-weight: 800;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, sans-serif;
}

#summaryLabel {
    font-size: 10px;
    color: #94A3B8;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Filter Navigation Bar */
#filterBarContainer {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 3px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

#filterTab {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 7px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}

#filterTab:hover {
    color: #FFFFFF;
}

#filterTabSelected {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 700;
}

/* Date Navigator */
#dateNavContainer {
    background-color: transparent;
    padding: 0px;
}

#dateNavBtn {
    background-color: rgba(255, 255, 255, 0.04);
    color: #CBD5E1;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: bold;
}

#dateNavBtn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #FFFFFF;
}

#currentDateLabel {
    font-size: 12px;
    font-weight: 700;
    color: #E2E8F0;
}

/* Sessions Scroll Area */
QScrollArea {
    border: none;
    background-color: transparent;
}

#sessionItem {
    background-color: rgba(255, 255, 255, 0.04);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 9px 12px;
    margin-bottom: 4px;
}

#sessionItem:hover {
    border-color: rgba(255, 255, 255, 0.15);
    background-color: rgba(255, 255, 255, 0.06);
}

#sessionTime {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
}

#sessionDurationGreen {
    font-size: 13px;
    font-weight: 800;
    color: #10B981;
    font-family: 'Consolas', monospace;
}

#sessionSubtext {
    font-size: 11px;
    color: #94A3B8;
}

#deleteItemBtn {
    background-color: transparent;
    color: #64748B;
    border: none;
    font-size: 12px;
    padding: 2px 4px;
    border-radius: 4px;
}

#deleteItemBtn:hover {
    color: #EF4444;
}

/* Custom Scrollbar */
QScrollBar:vertical {
    border: none;
    background: rgba(255, 255, 255, 0.04);
    width: 6px;
    border-radius: 3px;
    margin: 0px 0px 0px 2px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.35);
    border-radius: 3px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.65);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ================= FLOATING BOTTOM PILL DOCK ================= */
/* Outer window of pill must have zero background */
QWidget#pillRoot {
    background: transparent;
}

#pillFrame {
    background-color: #000000;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.35);
}

#pillFrame:hover {
    background-color: #0A0A0A;
    border-color: rgba(255, 255, 255, 0.6);
}

#pillDot {
    font-size: 12px;
    font-weight: bold;
}

#pillText {
    font-size: 12px;
    font-weight: 700;
    color: #F8FAFC;
    font-family: 'Consolas', 'Segoe UI', monospace;
}

#pillPlayBtn {
    background-color: #FFFFFF;
    border: none;
    border-radius: 12px;
    color: #000000;
    width: 24px;
    height: 24px;
    font-size: 10px;
    font-weight: 900;
}

#pillPlayBtn:hover {
    background-color: #E2E8F0;
}

#pillExpandBtn {
    background-color: transparent;
    border: none;
    color: #94A3B8;
    font-size: 12px;
    padding: 2px;
}

#pillExpandBtn:hover {
    color: #FFFFFF;
}
"""
