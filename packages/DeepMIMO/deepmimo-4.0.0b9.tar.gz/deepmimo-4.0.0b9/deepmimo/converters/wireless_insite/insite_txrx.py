"""
Wireless Insite TX/RX Set Converter.

This module provides functionality to convert Wireless Insite TX/RX set configurations
to DeepMIMO format. It handles both grid-based and point-based TX/RX sets, including
antenna configurations and spatial positions.

This module provides:
- InSiteTxRxSet class for parsing and managing Wireless Insite TX/RX configurations
- Functions to convert InSite sets to DeepMIMO format
- Visualization tools for TX/RX set layouts
- XML parsing and data extraction utilities

The module serves as a bridge between Wireless Insite's XML-based configuration
and DeepMIMO's standardized dataset format.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from ...txrx import TxRxSet
from .xml_parser import parse_insite_xml
from ...config import config

@dataclass
class InSiteTxRxSet:
    """Class for managing Wireless Insite TX/RX set configurations.
    
    This class handles both grid-based and point-based TX/RX sets from Wireless Insite,
    providing properties to access various configuration parameters and methods to
    convert to DeepMIMO format.

    Attributes:
        data (Dict[str, Any]): Raw dictionary containing the TX/RX set configuration
        set_type (str): Type of set, either 'grid' or 'point'
    """
    data: Dict[str, Any]
    set_type: str  # 'grid' or 'point'
    
    @property
    def conform_to_terrain(self) -> bool:
        """Whether the set conforms to terrain elevation."""
        return self.data['ConformToTerrain']['remcom_rxapi_Boolean']
    
    @property
    def output_id(self) -> int:
        """Unique identifier for this TX/RX set."""
        return self.data['OutputID']['remcom_rxapi_Integer']
    
    @property
    def short_description(self) -> str:
        """Short description/name of the TX/RX set."""
        return self.data['ShortDescription']['remcom_rxapi_String']
    
    @property
    def use_apg_acceleration(self) -> bool:
        """Whether APG acceleration is enabled for this set."""
        return self.data['UseAPGAcceleration']['remcom_rxapi_Boolean']
    
    @property
    def points(self) -> List[Dict[str, float]]:
        """List of control points defining the set's spatial configuration.
        
        Returns:
            List of dictionaries containing x, y, z coordinates for each point
        """
        points_list = self.data['ControlPoints']['remcom_rxapi_ProjectedPointList']['ProjectedPoint']
        if isinstance(points_list, dict):
            points_list = [points_list]
        
        return [{
            'x': p['remcom_rxapi_CartesianPoint']['X']['remcom_rxapi_Double'],
            'y': p['remcom_rxapi_CartesianPoint']['Y']['remcom_rxapi_Double'],
            'z': p['remcom_rxapi_CartesianPoint']['Z']['remcom_rxapi_Double']
        } for p in points_list]
    
    @property
    def length_x(self) -> Optional[float]:
        """Length of the grid in X dimension (for grid sets only)."""
        return self.data.get('LengthX', {}).get('remcom_rxapi_Double')
    
    @property
    def length_y(self) -> Optional[float]:
        """Length of the grid in Y dimension (for grid sets only)."""
        return self.data.get('LengthY', {}).get('remcom_rxapi_Double')
    
    @property
    def spacing(self) -> Optional[float]:
        """Spacing between points in the grid (for grid sets only)."""
        return self.data.get('Spacing', {}).get('remcom_rxapi_Double')
    
    def _get_antenna_data(self, tx_rx: str) -> Optional[Dict[str, Any]]:
        """Get antenna configuration data for either transmitter or receiver.
        
        Args:
            tx_rx (str): Either 'Transmitter' or 'Receiver'
            
        Returns:
            Dictionary containing antenna configuration including polarization and rotations,
            or None if the specified type is not present
        """
        if tx_rx not in self.data:
            return None
            
        ant_data = self.data[tx_rx]['remcom_rxapi_' + tx_rx]
        
        # Get antenna configuration
        isotropic_dict = ant_data['Antenna']['remcom_rxapi_Isotropic']
        antenna_config = {
            'polarization': isotropic_dict['Polarization']['remcom_rxapi_PolarizationEnum'],
            'power_threshold': isotropic_dict['PowerThreshold']['remcom_rxapi_Double']
        }
        
        # Handle different rotation structures based on Wireless Insite version
        if config.get('wireless_insite_version').startswith('4.'):
            # Version 4.x uses AntennaAlignment with SphericalAlignment
            alignment = ant_data['AntennaAlignment']['remcom_rxapi_SphericalAlignment']
            rotations = {
                'bearing': alignment['Phi']['remcom_rxapi_Double'],
                'pitch': alignment['Theta']['remcom_rxapi_Double'],
                'roll': alignment['Roll']['remcom_rxapi_Double']
            }
        else:
            # Version 3.x uses AntennaRotations with Rotations
            rot_dict = ant_data['AntennaRotations']['remcom_rxapi_Rotations']
            rotations = {
                'bearing': rot_dict['Bearing']['remcom_rxapi_Double'],
                'pitch': rot_dict['Pitch']['remcom_rxapi_Double'],
                'roll': rot_dict['Roll']['remcom_rxapi_Double']
            }
        
        return {
            'antenna': antenna_config,
            'rotations': rotations
        }
    
    @property
    def transmitter(self) -> Optional[Dict[str, Any]]:
        """Get transmitter antenna configuration if present."""
        return self._get_antenna_data('Transmitter')
    
    @property
    def receiver(self) -> Optional[Dict[str, Any]]:
        """Get receiver antenna configuration if present."""
        return self._get_antenna_data('Receiver')
    
    def copy(self) -> 'InSiteTxRxSet':
        """Create a deep copy of this set with a new data dictionary.
        
        Returns:
            A new InSiteTxRxSet instance with copied data
        """
        from copy import deepcopy
        return InSiteTxRxSet(deepcopy(self.data), self.set_type)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], set_type: str = 'point') -> 'InSiteTxRxSet':
        """Create an InSiteTxRxSet instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing TX/RX set configuration
            set_type (str, optional): Type of set. Defaults to 'point'.
            
        Returns:
            New InSiteTxRxSet instance
        """
        return cls(data, set_type)

    def generate_points(self) -> np.ndarray:
        """Generate XYZ coordinates for all points in the set.
        
        For grid sets, generates a regular grid of points based on the control point,
        length, and spacing parameters. For point sets, returns the control points directly.
        
        Returns:
            numpy.ndarray: Array of shape (N, 3) containing XYZ coordinates for all points
        """
        if self.set_type == 'grid':
            # Get origin point
            origin = self.points[0]
            
            # Calculate number of points in each dimension
            nx = int(self.length_x / self.spacing) + 1
            ny = int(self.length_y / self.spacing) + 1
            
            # Create coordinate arrays
            x = np.linspace(origin['x'], origin['x'] + self.length_x, nx)
            y = np.linspace(origin['y'], origin['y'] + self.length_y, ny)
            
            # Create grid of points
            xx, yy = np.meshgrid(x, y)
            zz = np.full_like(xx, origin['z'])
            
            # Stack coordinates into (N, 3) array
            return np.column_stack((xx.flatten(), yy.flatten(), zz.flatten()))
        else:
            return np.array([[p['x'], p['y'], p['z']] for p in self.points])

    def to_deepmimo_txrxset(self, id_: int, points: np.ndarray) -> TxRxSet:
        """Convert this set to DeepMIMO TxRxSet format.
        
        Args:
            id_ (int): Unique identifier for the DeepMIMO set
            points (np.ndarray): Array of XYZ coordinates for all points
            
        Returns:
            TxRxSet: DeepMIMO format TX/RX set
        """
        is_tx = self.transmitter is not None
        is_rx = self.receiver is not None
        
        # Get antenna parameters from the appropriate source
        if is_rx:
            antenna = self.receiver['antenna']
            rotations = self.receiver['rotations']
        else:
            antenna = self.transmitter['antenna']
            rotations = self.transmitter['rotations']
        
        return TxRxSet(
            name=self.short_description,
            id_orig=self.output_id,
            id=id_,
            is_tx=is_tx,
            is_rx=is_rx,
            num_points=len(points),
            num_active_points=len(points),  # Initially assume all points are active
            num_ant=1 if antenna['polarization'] in ['Vertical', 'Horizontal'] else 2,
            dual_pol=antenna['polarization'] == 'Both',
            array_orientation=[rotations['bearing'], rotations['pitch'], rotations['roll']]
        )

def convert_sets_to_deepmimo(insite_sets: List[InSiteTxRxSet]) \
                             -> Tuple[List[TxRxSet], Dict[int, np.ndarray]]:
    """Convert multiple InSite sets to DeepMIMO format.
    
    This function handles sets that contain both transmitter and receiver configurations
    by splitting them into separate TX and RX sets when necessary.
    
    Args:
        insite_sets (List[InSiteTxRxSet]): List of InSite TX/RX sets to convert
        
    Returns:
        Tuple containing:
            - List of DeepMIMO TxRxSet objects
            - Dictionary mapping set IDs to their point coordinates
    """
    txrx_sets = []
    point_locations = {}
    
    for insite_set in insite_sets:
        # Generate points
        points = insite_set.generate_points()
        
        # If both TX and RX present, check if they have different antennas
        if insite_set.transmitter and insite_set.receiver:
            same_antennas = (insite_set.transmitter['antenna'] == insite_set.receiver['antenna'] and 
                             insite_set.transmitter['rotations'] == insite_set.receiver['rotations'])
            
            if not same_antennas:
                # Create TX-only set
                insite_set_tx = insite_set.copy()
                insite_set_tx.data.pop('Receiver', None)
                tx_id = len(txrx_sets)
                txrx_tx = insite_set_tx.to_deepmimo_txrxset(id_=tx_id, points=points)
                txrx_sets.append(txrx_tx)
                point_locations[tx_id] = points

                # Change the other set to be RX-only
                insite_set.data.pop('Transmitter', None)

        current_id = len(txrx_sets)
        txrx = insite_set.to_deepmimo_txrxset(id_=current_id, points=points)
        txrx_sets.append(txrx)
        point_locations[current_id] = points
        
    return txrx_sets, point_locations

def get_txrx_insite_sets_from_xml(xml_file: str) -> List[InSiteTxRxSet]:
    """Extract TxRxSets from InSite XML file.
    
    Args:
        xml_file (str): Path to InSite XML file
        
    Returns:
        List[InSiteTxRxSet]: List of parsed InSite TX/RX sets
    """
    data = parse_insite_xml(xml_file)
    
    # Get TxRxSetList
    txrx_list = (data['remcom_rxapi_Job']['Scene']['remcom_rxapi_Scene']
                ['TxRxSetList']['remcom_rxapi_TxRxSetList']['TxRxSet'])
    
    insite_sets = []
    for txrx_set in txrx_list:
        txrx_type = list(txrx_set.keys())[0]
        set_data = txrx_set[txrx_type]
        
        # Convert to InSiteTxRxSet with appropriate type
        set_type = 'grid' if txrx_type == 'remcom_rxapi_GridSet' else 'point'
        insite_sets.append(InSiteTxRxSet.from_dict(set_data, set_type=set_type))
        
    return insite_sets

def plot_txrx_sets(txrx_sets: List[TxRxSet], point_locations: Dict[int, np.ndarray], 
                   max_points: int = 5000, figsize: Tuple[float, float] = (8, 8)) -> None:
    """Create a 2D visualization of TxRx sets and their positions.
    
    Args:
        txrx_sets (List[TxRxSet]): List of DeepMIMO TX/RX sets
        point_locations (Dict[int, np.ndarray]): Dictionary mapping set IDs to their point coordinates
        max_points (int, optional): Maximum number of points to plot per set. Defaults to 5000.
        figsize (Tuple[float, float], optional): Figure size as (width, height). Defaults to (8, 8).
    """
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=figsize)
    for txrx_set in txrx_sets:
        points = point_locations[txrx_set.id]
        # Subsample if too many points
        ss = len(points) // max_points if len(points) > max_points else 1
        plt.scatter(points[::ss, 0], points[::ss, 1], 
                   label=f"{txrx_set.name} ({'TX' if txrx_set.is_tx else 'RX'})")
    
    plt.legend()
    plt.axis('equal')
    plt.grid(True)
    plt.title("TxRx Sets")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.show()

def read_txrx(folder: str, plot: bool = False) -> Dict[str, Any]:
    """Create TX/RX information from a folder containing Wireless Insite files.
    
    This function:
    1. Reads the XML file to get TX/RX set configurations
    2. Returns a dictionary with all TX/RX information
    
    Args:
        folder (str): Path to simulation folder containing XML file
        plot (bool, optional): Whether to plot the TX/RX sets. Defaults to False.
        
    Returns:
        Dict[str, Any]: Dictionary containing TX/RX set information and indices
    """
    sim_folder = Path(folder)

    # Find .txrx file
    xml_files = list(sim_folder.glob("*.xml"))
    if not xml_files:
        raise ValueError(f"No .xml file found in {sim_folder}")
    if len(xml_files) > 1:
        raise ValueError(f"Multiple .xml files found in {sim_folder}")
    
    # Parse TX/RX sets
    xml_file = str(xml_files[0])
    
    print(f'Reading xml file: {os.path.basename(xml_file)}')

    insite_sets = get_txrx_insite_sets_from_xml(xml_file)
    txrx_sets, point_locations = convert_sets_to_deepmimo(insite_sets)
    
    # Create txrx_sets dictionary with idx-based keys
    txrx_dict = {}
    for obj in txrx_sets:
        txrx_dict[f'txrx_set_{obj.id}'] = obj.to_dict()
    
    # Optional visualization
    if plot:
        plot_txrx_sets(txrx_sets, point_locations)
    
    return txrx_dict


# Example usage:
if __name__ == "__main__":
    # Example 1: Grid set dictionary
    grid_dict = {
        'ConformToTerrain': {'remcom_rxapi_Boolean': True},
        'ControlPoints': {
            'remcom_rxapi_ProjectedPointList': {
                'ProjectedPoint': {
                    'remcom_rxapi_CartesianPoint': {
                        'X': {'remcom_rxapi_Double': 242.42327880859378},
                        'Y': {'remcom_rxapi_Double': 297.17103576660156},
                        'Z': {'remcom_rxapi_Double': 2}
                    }
                }
            }
        },
        'LengthX': {'remcom_rxapi_Double': 36},
        'LengthY': {'remcom_rxapi_Double': 550},
        'OutputID': {'remcom_rxapi_Integer': 1},
        'ShortDescription': {'remcom_rxapi_String': 'RX_1'},
        'Spacing': {'remcom_rxapi_Double': 0.2},
        'UseAPGAcceleration': {'remcom_rxapi_Boolean': False},
        'Receiver': {
            'remcom_rxapi_Receiver': {
                'Antenna': {
                    'remcom_rxapi_Isotropic': {
                        'CableLoss': {'remcom_rxapi_Double': 0},
                        'Polarization': {'remcom_rxapi_PolarizationEnum': 'Vertical'},
                        'PowerThreshold': {'remcom_rxapi_Double': -250},
                        'Temperature': {'remcom_rxapi_Double': 293},
                        'VSWR': {'remcom_rxapi_Double': 1},
                        'Waveform': {
                            'remcom_rxapi_Sinusoid': {
                                'Amplitude': {'remcom_rxapi_Double': 1},
                                'Bandwidth': {'remcom_rxapi_Double': 1},
                                'CarrierFrequency': {'remcom_rxapi_Double': 28000000000},
                                'Dispersive': {'remcom_rxapi_Boolean': False},
                                'Phase': {'remcom_rxapi_Double': 0}
                            }
                        }
                    }
                },
                'AntennaRotations': {
                    'remcom_rxapi_Rotations': {
                        'Bearing': {'remcom_rxapi_Double': 0},
                        'Pitch': {'remcom_rxapi_Double': 0},
                        'Roll': {'remcom_rxapi_Double': 0}
                    }
                },
                'CollectionRadius': {'remcom_rxapi_Double': 0}
            }
        }
    }
    
    # Create InSiteSet instance
    grid = InSiteTxRxSet.from_dict(grid_dict, set_type='grid')
    print(f"Grid spacing: {grid.spacing}")
    print(f"First control point: {grid.points[0]}")
    
    # Example 2: With a file
    xml_file = r"F:\deepmimo_loop_ready\o1b_28\O1_28B.RT_O1_28B.xml"
    
    # Parse XML and get TxRxSets
    data = parse_insite_xml(xml_file)
    
    # Convert to DeepMIMO format
    insite_sets = get_txrx_insite_sets_from_xml(xml_file)
    txrx_sets, point_locations = convert_sets_to_deepmimo(insite_sets)
    
    # Print information about each set
    for txrx_set in txrx_sets:
        print(f"\n{txrx_set}")
        points = point_locations[txrx_set.id]
        print(f"Point locations shape: {points.shape}")
        print(f"First 3 points:\n{points[:3]}")
    
    # Visualize using the new function
    plot_txrx_sets(txrx_sets, point_locations)
