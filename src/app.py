import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from GraduateStudyPlanParser import GraduateStudyPlanParser  # Assuming this is in the same directory
from DegreeWorksParser import parse_degreeworks
from FouryearScheduleParser import load_csv_schedule
import re
globaldict = {
    "default_dw_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\1stsemdeg.pdf",
    "default_gsp_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\Graduate Study Plans -revised(Sheet1).csv",
    "default_schedule_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\fouryear.csv",
    "degreeworks_path": None,
    "gsp_path": None,
    "schedule_path": None,
    "degreeworks_df": None,
    "gsp_df": None,
    "schedule_df": None,
    "degreeworks_parsed": False,
    "gsp_parsed": False,
    "schedule_parsed": False
}


# Main Application Window Class
class SmartClassPlanningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Class Planning Tool")
        self.geometry("600x600")
        
        # Initialize screens
        self.welcome_screen = WelcomeScreen(self)
        self.file_selection_screen = FileSelectionScreen(self)
        self.validation_screen = ValidationScreen(self)
        self.course_planning_screen = CoursePlanningScreen(self)
        self.output_generation_screen = OutputGenerationScreen(self)
        self.completion_screen = CompletionScreen(self)
        self.usage_screen = UsageScreen(self)

        # Show the Welcome Screen initially
        self.show_screen(self.welcome_screen)

    def show_screen(self, screen):
        """Raise the specified screen to the front."""
        screen.tkraise()


# Base Screen Class with common footer
class BaseScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nsew")
        
        # Footer buttons
        footer_frame = tk.Frame(self)
        footer_frame.pack(side="bottom", fill="x", pady=10)

        # Back button
        back_button = tk.Button(footer_frame, text="Back", command=self.go_back)
        back_button.pack(side="left", padx=10)

        go_home_button = tk.Button(footer_frame, text="Go to Home", command=lambda: parent.show_screen(parent.welcome_screen))
        go_home_button.pack(side="left", padx=10)

        usage_button = tk.Button(footer_frame, text="Usage", command=lambda: parent.show_screen(parent.usage_screen))
        usage_button.pack(side="left", padx=10)

        contact_label = tk.Label(footer_frame, text="Contact Supervisor: supervisor@example.com", fg="blue", cursor="hand2")
        contact_label.pack(side="right", padx=10)
        contact_label.bind("<Button-1>", lambda e: messagebox.showinfo("Contact", "Email: supervisor@example.com"))

    def go_back(self):
        # Get all screens
        screens = [
            self.master.welcome_screen,
            self.master.file_selection_screen, 
            self.master.validation_screen,
            self.master.course_planning_screen,
            self.master.output_generation_screen,
            self.master.completion_screen,
            self.master.usage_screen
        ]
        
        # Find current screen index
        current_index = screens.index(self)
        
        # Go to previous screen if not on first screen
        if current_index > 0:
            self.master.show_screen(screens[current_index - 1])

class WelcomeScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        title_label = tk.Label(self, text="Smart Class Planning Tool", font=("Helvetica", 16))
        title_label.pack(pady=10, anchor="center")

        description_label = tk.Label(self, text="Welcome message introducing the application.", font=("Helvetica", 12))
        description_label.pack(pady=10, anchor="center")

        get_started_button = tk.Button(self, text="Get Started", font=("Helvetica", 12), 
                                       command=lambda: parent.show_screen(parent.file_selection_screen))
        get_started_button.pack(pady=20, anchor="center")

