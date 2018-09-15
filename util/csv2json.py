# csv2json.py
#
# Copyright 2009 Brian Gershon -- briang at webcollective.coop
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import csv
from os.path import dirname
import json

try:
    script, input_file_name, model_name = sys.argv
except ValueError:
    print("\nRun via:\n\n%s input_file_name model_name" % sys.argv[0])
    print("\ne.g. %s airport.csv app_airport.Airport" % sys.argv[0])
    print("\nNote: input_file_name should be a path relative to where this script is.")
    sys.exit()

in_file = dirname(__file__) + input_file_name
out_file = dirname(__file__) + input_file_name[:input_file_name.rindex(".")] + ".json"

print("Converting %s from CSV to JSON as %s" % (in_file, out_file))

f = open(in_file, 'r')
fo = open(out_file, 'w')

reader = csv.reader(f)

header_row = []
entries = []

# debugging
# if model_name == 'app_airport.Airport':
#     import pdb ; pdb.set_trace( )

for row in reader:
    if not header_row:
        header_row = row
        continue

    pk = row[0]
    model = model_name
    fields = {}
    for i in range(len(row)-1):
        field_name = header_row[i+1]
        if field_name[-4:] == '-fnk':
            field_name = field_name[:-4]
            is_foreign_natural_key = True
        else:
            is_foreign_natural_key = False
        field_value = row[i+1]

        # convert numeric strings into actual numbers by converting to either int or float
        if field_value.isdigit():
            try:
                field_value = int(field_value)
            except ValueError:
                field_value = float(field_value)
        else:
            field_value = field_value.strip()

        if is_foreign_natural_key:
            field_value = [field_value]

        fields[field_name] = field_value

    row_dict = {}
    row_dict["pk"] = int(pk)
    row_dict["model"] = model_name

    row_dict["fields"] = fields
    entries.append(row_dict)

fo.write("%s" % json.dumps(entries, indent=4))

f.close()
fo.close()
