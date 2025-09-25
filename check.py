import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import requests
import time
import pyperclip 

try:
    import pyperclip as _pc
    CAN_COPY = True
except Exception:
    CAN_COPY = False

APP_TITLE = "OG IPChecker — Santri IT Edition"

def resolve_domain(domain: str):
    """Return IP address for domain, or raise exception."""
    return socket.gethostbyname(domain.strip())

def fetch_geo(ip: str, timeout=6):
    """Fetch geolocation info from ip-api.com, return dict or None on failure."""
    try:
        url = f"http://ip-api.com/json/{ip}"
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                return data
    except Exception:
        pass
    return None

class IPCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg="#0b0f12")
        self.geometry("780x460")
        self.minsize(640, 420)

        self.bg = "#0b0f12"
        self.panel = "#071017"
        self.accent = "#00ff88"
        self.dim = "#1a242b"
        self.text_color = "#a8f0c6"
        self.muted = "#7aa788"
        self.font_mono = ("Consolas", 11)
        self.font_title = ("Consolas", 14, "bold")

        self.create_widgets()

    def create_widgets(self):

        top = tk.Frame(self, bg=self.bg)
        top.pack(fill="x", padx=12, pady=(12, 0))

        lbl_title = tk.Label(top, text="OG IPChecker", fg=self.accent, bg=self.bg, font=self.font_title)
        lbl_title.pack(side="left")

        lbl_sub = tk.Label(top, text="— hacker vibes, but ethical", fg=self.muted, bg=self.bg, font=self.font_mono)
        lbl_sub.pack(side="left", padx=(8,0))

        main = tk.Frame(self, bg=self.bg)
        main.pack(fill="both", expand=True, padx=12, pady=12)

        left = tk.Frame(main, bg=self.panel, bd=0, relief="flat")
        left.pack(side="left", fill="y", padx=(0,10), ipady=6)

        lbl = tk.Label(left, text="Target (domain or IP):", fg=self.text_color, bg=self.panel, font=self.font_mono)
        lbl.pack(anchor="w", padx=12, pady=(12,4))

        self.entry_domain = tk.Entry(left, bg=self.bg, fg=self.text_color, insertbackground=self.text_color,
                                     font=self.font_mono, width=28, relief="flat")
        self.entry_domain.pack(padx=12, pady=(0,8))

        btn_frame = tk.Frame(left, bg=self.panel)
        btn_frame.pack(padx=12, pady=(0,8), anchor="w")

        self.btn_check = tk.Button(btn_frame, text="▶ Check IP", command=self.on_check,
                                   bg="#0b9072", fg="#00110a", font=self.font_mono, relief="flat")
        self.btn_check.pack(side="left", ipadx=8, ipady=4)

        self.btn_ping = tk.Button(btn_frame, text="⚡ Ping", command=self.on_ping,
                                  bg="#3b6fb0", fg="#e9f7ff", font=self.font_mono, relief="flat")
        self.btn_ping.pack(side="left", padx=(8,0), ipadx=8, ipady=4)

        self.btn_copy = tk.Button(btn_frame, text="⧉ Copy IP", command=self.on_copy,
                                  bg="#444", fg=self.text_color, font=self.font_mono, relief="flat")
        self.btn_copy.pack(side="left", padx=(8,0), ipadx=8, ipady=4)
        if not CAN_COPY:
            self.btn_copy.config(state="disabled", text="⧉ Copy (pip install pyperclip)")

        self.status_var = tk.StringVar(value="Ready.")
        lbl_status = tk.Label(left, textvariable=self.status_var, fg=self.muted, bg=self.panel, font=self.font_mono)
        lbl_status.pack(anchor="w", padx=12, pady=(8,12))

        right = tk.Frame(main, bg=self.bg)
        right.pack(side="left", fill="both", expand=True)

        res_frame = tk.LabelFrame(right, text="Result", fg=self.accent, bg=self.bg, font=self.font_mono, bd=0,
                                  labelanchor="nw")
        res_frame.pack(fill="x", padx=6, pady=(0,8))

        self.txt_result = tk.Text(res_frame, height=10, bg="#071017", fg=self.text_color, font=self.font_mono,
                                  bd=0, padx=8, pady=8, wrap="word")
        self.txt_result.pack(fill="x", padx=6, pady=6)
        self.txt_result.insert("1.0", "Masukkan domain atau IP lalu klik 'Check IP'.\nContoh: example.com atau 8.8.8.8\n")
        self.txt_result.config(state="disabled")

        hist_frame = tk.LabelFrame(right, text="History", fg=self.accent, bg=self.bg, font=self.font_mono, bd=0,
                                  labelanchor="nw")
        hist_frame.pack(fill="both", expand=True, padx=6, pady=(0,6))

        self.list_hist = tk.Listbox(hist_frame, bg="#061217", fg=self.text_color, font=self.font_mono, bd=0,
                                    activestyle="none")
        self.list_hist.pack(side="left", fill="both", expand=True, padx=(6,0), pady=6)
        self.list_hist.bind("<<ListboxSelect>>", self.on_history_select)

        scrollbar = tk.Scrollbar(hist_frame, orient="vertical", command=self.list_hist.yview)
        scrollbar.pack(side="left", fill="y", padx=(0,6), pady=6)
        self.list_hist.config(yscrollcommand=scrollbar.set)

        bottom = tk.Frame(self, bg=self.bg)
        bottom.pack(fill="x", padx=12, pady=(0,10))
        lbl_credit = tk.Label(bottom, text="Made for Santri IT — gunakan untuk tujuan yang etis.", fg=self.muted, bg=self.bg, font=("Consolas",9))
        lbl_credit.pack(side="left")

        self.history = []  
        self.current_ip = None
        self.lock = threading.Lock()

    def set_status(self, text: str):
        self.status_var.set(text)

    def append_result(self, text: str):
        self.txt_result.config(state="normal")
        self.txt_result.insert("end", text + "\n")
        self.txt_result.see("end")
        self.txt_result.config(state="disabled")

    def clear_result(self):
        self.txt_result.config(state="normal")
        self.txt_result.delete("1.0", "end")
        self.txt_result.config(state="disabled")

    def on_check(self):
        domain = self.entry_domain.get().strip()
        if not domain:
            messagebox.showwarning("Input required", "Masukkan domain atau IP tujuan.")
            return

        self.btn_check.config(state="disabled")
        self.set_status("Resolving domain...")
        t = threading.Thread(target=self._do_check, args=(domain,), daemon=True)
        t.start()

    def _do_check(self, domain):
        start = time.time()
        ip = None
        geo = None
        try:
            ip = resolve_domain(domain)
            self.current_ip = ip
            self._safe_append(f"> {domain} -> {ip}")
            self._safe_status("Fetching geolocation...")
            geo = fetch_geo(ip)
            if geo:
                info_lines = [
                    f"ISP: {geo.get('isp','-')}",
                    f"Org: {geo.get('org','-')}",
                    f"Country: {geo.get('country','-')} ({geo.get('countryCode','')})",
                    f"Region: {geo.get('regionName','-')} / {geo.get('region','-')}",
                    f"City: {geo.get('city','-')}",
                    f"ZIP: {geo.get('zip','-')}",
                    f"Lat,Lon: {geo.get('lat','-')}, {geo.get('lon','-')}",
                ]
                self._safe_append("\n".join(info_lines))
            else:
                self._safe_append("(No geolocation info or request failed.)")
            elapsed = time.time() - start
            self._safe_append(f"[done in {elapsed:.2f}s]")
            tstr = time.strftime("%Y-%m-%d %H:%M:%S")
            with self.lock:
                self.history.insert(0, (domain, ip, tstr, geo))
            self._safe_update_history_list()
        except Exception as e:
            self._safe_append(f"Error: {str(e)}")
        finally:
            self._safe_status("Ready.")
            self.btn_check.config(state="normal")

    def on_ping(self):
        ip = None
        domain = self.entry_domain.get().strip()
        if domain:
            try:
                ip = resolve_domain(domain)
            except Exception as e:
                messagebox.showerror("Resolve failed", f"Gagal resolve domain: {e}")
                return
        elif self.current_ip:
            ip = self.current_ip
        else:
            messagebox.showwarning("No target", "Masukkan domain atau IP untuk ping.")
            return

        self.set_status(f"Pinging {ip} ...")
        self.btn_ping.config(state="disabled")
        t = threading.Thread(target=self._do_ping, args=(ip,), daemon=True)
        t.start()

    def _do_ping(self, ip):
        ports = [80, 443, 53]
        best = None
        for p in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.5)
                start = time.time()
                s.connect((ip, p))
                elapsed = (time.time() - start) * 1000.0
                s.close()
                best = elapsed
                break
            except Exception:
                continue
        if best is not None:
            self._safe_append(f"Ping (approx): {best:.2f} ms to {ip}")
        else:
            self._safe_append("Ping failed (no reachable TCP port).")
        self._safe_status("Ready.")
        self.btn_ping.config(state="normal")

    def on_copy(self):
        if not CAN_COPY:
            messagebox.showinfo("Copy not available", "Install pyperclip: pip install pyperclip")
            return
        if not self.current_ip:
            messagebox.showwarning("No IP", "Belum ada IP untuk di-copy.")
            return
        try:
            _pc.copy(self.current_ip)
            self._safe_append(f"IP {self.current_ip} copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Copy failed", str(e))

    def _safe_update_history_list(self):
        self.after(0, self._update_history_list)

    def _update_history_list(self):
        self.list_hist.delete(0, "end")
        for item in self.history:
            domain, ip, tstr, _ = item
            self.list_hist.insert("end", f"{tstr} — {domain} → {ip}")

    def on_history_select(self, event):
        sel = event.widget.curselection()
        if not sel:
            return
        idx = sel[0]
        item = self.history[idx]
        domain, ip, tstr, geo = item
        self.clear_result()
        self.append_result(f"{tstr}  |  {domain} -> {ip}\n")
        if geo:
            lines = [
                f"ISP: {geo.get('isp','-')}",
                f"Org: {geo.get('org','-')}",
                f"Country: {geo.get('country','-')} ({geo.get('countryCode','')})",
                f"Region: {geo.get('regionName','-')} / {geo.get('region','-')}",
                f"City: {geo.get('city','-')}",
                f"ZIP: {geo.get('zip','-')}",
                f"Lat,Lon: {geo.get('lat','-')}, {geo.get('lon','-')}",
            ]
            self.append_result("\n".join(lines))
        else:
            self.append_result("(No geolocation)")

    def _safe_append(self, text):
        self.after(0, lambda: self.append_result(text))

    def _safe_status(self, text):
        self.after(0, lambda: self.set_status(text))

def main():
    app = IPCheckerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
