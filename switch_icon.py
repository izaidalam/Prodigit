import sys
import shutil
import os
import subprocess

CONCEPTS = {
    '1': ('icon_emerald_chrono.ico', 'Emerald Chrono'),
    '2': ('icon_swiss_mono.ico', 'Swiss Monochrome'),
    '3': ('icon_cyber_cyan.ico', 'Cyber Cyan Pulse'),
}

def apply_icon(choice='1'):
    choice = str(choice).strip()
    if choice not in CONCEPTS:
        print(f"Invalid option '{choice}'. Choose 1, 2, or 3:")
        for k, v in CONCEPTS.items():
            print(f"  {k}: {v[1]}")
        return

    source_ico, name = CONCEPTS[choice]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(script_dir, source_ico)
    target_path = os.path.join(script_dir, 'prodigit.ico')
    
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found.")
        return

    shutil.copy(src_path, target_path)
    print(f"Set prodigit.ico to {name}")

    # Update Windows Desktop shortcut
    desktop_lnk = r"C:\Users\Zaid alam\Desktop\Prodigit.lnk"
    if os.path.exists(desktop_lnk):
        ps_cmd = f"""
        $sh = New-Object -ComObject WScript.Shell
        $s = $sh.CreateShortcut('{desktop_lnk}')
        $s.IconLocation = '{target_path},0'
        $s.Save()

        Add-Type -TypeDefinition @"
        using System;
        using System.Runtime.InteropServices;
        public class SHNotif {{
            [DllImport("shell32.dll", CharSet = CharSet.Auto, SetLastError = true)]
            public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);
        }}
"@
        [SHNotif]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
        print(f"Updated Desktop shortcut to {name} and refreshed Windows shell!")

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else '1'
    apply_icon(arg)
