from abc import ABC, abstractmethod

from gemini_framework.framework.boot_plant import setup


class ApplicationAbstract(ABC):
    """Abstract class fpr application"""
    def __init__(self):
        self.plant = None
        self.unit = None

        self.parameters = dict()
        self.inputs = dict()
        self.outputs = dict()

    def load_plant(self, project_path, plant_name):
        """Function to load the plant"""
        self.plant = setup(project_path, plant_name)

    def select_unit(self, unit_name):
        """Function to select unit for calculation"""
        for unit in self.plant.units:
            if unit.name == unit_name:
                self.unit = unit

    def set_input(self, inputs):
        """Function to set the input"""
        self.inputs = inputs

    def get_input(self):
        """Function to get the input"""
        return self.inputs

    def get_output(self):
        """Function to get the output"""
        return self.outputs

    @abstractmethod
    def init_parameters(self, initial_parameters):
        """Abstract function to initialize the model parameters"""
        pass

    @abstractmethod
    def calculate(self):
        """Abstract function to calculate the model"""
        pass
