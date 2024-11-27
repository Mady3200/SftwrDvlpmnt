# Smart Class Planning Tool

## Description

The Smart Class Planning Tool is a desktop application designed to assist students in planning their academic courses. It parses input files such as DegreeWorks PDFs, Graduate Study Plans, and 4-Year Schedules to generate a comprehensive course plan.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Development Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Mady3200/SftwrDvlpmnt
   cd Project
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

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.
