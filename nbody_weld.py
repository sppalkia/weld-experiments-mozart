"""
NBody in N^2 complexity

Note that we are using only Newtonian forces and do not consider relativity
Neither do we consider collisions between stars
Thus some of our stars will accelerate to speeds beyond c
This is done to keep the simulation simple enough for teaching purposes

All the work is done in the calc_force, move and random_galaxy functions.
To vectorize the code these are the functions to transform.

https://benchpress.readthedocs.io/autodoc_benchmarks/nbody_nice.html
"""

import argparse
import sys
import time

import numpy as np

import weldnumpy as wn
# import weldnumpy as np
from weldnumpy import weldarray

def fill_diagonal(a, val):
    """ Set diagonal of 2D matrix a to val in-place. """
    d, _ = a.shape
    a.shape = d * d
    a[::d] = val
    a.shape = (d, d)

def diagonal(ary, offset=0):
    """
    """
    if ary.ndim != 2:
        raise Exception("diagonal only supports 2 dimensions\n")
    if offset < 0:
        offset = -offset
        if (ary.shape[0]-offset) > ary.shape[1]:
            ary_diag = ary[offset, :]
        else:
            ary_diag = ary[offset:, 0]
    else:
        if ary.shape[1] - offset > ary.shape[0]:
            ary_diag = ary[:, offset]
        else:
            ary_diag = ary[0, offset:]

    ary_diag.strides = (ary.strides[0]+ary.strides[1],)

    if isinstance(ary_diag, weldarray):
        ary_diag._weldarray_view.strides = ary_diag.strides

    return ary_diag

def random_galaxy(N):
    """ Generate a galaxy of random bodies """
    m =  np.array((np.arange(0.0, 1.0, step=1.0 / N) + np.float64(10)) * np.float64(m_sol/10))
    x =  np.array((np.arange(0.0, 1.0, step=1.0 / N) - np.float64(0.5)) * np.float64(r_ly/100))
    y =  np.array((np.arange(0.0, 1.0, step=1.0 / N) - np.float64(0.5)) * np.float64(r_ly/100))
    z =  np.array((np.arange(0.0, 1.0, step=1.0 / N) - np.float64(0.5)) * np.float64(r_ly/100))
    vx = np.zeros(N, dtype=np.float64)
    vy = np.zeros(N, dtype=np.float64)
    vz = np.zeros(N, dtype=np.float64)

    assert len(m) == N
    return weldarray(m), weldarray(x), weldarray(y), weldarray(z), weldarray(vx), weldarray(vy), weldarray(vz)

def move(m, x, y, z, vx, vy, vz, dt):
    """ Move the bodies.

    first find forces and change velocity and then move positions.
    """

    start = time.time()

    dx = x - x[:,None]
    dy = np.subtract(y, y[:,None])
    dz = np.subtract(z, z[:,None])
    pm = np.multiply(m, m[:,None])

    end = time.time()
    print("Step 0:", end - start)

    start = end

    r = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    tmp = G * pm / r ** 2
    Fx = tmp * (dx / r)
    Fy = tmp * (dy / r)
    Fz = tmp * (dz / r)

    end = time.time()
    print("Step 1:", end - start)
    start = end

    diagonal(Fx)[:] = 0.0
    diagonal(Fy)[:] = 0.0
    diagonal(Fz)[:] = 0.0
    Fx = Fx.evaluate()
    Fy = Fy.evaluate()
    Fz = Fz.evaluate()
    end = time.time()
    print("Step 2:", end - start)
    start = end

    mdt = m / dt

    # Update state.
    vx += np.add.reduce(Fx, axis=1) / mdt
    vy += np.add.reduce(Fy, axis=1) / mdt
    vz += np.add.reduce(Fz, axis=1) / mdt
    x += vx * dt
    y += vy * dt
    z += vz * dt

    end = time.time()
    print("Step 3:", end - start)
    start = end
    return Fx, Fy, Fz

def simulate(m, x, y, z, vx, vy, vz, timesteps):
    start = time.time()
    for i in range(timesteps):
        ret = move(m, x, y, z, vx, vy, vz, dt)
        print(x, y, z)
    end = time.time()
    print("Simulation time:", end - start)

####################################################################3
#                            ENTRY POINT
####################################################################3

parser = argparse.ArgumentParser(
    description="N-Body benchmark."
)
parser.add_argument('-s', "--size", type=int, default=10, help="Size of each array")
parser.add_argument('-i', "--iterations", type=int, default=1, help="Iterations of simulation")
parser.add_argument('-p', "--piece_size", type=int, default=16384, help="Size of each piece.")
parser.add_argument('-t', "--threads", type=int, default=1, help="Number of threads.")
parser.add_argument('-v', "--verbosity", type=str, default="none",\
        help="Log level (debug|info|warning|error|critical|none)")
args = parser.parse_args()

size = (1 << args.size)
iterations = args.iterations 
piece_size = args.piece_size
threads = args.threads
loglevel = args.verbosity

assert threads >= 1

print("Size:", size)
print("Piece Size:", piece_size)
print("Threads:", threads)
print("Log Level", loglevel)

# Constants
G     = np.float64(6.67384e-11)     # m/(kg*s^2)
dt    = np.float64(60*60*24*365.25) # Years in seconds
r_ly  = np.float64(9.4607e15)       # Lightyear in m
m_sol = np.float64(1.9891e30)       # Solar mass in kg

np.seterr(divide='ignore', invalid='ignore')

sys.stdout.write("Generating data...")
sys.stdout.flush()
m, x, y, z, vx, vy, vz = random_galaxy(size)
print("done.")

simulate(m, x, y, z, vx, vy, vz, iterations)
R2 = x + y + z
R2.evaluate()
print(x)
