import logging
from collections import OrderedDict
from itertools import tee
import re
from jetto_tools._utils import is_int, is_float

import numpy as np

from IPython import embed

logger = logging.getLogger('jetto_tools.jams')
logger.setLevel(logging.INFO)
try:
	from omas import ODS
except ImportError:
    logger.warning("Python module 'omas' not found. Submodule 'jams' needs it")
    raise


def convert_leafs(self):
    for item in self.keys():
        val = self.getraw(item)
        if isinstance(val, ODS):
            val.convert_leafs()
        else:
            if val == 'false':
                self.setraw(item, False)
            elif val == 'true':
                self.setraw(item, False)
            elif is_int(val):
                self.setraw(item, int(val))
            elif is_float(val):
                self.setraw(item, float(val))

def consolidate_arraylike_leafs(self):
    for item in self.keys():
        val = self.getraw(item)
        if isinstance(val, ODS):
            if len(val.paths()[0]) != 1 or not is_int(val.paths()[0][0]):
                # Is not an array, recurse
                val.consolidate_arraylike_leafs()
            else:
                # Is an array, try to convert
                child = val.getraw(0)
                if isinstance(child, str):
                    # Represent all strings in arrays as a single dtype
                    dtype = 'U128'
                elif isinstance(child, np.ndarray):
                    # Copy the dtype of the first underlying array
                    dtype = child.dtype
                else:
                    # This is probably is singular value, just copy the dtype
                    dtype = type(child)

                if isinstance(child, np.ndarray):
                    # If it is already an numpy array, we don't need to convert, just to stack if possible
                    subarrs = val.values()
                    for ii in range(len(subarrs)):
                        if subarrs[ii].dtype != dtype:
                            if dtype == np.dtype(float) and subarrs[ii].dtype == np.dtype(int):
                                # The dtype should be float, but for this subarray is int
                                subarrs[ii] = subarrs[ii].astype(float)
                            elif dtype == np.dtype(float) and np.issubdtype(np.dtype(str), subarrs[ii].dtype):
                                # The dtype should be float, but for this subarray is str
                                subarrs[ii] = np.full_like(subarrs[ii], np.nan, dtype=float)
                            elif dtype == np.dtype(int) and np.issubdtype(np.dtype(str), subarrs[ii].dtype):
                                # The dtype should be int, but for this subarray is str
                                print('Converting unicode str to int')
                                print('Define this conversion!')
                                embed()
                            else:
                                # No sane way to define this conversion
                                print('Cannot convert, giving up on {!s}!'.format(val))
                    try:
                        arr = np.vstack(subarrs)
                    except:
                        print('Cannot stack, giving up on {!s}!'.format(val))
                    else:
                        self.setraw(item, arr)
                    continue # No need to convert stuff, continue the loop

                # Deal with missing values, use -99999 for ints (UGLY!)
                if isinstance(child, float):
                    vals = [dtype(val) if is_float(val) else None for val in val.values()]
                elif isinstance(child, int):
                    vals = [dtype(val) if is_int(val) else -99999 for val in val.values()]
                else:
                    vals = val.values()

                try:
                    arr = np.fromiter(vals, dtype, count=len(val))
                except:
                    print('UNEXPECTED CONVERSION ERROR in {!s}'.format(val))
                    arr = "CONVERSION ERROR"

                self.setraw(item, arr)

# Hacky-hacky hook to ODS class
ODS.convert_leafs = convert_leafs
ODS.consolidate_arraylike_leafs = consolidate_arraylike_leafs

header_finder = re.compile(r'\*\n\*([\w, \d]+)\n')
namelist_finder = re.compile(r'^(\w+)(?:\[(\d+)\])?\..*', re.MULTILINE)
#keyval_finder = re.findall(r'^(\w+)[^,.]*:', string, re.MULTILINE)
keyval_finder = re.compile(r'^([\w,\d]+)(?:\[(\d+)\])?(?:\[(\d+)\])?(.*):(.*)', re.MULTILINE)
leaf_finder = re.compile(r'^([\w,\d\.]+)(?:\[(\d+)\])?(?:\[(\d+)\])?\s* : (.*)')
#dimension_finder = re.compile('(\w+)(?:\[(\d+)\])?(?:\[(\d+)\])?.*:', re.MULTILINE)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

