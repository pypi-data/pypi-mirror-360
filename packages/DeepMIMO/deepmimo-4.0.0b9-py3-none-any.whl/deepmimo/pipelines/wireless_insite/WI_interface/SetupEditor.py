"""
SetupEditor module for electromagnetic simulation setup.

This module provides functionality to create, edit, and save setup files for
electromagnetic simulations, including study area, ray tracing parameters, and features.
"""

import numpy as np
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class StudyArea:
    """Class representing the study area for electromagnetic simulation.
    
    Attributes:
        zmin (float): Minimum z-coordinate of the study area
        zmax (float): Maximum z-coordinate of the study area
        num_vertex (int): Number of vertices defining the study area boundary
        all_vertex (np.ndarray): Array of vertices defining the study area boundary
    """
    zmin: float
    zmax: float
    num_vertex: int
    all_vertex: np.ndarray  # np.empty((num_vertex, 3))


@dataclass
class RayTracingParam:
    """Class representing ray tracing parameters for electromagnetic simulation.
    
    Attributes:
        max_paths (int): Maximum number of paths to render
        ray_spacing (float): Spacing between rays
        max_reflections (int): Maximum number of reflections
        max_transmissions (int): Maximum number of transmissions
        max_diffractions (int): Maximum number of diffractions
        ds_enable (bool): Whether diffuse scattering is enabled
        ds_max_reflections (int): Maximum number of diffuse reflections
        ds_max_transmissions (int): Maximum number of diffuse transmissions
        ds_max_diffractions (int): Maximum number of diffuse diffractions
        ds_final_interaction_only (bool): Whether to only apply diffuse scattering at final interaction
    """
    max_paths: int
    ray_spacing: float
    max_reflections: int
    max_transmissions: int
    max_diffractions: int
    ds_enable: bool
    ds_max_reflections: int
    ds_max_transmissions: int
    ds_max_diffractions: int
    ds_final_interaction_only: bool


@dataclass
class Feature:
    """Class representing a feature in the electromagnetic simulation.
    
    Attributes:
        index (int): Index of the feature
        type (str): Type of the feature (e.g., 'terrain', 'city', 'road')
        path (str): Path to the feature file
    """
    index: int
    type: str
    path: str


