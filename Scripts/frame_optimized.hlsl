// Invert the normalized UV frame algebraically; determinant magnitudes cancel.
float3 N = normalize(NormalWS);
float uvDet = UVdx.x * UVdy.y - UVdx.y * UVdy.x;
float3 U = Pdx * UVdy.y - Pdy * UVdx.y;
float3 V = Pdy * UVdx.x - Pdx * UVdy.x;
// Cross products implicitly project onto the tangent plane.
float3 dualU = cross(V,N);
float3 dualV = cross(N,U);
float2 axisLength2 = float2(dot(dualV,dualV),dot(dualU,dualU));
float basisDet = dot(U,dualU);
// A single relative check handles collapsed UVs and collapsed surface axes.
float invBasis = basisDet*basisDet > 1e-10*axisLength2.x*axisLength2.y ? rcp(basisDet) : 0;
invBasis *= uvDet < 0 ? -1 : 1;
float2 xy = float2(dot(VectorWS,dualU),dot(VectorWS,dualV));
float3 result = float3(xy * sqrt(axisLength2) * invBasis, dot(VectorWS,N));
RETURN_RESULT
