"""
This module defines various mesh part instances with the base class of MeshPart.
It includes the StructuredRectangular3D class, which represents a 3D 
structured rectangular mesh part.It provides functionality to 
initialize, generate, and validate a structured rectangular mesh grid using 
the PyVista library.

Classes:
    StructuredRectangular3D: A class representing a 3D structured rectangular mesh part.
    CustomRectangularGrid3D: A class representing a 3D custom rectangular grid mesh part.
    GeometricStructuredRectangular3D: A class representing a 3D geometric structured rectangular mesh part.
    CustomMesh: A class representing a custom mesh part that can load from a file or accept an existing PyVista mesh.

Functions:
    generate_mesh: Generates a structured rectangular mesh.
    get_parameters: Returns a list of parameters for the mesh part type.
    validate_parameters: Validates the input parameters for the mesh part.
    is_elemnt_compatible: Returns True if the element is compatible with the mesh part type.
    update_parameters: Updates the mesh part parameters.
    get_Notes: Returns notes for the mesh part type.


Usage:
    This module is intended to be used as part of the MeshMaker lib for 
    defining and manipulating 3D structured rectangular mesh parts.
"""
from typing import Dict, List, Tuple, Union
from abc import ABC, abstractmethod
import numpy as np
import pyvista as pv
import os
from femora.components.Mesh.meshPartBase import MeshPart, MeshPartRegistry
from femora.components.Element.elementBase import Element
from femora.components.Region.regionBase import RegionBase