class SetupEditor:
    """Class for editing setup files for electromagnetic simulation.
    
    This class provides methods to create, edit, and save setup files for
    electromagnetic simulations, including study area, ray tracing parameters, and features.
    
    Attributes:
        scenario_path (str): Path to the scenario directory
        feature_template (List[str]): Template for feature section
        txrx_template (List[str]): Template for transmitter/receiver section
        num_feature (int): Number of features
        feature_sec (List[str]): Feature section of the setup file
        txrx_sec (List[str]): Transmitter/receiver section of the setup file
        setup_file (List[str]): Contents of the setup file
        name (str): Name of the setup
        features (List[Feature]): List of features in the setup
    """
    
    def __init__(self, scenario_path: str) -> None:
        """Initialize the SetupEditor with a scenario path and optional setup name.
        
        Args:
            scenario_path (str): Path to the scenario directory
        """
        self.scenario_path = scenario_path
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        setup_template_folder = os.path.join(script_dir, "..", "resources", "setup")
        with open(os.path.join(setup_template_folder, "feature.txt")) as f1:
            self.feature_template = f1.readlines()
        with open(os.path.join(setup_template_folder, "txrx.txt")) as f1:
            self.txrx_template = f1.readlines()

        self.num_feature = 0
        self.features = []
        self.feature_sec = []
        self.txrx_sec = self.txrx_template.copy()

        with open(os.path.join(setup_template_folder, "template.setup"), "r") as f:
            self.setup_file = f.readlines()
        self.name = self.setup_file[1].split(" ")[-1][:-1]

    def set_carrierFreq(self, carrier_frequency: float) -> None:
        """Set the carrier frequency.
        
        Args:
            carrier_frequency (float): Carrier frequency in Hz
        """
        self.carrier_frequency = carrier_frequency

    def set_bandwidth(self, bandwidth: float) -> None:
        """Set the bandwidth.
        
        Args:
            bandwidth (float): Bandwidth in Hz
        """
        self.bandwidth = bandwidth

    def set_study_area(self, zmin: float, zmax: float, all_vertex: np.ndarray) -> None:
        """Set the study area parameters.
        
        Args:
            zmin (float): Minimum z-coordinate of the study area
            zmax (float): Maximum z-coordinate of the study area
            all_vertex (np.ndarray): Array of vertices defining the study area boundary
        """
        self.study_area = StudyArea(zmin, zmax, all_vertex.shape[0], all_vertex)

    def set_origin(self, origin_lat: float, origin_lon: float) -> None:
        """Set the origin parameters.
        
        Args:
            origin_lat (float): Latitude of the origin
            origin_lon (float): Longitude of the origin
        """
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon

    def set_ray_tracing_param(self, params: RayTracingParam | Dict[str, Any]) -> None:
        """Set the ray tracing parameters.
        
        Args:
            params: Either a RayTracingParam instance or a dictionary containing the fields of RayTracingParam
        """
        if isinstance(params, RayTracingParam):
            self.ray_tracing_param = params
        else:
            self.ray_tracing_param = RayTracingParam(**params)

    def set_txrx(self, txrx_filename: str) -> None:
        """Set the transmitter/receiver file path.
        
        Args:
            txrx_filename (str): Name of the transmitter/receiver file
            
        Raises:
            ValueError: If no transmitters/receivers are defined in the file
        """
        num_txrx = 0
        self.txrx_filename = txrx_filename
        txrx_file_path = os.path.join(self.scenario_path, txrx_filename)
        with open(txrx_file_path) as f1:
            txrx_file = f1.readlines()

        for line in txrx_file:
            if line.startswith("project_id"):
                num_txrx += 1
                first_available_txrx = np.int64(line.split(" ")[-1][:-1]) + 1

        if num_txrx <= 0:
            raise ValueError("Zero TxRx is defined!")

        self.txrx_sec[1] = self.txrx_sec[1].replace("[path]", "./" + txrx_file_path)
        self.txrx_sec[2] = self.txrx_sec[2].replace("[index]", str(first_available_txrx))

        self.first_available_txrx = first_available_txrx
        return

    def add_feature(self, feature_file_path: str, feature_type: str = "object") -> None:
        """Add a feature to the setup.
        
        Args:
            feature_file_path (str): Path to the feature file
            feature_type (str, optional): Type of the feature. Defaults to "object".
        """
        tmp = self.feature_template.copy()
        tmp[1] = tmp[1].replace("[index]", str(self.num_feature))
        tmp[2] = tmp[2].replace("[type]", feature_type)
        tmp[4] = tmp[4].replace("[path]", "./" + feature_file_path)

        self.feature_sec += tmp
        self.num_feature += 1

        self.features.append(Feature(self.num_feature, feature_type, feature_file_path))
        if feature_type == "terrain":
            self.terrain_filename = feature_file_path
        elif feature_type == "city":
            self.city_filename = feature_file_path
        elif feature_type == "road":
            self.road_filename = feature_file_path

    def update_carrier_frequency_bandwidth(self) -> None:
        """Update the carrier frequency and bandwidth in the setup file."""
        for i, line in enumerate(self.setup_file):
            if line.startswith("CarrierFrequency "):
                self.setup_file[i] = "CarrierFrequency %.6f\n" % self.carrier_frequency
                continue
            if line.startswith("bandwidth "):
                self.setup_file[i] = "bandwidth %.6f\n" % self.bandwidth
                continue
    
    def update_study_area(self) -> None:
        """Update the study area parameters in the setup file."""
        for i, line in enumerate(self.setup_file):
            if line.startswith("begin_<boundary>"):  # study area boundary
                self.setup_file[i + 8] = "zmin %.6f\n" % self.study_area.zmin
                self.setup_file[i + 9] = "zmax %.6f\n" % self.study_area.zmax
                self.setup_file[i + 10] = "nVertices %d\n" % self.study_area.num_vertex
                for j in range(self.study_area.num_vertex):
                    self.setup_file[i + j + 11] = "%.6f %.6f %.6f\n" % (
                        self.study_area.all_vertex[j, 0],
                        self.study_area.all_vertex[j, 1],
                        self.study_area.all_vertex[j, 2],
                    )
                return
    
    def update_origin(self) -> None:
        """Update the origin parameters in the setup file."""
        for i, line in enumerate(self.setup_file):
            if line.startswith("latitude"):
                self.setup_file[i] = "latitude %.8f\n" % self.origin_lat
                continue
            if line.startswith("longitude"):
                self.setup_file[i] = "longitude %.8f\n" % self.origin_lon
                continue
        return
    
    def update_ray_tracing_param(self) -> None:
        """Update the ray tracing parameters in the setup file."""
        for i, line in enumerate(self.setup_file):
            if line.startswith("MaxRenderedPaths"):
                self.setup_file[i] = "MaxRenderedPaths %d\n" % self.ray_tracing_param.max_paths
                continue
            if line.startswith("ray_spacing"):
                self.setup_file[i] = "ray_spacing %.6f\n" % self.ray_tracing_param.ray_spacing
                continue

            if line.startswith("max_reflections"):
                self.setup_file[i] = "max_reflections %d\n" % self.ray_tracing_param.max_reflections
                continue

            if line.startswith("max_transmissions"):
                self.setup_file[i] = "max_transmissions %d\n" % self.ray_tracing_param.max_transmissions
                continue

            if line.startswith("max_wedge_diffractions"):
                self.setup_file[i] = "max_wedge_diffractions %d\n" % self.ray_tracing_param.max_diffractions
                continue

            if line.startswith("begin_<diffuse_scattering>"):
                self.setup_file[i + 1] = "enabled yes\n" if self.ray_tracing_param.ds_enable else "enabled no\n"
                self.setup_file[i + 2] = "diffuse_reflections %d\n" % self.ray_tracing_param.ds_max_reflections
                self.setup_file[i + 3] = "diffuse_diffractions %d\n" % self.ray_tracing_param.ds_max_diffractions
                self.setup_file[i + 4] = "diffuse_transmissions %d\n" % self.ray_tracing_param.ds_max_transmissions
                self.setup_file[i + 5] = "final_interaction_only yes\n" if self.ray_tracing_param.ds_final_interaction_only else "final_interaction_only no\n"
                continue

    def update_features(self) -> None:
        """Update the features in the setup file."""
        for i, line in enumerate(self.setup_file):
            if line.startswith("end_<studyarea>"):
                self.feature_start = i + 1
                break
        self.setup_file = (
            self.setup_file[: self.feature_start]
            + self.feature_sec
            + self.txrx_sec
            + self.setup_file[self.feature_start :]
        )

    def update_all(self) -> None:
        """Update all parameters in the setup file."""
        self.update_carrier_frequency_bandwidth()
        self.update_study_area()
        self.update_origin()
        self.update_ray_tracing_param()
        self.update_features()

    def save(self, name: str, save_path: Optional[str] = None) -> None:
        """Save the setup file.
        
        Args:
            name (str): Name of the setup file
            save_path (Optional[str], optional): Path to save the setup file. Defaults to None.
        """
        if not save_path:
            save_path = os.path.join(self.scenario_path, name + ".setup")
        self.update_all()
        self.setup_file[1] = self.setup_file[1].replace("template", name)

        # clean the output file before writing
        open(save_path, "w+").close()
        with open(save_path, "w") as f:
            for line in self.setup_file:
                f.write(line)

    def get_txrx_path(self) -> str:
        """Return full path to TXRX file."""
        return os.path.join(self.scenario_path, self.txrx_filename)

    def get_terrain_path(self) -> str:
        """Return full path to terrain file."""
        return os.path.join(self.scenario_path, self.terrain_filename)

    def get_city_path(self) -> str:
        """Return full path to city file."""
        return os.path.join(self.scenario_path, self.city_filename)

    def get_road_path(self) -> str:
        """Return full path to road file."""
        return os.path.join(self.scenario_path, self.road_filename)


if __name__ == "__main__":
    scenario = SetupEditor(scenario_path="scenario_test/")
    scenario.set_txrx("gwc.txrx")
    scenario.set_study_area(
        0,
        17.5,
        np.asarray([[-200, -165, 0], [200, -165, 0], [200, 165, 0], [-200, 165, 0]]),
    )
    scenario.add_feature("newTerrain.ter", "terrain")
    scenario.add_feature("gwc_building.city", "city")
    scenario.add_feature("gwc_road.city", "city")

    scenario.save("gwc")
    print("done")
