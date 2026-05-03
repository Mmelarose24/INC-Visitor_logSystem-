import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import os

# --- OFFICIAL COLORS ---
COLOR_BG = "#FFFFFF"        
COLOR_VIOLET = "#7C3AED"    
COLOR_BLUE = "#1D4ED8"      
COLOR_GREEN = "#059669"     
COLOR_DANGER = "#DC2626"    

def init_db():
    conn = sqlite3.connect('barangay_log.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, contact TEXT, purpose TEXT, date TEXT, time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admin_account (username TEXT, password TEXT)''')
    conn.commit(); conn.close()

def update_clock():
    now = datetime.now().strftime("%I:%M:%S %p")
    clock_label.config(text=now)
    root.after(1000, update_clock)

def load_data():
    for i in tree.get_children(): tree.delete(i)
    conn = sqlite3.connect('barangay_log.db')
    for row in conn.execute("SELECT * FROM visitors ORDER BY id DESC"):
        if not admin_logged_in.get():
            masked_row = (row[0], row[1], "******", "******", row[4], row[5], row[6])
            tree.insert("", tk.END, values=masked_row)
        else:
            tree.insert("", tk.END, values=row)
    conn.close()

# --- ADMIN FEATURES ---
def delete_rec():
    if not admin_logged_in.get():
        messagebox.showwarning("Restricted", "Please Login as Admin First!")
        return
    sel = tree.selection()
    if not sel: return
    if messagebox.askyesno("Confirm", "Are you sure you want to DELETE this record?"):
        rid = tree.item(sel)['values'][0]
        conn = sqlite3.connect('barangay_log.db'); c = conn.cursor()
        c.execute("DELETE FROM visitors WHERE id=?", (rid,))
        conn.commit(); conn.close(); load_data()

def generate_report():
    if not admin_logged_in.get():
        messagebox.showwarning("Restricted", "Please Login as Admin to Print Report!")
        return
    conn = sqlite3.connect('barangay_log.db'); c = conn.cursor()
    c.execute("SELECT username FROM admin_account"); admin_data = c.fetchone()
    admin_name = admin_data[0] if admin_data else "OFFICIAL ADMIN"
    filename = "OFFICIAL_VISITOR_REPORT.txt"
    with open(filename, "w") as f:
        f.write("BARANGAY HALL VISITOR LOG REPORT\n" + "="*50 + "\n")
        f.write(f"PRINTED ON: {datetime.now().strftime('%B %d, %Y | %I:%M %p')}\n\n")
        for r in c.execute("SELECT name, address, contact, purpose, date FROM visitors"):
            f.write(f"NAME: {r[0]}\nADDR: {r[1]}\nCONT: {r[2]}\nWHY:  {r[3]}\nDATE: {r[4]}\n" + "-"*30 + "\n")
        f.write("\n\nVERIFIED BY:\n\n\n______________________________\n")
        f.write(f"NAME: {admin_name.upper()}\nOFFICIAL SIGNATURE")
        conn.close()
    os.startfile(filename)

# --- ADMIN LOGIN & SETUP ---
def open_setup():
    win = tk.Toplevel(root); win.title("Setup"); win.geometry("400x450"); win.configure(bg=COLOR_BG)
    tk.Label(win, text="ACCOUNT SETUP", font=("Arial", 20, "bold"), bg=COLOR_BG, fg=COLOR_VIOLET).pack(pady=30)
    tk.Label(win, text="NEW USERNAME", font=("Arial", 12, "bold"), bg=COLOR_BG, fg=COLOR_BLUE).pack()
    u_e = tk.Entry(win, font=("Arial", 14), highlightthickness=2, highlightbackground=COLOR_BLUE, bd=0, justify="center")
    u_e.pack(pady=10, ipady=10, padx=40, fill="x")
    tk.Label(win, text="NEW PASSWORD", font=("Arial", 12, "bold"), bg=COLOR_BG, fg=COLOR_BLUE).pack(pady=(15,0))
    p_e = tk.Entry(win, font=("Arial", 14), highlightthickness=2, highlightbackground=COLOR_BLUE, bd=0, justify="center")
    p_e.pack(pady=10, ipady=10, padx=40, fill="x")
    def save():
        if u_e.get().strip() and p_e.get().strip():
            conn = sqlite3.connect('barangay_log.db'); c = conn.cursor()
            c.execute("DELETE FROM admin_account"); c.execute("INSERT INTO admin_account VALUES (?, ?)", (u_e.get().strip(), p_e.get().strip()))
            conn.commit(); conn.close(); win.destroy(); messagebox.showinfo("SUCCESS", "ADMIN ACCOUNT SAVED")
    tk.Button(win, text="SAVE ADMIN", command=save, bg=COLOR_GREEN, fg="white", font=("Arial", 14, "bold"), bd=0).pack(pady=30, ipady=10, padx=40, fill="x")

