# Nvidia new HW thermal control algorithm test plan

## Overview

Originally, there are two major parts of SONiC thermal control:
-   thermalctld runs thermal policies in user space to handle thermal event
-	Kernel runs step wise thermal algorithm which monitors thermal zones(asic, module, gearbox) and manages cooling devices(fan).

Currently, we will move kernel part thermal algorithm to user space and extend existing hw-mgmt thermal control service. Some reasons:
-	Step wise thermal algorithm is not so efficiency
-	Conflict between user space and kernel when setting fan speed
-	Fixing/optimizing kernel algorithm is difficult.
-	kernel patches take long time to be approved
-	changing step wise algorithm is not likely to be approved as it is used widely over the world
-	Hard to debug kernel code
-	Hard to test kernel code

The new hw-mgmt thermal control service contains below functions:
-	A thermal algorithm to replace kernel step wise algorithm
-	Thermal event handler which “equals” to existing SONiC thermal policies
-	New logic such as handling memory/CPU thermal zones, etc.

This feature shall migrate the new hw-mgmt thermal control service to SONiC:
-	Enable hw-mgmt thermal algorithm on SONiC side
-	Remove existing SONiC thermal policies configuration from Nvidia platform (thermal_control.json)
-	Remove thermal policies related code from Nvidia platform API

### Scope

The test is to verify new HW thermal control algorithm work as what as expected on nvidia platform

### Scale / Performance

No scale/performance test involved in this test plan

### Related **DUT** CLI commands
```
service hw-management start/stop/status
service hw-management-tc start/stop/status
```


### Supported topology
The tests will be supported on any topo.


### Test cases #1 - Check tc service behaviors after reboot
1. Set hw-management-tc service to enabled state
2. Reboot system( Randomly select cold,warm,fast, config reload)
3. Wait for TC init (~120 sec after login prompt)
4. Check syslog messages
5. Check service status 

### Test cases #2 - Check tc service behaviors when start and stop TC service
1. Stop hw-management-tc service
2. Check syslog and service state
3. Check PWM value. It should be at maximum(100).
4. Check FAN speed is set to correct range as below formula:
   The values of rpm_max, slope, rpm_tolerance and rpm_min can be read from /var/run/hw-management/config//tc_config.json
   The value of pwm_curr can be read from /var/run/hw-management/thermal/pwm1
   (In the all test cases that followed, we also use the below formula to check FAN speed)
   - b = rpm_max - slope * PWM_MAX (100)
   - rpm_calcuated = slope * pwm_curr + b
   - rpm_diff = abs(rpm_real - rpm_calcuated)
   - rpm_diff_norm = float(rpm_diff) / rpm_calcuated
   - rpm_diff_norm < rpm_tolerance
   - rpm_real >= rpm_min*(1-rpm_tolerance)
5. Start hw-management-tc service.
6. Immediately after start  - check PWM value . It should be at maximum
7. wait 120 sec for service init
8. Check syslog and service state
9. Check PWM value is not maximum(100)
10. Check FAN speed is set to correct range

### Test cases #3 - Check tc service behaviors when hw-management is not fully initialized.
1. Stop hw-management-tc service
2. Stop hw-management service
3. Start hw-management-tc service
4. Check PWM value. It should be at maximum
5. Check FAN speed is set to correct range
6. Wait 3 minutes
7. Check PWM value. It should be at maximum
8. Check FAN speed is set to correct range

### Test cases #4 - Check PWM is the correct value when suspend and resume TC 
1. Start TC service.
2. Check PWM is not maximum(100)
3. Check FAN speed is set to correct range
4. Set TC suspend with echo 1 >> /var/run/hw-management/config/suspend & wait 30sec
5. Check PWM is maximum (100), and check FAN speed is set to correct range
6. Set TC resume with echo 0 >> /var/run/hw-management/config/suspend & wait 30sec
7. Check PWM is not maximum(100), and check FAN speed is set to correct range

### Test cases #5 - Temperature sweep 
1. Save the soft-links of tested sensors. Create static files with the same file name for the tested sensors.
2. Get tested sensor parameters from /var/run/hw-management/config/tc_config.json like below e.g.:
   {"asic":           {"pwm_min": 20, "pwm_max" : 100, "val_min":"!70000", "val_max":"!105000", "poll_time": 3}}
