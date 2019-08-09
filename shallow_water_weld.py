"""
A hacky manual Weld implementation of Shallow Water.
"""

from weldpython.compiled import compile, THREADS
from weldpython.bindings import *
from weldpython.encoders import *

import argparse
import ctypes
import sys
import time

import numpy as np

####################################################################
#                           WELD FUNCTIONS
####################################################################

weldSaxpy = """
|x: vec[f64], y: vec[f64], dt: f64|
  result(for(zip(x, y),
    appender[f64](len(x)),
    |b, i, e| merge(b, e.$0 + e.$1 * dt)))
"""
args = (NumpyArrayEncoder(), NumpyArrayEncoder(), float)
restype = WeldVec(WeldDouble())
decoder = NumpyArrayDecoder()
weldSaxpy = compile(weldSaxpy, args, restype, decoder)

weldDetaDt = """
|ddx: vec[f64], ddy: vec[f64], eta: vec[f64], dt: f64|
  result(for(zip(ddx, ddy, eta),
    appender[f64](len(ddy)),
    |b, i, e| merge(b, e.$2 + (-(e.$0) - e.$1)*dt)))
"""
args = (NumpyArrayEncoder(), NumpyArrayEncoder(), NumpyArrayEncoder(), float)
restype = WeldVec(WeldDouble())
decoder = NumpyArrayDecoder()
weldDetaDt = compile(weldDetaDt, args, restype, decoder)

weldGridSpaceDiv = """
|roll1: vec[f64], roll2: vec[f64], gs: f64|
    result(for(zip(roll1, roll2),
            appender[f64](len(roll1)),
            |b, i, e| merge(b, (e.$0 - e.$1) / gs)))
"""
args = (NumpyArrayEncoder(), NumpyArrayEncoder(), float)
restype = WeldVec(WeldDouble())
decoder = NumpyArrayDecoder()
weldGridSpaceDiv = compile(weldGridSpaceDiv, args, restype, decoder)

weldDudtDvdt = """
|minus_g: f64, H: f64, inpb: f64, eta_dx: vec[f64], eta_dy: vec[f64], u: vec[f64], v: vec[f64], eta: vec[f64]|

  let results = 
  for(zip(eta_dx, eta_dy, u, v, eta),
    {appender[f64](len(v)), appender[f64](len(v)), appender[f64](len(v)), appender[f64](len(v))},
    |b, i, e|
    {
      merge(b.$0, minus_g * e.$0 - inpb * e.$2),
      merge(b.$1, minus_g * e.$1 - inpb * e.$3),
      merge(b.$2, e.$2 * (H + e.$4)),
      merge(b.$3, e.$3 * (H + e.$4))
    }
  );
  {result(results.$0), result(results.$1), result(results.$2), result(results.$3)}
"""
args = (float, float, float, NumpyArrayEncoder(), NumpyArrayEncoder(),\
        NumpyArrayEncoder(), NumpyArrayEncoder(), NumpyArrayEncoder())
restype = WeldStruct([WeldVec(WeldDouble()), WeldVec(WeldDouble()), WeldVec(WeldDouble()), WeldVec(WeldDouble())])
decoder = StructDecoder(\
        [WeldVec(WeldDouble()), WeldVec(WeldDouble()), WeldVec(WeldDouble()), WeldVec(WeldDouble())],
        [NumpyArrayDecoder(), NumpyArrayDecoder(), NumpyArrayDecoder(), NumpyArrayDecoder()])
weldDudtDvdt = compile(weldDudtDvdt, args, restype, decoder)

####################################################################
#                       MAIN BENCHMARK
####################################################################

from collections import defaultdict
taskTimes = defaultdict(lambda: 0)

def spatial_derivative(A, axis):

    start = time.time()
    roll1 = np.roll(A, -1, axis)
    roll2 = np.roll(A,  1, axis)
    end = time.time()
    taskTimes["roll"] += (end - start)

    # (roll1 - roll2) / (grid_spacing * 2.0)
    start = time.time()
    res = weldGridSpaceDiv(roll1.reshape(-1), roll2.reshape(-1), grid_spacing * 2.0)
    end = time.time()
    taskTimes["gridSpace"] += (end - start)
    return res

def d_dx(A):
    A = A.reshape((n,n))
    return spatial_derivative(A, 1)

def d_dy(A):
    A = A.reshape((n,n))
    return spatial_derivative(A, 0)

def evolveEuler(eta, u, v):

    elapsed = 0
    yield eta, u, v, elapsed

    while True:
        eta_dx = d_dx(eta)
        eta_dy = d_dy(eta)

        start = time.time()
        du_dt, dv_dt, ueta, veta = weldDudtDvdt(-g, H, b, eta_dx, eta_dy, u, v, eta)
        end = time.time()
        taskTimes["dudtdvdt"] += (end - start)

        ddx_ueta = d_dx(ueta)
        ddy_veta = d_dy(veta)

        start = time.time()
        eta = weldDetaDt(ddx_ueta, ddy_veta, eta, dt)
        end = time.time()
        taskTimes["detaDt"] += (end - start)

        start = time.time()
        u = weldSaxpy(u, du_dt, dt)
        v = weldSaxpy(v, dv_dt, dt)
        end = time.time()
        taskTimes["saxpy"] += (end - start)

        elapsed += dt

        yield eta, u, v, elapsed


def simulate(eta, u, v, iterations, threads):

    trajectory = evolveEuler(eta, u, v)
    start = time.time()
    # Emit initial conditions.
    eta, u, v, elapsed = next(trajectory)
    for i in range(iterations):
        istart = time.time()
        eta, u, v, elapsed = next(trajectory)
        iend = time.time()
        print(eta[0])
        print("Iteration", i, ":", iend-istart)

    end = time.time()
    print("Total time:", end - start)
    print("Final State:")
    for key, value in taskTimes.iteritems():
        print key, ":", value
    print(eta[0])


####################################################################
#                            ENTRY POINT
####################################################################

parser = argparse.ArgumentParser(
    description="Shallow Water benchmark with Weld."
)
parser.add_argument('-s', "--size", type=int, default=10, help="Size of each array")
parser.add_argument('-i', "--iterations", type=int, default=1, help="Iterations of simulation")
parser.add_argument('-t', "--threads", type=int, default=1, help="Number of threads.")
args = parser.parse_args()

size = (1 << args.size)
iterations = args.iterations 
threads = args.threads

assert threads >= 1

THREADS[0] = str(threads)

print("Size:", size)
print("Threads:", threads)

sys.stdout.write("Generating data...")
sys.stdout.flush()

# Initial Conditions
n = size

# velocity in x direction
u = np.zeros((n, n))
# velocity in y direction
v = np.zeros((n, n))
# pressure deviation (like height)
eta = np.ones((n, n))

# Set eta.
for i in range(n):
    eta[i] *= 0.1 * i

# Constants
G     = 6.67384e-11     # m/(kg*s^2)
dt    = 60*60*24*365.25 # Years in seconds
r_ly  = 9.4607e15       # Lightyear in m
m_sol = 1.9891e30       # Solar mass in kg
b     = 0.0
H     = 0.0

box_size = 1.
grid_spacing =  1.0 * box_size / n
g = 1.
dt = grid_spacing / 100.
print("done.")

simulate(eta, u, v, iterations, threads)
