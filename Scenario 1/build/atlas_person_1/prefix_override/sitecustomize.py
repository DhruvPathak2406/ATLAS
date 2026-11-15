import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/mnt/c/Users/drash/ATLAS_AIR/ATLAS/Scenario 1/install/atlas_person_1'
