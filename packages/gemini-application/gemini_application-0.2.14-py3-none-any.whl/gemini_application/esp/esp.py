from gemini_application.application_abstract import ApplicationAbstract
from gemini_model.pump.esp import ESP
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import pytz
from datetime import datetime, timezone

tzobject = pytz.timezone('Europe/Amsterdam')


class ESPApp(ApplicationAbstract):
    """Class for application ESP calculation"""

    def __init__(self):
        super().__init__()

        self.ESP = ESP()

    def init_parameters(self):
        """Function to initialize model parameters"""
        esp_unit = self.unit

        esp_param = dict()
        esp_param['no_stages'] = esp_unit.parameters['property']['esp_no_stage'][0]
        esp_param['pump_name'] = esp_unit.parameters['property']['esp_type'][0]
        esp_param['head_coeff'] = np.asarray(
            esp_unit.parameters['property']['esp_head_coeff'][0].split(';'),
            dtype=np.float32)
        esp_param['power_coeff'] = np.asarray(
            esp_unit.parameters['property']['esp_power_coeff'][0].split(';'),
            dtype=np.float32)
        esp_param['min_flow'] = esp_unit.parameters['property']['esp_min_flow'][0]
        esp_param['max_flow'] = esp_unit.parameters['property']['esp_max_flow'][0]
        esp_param['bep_flow'] = esp_unit.parameters['property']['esp_bep_flow'][0]

        self.ESP.update_parameters(esp_param)

        self.outputs['esp_correction_factor'] = \
            esp_unit.parameters['property']['esp_correction_factor'][0]

    def get_data(self):

        start_time = datetime.strptime(self.inputs['start_time'], '%Y-%m-%d %H:%M:%S')
        start_time = tzobject.localize(start_time)
        start_time = start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        end_time = datetime.strptime(self.inputs['end_time'], '%Y-%m-%d %H:%M:%S')
        end_time = tzobject.localize(end_time)
        end_time = end_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        timestep = 3600  # hardcoded 1 hour since flowrate is in m3/h

        database = self.plant.database

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_flow.measured',
            start_time,
            end_time,
            timestep
        )
        self.outputs['flow_measured'] = np.array(result)  # m3/hr
        self.outputs['time'] = np.array(time)

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_frequency.measured',
            start_time,
            end_time,
            timestep
        )
        self.outputs['frequency_measured'] = np.array(result)  # Hz

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_inlet_pressure.measured',
            start_time,
            end_time,
            timestep
        )
        self.outputs['inlet_pressure_measured'] = np.array(result)  # bar

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_vlp_head.calculated',
            start_time,
            end_time,
            timestep
        )
        self.outputs['esp_vlp_head_calculated'] = np.array(result)

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_theoretical_head.calculated',
            start_time,
            end_time,
            timestep
        )
        self.outputs['esp_theoretical_head_calculated'] = np.array(result)  # bar

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_vlp_outlet_pressure.calculated',
            start_time,
            end_time,
            timestep
        )
        self.outputs['esp_vlp_outlet_pressure_calculated'] = np.array(result)  # bar

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_vlp_ipr_inlet_pressure.calculated',
            start_time,
            end_time,
            timestep
        )
        self.outputs['esp_vlp_ipr_inlet_pressure_calculated'] = np.array(result)  # bar

        result, time = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_theoretical_outlet_pressure.calculated',
            start_time,
            end_time,
            timestep
        )
        self.outputs['esp_theoretical_outlet_pressure_calculated'] = np.array(result)  # bar

    def calibrate_esp_head_simple(self):

        start_time = datetime.strptime(self.inputs['calibration_start_time'], '%Y-%m-%d %H:%M:%S')
        start_time = tzobject.localize(start_time)
        start_time = start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        end_time = datetime.strptime(self.inputs['calibration_end_time'], '%Y-%m-%d %H:%M:%S')
        end_time = tzobject.localize(end_time)
        end_time = end_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        timestep = 3600  # hardcoded 1 hour since flowrate is in m3/h

        database = self.plant.database

        esp_vlp_head, _ = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_vlp_head.calculated',
            start_time,
            end_time,
            timestep
        )

        esp_theoretical_head, _ = database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'esp_theoretical_head.calculated',
            start_time,
            end_time,
            timestep
        )

        x = []
        y = []
        for xi, yi in zip(esp_vlp_head, esp_theoretical_head):
            if xi is not None and yi is not None:
                x.append(xi)
                y.append(yi)
        x = np.array(x)
        y = np.array(y)

        if len(x) < 2:
            raise ValueError("Not enough valid data points for calibration.")

        # Linear regression: y = ax + b
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        a = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
        b = y_mean - a * x_mean

        self.outputs['esp_correction_factor'] = f"{a};{b}"

    def calculate(self):
        """Function to calcaulte IPR, VLP, ESP"""
        xValues_arrays = []
        min_flow_array = []
        max_flow_array = []
        frequency_array = np.arange(self.inputs['min_frequency'],
                                    self.inputs['max_frequency'] + 10,
                                    10)
        min_flow = self.ESP.parameters['min_flow']
        max_flow = self.ESP.parameters['max_flow']

        for freq in frequency_array:
            Xmin = 0
            Xmax = max_flow * 2
            min_flow_freq = min_flow * freq / 60
            min_flow_array.append(min_flow_freq)
            max_flow_freq = max_flow * freq / 60
            max_flow_array.append(max_flow_freq)

            # Flow rates scaled by frequency
            x_array = np.arange(Xmin * freq / 60,
                                Xmax * freq / 60,
                                10 * freq / 60)
            xValues_arrays.append(x_array)

        self.outputs['xValues'] = xValues_arrays
        self.outputs['frequency'] = frequency_array
        self.outputs['min_flow_array'] = min_flow_array
        self.outputs['max_flow_array'] = max_flow_array

        self.get_data()
        self.calculate_pump_head_curve()

    def calculate_pump_head_curve(self):
        """Function to calculate ESP output"""
        try:
            pump_head_all = []
            pump_power_all = []
            pump_eff_all = []
            head_min_flow_freq = []
            head_max_flow_freq = []
            min_flow = self.ESP.parameters['min_flow']
            max_flow = self.ESP.parameters['max_flow']

            for freq_idx, freq in enumerate(self.outputs['frequency']):
                u = dict()
                pump_head_freq = []
                pump_power_freq = []
                pump_eff_freq = []
                xValues_array = self.outputs['xValues'][freq_idx]

                for flow in xValues_array:
                    u['pump_freq'] = freq
                    u['pump_flow'] = flow * 60 / freq / 3600  # Convert flow to m^3/s

                    x = []
                    self.ESP.calculate_output(u, x)

                    # ASSERT
                    y = self.ESP.get_output()
                    pump_head_freq.append(y['pump_head'] / 1e5)  # Convert to bar
                    pump_power_freq.append(y['pump_power'])
                    pump_eff_freq.append(y['pump_eff'])

                pump_head_all.append(pump_head_freq)
                pump_power_all.append(pump_power_freq)
                pump_eff_all.append(pump_eff_freq)

                # Min flow
                u = dict()
                u['pump_freq'] = freq
                u['pump_flow'] = min_flow / 3600  # Convert flow to m^3/s

                x = []
                self.ESP.calculate_output(u, x)

                # ASSERT
                y = self.ESP.get_output()
                head_min_flow = y['pump_head'] / 1e5
                head_min_flow_freq.append(head_min_flow)

                # Max flow
                u = dict()
                u['pump_freq'] = freq
                u['pump_flow'] = max_flow / 3600  # Convert flow to m^3/s

                x = []
                self.ESP.calculate_output(u, x)

                # ASSERT
                y = self.ESP.get_output()
                head_max_flow = y['pump_head'] / 1e5
                head_max_flow_freq.append(head_max_flow)

        except Exception as e:
            print("ERROR:" + repr(e))
            pump_head_all = None
            pump_power_all = None
            pump_eff_all = None

        self.outputs['pump_head'] = pump_head_all
        self.outputs['pump_power'] = pump_power_all
        self.outputs['pump_eff'] = pump_eff_all
        self.outputs['pump_head_min_flow'] = head_min_flow_freq
        self.outputs['pump_head_max_flow'] = head_max_flow_freq

    def plot(self):
        """Function to plot pump curves and the measured data"""

        bar_to_meters = 10.1972  # 1 bar ≈ 10.1972 meters of water head

        def format_func(value, ti):
            date = pd.to_datetime(value)
            return date.strftime('%d %B %Y')

        time_measured = pd.to_datetime(self.outputs['time'])
        flow_measured = self.outputs['flow_measured']
        esp_vlp_head_calculated = self.outputs['esp_vlp_head_calculated']
        time_x = flow_measured

        pump_head_all = self.outputs['pump_head']
        xValues = self.outputs['xValues']
        frequency_array = self.outputs['frequency']

        # Head calibration
        a, b = [float(x) for x in self.outputs['esp_correction_factor'].split(';')]
        head_corrected = np.array(
            [a * x + b if x is not None else None for x in esp_vlp_head_calculated])
        head_corrected_m = head_corrected * bar_to_meters

        plt.figure()

        # Plot measured data with a color map representing time
        scatter = plt.scatter(time_x, head_corrected_m,
                              c=time_measured.astype('int64'), cmap='jet')
        colorbar = plt.colorbar(scatter)
        colorbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))

        # Iterate over each frequency and corresponding flow array
        for i, freq in enumerate(frequency_array):
            pump_head_meters = np.array(pump_head_all[i]) * bar_to_meters
            plt.plot(xValues[i], pump_head_meters, label=f'Frequency: {freq} Hz')

        head_min_flow_freq = np.array(self.outputs['pump_head_min_flow']) * bar_to_meters
        head_max_flow_freq = np.array(self.outputs['pump_head_max_flow']) * bar_to_meters
        min_flow_array = self.outputs['min_flow_array']
        max_flow_array = self.outputs['max_flow_array']
        plt.plot(min_flow_array, head_min_flow_freq, label='Min optimum rate', linestyle='--')
        plt.plot(max_flow_array, head_max_flow_freq, label='Max optimum rate', linestyle='--')
        plt.xlabel('Flow Rate (m³/h)')
        plt.ylabel('Pump Head (m)')
        plt.title('Pump Head vs Flow Rate')
        plt.legend()
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        plt.xticks(ticks=range(0, int(max(xValues[i])) + 20, 20))
        plt.yticks(ticks=range(0, int(max(pump_head_meters)) + 100, 100))
        plt.grid(True)
        plt.show()

    def plot_comparison(self):
        """Function to plot the measured and calculated tags"""

        time_measured = pd.to_datetime(self.outputs['time'])
        flow_measured = self.outputs['flow_measured']
        frequency_measured = self.outputs['frequency_measured']
        esp_vlp_head_calculated = self.outputs['esp_vlp_head_calculated']
        esp_theoretical_head_calculated = self.outputs['esp_theoretical_head_calculated']
        esp_vlp_outlet_pressure_calculated = self.outputs[
            'esp_vlp_outlet_pressure_calculated']
        esp_vlp_ipr_inlet_pressure_calculated = self.outputs[
            'esp_vlp_ipr_inlet_pressure_calculated']
        intake_pressure_measured = self.outputs['inlet_pressure_measured']
        esp_theoretical_outlet_pressure_calculated = self.outputs[
            'esp_theoretical_outlet_pressure_calculated']

        # Head calibration
        a, b = [float(x) for x in self.outputs['esp_correction_factor'][0].split(';')]
        head_corrected = np.array(
            [a * x + b if x is not None else None for x in esp_vlp_head_calculated])

        fig, axes = plt.subplots(4, 2, figsize=(12, 12))
        fig.tight_layout(pad=4.0)

        axes[0, 0].plot(time_measured, flow_measured, label='Flow')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        axes[0, 0].set_title('Flow vs Time')

        axes[0, 1].plot(time_measured, frequency_measured, label='Frequency')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        axes[0, 1].set_title('Frequency vs Time')

        axes[1, 0].plot(time_measured, esp_vlp_head_calculated, label='Calculated Head via VLP')
        axes[1, 0].plot(
            time_measured, esp_theoretical_head_calculated, label='Theoretical Head')
        axes[1, 0].plot(
            time_measured, head_corrected,
            label=f'Calibrated VLP Head ({a:.2f}*x + {b:.2f})',
            linestyle='--')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        axes[1, 0].set_title('Head vs Time')

        axes[1, 1].plot(
            time_measured, esp_vlp_head_calculated - esp_theoretical_head_calculated,
            label='differences')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        axes[1, 1].set_title('Calculated head via VLP - Theoretical head vs Time')

        axes[2, 0].plot(
            time_measured,
            esp_vlp_outlet_pressure_calculated,
            label='Calculated Outlet Pressure via VLP')
        axes[2, 0].plot(
            time_measured, esp_theoretical_outlet_pressure_calculated,
            label='Theoretical Outlet Pressure')
        axes[2, 0].legend()
        axes[2, 0].grid(True)
        axes[2, 0].set_title('Outlet Pressure vs Time')

        axes[2, 1].plot(
            time_measured,
            esp_vlp_outlet_pressure_calculated - esp_theoretical_outlet_pressure_calculated,
            label='differences'
        )
        axes[2, 1].legend()
        axes[2, 1].grid(True)
        axes[2, 1].set_title(
            'Calculated Outlet Pressure via VLP - Theoretical Outlet Pressure vs Time')

        axes[3, 0].plot(time_measured, intake_pressure_measured, label='Measured Inlet Pressure')
        axes[3, 0].plot(
            time_measured, esp_vlp_ipr_inlet_pressure_calculated,
            label='Calculated Inlet Pressure via VLP-IPR')
        axes[3, 0].legend()
        axes[3, 0].grid(True)
        axes[3, 0].set_title('Inlet Pressure vs Time')

        axes[3, 1].plot(
            time_measured, intake_pressure_measured - esp_vlp_ipr_inlet_pressure_calculated,
            label='differences')
        axes[3, 1].legend()
        axes[3, 1].grid(True)
        axes[3, 1].set_title(
            'Measured Inlet Pressure - Calculated Inlet Pressure via VLP-IPR vs Time')

        plt.show()
