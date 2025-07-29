def read_catid(path):

  import pandas as pd
  from pathlib import Path

  with open(Path(path) / 'jetto.catid') as f:
    #df = pd.read_fwf(f,skiprows=2,delimiter=' : ',header=None)
    df = pd.read_fwf(f,skiprows=2,header=None)
    d = df.set_index(0)[3].to_dict()
    return d

# if already cataloged, determine shot, machine, date from path.split
