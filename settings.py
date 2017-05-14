import os


xdg_data_home = os.getenv('XDG_DATA_HOME')
if xdg_data_home is not None:
    data_file = os.path.join(xdg_data_home, 'tasks.json')
else:
    data_file = os.path.join(os.getenv('HOME'), '.tasks.json')

date_format = '%Y-%m-%d'
