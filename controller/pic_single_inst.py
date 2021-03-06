from . import test
from . import signal
from .exceptions import PlaybackDeviceException

class PICSingleInstructionGlitch(test.DeviceTest):
    test_name = 'PIC Single Instruction Glitch'

    parameters = [
        #TestParameter('Duration', ('s', 'cycles'), float)
    ]

    relevant_inputs = [
        test.TestIOMapping('Reset'),
        test.TestIOMapping('Button'),
        test.TestIOMapping('Clock')
    ]

    relevant_outputs = [
    ]

    def run(self, inputs, outputs):
        #Reminder: these are the zybo pins
        reset = self.relevant_input_values[0]
        button = self.relevant_input_values[1]
        clock = self.relevant_input_values[2]

        #clock_rate = 4000000
        clock_rate = 50000

        reset.signal = signal.Signal(initial_value=signal.LOW, sample_rate=2*clock_rate, duration=16/clock_rate)
        reset.signal = reset.signal.append(signal.Signal(initial_value=signal.HIGH, sample_rate=2*clock_rate, duration=16/clock_rate))


        button_high = 64/clock_rate #How long to hold the start button high
        button_low = 64/clock_rate   #How long to press the button
        #button_rest = 32/clock_rate #Leave the button high for the remainder
        button_rest = 64/clock_rate #Leave the button high for the remainder

        button.signal = signal.Signal(initial_value=signal.HIGH, sample_rate=2*clock_rate, duration=button_high)
        button.signal = button.signal.append(signal.Signal(initial_value=signal.LOW, sample_rate=2*clock_rate, duration=button_low))
        button.signal = button.signal.append(signal.Signal(initial_value=signal.HIGH, sample_rate=2*clock_rate, duration=button_rest))

        #Empirically measured that we should glitch at 20 cycles after the
        #button press
        #glitch_location=button_high+(20/clock_rate)
        #glitch_location_samples = int(glitch_location*clock.signal.sample_rate)
        #print('glitch_location (seconds): ', glitch_location)
        #print('glitch_location (samples): ', glitch_location_samples)

        sample_rate=40*clock_rate
        #glitch_start = 82.71
        #glitch_start = 84.00

        #for glitch_start in range(165,170):
        for glitch_start in [165]:

            #Manually generate a clock        
            clock.signal = signal.Signal(initial_value=signal.LOW, duration=0.5/clock_rate, sample_rate=sample_rate)
            for factor in [0.01]:
            #for factor in [0.01,0.025,0.05,0.10,0.20]:
                glitch_size=factor/clock_rate
                glitch_size=25e-08
                #glitch_size=5e-06
                print("Trying a glitch of %g at %g "%(glitch_size,glitch_start))
                for i in range(200):
                    if i % 2 == 0:
                        signal_value = signal.HIGH
                    else:
                        signal_value = signal.LOW

                    if i == glitch_start or i == glitch_start+1:
                        #Insert glitch
                        duration=glitch_size
                        print("Inserted glitch at time ", i*(0.5/clock_rate))
                    else:
                        duration=0.5/clock_rate
                    clock.signal = clock.signal.append(signal.Signal(initial_value=signal_value, sample_rate=sample_rate, duration=duration))

                #self.environment.plot(['inputs'])
                self.send_inputs(inputs, outputs)

                if not self.behavior_model.validate(inputs, outputs):
                    print("---")
                    print("Behavior model not validated")
                    print("glitch_start: ", glitch_start)
                    print("glitch_size: ", glitch_size)
                    print("---")


                    print("---")