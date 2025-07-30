"""
Wireless InSite TxRx Editor.

This module provides functionality to create and edit transmitter and receiver configurations
for Wireless InSite simulations. It supports both single points and arrays of points for
transmitter and receiver positions.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
import os

# Constants
COORD_PREC = 2  # Number of decimal places for coordinate values
COORD_FORMAT = "%%.%df %%.%df %%.%df\n" % (COORD_PREC, COORD_PREC, COORD_PREC)


@dataclass
class TxRx:
    """
    Class representing a transmitter or receiver in the Wireless InSite simulation.
    
    Attributes:
        txrx_name (str): Name of the transmitter/receiver
        txrx_id (int): Unique identifier
        txrx_type (str): Type of transmitter/receiver ('points' or 'grid')
        is_transmitter (bool): Whether this is a transmitter
        is_receiver (bool): Whether this is a receiver
        txrx_pos (np.ndarray): Position(s) of the transmitter/receiver. Shape (3,) for single point or (N, 3) for multiple points
        grid_side (Optional[np.ndarray]): Grid dimensions [width, height] if type is 'grid'
        grid_spacing (Optional[float]): Grid spacing if type is 'grid'
    """
    txrx_type: str
    is_transmitter: bool
    is_receiver: bool
    pos: List[float] | np.ndarray
    txrx_name: str
    txrx_id: Optional[int] = None
    grid_side: Optional[List[float]] = None
    grid_spacing: Optional[float] = None
    conform_to_terrain: Optional[bool] = False
    txrx_pos: np.ndarray = field(init=False)
    
    def __post_init__(self):
        # Convert pos to numpy array and ensure correct shape
        self.txrx_pos = np.asarray(self.pos)
        if self.txrx_pos.ndim == 1:
            # Single point case - ensure shape (3,)
            self.txrx_pos = self.txrx_pos.reshape(3)
        elif self.txrx_pos.ndim == 2:
            # Multiple points case - ensure shape (N, 3)
            if self.txrx_pos.shape[1] != 3:
                raise ValueError("Position array must have shape (N, 3) for multiple points")
        else:
            raise ValueError("Position must be a 1D or 2D array")
            
        self.grid_side = np.asarray(self.grid_side) if self.grid_side is not None else None

class TxRxEditor:
    """
    Editor class for managing transmitters and receivers in Wireless InSite simulations.
    
    This class provides functionality to add, remove, and modify transmitter and receiver
    configurations, supporting both single points and arrays of points.
    """
    def __init__(self, infile_path: Optional[str] = None, template_path: Optional[str] = None):
        self.infile_path = infile_path
        self.txrx: List[TxRx] = []
        self.txrx_file = None
        self.txpower = 0  # only supports tx_power = 0
        self.template_path = template_path
        if template_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.template_path = os.path.join(script_dir, "..", "resources", "txrx")
        
    def add_txrx(self, 
                txrx_type: str,
                is_transmitter: bool,
                is_receiver: bool,
                pos: List[float] | np.ndarray,
                name: str,
                id: Optional[int] = None,
                grid_side: Optional[List[float]] = None,
                grid_spacing: Optional[float] = None,
                conform_to_terrain: Optional[bool] = None) -> None:
        """
        Add a new transmitter or receiver.
        
        Args:
            txrx_type: Type of transmitter/receiver ('points' or 'grid')
            is_transmitter: Whether this is a transmitter
            is_receiver: Whether this is a receiver
            pos: Position(s) as [x, y, z] for single point or array of shape (N, 3) for multiple points
            name: Name of the transmitter/receiver
            id: Optional unique identifier (auto-generated if None)
            grid_side: Optional grid dimensions [width, height] if type is 'grid'
            grid_spacing: Optional grid spacing if type is 'grid'
            conform_to_terrain: Optional flag to conform to terrain if type is 'grid'
        """
        if not id:
            try:
                id = self.txrx[-1].txrx_id + 1
            except (IndexError, AttributeError):
                id = 1
        new_txrx = TxRx(txrx_type, is_transmitter, is_receiver, pos, name, txrx_id=id, 
                        grid_side=grid_side, grid_spacing=grid_spacing, 
                        conform_to_terrain=conform_to_terrain)
        self.txrx.append(new_txrx)

    def save(self, outfile_path: str) -> None:
        """
        Save the transmitter/receiver configuration to a file.
        
        Args:
            outfile_path: Path to save the configuration file
        """
        # clean the output file before writing
        open(outfile_path, "w+").close()
        for x in self.txrx:
            with open(self.template_path+"/"+x.txrx_type+".txt", "r") as f:
                template = f.readlines()
            for i, line in enumerate(template):
                if ("begin_<points>" in line) or ("begin_<grid>" in line):
                    template[i] = "begin_<%s> %s\n" % (x.txrx_type, x.txrx_name)
                    template[i+1] = "project_id %d\n" % x.txrx_id

                if "nVertices" in line:
                    # Handle both single point and multiple points cases
                    if x.txrx_pos.ndim == 1:
                        # Single point case
                        template[i+1] = COORD_FORMAT % tuple(x.txrx_pos)
                    else:
                        # Multiple points case - write each point on a new line
                        points_str = ""
                        for point in x.txrx_pos:
                            points_str += COORD_FORMAT % tuple(point)
                        template[i+1] = points_str
                
                if "is_transmitter" in line:
                    tmp = "yes" if x.is_transmitter else "no"
                    template[i] = "is_transmitter %s\n" % tmp

                if "is_receiver" in line:
                    tmp = "yes" if x.is_receiver else "no"
                    template[i] = "is_receiver %s\n" % tmp

                if "side1" in line and x.grid_side is not None:
                    template[i] = "side1 %.5f\n" % np.float32(x.grid_side[0])
                    template[i+1] = "side2 %.5f\n" % np.float32(x.grid_side[1])
                    template[i+2] = "spacing %.5f\n" % np.float32(x.grid_spacing)
                if line.split(" ")[0] == "power":
                    template[i] = "power %.5f\n" % self.txpower
            with open(outfile_path, "a") as out:
                out.writelines(template)


if __name__ == "__main__":
    outfile_path = "test/gwc_test.txrx"
    editor = TxRxEditor()
    # Example of single point transmitter
    editor.add_txrx("points", True, True, [0, 0, 6], "BS")
    # Example of multiple point receivers
    rx_points = np.array([[0, 0, 2], [5, 5, 2], [10, 10, 2]])  # 3 receiver points
    editor.add_txrx("points", False, True, rx_points, "UE_points")
    # Example of grid receiver
    editor.add_txrx("grid", False, True, [-187, -149, 2], "UE_grid", grid_side=[379, 299], grid_spacing=5)
    editor.save(outfile_path)
    print("done")