class FileSelectionScreen(BaseScreen):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.df = None

        instructions_label = tk.Label(self, text="Please upload the following files:", font=("Helvetica", 12))
        instructions_label.pack(pady=10)

        # File upload fields and buttons
        self.dw_entry = self.create_file_upload_field("DegreeWorks PDF", filetypes=[("PDF files", "*.pdf")])
        self.gsp_entry = self.create_file_upload_field("Graduate Study Plan", filetypes=[("CSV files", "*.csv")])
        self.schedule_entry = self.create_file_upload_field("4-Year Schedule", filetypes=[("CSV files", "*.csv")])
        self.dw_entry.insert(0, globaldict["default_dw_path"])
        self.gsp_entry.insert(0, globaldict["default_gsp_path"])
        self.schedule_entry.insert(0, globaldict["default_schedule_path"])
        proceed_button = tk.Button(self, text="Proceed", command=self.validate_and_proceed)
        proceed_button.pack(pady=20)

        # Parse File Button
        parse_gsp_button = tk.Button(self, text="Parse Graduate Study Plan", command=self.parse_file_gsp)
        parse_gsp_button.pack(pady=10)

        parse_degreeworks_button = tk.Button(self, text="Parse DegreeWorks PDF", command=self.parse_file_dw)
        parse_degreeworks_button.pack(pady=10)

        parse_schedule_button = tk.Button(self, text="Parse 4-Year Schedule", command=self.parse_file_schedule)
        parse_schedule_button.pack(pady=10)

        # Treeview frame with both vertical and horizontal scrollbars
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="x", padx=10, pady=10)

        # Treeview for displaying parsed data with fixed height
        self.tree = ttk.Treeview(self.tree_frame, height=10)
        self.tree.pack(side="left", fill="x", expand=True)

        # Vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.v_scrollbar.set)

        # Horizontal scrollbar
        self.h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.h_scrollbar.pack(fill="x", padx=10, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)
        
        # Clear Display Button
        clear_button = tk.Button(self, text="Clear Display", command=self.clear_display)
        clear_button.pack(pady=10)

        

    def create_file_upload_field(self, label_text, filetypes=None):
        """Create a file upload field with label, entry, and button."""
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=f"{label_text}:").pack(side="left")
        entry = tk.Entry(frame, width=30)
        entry.pack(side="left", padx=5)
        tk.Button(frame, text="Choose File", command=lambda: self.select_file(entry, filetypes)).pack(side="left")
        return entry

    def select_file(self, entry, filetypes=None):
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

    def parse_file_gsp(self):
        """Parse the selected Graduate Study Plan CSV file and display the results."""
        gsp_path = self.gsp_entry.get()
        if not gsp_path:
            messagebox.showerror("Error", "Please select the Graduate Study Plan CSV file.")
            return

        try:
            # Parse the CSV file using GraduateStudyPlanParser
            parser = GraduateStudyPlanParser(gsp_path)
            parser.load_data()
            parser.process_data()
            parser.rename_columns()
            self.df = parser.df  # Store the parsed DataFrame
            globaldict["gsp_df"] = self.df.copy()

            # Display parsed data in Treeview
            self.display_data(is_gsp=True)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse the file: {e}")

    def parse_file_dw(self):
        dw_path = self.dw_entry.get()
        if not dw_path:
            messagebox.showerror("Error", "Please select the DegreeWorks PDF file.")
            return
        try:
            self.raw_text,self.student_info, self.courses_info = parse_degreeworks(dw_path,True,False)
            globaldict["degreeworks_df"] = [
                self.raw_text,
                self.student_info,
                self.courses_info
            ]
            self.display_data(is_degreeworks=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse the file: {e}")

    def parse_file_schedule(self):
        schedule_path = self.schedule_entry.get()
        if not schedule_path:
            messagebox.showerror("Error", "Please select the 4-Year Schedule CSV file.")
            return
        try:
            self.df = load_csv_schedule(schedule_path,0)
            globaldict["schedule_df"] = self.df.copy()
            self.display_data(is_schedule=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse the file: {e}")

    def display_data(self, is_degreeworks=False,is_gsp=False,is_schedule=False):
        """Display the parsed DataFrame in the Treeview table."""
        # Clear any existing data in Treeview
        self.tree.delete(*self.tree.get_children())

        # Set up columns in Treeview
        if is_gsp:
            self.tree["columns"] = list(self.df.columns)
            self.tree["show"] = "headings"

            for col in self.df.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)

            # Insert rows from DataFrame into Treeview
            for _, row in self.df.iterrows():
                self.tree.insert("", "end", values=list(row))
        
        if is_degreeworks:
            self.tree["columns"] = ["key","value"]
            self.tree["show"] = "headings"

            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)

            self.tree.insert("", "end", values=["raw_text",self.raw_text])
            for key,value in self.student_info.items():
                self.tree.insert("", "end", values=[key,value])
            for key,value in self.courses_info.items():
                self.tree.insert("", "end", values=[key,value])

        if is_schedule:
            self.tree["columns"] = list(self.df.columns[:5])
            self.tree["show"] = "headings"

            for col in self.df.columns[:5]:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)

            for _, row in self.df.iterrows():
                self.tree.insert("", "end", values=list(row)[:5])

    def clear_display(self):
        """Clear the Treeview display and column headers."""
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []
        self.tree["show"] = "headings"
        self.df = None

    def validate_and_proceed(self):
        dw_path = self.dw_entry.get()
        gsp_path = self.gsp_entry.get()
        schedule_path = self.schedule_entry.get()
        globaldict["degreeworks_path"] = dw_path
        globaldict["gsp_path"] = gsp_path
        globaldict["schedule_path"] = schedule_path

        if not dw_path or not gsp_path or not schedule_path:
            messagebox.showerror("Error", "Please upload all required files.")
        elif dw_path == gsp_path or dw_path == schedule_path or gsp_path == schedule_path:
            messagebox.showerror("Error", "No two files should be of the same path.")
        else:
            self.parent.validation_screen.update_status()
            self.parent.show_screen(self.parent.validation_screen)

class ValidationScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        self.parsed_status = tk.StringVar(value="Status: Parsing Input Files...")
        tk.Label(self, textvariable=self.parsed_status, font=("Helvetica", 12)).pack(pady=10)

        # Parsed file status
        self.dw_status = tk.StringVar(value="")
        self.gsp_status = tk.StringVar(value="")
        self.schedule_status = tk.StringVar(value="")
        tk.Label(self, textvariable=self.dw_status).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.gsp_status).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.schedule_status).pack(anchor="w", padx=20)

        # Data Summary
        tk.Label(self, text="Extracted Data Summary:", font=("Helvetica", 12)).pack(pady=10)
        self.student_name = tk.StringVar(value="Student Name: N/A   ")
        self.student_id = tk.StringVar(value="Student ID: N/A")    
        # Program
        self.program = tk.StringVar(value="Program: N/A")
        # Concentration
        self.concentration = tk.StringVar(value="Concentration: N/A")
        self.required_credits = tk.StringVar(value="Required Credits: N/A")
        self.applied_credits = tk.StringVar(value="Applied Credits: N/A")
        self.current_credits = tk.StringVar(value="Current Credits: N/A")
        self.current_still_needed = tk.StringVar(value="Still Needed Credits: N/A")
        tk.Label(self, textvariable=self.student_name).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.student_id).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.program).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.concentration).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.required_credits).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.applied_credits).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.current_credits).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.current_still_needed).pack(anchor="w", padx=20)

        next_button = tk.Button(self, text="Next", command=self.go_to_course_planning)
        next_button.pack(pady=20)
        self.parent = parent

    def update_status(self):
        self.parsed_status.set("Parsing input files...")
        
        # Parse DegreeWorks PDF
        try:
            raw_text, student_info, courses_info = parse_degreeworks(globaldict["degreeworks_path"],True,False)
            globaldict["degreeworks_parsed"] = True
            globaldict["degreeworks_df"] = [raw_text,student_info,courses_info]
            self.dw_status.set("✓ DegreeWorks PDF parsed successfully.")
        except Exception as e:
            self.dw_status.set("✗ Error parsing DegreeWorks PDF")
            messagebox.showerror("Error", f"Failed to parse DegreeWorks PDF: {str(e)}")
            return

        # Parse Graduate Study Plan
        try:
            gsp_parser = GraduateStudyPlanParser(globaldict["gsp_path"])
            gsp_parser.load_data()
            gsp_parser.process_data()
            gsp_parser.rename_columns()
            gsp_data = gsp_parser.df
            globaldict["gsp_parsed"] = True 
            globaldict["gsp_df"] = gsp_data
            self.gsp_status.set("✓ Graduate Study Plan parsed successfully.")
        except Exception as e:
            self.gsp_status.set("✗ Error parsing Graduate Study Plan")
            messagebox.showerror("Error", f"Failed to parse Graduate Study Plan: {str(e)}")
            return

        # Parse 4-Year Schedule
        try:
            schedule_df = load_csv_schedule(globaldict["schedule_path"], 0)
            globaldict["schedule_parsed"] = True
            globaldict["schedule_df"] = schedule_df
            self.schedule_status.set("✓ 4-Year Schedule parsed successfully.")
        except Exception as e:
            self.schedule_status.set("✗ Error parsing 4-Year Schedule")
            messagebox.showerror("Error", f"Failed to parse 4-Year Schedule: {str(e)}")
            return

        try:
            self.program.set(f"Program: {globaldict['degreeworks_df'][1]['Program']}")
            self.student_name.set(f"Student Name: {globaldict['degreeworks_df'][1]['Student Name']}")
            self.student_id.set(f"Student ID: {globaldict['degreeworks_df'][1]['Student ID']}")
            self.concentration.set(f"Concentration: {globaldict['degreeworks_df'][1]['Concentration']}")
            globaldict["concentration"] = globaldict['degreeworks_df'][1]['Concentration']
        except:
            self.student_name.set(f"Student Name: N/A")
            self.program.set(f"Program: N/A")
            self.student_id.set(f"Student ID: N/A")
            self.concentration.set(f"Concentration: N/A")

        self.required_credits.set(f"Required Credits: {globaldict['degreeworks_df'][1]['Credits Required']}")
        self.applied_credits.set(f"Applied Credits: {globaldict['degreeworks_df'][1]['Credits Applied']}")
        self.current_credits.set(f"Current Credits: {globaldict['degreeworks_df'][1]['Current Credits']}")
        self.current_still_needed.set(f"Still Needed Credits: {globaldict['degreeworks_df'][1]['Credits Still Needed']}")

        self.parsed_status.set("All files parsed successfully!")

    def go_to_course_planning(self):
        if not all([globaldict["degreeworks_parsed"], 
                   globaldict["gsp_parsed"],
                   globaldict["schedule_parsed"]]):
            messagebox.showerror("Error", "Please ensure all files are parsed successfully before proceeding.")
            return
        self.parent.course_planning_screen.update_status()
        self.parent.show_screen(self.parent.course_planning_screen)


class CoursePlanningScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Extracted Course Data:", font=("Helvetica", 12)).pack(pady=10)
        self.course_plan_frame = tk.Frame(self)
        self.course_plan_frame.pack(pady=5, anchor="w", padx=20)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        # self.adjust_button = tk.Button(button_frame, text="Adjust Plan", command=self.adjust_plan)
        # self.adjust_button.grid(row=0, column=0, padx=10)
        self.generate_button = tk.Button(button_frame, text="Generate Plan", command=self.generate_plan)
        self.generate_button.grid(row=0, column=1, padx=10)
        self.parent = parent

    def update_status(self):
        print("Updating status in course planning screen",bool(globaldict["degreeworks_df"]),bool(globaldict["degreeworks_df"][2]))
        if globaldict["degreeworks_df"] and globaldict["degreeworks_df"][2]:
            # Get courses from degreeworks data
            courses = globaldict["degreeworks_df"][2]  # Dictionary of courses
            print(courses)
            
            # Extract unique terms and sort them
            terms = sorted(list({courses[course][0] for course in courses }))
            print(terms)
            # get first term into var in global dict
            globaldict["first_term"] = terms[0]
            # store terms
            globaldict["terms"] = terms
            
            for term in terms:
                # Get courses for this term
                term_courses = [course for course in courses.items() if course[1][0] == term]
                total_credits = [re.search(r'\d+', course[1][2]) for course in term_courses]
                total_credits = [int(i.group()) if i != None else 3 for i in total_credits ]
                tc = 0
                for i in total_credits:
                    if i != None:
                        tc += int(i)
                total_credits = tc
                
                # Create term header label
                tk.Label(self.course_plan_frame, text=f"Semester {term}: Total Credits: {total_credits}",
                        font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10,5))
                
                # Create label for each course in the term
                for course_code, course_data in term_courses:
                    grade = course_data[1]
                    credits = course_data[2]
                    tk.Label(self.course_plan_frame,
                            text=f"  • {course_code} - Credits: {credits} - Grade: {grade}").pack(anchor="w", padx=20)


    # def adjust_plan(self):
    #     messagebox.showinfo("Adjust Plan", "Adjusting the plan...")

    def generate_plan(self):
        self.parent.output_generation_screen.update_status()
        self.master.show_screen(self.master.output_generation_screen)

class OutputGenerationScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Status: Generating Your Course Plan...", font=("Helvetica", 12)).pack(pady=10)
        # conc plan label holder with na
        self.conc_plan_label = tk.StringVar(value="Concentration Plan: N/A")
        tk.Label(self, textvariable=self.conc_plan_label).pack(pady=10)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)
        self.progress.start(10)  # Simulate progress

        self.status_message = tk.StringVar(value="")
        tk.Label(self, textvariable=self.status_message).pack(pady=10)
        download_button = tk.Button(self, text="Saved as output.csv (view your plan in output directory 'outputs/output.csv')", command=self.download_file)
        download_button.pack(pady=20)

        tk.Label(self, text="General Plan for all sems of your concentration", font=("Helvetica", 12, "bold")).pack(pady=10)
        # general plan root view of tree to diplay table
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="x", padx=10, pady=10)

        # utilized following from GraduateStudyPlan label text under this

        
        # Treeview for displaying parsed data with fixed height
        self.tree = ttk.Treeview(self.tree_frame, height=10)
        self.tree.pack(side="left", fill="x", expand=True)

        self.after(2000, self.show_success_message)

    def show_success_message(self):
        self.progress.stop()
        self.status_message.set("✓ Course plan generated successfully!")

    def download_file(self):
        messagebox.showinfo("Download", "Course plan downloaded successfully at ouptut.csv")
        self.master.show_screen(self.master.completion_screen)
    
    def update_status(self):
        # conc 
        concentration = globaldict["concentration"]

        if "Software" in concentration:
            concentration = "ACS -  Software Dev"
        elif "AI" in concentration:
            concentration = "ACS -  AI and Data Science"
        elif "General" in concentration:
            concentration = "ACS -  General"
        elif "Management" in concentration:
            concentration = "CYBR - Management"
        elif "Defense" in concentration:
            concentration = "CYBR - Cyber Defense"
        self.conc_plan_label.set(f"Concentration Plan: {concentration}")

        # selecct that conc in program column of gsp df
        gsp_df = globaldict["gsp_df"]
        gsp_df = gsp_df[gsp_df["Program"] == concentration]
        print(gsp_df)
        print(globaldict["first_term"])

        #  if fall or spring in first term in global dict, then display the gsp df in the general plan frame
        if "Fall" in globaldict["first_term"]:
            gsp_df = gsp_df[gsp_df["Starting_Semester"] == "Fall"]
        elif "Spring" in globaldict["first_term"]:
            gsp_df = gsp_df[gsp_df["Starting_Semester"] == "Spring"]

        # display the gsp df in the general plan frame
        #  columns as header

        self.tree["columns"] = list(gsp_df.columns)
        self.tree["show"] = "headings"

        for col in gsp_df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        for _, row in gsp_df.iterrows():
            self.tree.insert("", "end", values=list(row))

        #  replace the ffirst term courses with first column of gsp df .. like wise until None of term
        columns = gsp_df.columns
        i = 0
        for term in globaldict["terms"]:
            if term == "None":
                break
            term_courses = [course for course in globaldict["degreeworks_df"][2].items() if course[1][0] == term]
            # print(term,term_courses)
            column = columns[i]
            course_count = 0
            for course in term_courses:
                course_code = course[0]
                gsp_df.iloc[course_count,i] = course_code
                course_count += 1
            # rename column in gsp_df to term
            gsp_df = gsp_df.rename(columns={column: term})
            i += 1
        # save as csv in outputs dir
        import os
        # list os dir ../
        print(os.listdir("../"))
        gsp_df.to_csv("../outputs/output_new.csv", index=False)




class CompletionScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Thank you for using the Smart Class Planning Tool!", font=("Helvetica", 12)).pack(pady=10)
        option_frame = tk.Frame(self)
        option_frame.pack(pady=20)
        plan_another_button = tk.Button(option_frame, text="Plan Another Schedule", command=self.plan_another)
        plan_another_button.grid(row=0, column=0, padx=10)
        exit_button = tk.Button(option_frame, text="Exit", command=self.master.quit)
        exit_button.grid(row=0, column=1, padx=10)

    def plan_another(self):
        self.master.show_screen(self.master.welcome_screen)


class UsageScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="How to Use the Smart Class Planning Tool", font=("Helvetica", 16)).pack(pady=10)
        
        steps = [
            "1. Start by clicking 'Get Started' on the Welcome Screen.",
            "2. Upload the required files: DegreeWorks PDF, Graduate Study Plan, and 4-Year Schedule.",
            "3. Proceed to validate your input files.",
            "4. Review the proposed course plan and address any warnings.",
            "5. Generate the final course plan and download it as an Excel file.",
            "6. Optionally, you can plan another schedule or exit the application."
        ]
        for step in steps:
            tk.Label(self, text=step, font=("Helvetica", 12), wraplength=450, anchor="w").pack(pady=2, anchor="w")

# Run the application
if __name__ == "__main__":
    app = SmartClassPlanningApp()
    app.mainloop()
