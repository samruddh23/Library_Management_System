import tkinter as tk
from tkinter import messagebox, ttk
import requests

API_URL = "http://localhost:3000/api"

BG_COLOR = "#1e1e24"        
CARD_COLOR = "#2a2a35"      
TEXT_COLOR = "#f4f4f9"      
ACCENT_GREEN = "#00b4d8"    
ACCENT_HOVER = "#0077b6"    
ACCENT_RED = "#ef233c"      

class RoxyLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ROXY Library System")
        self.root.geometry("880x720") 
        self.root.configure(bg=BG_COLOR)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=CARD_COLOR, foreground=TEXT_COLOR, padding=[12, 4], font=("Arial", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT_GREEN)], foreground=[("selected", "#ffffff")])

        title_frame = tk.Frame(root, bg=BG_COLOR)
        title_frame.pack(fill="x", pady=15)
        tk.Label(title_frame, text="ROXY LIBRARY SYSTEM", font=("Helvetica", 20, "bold"), fg=ACCENT_GREEN, bg=BG_COLOR).pack()
        tk.Label(title_frame, text="Management & Distribution Hub", font=("Helvetica", 10, "italic"), fg="#8b8c8f", bg=BG_COLOR).pack()

        self.tabControl = ttk.Notebook(root)
        self.tab1 = tk.Frame(self.tabControl, bg=BG_COLOR)
        self.tab2 = tk.Frame(self.tabControl, bg=BG_COLOR)
        self.tab_student = tk.Frame(self.tabControl, bg=BG_COLOR) # New Tab Frame
        self.tab3 = tk.Frame(self.tabControl, bg=BG_COLOR)
        self.tab4 = tk.Frame(self.tabControl, bg=BG_COLOR)
        
        self.tabControl.add(self.tab1, text='  Search Assets  ')
        self.tabControl.add(self.tab2, text='  Issue & Return  ')
        self.tabControl.add(self.tab_student, text='  Student Workspace  ') # Linked
        self.tabControl.add(self.tab3, text='  Catalog Control  ')
        self.tabControl.add(self.tab4, text='  Analytics & Logs  ') 
        self.tabControl.pack(expand=1, fill="both", padx=15, pady=15)

        self.setup_search_tab()
        self.setup_action_tab()
        self.setup_student_tab() # Initialized
        self.setup_management_tab()
        self.setup_report_tab()

    def create_custom_button(self, parent, text, command, bg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER):
        btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg="white", 
                        font=("Arial", 10, "bold"), activebackground=hover_color, 
                        activeforeground="white", bd=0, padx=15, pady=6, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
        return btn

    def style_entry_label(self, parent, label_text, row, col):
        lbl = tk.Label(parent, text=label_text, font=("Arial", 10), fg="#b0b0b9", bg=CARD_COLOR)
        lbl.grid(row=row, column=col, padx=10, pady=8, sticky="w")
        entry = tk.Entry(parent, font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=1, relief="solid")
        return entry

    # --- TAB 1: SEARCH ---
    def setup_search_tab(self):
        search_frame = tk.Frame(self.tab1, bg=BG_COLOR)
        search_frame.pack(fill="x", pady=10)
        self.search_entry = tk.Entry(search_frame, width=45, font=("Arial", 12), bg=CARD_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=1, relief="solid")
        self.search_entry.pack(side="left", padx=10, ipady=4)
        self.create_custom_button(search_frame, "Search Catalog", self.search_books).pack(side="left", padx=5)

        table_frame = tk.Frame(self.tab1, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, pady=10)
        columns = ('id', 'title', 'author', 'category', 'qty')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        self.tree.heading('id', text='Book ID')
        self.tree.heading('title', text='Title')
        self.tree.heading('author', text='Author')
        self.tree.heading('category', text='Category')
        self.tree.heading('qty', text='Availability Status')
        self.tree.column('id', width=60, anchor="center")
        self.tree.column('title', width=220)
        self.tree.column('author', width=160)
        self.tree.column('category', width=130)
        self.tree.column('qty', width=140, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def search_books(self):
        query = self.search_entry.get()
        try:
            response = requests.get(f"{API_URL}/books?search={query}", timeout=5)
            for item in self.tree.get_children():
                self.tree.delete(item)
            if response.status_code != 200: return
            books = response.json()
            for b in books:
                status_str = f"{b['available_copies']} / {b['total_copies']} Available"
                self.tree.insert('', tk.END, values=(b['book_id'], b['title'], b['author'], b['category'], status_str))
        except Exception as e: messagebox.showerror("Network Alert", f"Error connecting: {e}")

    # --- TAB 2: ACTIONS ---
    def setup_action_tab(self):
        frame1 = tk.LabelFrame(self.tab2, text=" Issue Desk Asset Allocation ", font=("Arial", 10, "bold"), fg=ACCENT_GREEN, bg=CARD_COLOR, bd=1, padx=15, pady=15)
        frame1.pack(fill="x", padx=15, pady=15)
        self.issue_book_id = self.style_entry_label(frame1, "Catalog Book ID:", 0, 0)
        self.issue_book_id.grid(row=0, column=1, padx=10, pady=8, ipady=3)
        self.issue_student_id = self.style_entry_label(frame1, "Borrower Student ID:", 0, 2)
        self.issue_student_id.grid(row=0, column=3, padx=10, pady=8, ipady=3)
        self.create_custom_button(frame1, "Authorize Circulation Issue", self.issue_book).grid(row=1, column=0, columnspan=4, pady=10)

        frame2 = tk.LabelFrame(self.tab2, text=" Return Intake Processing ", font=("Arial", 10, "bold"), fg="#ff9800", bg=CARD_COLOR, bd=1, padx=15, pady=15)
        frame2.pack(fill="x", padx=15, pady=15)
        self.return_issue_id = self.style_entry_label(frame2, "Active Transaction/Issue ID:", 0, 0)
        self.return_issue_id.grid(row=0, column=1, padx=10, pady=8, ipady=3)
        self.create_custom_button(frame2, "Process Inbound Return", self.return_book, bg_color="#ff9800", hover_color="#e68a00").grid(row=1, column=0, columnspan=2, pady=10)

    def issue_book(self):
        try:
            payload = {"book_id": int(self.issue_book_id.get()), "student_id": int(self.issue_student_id.get())}
            res = requests.post(f"{API_URL}/issue", json=payload)
            if res.status_code == 200: messagebox.showinfo("Success", res.json()['message'])
            else: messagebox.showwarning("Warning", res.json().get('error'))
        except: messagebox.showerror("Input Error", "Please check input characters.")

    def return_book(self):
        try:
            payload = {"issue_id": int(self.return_issue_id.get())}
            res = requests.post(f"{API_URL}/return", json=payload)
            if res.status_code == 200:
                data = res.json()
                messagebox.showinfo("Return Confirmed", f"{data['message']}\nOverdue Fine: ${data['fine_amount']}")
            else: messagebox.showwarning("Warning", res.json().get('error'))
        except: messagebox.showerror("Input Error", "Please check input reference index.")

    # --- NEW TAB: STUDENT REGISTRY WORKSPACE ---
    def setup_student_tab(self):
        top_bar = tk.Frame(self.tab_student, bg=BG_COLOR)
        top_bar.pack(fill="x", pady=5)
        
        self.create_custom_button(top_bar, "Fetch & Refresh Registry", self.fetch_students).pack(side="left", padx=10)
        self.student_count_lbl = tk.Label(top_bar, text="Registered Members: --", font=("Helvetica", 11, "bold"), fg=ACCENT_GREEN, bg=BG_COLOR)
        self.student_count_lbl.pack(side="left", padx=20)

        # Split Forms Layout
        forms_frame = tk.Frame(self.tab_student, bg=BG_COLOR)
        forms_frame.pack(fill="x", pady=10)

        # Add Student Box
        add_box = tk.LabelFrame(forms_frame, text=" Enroll New Student ", font=("Arial", 10, "bold"), fg=ACCENT_GREEN, bg=CARD_COLOR, bd=1, padx=10, pady=10)
        add_box.pack(side="left", fill="both", expand=True, padx=10)
        self.stud_name_entry = self.style_entry_label(add_box, "Full Name:", 0, 0)
        self.stud_name_entry.grid(row=0, column=1, padx=5, pady=5, ipady=2)
        self.stud_email_entry = self.style_entry_label(add_box, "Email Address:", 1, 0)
        self.stud_email_entry.grid(row=1, column=1, padx=5, pady=5, ipady=2)
        self.create_custom_button(add_box, "Add Student", self.add_student).grid(row=2, column=0, columnspan=2, pady=5)

        # Delete Student Box
        del_box = tk.LabelFrame(forms_frame, text=" Revoke/Delete Student ", font=("Arial", 10, "bold"), fg=ACCENT_RED, bg=CARD_COLOR, bd=1, padx=10, pady=10)
        del_box.pack(side="right", fill="both", expand=True, padx=10)
        self.stud_del_id = self.style_entry_label(del_box, "Target Student ID:", 0, 0)
        self.stud_del_id.grid(row=0, column=1, padx=5, pady=5, ipady=2)
        self.create_custom_button(del_box, "Remove Student", self.delete_student, bg_color=ACCENT_RED, hover_color="#c1121f").grid(row=1, column=0, columnspan=2, pady=15)

        # Data Sheet Table Viewer
        list_frame = tk.LabelFrame(self.tab_student, text=" Active Registered Student Directory ", font=("Arial", 10, "bold"), fg=TEXT_COLOR, bg=CARD_COLOR, bd=1, padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ('id', 'name', 'email')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.student_tree.heading('id', text='Student ID')
        self.student_tree.heading('name', text='Full Name')
        self.student_tree.heading('email', text='Email Address')
        
        self.student_tree.column('id', width=100, anchor="center")
        self.student_tree.column('name', width=250)
        self.student_tree.column('email', width=350)
        self.student_tree.pack(fill="both", expand=True)

    def fetch_students(self):
        try:
            res = requests.get(f"{API_URL}/students")
            if res.status_code == 200:
                students = res.json()
                self.student_count_lbl.config(text=f"Registered Members:  {len(students)} Students")
                for item in self.student_tree.get_children(): self.student_tree.delete(item)
                for s in students:
                    self.student_tree.insert('', tk.END, values=(s['student_id'], s['name'], s['email']))
        except Exception as e: messagebox.showerror("Error", f"Could not sync student log elements.\n{e}")

    def add_student(self):
        name = self.stud_name_entry.get()
        email = self.stud_email_entry.get()
        if not name or not email: return
        try:
            res = requests.post(f"{API_URL}/students/add", json={"name": name, "email": email})
            if res.status_code == 200:
                messagebox.showinfo("Success", res.json()['message'])
                self.fetch_students()
            else: messagebox.showwarning("Warning", res.json().get('error'))
        except: pass

    def delete_student(self):
        try:
            target_id = int(self.stud_del_id.get())
            res = requests.delete(f"{API_URL}/students/delete/{target_id}")
            if res.status_code == 200:
                messagebox.showinfo("Purged", res.json()['message'])
                self.fetch_students()
            else: messagebox.showwarning("Constraint Block", res.json().get('error'))
        except: messagebox.showerror("Data Error", "Provide numeric codes.")

    # --- TAB 3: CATALOG CONTROL ---
    def setup_management_tab(self):
        add_frame = tk.LabelFrame(self.tab3, text=" Append New Master Book Entry ", font=("Arial", 10, "bold"), fg=ACCENT_GREEN, bg=CARD_COLOR, bd=1, padx=10, pady=10)
        add_frame.pack(fill="x", padx=15, pady=10)
        self.add_title = self.style_entry_label(add_frame, "Book Title:", 0, 0)
        self.add_title.grid(row=0, column=1, padx=5, pady=5, ipady=2)
        self.add_author = self.style_entry_label(add_frame, "Author Name:", 0, 2)
        self.add_author.grid(row=0, column=3, padx=5, pady=5, ipady=2)
        self.add_category = self.style_entry_label(add_frame, "Genre/Category:", 1, 0)
        self.add_category.grid(row=1, column=1, padx=5, pady=5, ipady=2)
        self.add_qty = self.style_entry_label(add_frame, "Initial Quantity:", 1, 2)
        self.add_qty.grid(row=1, column=3, padx=5, pady=5, ipady=2)
        self.create_custom_button(add_frame, "Commit to Catalog Records", self.add_book).grid(row=2, column=0, columnspan=4, pady=10)

        update_frame = tk.LabelFrame(self.tab3, text=" Bulk Inventory Supply Adjustment ", font=("Arial", 10, "bold"), fg="#4a4ae2", bg=CARD_COLOR, bd=1, padx=10, pady=10)
        update_frame.pack(fill="x", padx=15, pady=10)
        self.up_id = self.style_entry_label(update_frame, "Target Book ID:", 0, 0)
        self.up_id.grid(row=0, column=1, padx=5, pady=5, ipady=2)
        self.up_qty = self.style_entry_label(update_frame, "New Total Supply Count:", 0, 2)
        self.up_qty.grid(row=0, column=3, padx=5, pady=5, ipady=2)
        self.create_custom_button(update_frame, "Modify Supply Metrics", self.update_book, bg_color="#4a4ae2", hover_color="#3535b8").grid(row=1, column=0, columnspan=4, pady=10)

        delete_frame = tk.LabelFrame(self.tab3, text=" Safe Record Purging ", font=("Arial", 10, "bold"), fg=ACCENT_RED, bg=CARD_COLOR, bd=1, padx=10, pady=10)
        delete_frame.pack(fill="x", padx=15, pady=10)
        self.del_id = self.style_entry_label(delete_frame, "Target Book ID to Purge:", 0, 0)
        self.del_id.grid(row=0, column=1, padx=5, pady=5, ipady=2)
        self.create_custom_button(delete_frame, "Purge Entry Permanently", self.delete_book, bg_color=ACCENT_RED, hover_color="#c1121f").grid(row=0, column=2, padx=20)

    def add_book(self):
        payload = {"title": self.add_title.get(), "author": self.add_author.get(), "category": self.add_category.get(), "total_copies": self.add_qty.get()}
        if not all(payload.values()): return
        res = requests.post(f"{API_URL}/books/add", json=payload)
        if res.status_code == 200: messagebox.showinfo("Success", "Catalog added.")

    def update_book(self):
        try:
            payload = {"book_id": int(self.up_id.get()), "total_copies": int(self.up_qty.get())}
            res = requests.put(f"{API_URL}/books/update", json=payload)
            messagebox.showinfo("Updated", res.json().get('message', 'Done'))
        except: pass

    def delete_book(self):
        try:
            res = requests.delete(f"{API_URL}/books/delete/{int(self.del_id.get())}")
            messagebox.showinfo("Response", res.json().get('message'))
        except: pass

    # --- TAB 4: ANALYTICS & LOGS ---
    def setup_report_tab(self):
        stats_frame = tk.Frame(self.tab4, bg=BG_COLOR)
        stats_frame.pack(fill="x", pady=5)

        self.create_custom_button(stats_frame, "Refresh System Live Logs", self.fetch_report).pack(side="left", padx=10, pady=5)
        self.avail_lbl = tk.Label(stats_frame, text="Shelved: --", font=("Helvetica", 11, "bold"), fg="#4CAF50", bg=BG_COLOR)
        self.avail_lbl.pack(side="left", padx=20)
        self.borrow_lbl = tk.Label(stats_frame, text="On Loan: --", font=("Helvetica", 11, "bold"), fg="#2196F3", bg=BG_COLOR)
        self.borrow_lbl.pack(side="left", padx=20)

        log_frame = tk.LabelFrame(self.tab4, text=" Active Outbound Circulation Records ", font=("Arial", 10, "bold"), fg=ACCENT_GREEN, bg=CARD_COLOR, bd=1, padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ('issue_id', 'student', 'book', 'date')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=10)
        self.log_tree.heading('issue_id', text='Issue Transaction ID')
        self.log_tree.heading('student', text='Borrowing Student Name')
        self.log_tree.heading('book', text='Book Title Asset')
        self.log_tree.heading('date', text='Date Issued')
        
        self.log_tree.column('issue_id', width=130, anchor="center")
        self.log_tree.column('student', width=180)
        self.log_tree.column('book', width=280)
        self.log_tree.column('date', width=110, anchor="center")
        self.log_tree.pack(fill="both", expand=True)

    def fetch_report(self):
        try:
            res = requests.get(f"{API_URL}/reports")
            data = res.json()
            self.avail_lbl.config(text=f"Shelved Assets: {data['total_available']} Units")
            self.borrow_lbl.config(text=f"On Loan: {data['total_borrowed']} Units")
            for item in self.log_tree.get_children(): self.log_tree.delete(item)
            for record in data.get('logs', []):
                clean_date = record['issue_date'].split('T')[0] if 'T' in record['issue_date'] else record['issue_date']
                self.log_tree.insert('', tk.END, values=(record['issue_id'], record['student_name'], record['book_title'], clean_date))
        except Exception as e: messagebox.showerror("Error", f"Sync failure: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RoxyLibraryApp(root)
    root.mainloop()