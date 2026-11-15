import re

log = open('/mnt/c/Users/drash/ATLAS_AIR/ATLAS/task2_submission/mission1_run.log').read()
ts = re.findall(r'\[(\d+\.\d+)\]', log)
if ts:
    start = float(ts[0])
    end = float(ts[-1])
    print(f'Start ts: {start}')
    print(f'End ts:   {end}')
    print(f'Elapsed:  {end - start:.2f}s')
dist = re.findall(r'Distance remaining: (\d+\.\d+)', log)
print(f'Nav feedback count: {len(dist)}')
steps = len(re.findall(r'Passing new path to controller', log))
print(f'Controller steps: {steps}')
goal = 'Mission goal reached successfully' in log
print(f'Goal reached: {goal}')