def open_login():
    win = tk.Toplevel(root); win.title("Login"); win.geometry("400x450"); win.configure(bg=COLOR_BG)
    tk.Label(win, text="ADMIN LOGIN", font=("Arial", 20, "bold"), bg=COLOR_BG, fg=COLOR_VIOLET).pack(pady=30)
    tk.Label(win, text="USERNAME", font=("Arial", 12, "bold"), bg=COLOR_BG, fg=COLOR_BLUE).pack()
    u_e = tk.Entry(win, font=("Arial", 14), highlightthickness=2, highlightbackground=COLOR_VIOLET, bd=0, justify="center")
    u_e.pack(pady=10, ipady=10, padx=40, fill="x")
    tk.Label(win, text="PASSWORD", font=("Arial", 12, "bold"), bg=COLOR_BG, fg=COLOR_BLUE).pack(pady=(15,0))
    p_e = tk.Entry(win, show="*", font=("Arial", 14), highlightthickness=2, highlightbackground=COLOR_VIOLET, bd=0, justify="center")
    p_e.pack(pady=10, ipady=10, padx=40, fill="x")
    def verify():
        conn = sqlite3.connect('barangay_log.db'); c = conn.cursor()
        c.execute("SELECT * FROM admin_account"); acc = c.fetchone(); conn.close()
        if acc and u_e.get().strip() == acc[0] and p_e.get().strip() == acc[1]:
            admin_logged_in.set(True); status_label.config(text="● ADMIN ACTIVE", fg=COLOR_GREEN); load_data(); win.destroy()
        else: messagebox.showerror("DENIED", "WRONG CREDENTIALS")
    tk.Button(win, text="UNLOCK SYSTEM", command=verify, bg=COLOR_VIOLET, fg="white", font=("Arial", 14, "bold"), bd=0).pack(pady=30, ipady=10, padx=40, fill="x")

# --- MAIN UI ---
init_db()
root = tk.Tk(); root.title("Barangay Visitor System"); root.geometry("1400x800"); root.configure(bg=COLOR_BG)
admin_logged_in = tk.BooleanVar(value=False)

# HEADER - Fixed Clock Visibility
header = tk.Frame(root, bg=COLOR_VIOLET, height=130); header.pack(fill="x")
tk.Label(header, text="BARANGAY HALL VISITOR SYSTEM", fg="white", bg=COLOR_VIOLET, font=("Arial", 28, "bold")).pack(side="left", padx=50, pady=20)
clock_label = tk.Label(header, text="", fg="white", bg=COLOR_VIOLET, font=("Arial", 22, "bold")); clock_label.pack(side="right", padx=50, pady=20); update_clock()

paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=12, bg=COLOR_VIOLET, sashrelief=tk.FLAT, cursor="sb_h_double_arrow")
paned.pack(fill="both", expand=True, padx=20, pady=20)

# LEFT FORM - Using a scrollable area or reduced padding to ensure SAVE button is seen
left = tk.Frame(paned, bg=COLOR_BG, padx=40, pady=10); paned.add(left, minsize=450)
tk.Label(left, text="VISITOR REGISTRATION", font=("Arial", 20, "bold"), bg=COLOR_BG, fg=COLOR_BLUE).pack(anchor="w", pady=10)

