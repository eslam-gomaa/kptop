
from termgraph import termgraph as tg
import numpy as np

# بيانات الرسم البياني
labels = ['2017', '2018', '2019', '2020', '2021']
data = [[3, 4, 9, 16, 25]]

# إعدادات الرسم البياني
args = {
    'filename': '',
    'title': 'Sample ASCII Plot',
    'width': 50,
    'format': '{:<5.1f}',
    'suffix': '',
    'no_labels': False,
    'color': None,
    'vertical': False,
    'stacked': False,
    'different_scale': False,
    'calendar': False,
    'start_dt': None,
    'custom_tick': '',
    'delim': '',
    'verbose': False
}

# رسم الرسم البياني
tg.Chart(colors=['red', 'blue'], labels=labels, data=data, args=args).draw()