class Settings(OrderedDict):
    sectionMarker = '*'
    def __init__(self, namelists):
        pass

    @classmethod
    def read(cls, input_path):
        with open(input_path, 'r') as in_file:
            in_data = in_file.read()
        # First split the huge string into sections. A section starts with *\n*HEADER
        section_header_starts = [match.start() for match in header_finder.finditer(in_data)]
        section_header_starts.append(len(in_data)) # Also read the last section
        section_strings = [in_data[start:next_start] for start, next_start in pairwise(section_header_starts)]
        for sec_num, section_string in enumerate(section_strings[1:-1]):
            sec = Section.decode(section_string)
            return sec

def decode_line(line):
    parts = re.findall('(.*)\s+:\s+(?:\](\d+)\[)?(?:\](\d+)\[)?(.*)', line[::-1])
    if len(parts) > 1:
        raise Exception
    parts = [part[::-1] for part in parts[0]]
    return parts

legacy_paths = [
    r'EquilEscoRefPanel\.BField\s+',
    r'NeutralSourcePanel\.gasPuff\s+',
    r'NeutralSourcePanel\.recycle\s+',
    r'PelletSwing\.select\s+',
    r'SawteethPanel\.fixedTimes\s+',
    r'SetUpPanel\.maxTimeStep\s+',
    r'ECRHPanel\.ECRHGray\[\d+\]\.angpec\s+',
    r'ECRHPanel\.ECRHGray\[\d+\]\.powec\s+',
]
class Section(OrderedDict):
    @classmethod
    def decode(cls, string):
        section_name = header_finder.match(string).groups()[0]
        section_string = header_finder.sub('', string)
        #namelist_starts = [match.start() for match in namelist_finder.finditer(section_string)]
        #namelist_starts.append(len(section_string)) # Also read the last section
        #namelist_strings = [section_string[start:next_start] for start, next_start in pairwise(namelist_starts)]
        #namelist_labels = set(namelist_finder.findall(section_string))
        #namelist_starts = OrderedDict()
        #for label, number in namelist_labels:
        #    full_label = label
        #    if number != '':
        #        full_label += '[' + number + ']'
        #    start = section_string.find(full_label)
        #    namelist_starts[full_label] = start
        #namelist_starts = sorted(namelist_starts.items(), key=lambda kv: kv[1])
        #namelist_starts = OrderedDict(namelist_starts)
        #namelist_strings = [section_string[start:next_start] for start, next_start in pairwise(namelist_starts.values())]
        ods = ODS(consistency_check=False, dynamic_path_creation='dynamic_array_structures')
        oned_paths = OrderedDict()
        twod_paths = OrderedDict()
        for line in section_string.split('\n')[:-1]:
            if any(re.match(pattern, line) is not None for pattern in legacy_paths):
                #print('Ignoring legacy line', line)
                continue
            #print(leaf_finder.findall(line))
            try:
                #path, first_dim, second_dim, value = leaf_finder.findall(line)[0]
                #path, first_dim, second_dim, value = decode_line(line)
                value, first_dim, second_dim, path = decode_line(line)
            except:
                print('Could not decode path "{!s}"'.format(line))
                raise
            full_path = path
            if first_dim != '':
                full_path += '[' + first_dim + ']'
            if second_dim != '':
                full_path += '[' + second_dim + ']'

            if second_dim != '':
                twod_paths[(path, int(first_dim), int(second_dim))] = (full_path, value)
            elif first_dim != '':
                oned_paths[(path, int(first_dim))] = (full_path, value)
            else:
                try:
                    leaf_label = path.split('.')[-1]
                    if '[' in leaf_label:
                        pass
                    else:
                        ods[full_path] = value
                except TypeError as  e:
                    if e.args[0].endswith(' object does not support item assignment'):
                        print(full_path, 'trying to set ODS on an object. Is one of the underlying nodes legacy?')
                        raise
                except:
                    print('Skipping {!s}'.format(full_path))
                    raise
        for (path, idx), (full_path, value) in sorted(oned_paths.items(), key=lambda kv: kv[0]):
            try:
                ods[full_path] = value
            except TypeError as  e:
                if e.args[0].endswith(' object does not support item assignment'):
                    print(full_path, 'trying to set ODS on an object. Is one of the underlying nodes legacy?')
                    raise
            except:
                print('Could not set {!s}'.format(full_path))
                raise

        for (path, idx1, idx2), (full_path, value) in sorted(twod_paths.items(), key=lambda kv: kv[0]):
            try:
                ods[full_path] = value
            except TypeError as  e:
                if e.args[0].endswith(' object does not support item assignment'):
                    print(full_path, 'trying to set ODS on an object. Is one of the underlying nodes legacy?')
                    raise
            except:
                print('Could not set {!s}'.format(full_path))
                raise
        return ods
        #nml = KeyValueStore.decode(ods, section_string)
        #for full_label, namelist_string in zip(namelist_starts.keys(), namelist_strings):
        #    stripped = namelist_string.replace(full_label + '.', '')
        #    print('Parsing', full_label)
        #    if full_label == 'BoundCondPanel':
        #        nml = KeyValueStore.decode(stripped)

