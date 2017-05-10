import control

smu = control.Keithley2401()
smu.check_Keithley2401(v=True)
# smu.set_source("voltage", "fixed", "minimum", "0.01")
# smu.check_source(v=True)
# smu.set_sense("current", "auto", "1e-3")
# smu.check_sense(v=True)
smu.initiate()
smu.get_data()