fields_data = [("FULL NAME", "name_entry"), ("ADDRESS", "address_entry"), ("CONTACT #", "contact_entry"), ("PURPOSE", "purpose_entry")]
entries = {}
for label, var in fields_data:
    tk.Label(left, text=label, bg=COLOR_BG, font=("Arial", 11, "bold"), fg=COLOR_BLUE).pack(anchor="w", pady=(5,0))
    entry = tk.Entry(left, font=("Arial", 14), bg=COLOR_BG, highlightthickness=2, highlightbackground=COLOR_BLUE, bd=0)
    entry.pack(fill="x", ipady=8, pady=5)
    entries[var] = entry

def save_visitor():
    data = [entries['name_entry'].get().strip(), entries['address_entry'].get().strip(), entries['contact_entry'].get().strip(), entries['purpose_entry'].get().strip()]
    if all(data):
        d, t = datetime.now().strftime("%B %d, %Y"), datetime.now().strftime("%I:%M %p")
        conn = sqlite3.connect('barangay_log.db'); c = conn.cursor()
        c.execute("INSERT INTO visitors (name, address, contact, purpose, date, time) VALUES (?, ?, ?, ?, ?, ?)", (*data, d, t))
        conn.commit(); conn.close()
        for e in entries.values(): e.delete(0, tk.END)
        load_data(); messagebox.showinfo("SAVED", "VISITOR SUCCESSFULLY RECORDED")
    else: messagebox.showwarning("ERROR", "ALL FIELDS ARE REQUIRED")

# Reduced pady to 20 to ensure it's visible on smaller screens
tk.Button(left, text="SAVE VISITOR INFORMATION", command=save_visitor, bg=COLOR_GREEN, fg="white", font=("Arial", 14, "bold"), bd=0).pack(fill="x", pady=20, ipady=12)

# RIGHT DASHBOARD
right = tk.Frame(paned, bg=COLOR_BG); paned.add(right)
top_bar = tk.Frame(right, bg=COLOR_BG, pady=10); top_bar.pack(fill="x")

tk.Button(top_bar, text="Admin Login", command=open_login, bg=COLOR_BLUE, fg="white", font=("Arial", 11, "bold"), bd=0, padx=15).pack(side="left", padx=5, ipady=6)
tk.Button(top_bar, text="DELETE", command=delete_rec, bg=COLOR_DANGER, fg="white", font=("Arial", 11, "bold"), bd=0, padx=15).pack(side="left", padx=5, ipady=6)
tk.Button(top_bar, text="PRINT REPORT", command=generate_report, bg=COLOR_VIOLET, fg="white", font=("Arial", 11, "bold"), bd=0, padx=15).pack(side="left", padx=5, ipady=6)
status_label = tk.Label(top_bar, text="● RESTRICTED", fg=COLOR_DANGER, bg=COLOR_BG, font=("Arial", 11, "bold")); status_label.pack(side="left", padx=15)
tk.Button(top_bar, text="Setup Admin", command=open_setup, bg="white", fg=COLOR_VIOLET, font=("Arial", 9, "bold"), bd=0).pack(side="right", padx=10)

style = ttk.Style(); style.theme_use("clam")
style.configure("Treeview", background=COLOR_BG, foreground="#000000", fieldbackground=COLOR_BG, rowheight=35, font=("Arial", 11))
style.configure("Treeview.Heading", background=COLOR_BLUE, foreground="white", font=("Arial", 11, "bold"))

tree = ttk.Treeview(right, columns=("ID", "Name", "Address", "Contact", "Purpose", "Date", "Time"), show='headings')
for col in ["ID", "Name", "Address", "Contact", "Purpose", "Date", "Time"]:
    tree.heading(col, text=col); tree.column(col, width=120, anchor="center")
tree.column("ID", width=50); tree.pack(fill="both", expand=True)

load_data()
root.mainloop()