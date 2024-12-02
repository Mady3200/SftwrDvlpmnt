# Smart Class Planning Tool

## Purpose

The Smart Class Planning Tool is designed to assist students in effectively planning their academic courses. It automates the parsing of input files such as DegreeWorks PDFs, Graduate Study Plans, and 4-Year Schedules, enabling users to generate a comprehensive and organized course plan.

## Prerequisites

Before using the Smart Class Planning Tool, ensure you have the following:

- Python 3.6 or higher installed on your machine.
- Basic knowledge of command line operations.
- Required input files: DegreeWorks PDF, Graduate Study Plan CSV, and 4-Year Schedule CSV.

## Download

Download the executable from the [dist folder](https://github.com/Mady3200/SftwrDvlpmnt/tree/main/dist).

Link to app.exe: [app.exe](https://github.com/Mady3200/SftwrDvlpmnt/blob/main/dist/app.exe)

Click here to download app.exe: [app.exe](https://github.com/Mady3200/SftwrDvlpmnt/raw/refs/heads/main/dist/app.exe)

To Download the source code, click [here](https://github.com/Mady3200/SftwrDvlpmnt/archive/refs/heads/main.zip).

### Development Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Mady3200/SftwrDvlpmnt
   cd SftwrDvlpmnt
   ```

2. **Set up a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**

   ```bash
   python src/app.py
   ```

### Building the Application with PyInstaller

To create a standalone executable of the application using PyInstaller, follow these steps:

1. **Install PyInstaller:**

   ```bash
   pip install pyinstaller
   ```

2. **Build the application:**

   Navigate to the `src` directory and run the following command:

   ```bash
   pyinstaller --onefile src/app.py
   ```

   This will generate a `dist` folder containing the executable file.

3. **Run the executable:**

   You can find the executable in the `dist` folder. Run it directly to launch the application.

### Running the Application

1. **Locate the executable:**

   After building the application with PyInstaller, navigate to the `dist` directory of the project to find the executable file.

2. **Run the application:**

   Double-click the executable file to launch the Smart Class Planning Tool.

3. **Follow the on-screen instructions:**

   Once the application is running, follow the prompts to upload the required files and generate your course plan.

## Usage

1. **Follow the on-screen instructions to upload the required files and generate your course plan.**

## Features

- Parse and process DegreeWorks PDFs, Graduate Study Plans, and 4-Year Schedules.
- Generate a detailed course plan based on the input data.
- User-friendly interface with step-by-step guidance.


## Usage

1. **Start the Application:**
   - Click 'Get Started' on the Welcome Screen to begin the application.

2. **Upload Required Files:**
   - You will be prompted to upload the following files:
     - **DegreeWorks PDF:** This file contains your academic records.
     - **Graduate Study Plan (GSP):** A CSV file outlining your study plan.
     - **4-Year Schedule:** A CSV file detailing your course schedule.

3. **Parse the Files:**
   - After uploading the files, click on the respective "Parse" buttons to process each file. Ensure that the files are correctly formatted to avoid errors. The buttons for parsing are:
     - **Parse Graduate Study Plan:** Processes the GSP file.
     - **Parse DegreeWorks PDF:** Processes the DegreeWorks PDF file.
     - **Parse 4-Year Schedule:** Processes the 4-Year Schedule CSV file.

4. **Proceed with Course Planning:**
   - Once the files are parsed successfully, click the "Proceed" button to validate the data and move to the next step in generating your course plan.

5. **Follow On-Screen Instructions:**
   - The application will guide you through the remaining steps to generate your course plan based on the uploaded data. You will see buttons for navigation, each serving a specific purpose:
     - **Next:** To move to the next screen and continue the course planning process.
     - **Back:** To return to the previous screen and review or modify your inputs.
     - **Go to Home:** To return to the Welcome Screen and start over if needed.

6. **Screens Overview:**
   - The application consists of several screens, each designed to facilitate a specific part of the process:
     - **Welcome Screen:** Start your journey by clicking 'Get Started' to upload your files.
     - **File Selection Screen:** Upload the required files: DegreeWorks PDF, Graduate Study Plan, and 4-Year Schedule. You can also parse each file individually.
     - **Validation Screen:** Review the parsed data and ensure everything is correct before proceeding.
     - **Course Planning Screen:** Here, you will see the extracted course data and can generate your course plan.
     - **Output Generation Screen:** This screen will show the status of your course plan generation and allow you to download the final output.
     - **Completion Screen:** Thank you for using the tool! You can plan another schedule or exit the application.
     - **Usage Screen:** Instructions on how to use the application effectively.
     - **Prerequisite Extraction Screen:** Extract and view course prerequisites from the university catalog.

7. **Contact Support:**
   - If you encounter any issues, please refer to the contact information provided in the application for assistance.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.