class KeyValueStore(OrderedDict):
    @classmethod
    def decode(cls, ods, string):
        keyval_labels = set(keyval_finder.findall(string))
        keyval_starts = OrderedDict()
        for label, first_dim, second_dim, children, value in keyval_labels:
            full_label = label
            if first_dim != '':
                full_label += '[' + first_dim + ']'
            if second_dim != '':
                full_label += '[' + second_dim + ']'
            start = string.find(full_label)
            keyval_starts[full_label] = start
        #keyval_starts = sorted(keyval_starts.items(), key=lambda kv: kv[1])
        #keyval_starts = OrderedDict(keyval_starts)
        ##keyval_starts['next'] = len(string)
        #keyval_strings = [string[start:next_start] for start, next_start in pairwise(keyval_starts.values())]
        #kvstore = KeyValueStore()

        #for full_label, keyval_string in zip(keyval_starts.keys(), keyval_strings):
        #    print('Decoding ', cls.__name__, full_label)
        #    stripped = keyval_string.replace(full_label + '.', '')
        #    for label, first_dim, second_dim, children, value in keyval_finder.findall(stripped):
        #        if '.' in children:
        #            print('node', full_label, label, children, value)
        #            kvstore[full_label] = None
        #        else:
        #            print('leaf', full_label, label, children, value)
        #            kvstore[full_label] = None
                    #new_label = label
                    #if first_dim != '':
                    #    new_label += '[' + ':' + ']'
                    #if second_dim != '':
                    #    new_label += '[' + ':' + ']'
                    #if new_label not in kvstore:
                    #    if first_dim != '':
                    #        kvstore[new_label] = []
                    #    else:
                    #        kvstore[new_label] = value
                    #if first_dim != '':
                    #    kvstore[new_label].append(value)
                #    # Subgroup, recurse
                #sub_kv = KeyValueStore.decode(stripped)
                #kvstore[full_label] = KeyValueStore.decode(stripped)
            #else:
            #    # Reached a leaf! Stop recursing?
            #    #if full_label in ['tpoly']:
            #    #    embed()
            #    for label, first_dim, second_dim, value in keyval_finder.findall(keyval_string):
            #        new_label = label
            #        if first_dim != '':
            #            new_label += '[' + ':' + ']'
            #        if second_dim != '':
            #            new_label += '[' + ':' + ']'
            #        if new_label not in kvstore:
            #            if first_dim != '':
            #                kvstore[new_label] = []
            #            else:
            #                kvstore[new_label] = value
            #        if first_dim != '':
            #            kvstore[new_label].append(value)
            #        print(label, first_dim, second_dim, value)
#        return kvstore
                #nml = KeyValueStore.decode(stripped)

class Namelist(OrderedDict):
    def __init__(self, name, namelistOrder, panFile):
        self.name
        self.code
        self.debug
        self.diags
        self.twoDLabels

    @classmethod
    def decode(cls, string):
        namelist_labels = set(namelist_finder.findall(string))
        namelist_starts = OrderedDict()
        for label, number in namelist_labels:
            full_label = label
            if number != '':
                full_label += '[' + number + ']'
            start = string.find(full_label)
            namelist_starts[full_label] = start

        namelist_starts = sorted(namelist_starts.items(), key=lambda kv: kv[1])
        namelist_starts = OrderedDict(namelist_starts)
        namelist_strings = [string[start:next_start] for start, next_start in pairwise(namelist_starts.values())]

        #keyval_labels = set(namelist_finder.findall(string))
        embed()

if __name__ == '__main__':
    ods = Settings.read('../testdata/jetto-sanco-pencil-esco-qlknn/jetto.jset')
    ods.convert_leafs()
    #ods['BoundCondPanel']['current']['tpoly'].consolidate_arraylike_leafs()
    #ods['BoundCondPanel']['current'].consolidate_arraylike_leafs()
    ods.consolidate_arraylike_leafs()
    ods.consolidate_arraylike_leafs() # Again, there might be 2D arrays!
    embed()
