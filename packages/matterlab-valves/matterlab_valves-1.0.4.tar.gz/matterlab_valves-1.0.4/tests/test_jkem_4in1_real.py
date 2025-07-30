from pathlib import Path
from matterlab_valves import JKem4in1Valve


valve = JKem4in1Valve(com_port = "COM11", valve_num = 3, ports= {"2": 2})

print(valve.port)
valve.port = 1
print(valve.port)
#valve.switch_port("2")


#
# defaults = Path(__file__).parent.parent / "data" / "default_settings_jk.json"
# valve = Jkem4in1Valve(default_settings=defaults, settings={'com_port': 'COM9', 'valve_num': 1})
# print(valve.port)
# valve.port = 1
# print(valve.port)
# valve.port = 2
