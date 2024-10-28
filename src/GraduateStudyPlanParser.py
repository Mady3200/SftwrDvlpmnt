import pandas as pd
import argparse

class GraduateStudyPlanParser:
    """
    A class to parse and process graduate study plans from a CSV file.
    """

    def __init__(self, input_csv):
        self.input_csv = input_csv
        self.df = None

    def load_data(self):
        """
        Load the CSV data into a pandas DataFrame and initialize new columns.
        """
        self.df = pd.read_csv(self.input_csv, header=1)
        self.df = self.df[['Unnamed: 0', 'Fall ', 'Spring*', 'Summer ', 'Fall', 'Spring*.1']]
        self.df['Program'] = None
        self.df['Starting_Semester'] = None

    def process_data(self):
        """
        Process the DataFrame to populate the new columns and drop unnecessary rows.
        """
        current_program = None
        current_semester = None
        section = None
        drop_indexes = []

        for index, row in self.df.iterrows():
            section_now = row['Unnamed: 0']
            section = section_now
            if pd.notna(section):
                if '-' in section:
                    current_program = section.strip()
                    drop_indexes.append(index)
                elif 'Start' in section:
                    current_semester = section.split()[0]  # Extract 'Fall' or 'Spring'
            self.df.at[index, 'Program'] = current_program
            self.df.at[index, 'Starting_Semester'] = current_semester
            self.df.at[index, 'drop_index'] = index in drop_indexes

        self.df = self.df.drop(drop_indexes)

    def rename_columns(self):
        """
        Rename the columns of the DataFrame.
        """
        self.df = self.df[['Fall ', 'Spring*', 'Summer ', 'Fall', 'Spring*.1', 'Program', 'Starting_Semester']]
        self.df.columns = ['Fall1', 'Spring1', 'Summer1', 'Fall2', 'Spring2', 'Program', 'Starting_Semester']

    def display_data(self):
        """
        Display the DataFrame.
        """
        print(self.df.columns)
        print(self.df)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Graduate Study Plan Parser")
    parser.add_argument(
        '--input_csv',
        type=str,
        default='../inputs_new/Graduate Study Plans -revised(Sheet1).csv',
        help='Path to the input CSV file'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    parser = GraduateStudyPlanParser(args.input_csv)
    parser.load_data()
    parser.process_data()
    parser.rename_columns()
    parser.display_data()
