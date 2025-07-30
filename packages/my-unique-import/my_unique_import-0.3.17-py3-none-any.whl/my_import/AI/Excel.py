import pandas as pd

class Excel:

    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
        self.data = self.df.to_dict()

    def show(self):
        print(self.data)