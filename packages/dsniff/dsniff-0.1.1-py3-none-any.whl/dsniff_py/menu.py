import curses
import subprocess
import sys

# List of available tools and descriptions
TOOLS = [
    ("dsniff", "Sniff credentials across protocols (FTP, HTTP, IMAP, etc.)"),
    ("arpspoof", "ARP spoofing (MITM between host and gateway)"),
    ("dnsspoof", "DNS spoofing using hosts file mappings"),
    ("filesnarf", "Capture and dump NFS file reads"),
    ("mailsnarf", "Capture SMTP mail sessions"),
    ("msgsnarf", "Intercept messaging protocols (IRC, ICQ)",),
    ("urlsnarf", "Extract URLs from HTTP traffic"),
    ("macof", "Flood switch MAC table with random addresses"),
    ("sshow", "Show active sniffing sessions"),
    ("sshmitm", "SSH v1 man-in-the-middle attack"),
    ("webmitm", "HTTPS MITM with forged certificates"),
    ("webspy", "Passive HTTP sniffer"),
    ("tcpkill", "Terminate TCP connections (inject RST)"),
    ("tcpnice", "Throttle TCP flows by advertising small window sizes")
]

def draw_menu(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    current_row = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "dsniff Suite Menu (Use ↑/↓ to navigate, Enter to select, q to quit)"
        stdscr.addstr(0, 0, title)
        for idx, (tool, desc) in enumerate(TOOLS):
            x = 2
            y = idx + 2
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, f"{tool} - {desc}")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, f"{tool} - {desc}")
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(TOOLS) - 1:
            current_row += 1
        elif key in [curses.KEY_ENTER, ord('\n')]:
            return current_row
        elif key in [ord('q'), 27]:  # q or ESC
            return None

def main():
    try:
        idx = curses.wrapper(draw_menu)
        if idx is None:
            sys.exit(0)
        tool = TOOLS[idx][0]
        # Prompt for additional arguments
        args = input(f"Enter arguments for {tool} (or leave blank): ").strip()
        cmd = [tool] + (args.split() if args else [])
        return subprocess.call(cmd)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())