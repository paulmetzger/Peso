#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as pt
import matplotlib

sns.set(font_scale=1.5)
sns.set_style('white')
sns.set_palette('GnBu',3)
df = pd.read_csv('break_down.csv')
ax = df.ix[:,1:].plot(kind='bar', stacked=True)

ax.set_xticklabels(['With batching', 'Without batching'], rotation=360)
#ax.set_xlabel("Implementation")
ax.set_ylabel("Nanoseconds/Job")

sns.despine(right=True, top=True)
#pt.legend(frameon=False, bbox_to_anchor=(0.0, 0.6, 1, 0.5))
#pt.show()
pt.savefig('../../paper/figures/motivating_example_break_down.pdf', bbox_inches='tight')
