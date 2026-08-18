"""
Pastas do Projeto
nov.22
"""


from pathlib import Path


project_path = Path(__file__).parents[2]

# Datasets Path
dataset_path = Path(project_path.anchor) / 'Datasets' / project_path.name
dataset_path.mkdir(exist_ok=True)

# Data
data_path = dataset_path / 'data'
data_path.mkdir(exist_ok=True)

# Input
input_path = data_path / 'input'
input_path.mkdir(exist_ok=True)

input_path_tab_temp = input_path / 'tab_temp'
input_path_tab_temp.mkdir(exist_ok=True)

input_path_tab = input_path / 'tab'
input_path_tab.mkdir(exist_ok=True)

input_path_down = input_path / 'down'
input_path_down.mkdir(exist_ok=True)

# Output
output_path = data_path / 'output'
output_path.mkdir(exist_ok=True)

output_path_gpkg = output_path / 'gpkg'
output_path_gpkg.mkdir(exist_ok=True)

# Docs
docs_path = dataset_path / 'docs'
docs_path.mkdir(exist_ok=True)

# Scrapy
scrapy_path = project_path / 'scrapy'
scrapy_path.mkdir(exist_ok=True)

logs_path = scrapy_path / 'logs'
logs_path.mkdir(exist_ok=True)

adds_path = scrapy_path / 'adds'
adds_path.mkdir(exist_ok=True)

driver_path = scrapy_path / 'driver'
driver_path.mkdir(exist_ok=True)

if __name__ == '__main__':
    print(project_path)
