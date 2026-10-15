# Exact CSS & Design Spec for "Swiss Monochrome" from productivity_widget_10_designs.html
DARK_THEME = """
QWidget {
    background-color: transparent;
    color: #E2E8F0;
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 12px;
}

/* Outer Window Frame (Edgy Stark Bauhaus Swiss Monochrome) */
#mainFrame {
    background-color: #000000;
    border-radius: 0px;
    border: 1px solid rgba(255, 255, 255, 0.4);
}

/* Header Bar */
#headerBarContainer {
    background-color: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 8px;
    border-radius: 0px;
}

#appTitle {
    font-size: 12px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.05em;
}

#statusBadgeIdle {
    background-color: transparent;
    color: #FFFFFF;
    border: 1px solid #FFFFFF;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
}

#statusBadgeActive {
    background-color: transparent;
    color: #FFFFFF;
    border: 1px solid #FFFFFF;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
}

#headerIconBtn {
    background-color: rgba(255, 255, 255, 0.05);
    color: #94A3B8;
    border: none;
    border-radius: 0px;
    padding: 2px 6px;
    font-size: 12px;
}

#headerIconBtn:hover {
    color: #FFFFFF;
}

#headerCloseBtn {
    background-color: rgba(255, 255, 255, 0.05);
    color: #94A3B8;
    border: none;
    border-radius: 0px;
    padding: 2px 6px;
    font-size: 12px;
}

#headerCloseBtn:hover {
    color: #FB7185;
}

/* Timer Live Card (Edgy) */
#timerCard {
    background-color: rgba(0, 0, 0, 0.4);
    border-radius: 0px;
    border: 1px solid rgba(255, 255, 255, 0.05);
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
    font-family: 'Fira Code', 'Consolas', monospace;
    letter-spacing: -0.025em;
    margin: 4px 0px;
}

#timerSubtext {
    font-size: 11px;
    color: #94A3B8;
    font-weight: 400;
}

/* Big Action Button (Swiss Typography Mono - Rounded Capsule Pill) */
#startBtn, #stopBtn {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #FFFFFF;
    border-radius: 18px;
    padding: 10px 16px;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

#startBtn:hover, #stopBtn:hover {
    background-color: #D4D4D8;
    color: #000000;
}

#startBtn:pressed, #stopBtn:pressed {
    background-color: #A1A1AA;
    color: #000000;
}

/* Summary Stats Block (Edgy) */
#summaryCard {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 0px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

#summaryNumberBlue {
    font-size: 16px;
    font-weight: 700;
    color: #60A5FA;
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

#summaryNumberWhite {
    font-size: 16px;
    font-weight: 700;
    color: #E2E8F0;
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

#summaryLabel {
    font-size: 10px;
    color: #94A3B8;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Filter Navigation Bar (Edgy) */
#filterBarContainer {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 0px;
    border: none;
    padding: 4px;
}

#filterTab {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 0px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 500;
}

#filterTab:hover {
    color: #FFFFFF;
}

#filterTabSelected {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 0px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* Sessions Scroll Area (Edgy) */
QScrollArea {
    border: none;
    background-color: transparent;
}

#sessionItem {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 0px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 3px 6px;
    margin-bottom: 2px;
}

#sessionItem:hover {
    background-color: rgba(255, 255, 255, 0.08);
}

#sessionTime {
    font-size: 12px;
    font-weight: 600;
    color: #E2E8F0;
}

#sessionDurationGreen {
    font-size: 12px;
    font-weight: 600;
    color: #34D399;
    font-family: 'Fira Code', 'Consolas', monospace;
}

#sessionSubtext {
    font-size: 10px;
    color: #94A3B8;
}

#deleteItemBtn {
    background-color: transparent;
    color: #64748B;
    border: none;
    font-size: 12px;
    padding: 2px 4px;
    border-radius: 0px;
}

#deleteItemBtn:hover {
    color: #FB7185;
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
QWidget#pillRoot {
    background: transparent;
}

#pillFrame {
    background-color: #000000;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.6);
}

#pillFrame:hover {
    background-color: #080808;
    border-color: rgba(255, 255, 255, 0.85);
}

#pillDot {
    font-size: 11px;
    font-weight: bold;
}

#pillText {
    font-size: 12px;
    font-weight: 700;
    color: #FFFFFF;
    font-family: 'Fira Code', 'Consolas', monospace;
    letter-spacing: -0.025em;
}

#pillPlayBtn {
    background-color: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 12px;
    color: #FFFFFF;
    width: 24px;
    height: 24px;
    font-size: 10px;
    font-weight: bold;
}

#pillPlayBtn:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

#pillExpandBtn {
    background-color: transparent;
    border: none;
    color: #94A3B8;
    font-size: 12px;
    padding: 0px;
}

#pillExpandBtn:hover {
    color: #FFFFFF;
}
"""
