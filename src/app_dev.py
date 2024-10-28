# tkinter app to parse the input file and display the output
""" 

Project: A Smart Class Planning Tool for Academic Advising
Background.
Academic advising, especially properly planning courses across semesters to ensure students graduate on time, requires significant time and effort from both students and faculty. We are planning to build a Python-based smart class planning tool, which can be executed on any platform such as Windows, Linux, etc. 
It is important for students to enroll in the proper courses designed to meet the degree requirements. Many students mistakenly enroll in classes simply because the classes fit their schedule without considering factors such as prerequisite requirements and different course offering times over the academic year semesters.
Project Overview.
This smart advising tool can output a recommended class plan for a student to follow until the student’s graduation. This software requires three inputs to generate an output excel form where recommended classes for different semesters are listed. 
1)	The first input is a list of courses a student still needs until the student’s graduation, which will be obtained from Degreeworks as a pdf document. 
2)	The second input is Graduate Study Plans -revised, which shows the appropriate course plan for a student to take from his/her first semester till his/her graduation. 
3)	The last input is The 4-year schedule, which shows when the student's required courses will be offered. 
Requirements
Academic advising takes a long time for both students and faculty, especially when checking prerequisite issues. To facilitate class planning, we are to build a python based standalone application, which can be executed on the Windows platform.

•	Functional requirements:
1)	Course planning: The first goal of the software is to plan out classes among different semesters for a student until his/her graduation. The software takes three inputs and outputs an excel sheet where recommenced classes are listed. The recommended plan should be outputted by the software in the form of an excel document. 
2)	Prerequisite checking: Another function of the software is to detect if a student’s plan has prerequisite issues. To do this, you need to construct a web crawler component within your software to grab the prerequisite information from CPSC Course Descriptions because the descriptions include prerequisite information which is sometimes missing in DegreeWorks.
•	Non-functional requirements (constrains):
1)	The software should be configurable. Specifically, the inputs must be separated from the software and be parsed by the software.
2)	The software should be implemented in Python and can be executed on Windows.


 """


from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import scrolledtext

# main window
root = tk.Tk()
root.title("Graduate Study Plan Parser")
root.geometry("600x600")

# display date and time
date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
date_label = tk.Label(root, text=f"Date and Time: {date_time}")
date_label.pack()   

# title
title_label = tk.Label(root, text="Graduate Study Plan Parser", font=("Helvetica", 16))
title_label.pack()

# input file selection
def select_file():
    file_path = filedialog.askopenfilename()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

file_frame = tk.Frame(root)
file_frame.pack(pady=10)

file_label = tk.Label(file_frame, text="Select Input CSV File:")
file_label.pack(side=tk.LEFT)

file_entry = tk.Entry(file_frame, width=50)
file_entry.pack(side=tk.LEFT, padx=5)

file_button = tk.Button(file_frame, text="Browse", command=select_file)
file_button.pack(side=tk.LEFT)

# process button
def process_file():
    file_path = file_entry.get()
    if not file_path:
        messagebox.showerror("Error", "Please select a file")
        return
    # Here you would call the functions to process the file
    # For example:
    # parser = GraduateStudyPlanParser(file_path)
    # parser.load_data()
    # parser.process_data()
    # parser.rename_columns()
    # parser.display_data()
    messagebox.showinfo("Success", "File processed successfully")

process_button = tk.Button(root, text="Process File", command=process_file)
process_button.pack(pady=10)

# output display
output_frame = tk.Frame(root)
output_frame.pack(pady=10)

output_label = tk.Label(output_frame, text="Output:")
output_label.pack()

output_text = scrolledtext.ScrolledText(output_frame, width=70, height=15)
output_text.pack()

# main loop
root.mainloop()

#command to run the app

# python app.py