3. Mock tested sensor temperature to val_min/10000-1. 
   Wait poll_time secs
4. Mock temperature increase
   - Increase sensor temperature value with step 10
   - Calculate the expected PWM with below formula:
     - expected_pwm = pwm_min + ((new_temp - val_min)/(val_max-val_min)) * (pwm_max - pwm_min)
   - Wait poll_time secs, and get current system PWM by reading /var/run/hw-management/thermal/pwm1
   - Check current_system_pwm >= expected_pwm
   - Check FAN speed is set to correct range
   - Iterate the above steps until temperature is over val_max
5. Mock temperature decrease
   - decrease sensor temperature value with step 10
   - Calculate the expected PWM with below formula:
     - expected_pwm = pwm_min + ((new_temp - val_min)/(val_max-val_min)) * (pwm_max - pwm_min)
   - Wait poll_time secs, and get current system PWM
   - Check current_system_pwm >= expected_pwm
   - Check FAN speed is set to correct range
   - Iterate the above steps until temperature is under val_min
6. Repeat step 1~ step 5 for following sensors or randomly select one sensor to test(Need to check if dut includes this sensor. if no, skip testing this sensor):
   - asic
   - cpu-core
   - comex_voltmon1_temp_input
   - voltmon1_temp_input
   - module{X}
   - ambient
   - psu temp (1 ramdom PSU)
   - Gearbox
7. Recover config

### Test cases #6 - Check the response when injecting corresponding sensor error 
1. Mock the temperature for tested sensors to a minimum(30c)
2. Inject errors by writing err values to corresponding static files
3. Check expected PWM is changed to the value from Dmin table. 
   We can get the Dim table from /var/run/hw-management/config/tc_config.json
4. Check FAN speed is set to correct range
6. Repeat step 1 ~ step 4 for below scenarios
   - FAN present err (FAN not present)
     - e.g. echo 0 >> /run/hw-management/thermal/fan1_status
   - FAN direction err (One or more FANs have opposite dir)
     - e.g. echo 0 >> /run/hw-management/thermal/fan1_dir
   - FAN tacho err (Current FAN RPM is not correct and does not correspond to expected)
     - e.g. echo 10 >> /run/hw-management/thermal/fan1_speed_set
   - PSU present err (PSU not present)
     - e.g. echo 0 >> /run/hw-management/thermal/psu1_status
   - PSU FAN direction err (PSU FAN dir is opposite to system FAN)
     - e.g. echo 0 >> /run/hw-management/thermal/psu1_fan_dir
   - Thermal sensor reading error (cpu_pack, amb, module) file missing
     - remove the corresponding files
   - Thermal sensor reading error (cpu_pack, amb, module) file including incompatible value (reading null/none/wrong format numeric value from the file)
     - e.g. echo an incompatible value into the corresponding files
    
### Test cases #7 - Extended periodic report
1. Change the period to 10s by echo 10 to  {hw-management}/config/periodic_report
2. Restart TC service & wait 30s
3. Check there are thermal periodic reports in syslog, and the period is 10s.

### Test cases #8 - Add one sensor into blacklist, check it will not affect PWN calculation.
1. Add asic sensor to blacklist
   - Touch /var/run/hw-management/thermal/asic_blacklist
   - echo 1 > /var/run/hw-management/thermal/asic_blacklist
2. Mock asic temperature to val_max
3. Check PWM is not 100.


### Existing tests needed to be updated accordingly
1. test_thermal_control.py
   - test_dynamic_minimum_table 
   - test_set_psu_fan_speed
   - test_psu_absence_policy
   - test_cpu_thermal_control
    
2. test_psu_power_threshold.py
   - test_psu_power_threshold

3. test_platform_info.py
   - test_turn_on_off_psu_and_check_psustatus
   - test_show_platform_fanstatus_mocked
   - test_show_platform_temperature_mocked
   - test_thermal_control_load_invalid_format_json
   - test_thermal_control_load_invalid_value_json
   - test_thermal_control_fan_status

4. test_system_health.py
   - test_device_checker
   - test_system_health_config
