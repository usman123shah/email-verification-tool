import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import smtplib
import dns.resolver
import time

class EmailVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📧 Email Verifier Tool")
        self.root.geometry("700x600")
        self.root.config(bg="#f4f4f4")

        self.emails = []
        self.results = []
        self.current_index = 0
        self.file_path = ""

        self.header = tk.Label(root, text="Email Verifier", font=("Helvetica", 20, "bold"), bg="#f4f4f4", fg="#333")
        self.header.pack(pady=20)

        self.upload_btn = tk.Button(root, text="📂 Upload CSV and Verify", font=("Helvetica", 12), bg="#4CAF50", fg="white", padx=20, pady=10, command=self.select_file)
        self.upload_btn.pack(pady=10)

        self.time_label = tk.Label(root, text="", font=("Helvetica", 11), bg="#f4f4f4", fg="#777")
        self.time_label.pack()

        self.result_text = tk.Text(root, wrap=tk.WORD, height=25, width=80, font=("Consolas", 10), bg="white", fg="#222", borderwidth=2, relief="solid")
        self.result_text.pack(padx=20, pady=10)
        self.result_text.config(state=tk.DISABLED)

        self.reset_btn = tk.Button(root, text="🔄 Reset", font=("Helvetica", 12), bg="#FF5722", fg="white", padx=15, pady=8, command=self.reset_page)
        self.reset_btn.pack_forget()

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not self.file_path:
            return

        self.read_emails()
        if not self.emails:
            messagebox.showwarning("Warning", "No emails found in the file.")
            return

        est_time = len(self.emails) * 1  # assume 1 sec per email
        self.time_label.config(text=f"Estimated Time: ~{est_time} seconds")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)

        self.current_index = 0
        self.results = []
        self.verify_next()

    def read_emails(self):
        self.emails = []
        try:
            with open(self.file_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and len(row) > 0:
                        self.emails.append(row[0])
        except:
            messagebox.showerror("Error", "File could not be read.")

    def check_email(self, email):
        try:
            domain = email.split('@')[1]
            records = dns.resolver.resolve(domain, 'MX')
            mx_record = str(records[0].exchange)
            smtp = smtplib.SMTP(mx_record)
            smtp.helo()
            smtp.mail('test@example.com')
            code, _ = smtp.rcpt(email)
            smtp.quit()
            return "Valid" if code == 250 else "Invalid"
        except:
            return "Error"

    def verify_next(self):
        if self.current_index >= len(self.emails):
            self.save_results()
            return

        email = self.emails[self.current_index]
        self.append_text(f"Checking: {email}\n")

        status = self.check_email(email)
        self.append_text(f"✔ {email} → {status}\n\n")
        self.results.append([email, status])

        self.current_index += 1
        self.root.after(1000, self.verify_next)  # delay of 1 sec between each email

    def append_text(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def save_results(self):
        output_file = self.file_path.replace(".csv", "_verified.csv")
        try:
            with open(output_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Email", "Status"])
                writer.writerows(self.results)
        except:
            messagebox.showerror("Error", "Failed to write output file.")
            return

        messagebox.showinfo("Done", f"Verification Complete.\nSaved to:\n{output_file}")
        self.reset_btn.pack(pady=10)
        self.time_label.config(text="✅ Verification done!")

    def reset_page(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.reset_btn.pack_forget()
        self.time_label.config(text="")
        self.emails = []
        self.results = []
        self.current_index = 0
        self.file_path = ""

# Run app
root = tk.Tk()
app = EmailVerifierApp(root)
root.mainloop()
