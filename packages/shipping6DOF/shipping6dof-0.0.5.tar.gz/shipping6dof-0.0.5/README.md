# shipping6DOF
shipping6DOF is a simple package that calculates translations and rotations from planes, by means
of classical linear algebra. 

## Features
 - Define planes by an origin and unitary normal axis vector.
 - Define planes from 2, 3, and n co-planar (within limits) coordinate points
 - Calculate rotation matrices from quaternions, axis and rotation angle, and viceversa
 - Calculate displacements and rotations (Euler angles) between 2 planes by means of simple algebraic operations
 - Change of basis and rotation matrices available
 - The API follows a DDD approach ("Domain-Driven Design"), this means that linear algebra operations are directly
   implemented through overloaded abstractions and classes. No need to call numpy directly.
 - (FUTURE) calculation of 6DOF motions and hydrostatic forces on ships.

## Usage

See Jupyter notebooks attached.
 