class StructuredRectangular3D(MeshPart):
    """
    Structured Rectangular 3D Mesh Part
    """
    _compatible_elements = ["stdBrick", "bbarBrick", "SSPbrick", "PML3D"]
    def __init__(self, user_name: str, element: Element, region: RegionBase=None,**kwargs):
        """
        Initialize a 3D Structured Rectangular Mesh Part
        
        Args:
            user_name (str): Unique user name for the mesh part
            element (Optional[Element]): Associated element
        """
        super().__init__(
            category='volume mesh',
            mesh_type='Rectangular Grid',
            user_name=user_name,
            element=element,
            region=region
        )
        kwargs = self.validate_parameters(**kwargs)
        self.params = kwargs if kwargs else {}
        self.generate_mesh()


    def generate_mesh(self) -> pv.UnstructuredGrid:
        """
        Generate a structured rectangular mesh
        
        Returns:
            pv.UnstructuredGrid: Generated mesh
        """
        
        # Extract parameters
        x_min = self.params.get('X Min', 0)
        x_max = self.params.get('X Max', 1)
        y_min = self.params.get('Y Min', 0)
        y_max = self.params.get('Y Max', 1)
        z_min = self.params.get('Z Min', 0)
        z_max = self.params.get('Z Max', 1)
        nx = self.params.get('Nx Cells', 10)
        ny = self.params.get('Ny Cells', 10)
        nz = self.params.get('Nz Cells', 10)
        X = np.linspace(x_min, x_max, nx + 1)
        Y = np.linspace(y_min, y_max, ny + 1)
        Z = np.linspace(z_min, z_max, nz + 1)
        X, Y, Z = np.meshgrid(X, Y, Z, indexing='ij')
        self.mesh = pv.StructuredGrid(X, Y, Z).cast_to_unstructured_grid()
        return self.mesh


    @classmethod
    def get_parameters(cls) -> List[Tuple[str, str]]:
        """
        Get the list of parameters for this mesh part type.
        
        Returns:
            List[str]: List of parameter names
        """
        return [
            ("X Min", "Minimum X coordinate (float)"),
            ("X Max", "Maximum X coordinate (float)"),
            ("Y Min", "Minimum Y coordinate (float)"),
            ("Y Max", "Maximum Y coordinate (float)"),
            ("Z Min", "Minimum Z coordinate (float)"),
            ("Z Max", "Maximum Z coordinate (float)"),
            ("Nx Cells", "Number of cells in X direction (integer)"),
            ("Ny Cells", "Number of cells in Y direction (integer)"),
            ("Nz Cells", "Number of cells in Z direction (integer)")
        ]
    

    @classmethod
    def validate_parameters(cls, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the mesh part input parameters are valid.
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        valid_params = {}
        for param_name in ['X Min', 'X Max', 'Y Min', 'Y Max', 'Z Min', 'Z Max']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = float(kwargs[param_name])
                except ValueError:
                    raise ValueError(f"{param_name} must be a float number")
            else:
                raise ValueError(f"{param_name} parameter is required")
        
        for param_name in ['Nx Cells', 'Ny Cells', 'Nz Cells']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = int(kwargs[param_name])
                except ValueError:
                    raise ValueError(f"{param_name} must be an integer number")
            else:
                raise ValueError(f"{param_name} parameter is required")
            
        if valid_params['X Min'] >= valid_params['X Max']:
            raise ValueError("X Min must be less than X Max")
        if valid_params['Y Min'] >= valid_params['Y Max']:
            raise ValueError("Y Min must be less than Y Max")
        if valid_params['Z Min'] >= valid_params['Z Max']:
            raise ValueError("Z Min must be less than Z Max")
        
        if valid_params['Nx Cells'] <= 0:
            raise ValueError("Nx Cells must be greater than 0")
        if valid_params['Ny Cells'] <= 0:
            raise ValueError("Ny Cells must be greater than 0")
        if valid_params['Nz Cells'] <= 0:
            raise ValueError("Nz Cells must be greater than 0")
        
        return valid_params
    
    @classmethod
    def is_elemnt_compatible(cls, element:str) -> bool:
        """
        Get the list of compatible element types
        Returns:
            List[str]: List of compatible element types
        """
        return element in cls._compatible_elements
    


    def update_parameters(self, **kwargs) -> None:
        """
        Update mesh part parameters
        
        Args:
            **kwargs: Keyword arguments to update
        """
        validated_params = self.validate_parameters(**kwargs)
        self.params = validated_params


    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """
        Get notes for the mesh part type
        
        Returns:
            Dict[str, Union[str, list]]: Dictionary containing notes about the mesh part
        """
        return {
            "description": "Generates a structured 3D rectangular grid mesh with uniform spacing",
            "usage": [
                "Used for creating regular 3D meshes with equal spacing in each direction",
                "Suitable for simple geometries where uniform mesh density is desired",
                "Efficient for problems requiring regular grid structures"
            ],
            "limitations": [
                "Only creates rectangular/cuboid domains",
                "Cannot handle irregular geometries",
                "Uniform spacing in each direction"
            ],
            "tips": [
                "Ensure the number of cells (Nx, Ny, Nz) is appropriate for your analysis",
                "Consider mesh density requirements for accuracy",
                "Check that the domain bounds (Min/Max) cover your area of interest"
            ]
        }

# Register the 3D Structured Rectangular mesh part type
MeshPartRegistry.register_mesh_part_type('Volume mesh', 'Uniform Rectangular Grid', StructuredRectangular3D)


class CustomRectangularGrid3D(MeshPart):
    """
    Custom Rectangular Grid 3D Mesh Part
    """
    _compatible_elements = ["stdBrick", "bbarBrick", "SSPbrick", "PML3D"]
    def __init__(self, user_name: str, element: Element, region: RegionBase=None,**kwargs):
        """
        Initialize a 3D Custom Rectangular Grid Mesh Part
        
        Args:
            user_name (str): Unique user name for the mesh part
            element (Optional[Element]): Associated element
            region (Optional[RegionBase]): Associated region
            **kwargs: Additional keyword arguments
                x_coords (List[float]): List of X coordinates
                y_coords (List[float]): List of Y coordinates
                z_coords (List[float]): List of Z coordinates
        """
        super().__init__(
            category='volume mesh',
            mesh_type='Custom Rectangular Grid',
            user_name=user_name,
            element=element,
            region=region
        )
        self.params = kwargs
        self.generate_mesh()

    def generate_mesh(self) -> pv.UnstructuredGrid:
        """
        Generate a custom rectangular grid mesh
        
        Returns:
            pv.UnstructuredGrid: Generated mesh
        """
        x_coords = self.params.get('x_coords', None).split(',')
        y_coords = self.params.get('y_coords', None).split(',')
        z_coords = self.params.get('z_coords', None).split(',')
        x = np.array(x_coords)
        y = np.array(y_coords)
        z = np.array(z_coords)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        self.mesh = pv.StructuredGrid(X, Y, Z).cast_to_unstructured_grid()
        del x, y, z, X, Y, Z
        return self.mesh
    
    @classmethod
    def get_parameters(cls) -> List[Tuple[str, str]]:
        """
        Get the list of parameters for this mesh part type.
        
        Returns:
            List[str]: List of parameter names
        """
        return [
            ("x_coords", "List of X coordinates (List[float] , comma separated, required)"),
            ("y_coords", "List of Y coordinates (List[float] , comma separated, required)"),
            ("z_coords", "List of Z coordinates (List[float] , comma separated, required)")
        ]
    
    @classmethod
    def validate_parameters(cls, **kwargs) -> Dict[str, Union[int, float, str, List[float]]]:
        """
        Check if the mesh part input parameters are valid.
        
        Returns:
            Dict[str, Union[int, float, str, List[float]]: Dictionary of parmaeters with valid values
        """
        valid_params = {}
        for param_name in ['x_coords', 'y_coords', 'z_coords']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = [float(x) for x in kwargs[param_name].split(',')]
                    # check if the values are in ascending order
                    if not all(valid_params[param_name][i] < valid_params[param_name][i+1] for i in range(len(valid_params[param_name])-1)):
                        raise ValueError(f"{param_name} must be in ascending order")
                    valid_params[param_name] = kwargs[param_name]
                except ValueError:
                    raise ValueError(f"{param_name} must be a list of float numbers")
            else:
                raise ValueError(f"{param_name} parameter is required")
        return valid_params

    @classmethod
    def is_elemnt_compatible(cls, element:str) -> bool:
        """
        Get the list of compatible element types
        Returns:
            List[str]: List of compatible element types
        """
        return element in ["stdBrick", "bbarBrick", "SSPbrick", "PML3D"]


    def update_parameters(self, **kwargs) -> None:
        """
        Update mesh part parameters
        
        Args:
            **kwargs: Keyword arguments to update
        """
        validated_params = self.validate_parameters(**kwargs)
        self.params = validated_params


    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """
        Get notes for the mesh part type
        
        Returns:
            Dict[str, Union[str, list]]: Dictionary containing notes about the mesh part
        """
        return {
            "description": "Generates a 3D rectangular grid mesh with custom spacing",
            "usage": [
                "Used for creating 3D meshes with variable spacing in each direction",
                "Suitable for problems requiring non-uniform mesh density",
                "Useful when specific grid point locations are needed"
            ],
            "limitations": [
                "Only creates rectangular/cuboid domains",
                "Cannot handle irregular geometries",
                "Requires manual specification of all grid points"
            ],
            "tips": [
                "Provide coordinates as comma-separated lists of float values",
                "Ensure coordinates are in ascending order",
                "Consider gradual transitions in spacing for better numerical results"
            ]
        }


# Register the 3D Structured Rectangular mesh part type
MeshPartRegistry.register_mesh_part_type('Volume mesh', 'Custom Rectangular Grid', CustomRectangularGrid3D)




class GeometricStructuredRectangular3D(MeshPart):
    """
    Geometric Structured Rectangular 3D Mesh Part
    """
    _compatible_elements = ["stdBrick", "bbarBrick", "SSPbrick", "PML3D"]
    def __init__(self, user_name: str, element: Element, region: RegionBase=None,**kwargs):
        """
        Initialize a 3D Geometric Structured Rectangular Mesh Part
        
        Args:
            user_name (str): Unique user name for the mesh part
            element (Optional[Element]): Associated element
            region (Optional[RegionBase]): Associated region
            **kwargs: Additional keyword arguments
                x_min (float): Minimum X coordinate
                x_max (float): Maximum X coordinate
                y_min (float): Minimum Y coordinate
                y_max (float): Maximum Y coordinate
                z_min (float): Minimum Z coordinate
                z_max (float): Maximum Z coordinate
                nx (int): Number of cells in X direction
                ny (int): Number of cells in Y direction
                nz (int): Number of cells in Z direction
                x_ratio (float): Ratio of cell increment in X direction
                y_ratio (float): Ratio of cell increment in Y direction
                z_ratio (float): Ratio of cell increment in Z direction
        """
        super().__init__(
            category='volume mesh',
            mesh_type='Geometric Rectangular Grid',
            user_name=user_name,
            element=element,
            region=region
        )
        self.params = kwargs
        self.generate_mesh()

    @staticmethod
    def custom_linspace(start, end, num_elements, ratio=1):
        """
        Generate a sequence of numbers between start and end with specified spacing ratio.

        Parameters:
        - start (float): The starting value of the sequence.
        - end (float): The ending value of the sequence.
        - num_elements (int): The number of elements in the sequence.
        - ratio (float, optional): The ratio of increment between consecutive intervals. Defaults to 1 (linear spacing).

        Returns:
        - numpy.ndarray: The generated sequence.
        """
        if num_elements <= 0:
            raise ValueError("Number of elements must be greater than 0")

        if num_elements == 1:
            return np.array([start, end])
        
        num_intervals = num_elements
        total = end - start
        
        if ratio == 1:
            return np.linspace(start, end, num_elements+1)
        else:            
            # Determine the base increment
            x = total * (1 - ratio) / (1 - ratio**num_intervals)
            # Generate the increments using the ratio
            increments = x * (ratio ** np.arange(num_intervals))
            # Compute the cumulative sum and add the start value
            elements = start + np.cumsum(np.hstack([0, increments]))
            return elements

    def generate_mesh(self) -> pv.UnstructuredGrid:
        """
        Generate a geometric structured rectangular mesh
        
        Returns:
            pv.UnstructuredGrid: Generated mesh
        """
        x_min = self.params.get('x_min', 0)
        x_max = self.params.get('x_max', 1)
        y_min = self.params.get('y_min', 0)
        y_max = self.params.get('y_max', 1)
        z_min = self.params.get('z_min', 0)
        z_max = self.params.get('z_max', 1)
        nx = self.params.get('nx', 10)
        ny = self.params.get('ny', 10)
        nz = self.params.get('nz', 10)
        x_ratio = self.params.get('x_ratio', 1)
        y_ratio = self.params.get('y_ratio', 1)
        z_ratio = self.params.get('z_ratio', 1)
        x = self.custom_linspace(x_min, x_max, nx, x_ratio)
        y = self.custom_linspace(y_min, y_max, ny, y_ratio)
        z = self.custom_linspace(z_min, z_max, nz, z_ratio)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        self.mesh = pv.StructuredGrid(X, Y, Z).cast_to_unstructured_grid()

        return self.mesh

    @classmethod
    def get_parameters(cls) -> List[Tuple[str, str]]:
        """
        Get the list of parameters for this mesh part type.
        
        Returns:
            List[str]: List of parameter names
        """
        return [
            ("x_min", "Minimum X coordinate (float)"),
            ("x_max", "Maximum X coordinate (float)"),
            ("y_min", "Minimum Y coordinate (float)"),
            ("y_max", "Maximum Y coordinate (float)"),
            ("z_min", "Minimum Z coordinate (float)"),
            ("z_max", "Maximum Z coordinate (float)"),
            ("nx", "Number of cells in X direction (integer)"),
            ("ny", "Number of cells in Y direction (integer)"),
            ("nz", "Number of cells in Z direction (integer)"),
            ("x_ratio", "Ratio of cell increment in X direction (float)"),
            ("y_ratio", "Ratio of cell increment in Y direction (float)"),
            ("z_ratio", "Ratio of cell increment in Z direction (float)")
        ]
    
    @classmethod
    def validate_parameters(cls, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the mesh part input parameters are valid.
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        valid_params = {}
        for param_name in ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = float(kwargs[param_name])
                except ValueError:
                    raise ValueError(f"{param_name} must be a float number")
            else:
                raise ValueError(f"{param_name} parameter is required")
        
        for param_name in ['nx', 'ny', 'nz']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = int(kwargs[param_name])
                except ValueError:
                    raise ValueError(f"{param_name} must be an integer number")
            else:
                raise ValueError(f"{param_name} parameter is required")
            
        for param_name in ['x_ratio', 'y_ratio', 'z_ratio']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = float(kwargs[param_name])
                    # check if the value is greater than 0
                    if valid_params[param_name] <= 0:
                        raise ValueError(f"{param_name} must be greater than 0")
                except ValueError:
                    raise ValueError(f"{param_name} must be a float number")
            else:
                valid_params[param_name] = 1
        
        if valid_params['x_min'] >= valid_params['x_max']:
            raise ValueError("x_min must be less than x_max")
        if valid_params['y_min'] >= valid_params['y_max']:
            raise ValueError("y_min must be less than y_max")
        if valid_params['z_min'] >= valid_params['z_max']:
            raise ValueError("z_min must be less than z_max")
        
        if valid_params['nx'] <= 0:
            raise ValueError("nx must be greater than 0")
        if valid_params['ny'] <= 0:
            raise ValueError("ny must be greater than 0")
        if valid_params['nz'] <= 0:
            raise ValueError("nz must be greater than 0")
        
        return valid_params
    
    @classmethod
    def is_elemnt_compatible(cls, element:str) -> bool:
        """
        Get the list of compatible element types
        Returns:
            List[str]: List of compatible element types
        """
        return element in ["stdBrick", "bbarBrick", "SSPbrick", "PML3D"]
    
    def update_parameters(self, **kwargs) -> None:
        """
        Update mesh part parameters
        
        Args:
            **kwargs: Keyword arguments to update
        """
        validated_params = self.validate_parameters(**kwargs)
        self.params = validated_params

    
    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """
        Get notes for the mesh part type
        
        Returns:
            Dict[str, Union[str, list]]: Dictionary containing notes about the mesh part
        """
        return {
            "description": "Generates a structured 3D rectangular grid mesh with geometric spacing",
            "usage": [
                "Used for creating 3D meshes with variable spacing in each direction",
                "Suitable for problems requiring non-uniform mesh density",
                "Useful when specific grid point locations are needed"
            ],
            "limitations": [
                "Only creates rectangular/cuboid domains",
                "Cannot handle irregular geometries",
                "Requires manual specification of all grid points"
            ],
            "tips": [
                "Provide coordinates as comma-separated lists of float values",
                "Ensure coordinates are in ascending order",
                "Consider gradual transitions in spacing for better numerical results"
            ]
        }
    
# Register the 3D Geometric Structured Rectangular mesh part type
MeshPartRegistry.register_mesh_part_type('Volume mesh', 'Geometric Rectangular Grid', GeometricStructuredRectangular3D)


class ExternalMesh(MeshPart):
    """
    Custom Mesh Part that can load from a file or accept an existing PyVista mesh
    """
    _compatible_elements = ["stdBrick", "bbarBrick", "SSPbrick", "PML3D"]
    
    def __init__(self, user_name: str, element: Element, region: RegionBase=None, **kwargs):
        """
        Initialize a Custom Mesh Part
        
        Args:
            user_name (str): Unique user name for the mesh part
            element (Element): Associated element
            region (RegionBase, optional): Associated region
            **kwargs: Additional keyword arguments
                mesh (pv.UnstructuredGrid): Existing PyVista mesh to use
                filepath (str): Path to mesh file to load
                scale (float): Scale factor for the mesh
                rotate_x (float): Rotation angle around X-axis in degrees
                rotate_y (float): Rotation angle around Y-axis in degrees
                rotate_z (float): Rotation angle around Z-axis in degrees
                translate_x (float): Translation along X-axis
                translate_y (float): Translation along Y-axis
                translate_z (float): Translation along Z-axis
                transform_args (Dict): Optional transformation arguments dictionary
                    containing any of the above transformation parameters
        """
        super().__init__(
            category='volume mesh',
            mesh_type='Custom Mesh',
            user_name=user_name,
            element=element,
            region=region
        )
        self.params = self.validate_parameters(**kwargs)
        self.generate_mesh()

    def generate_mesh(self) -> pv.UnstructuredGrid:
        """
        Generate a mesh by loading from file or using the provided mesh and apply transformations
        
        Returns:
            pv.UnstructuredGrid: Generated mesh
        """
        if 'mesh' in self.params:
            # Use the provided mesh
            self.mesh = self.params['mesh']
        elif 'filepath' in self.params:
            # Load mesh from file
            self.mesh = pv.read(self.params['filepath'])
        else:
            raise ValueError("Either 'mesh' or 'filepath' parameter is required")
            
        # Apply scale if specified
        if 'scale' in self.params:
            self.mesh.scale(self.params['scale'], inplace=True)
            
        # Apply rotations if specified (in X, Y, Z order)
        if 'rotate_x' in self.params:
            self.mesh.rotate_x(self.params['rotate_x'], inplace=True)
        if 'rotate_y' in self.params:
            self.mesh.rotate_y(self.params['rotate_y'], inplace=True)
        if 'rotate_z' in self.params:
            self.mesh.rotate_z(self.params['rotate_z'], inplace=True)
            
        # Apply translation if specified
        translate_x = self.params.get('translate_x', 0)
        translate_y = self.params.get('translate_y', 0)
        translate_z = self.params.get('translate_z', 0)
        
        # Only translate if at least one component is non-zero
        if translate_x != 0 or translate_y != 0 or translate_z != 0:
            self.mesh.translate([translate_x, translate_y, translate_z], inplace=True)
            
        # Ensure we have an unstructured grid
        if not isinstance(self.mesh, pv.UnstructuredGrid):
            try:
                self.mesh = self.mesh.cast_to_unstructured_grid()
            except Exception as e:
                raise ValueError(f"Failed to convert mesh to unstructured grid: {str(e)}")
            
        return self.mesh

    @classmethod
    def get_parameters(cls) -> List[Tuple[str, str]]:
        """
        Get the list of parameters for this mesh part type.
        
        Returns:
            List[Tuple[str, str]]: List of parameter names and descriptions
        """
        return [
            ("mesh", "Existing PyVista mesh object (pv.UnstructuredGrid or convertible)"),
            ("filepath", "Path to mesh file to load (str)"),
            ("scale", "Scale factor for the mesh (float)"),
            ("rotate_x", "Rotation angle around X-axis in degrees (float)"),
            ("rotate_y", "Rotation angle around Y-axis in degrees (float)"),
            ("rotate_z", "Rotation angle around Z-axis in degrees (float)"),
            ("translate_x", "Translation along X-axis (float)"),
            ("translate_y", "Translation along Y-axis (float)"),
            ("translate_z", "Translation along Z-axis (float)"),
        ]
    
    @classmethod
    def validate_parameters(cls, **kwargs) -> Dict[str, Union[int, float, str, pv.UnstructuredGrid, Dict]]:
        """
        Check if the mesh part input parameters are valid.
        
        Returns:
            Dict[str, Union[int, float, str, pv.UnstructuredGrid, Dict]]: Dictionary of parameters with valid values
        """
        valid_params = {}
        
        # Check if either mesh or filepath is provided
        if 'mesh' in kwargs:
            try:
                # Verify it's a PyVista mesh
                mesh = kwargs['mesh']
                if not isinstance(mesh, (pv.UnstructuredGrid, pv.PolyData, pv.StructuredGrid)):
                    raise ValueError("'mesh' parameter must be a PyVista mesh")
                valid_params['mesh'] = mesh
            except Exception as e:
                raise ValueError(f"Invalid mesh object: {str(e)}")
        elif 'filepath' in kwargs:
            filepath = kwargs['filepath']
            if not isinstance(filepath, str):
                raise ValueError("'filepath' parameter must be a string")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Mesh file not found: {filepath}")
            valid_params['filepath'] = filepath
        else:
            raise ValueError("Either 'mesh' or 'filepath' parameter is required")
        
        # Process transformation parameters
        transform_params = ['scale', 'rotate_x', 'rotate_y', 'rotate_z', 
                           'translate_x', 'translate_y', 'translate_z']
        
        # Handle transform_args dict if provided
        if 'transform_args' in kwargs and isinstance(kwargs['transform_args'], dict):
            # Extract parameters from transform_args
            for param in transform_params:
                if param in kwargs['transform_args']:
                    try:
                        valid_params[param] = float(kwargs['transform_args'][param])
                    except ValueError:
                        raise ValueError(f"Transform parameter '{param}' must be a number")
        
        # Direct parameters override those in transform_args
        for param in transform_params:
            if param in kwargs:
                try:
                    valid_params[param] = float(kwargs[param])
                except ValueError:
                    raise ValueError(f"Parameter '{param}' must be a number")
                    
        # Scale must be positive if provided
        if 'scale' in valid_params and valid_params['scale'] <= 0:
            raise ValueError("Scale factor must be greater than 0")
            
        return valid_params
    
    @classmethod
    def is_elemnt_compatible(cls, element:str) -> bool:
        """
        Check if an element type is compatible with this mesh part
        
        Args:
            element (str): Element type name to check
            
        Returns:
            bool: True if compatible, False otherwise
        """
        return element in cls._compatible_elements
    
    def update_parameters(self, **kwargs) -> None:
        """
        Update mesh part parameters
        
        Args:
            **kwargs: Keyword arguments to update
        """
        # Merge with existing parameters to maintain required params
        merged_params = {**self.params, **kwargs}
        validated_params = self.validate_parameters(**merged_params)
        self.params = validated_params
        self.generate_mesh()  # Regenerate the mesh with new parameters

    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """
        Get notes for the mesh part type
        
        Returns:
            Dict[str, Union[str, list]]: Dictionary containing notes about the mesh part
        """
        return {
            "description": "Handles custom meshes imported from files or existing PyVista meshes",
            "usage": [
                "Used for importing pre-generated meshes from external sources",
                "Suitable for complex geometries created in other software",
                "Useful when working with irregular or complex domain shapes",
                "Can transform meshes with scaling, rotation, and translation operations",
                "Right now it only supports one kind of element type, but it can be extended to support more",
                "The compatibility of the element type is not checked, so it is the user's responsibility to check that the element type is compatible with the mesh part type"
            ],
            "limitations": [
                "Quality and compatibility of imported meshes depends on the source",
                "Some mesh types may require conversion to unstructured grid",
                "Not all mesh formats preserve all required metadata"
            ],
            "tips": [
                "Ensure imported meshes have appropriate element types for analysis",
                "Check mesh quality after import (aspect ratio, skewness, etc.)",
                "Parameters can be provided directly or in the transform_args dict",
                "Transformations are applied in this order: scale → rotate → translate",
                "Common file formats include .vtk, .vtu, .stl, .obj, and .ply"
            ]
        }

# Register the Custom Mesh part type under the General mesh category
MeshPartRegistry.register_mesh_part_type('General mesh', 'External mesh', ExternalMesh)
