import json
import math
import os
import random

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def mul(a,b): return [x*b for x in a]
def sub(a,b): return [x-y for x,y in zip(a,b)]
def cross(a,b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(a): return mul(a,1/math.sqrt(dot(a,a)))

def old(vec,n,px,py,ux,uy):
    det = ux[0]*uy[1]-ux[1]*uy[0]
    if abs(det) <= 1e-5*max(math.sqrt(dot(ux,ux)*dot(uy,uy)),1e-30): return [0,0,1]
    n = norm(n)
    u = mul(sub(mul(px,uy[1]),mul(py,ux[1])),1/det)
    v = mul(sub(mul(py,ux[0]),mul(px,uy[0])),1/det)
    u,v = sub(u,mul(n,dot(u,n))),sub(v,mul(n,dot(v,n)))
    if min(dot(u,u),dot(v,v)) < 1e-20: return [0,0,1]
    u,v = norm(u),norm(v)
    det = dot(u,cross(v,n))
    if abs(det) < 1e-5: return [0,0,1]
    return [dot(vec,cross(v,n))/det,dot(vec,cross(n,u))/det,dot(vec,n)]

def optimized(vec,n,px,py,ux,uy):
    n = norm(n)
    uvdet = ux[0]*uy[1]-ux[1]*uy[0]
    u = sub(mul(px,uy[1]),mul(py,ux[1]))
    v = sub(mul(py,ux[0]),mul(px,uy[0]))
    du,dv = cross(v,n),cross(n,u)
    u2,v2 = dot(dv,dv),dot(du,du)
    det = dot(u,du)
    inv = 1/det if det*det > 1e-10*u2*v2 else 0
    inv *= -1 if uvdet < 0 else 1
    return [dot(vec,du)*math.sqrt(u2)*inv,dot(vec,dv)*math.sqrt(v2)*inv,dot(vec,n)]

random.seed(426)
largest = 0
cases = 0
for i in range(12000):
    # Random surface orientations, smooth normals, UV rotation/mirroring/shear,
    # screen footprints and vector directions (camera or light).
    n = norm([random.uniform(-1,1) for _ in range(3)])
    t = norm(cross(n, [0,0,1] if abs(n[2]) < .9 else [0,1,0]))
    b = cross(n,t)
    px = mul(t,10**random.uniform(-2,2))
    py = mul(b,10**random.uniform(-2,2))
    smooth = norm([n[j]+random.uniform(-.15,.15) for j in range(3)])
    angle = random.uniform(-math.pi,math.pi)
    shear = random.uniform(-.8,.8)
    sx,sy = random.uniform(.2,3),random.choice([-1,1])*random.uniform(.2,3)
    ca,sa = math.cos(angle),math.sin(angle)
    ux = [ca*sx,sa*sx]
    uy = [(-sa+shear*ca)*sy,(ca+shear*sa)*sy]
    vec = norm([random.uniform(-1,1) for _ in range(3)])
    a,z = old(vec,smooth,px,py,ux,uy),optimized(vec,smooth,px,py,ux,uy)
    err = max(abs(x-y)/max(1,abs(x)) for x,y in zip(a,z))
    assert err < 1e-8, (i,err,a,z)
    largest = max(largest,err)
    cases += 1
for ux,uy in [([0,0],[0,0]),([1,1],[2,2])]:
    result = optimized([.3,.4,.8],[0,0,1],[1,0,0],[0,1,0],ux,uy)
    assert all(math.isfinite(x) for x in result) and result[:2] == [0,0]
# Rotating the surface 90 degrees about its normal must rotate view XY.
a = optimized([.3,.4,.8],[0,0,1],[1,0,0],[0,1,0],[1,0],[0,1])
b = optimized([.3,.4,.8],[0,0,1],[0,1,0],[-1,0,0],[1,0],[0,1])
assert max(abs(x-y) for x,y in zip(b,[a[1],-a[0],a[2]])) < 1e-12
report = {'random_equivalence_cases': cases, 'max_relative_error': largest,
          'degenerate_uv': 'pass', 'object_rotation_90_degrees': 'pass',
          'scope': 'CPU double-precision algebra regression; not a scene render test'}
open(os.path.join(os.path.dirname(__file__),'math_validation.json'),'w').write(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
