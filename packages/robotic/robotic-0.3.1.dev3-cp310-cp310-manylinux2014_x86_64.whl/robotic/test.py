import point_cloud_utils as pcu

# v is a [n, 3] shaped NumPy array of vertices
# f is a [m, 3] shaped integer NumPy array of indices into v
# n is a [n, 3] shaped NumPy array of vertex normals
v, f, n = pcu.load_mesh_vfn("bunny.ply")

# Generate barycentric coordinates of random samples
num_samples = 1000
fid, bc = pcu.sample_mesh_random(v, f, num_samples)

# Interpolate the vertex positions and normals using the returned barycentric coordinates
# to get sample positions and normals
rand_positions = pcu.interpolate_barycentric_coords(f, fid, bc, v)
rand_normals = pcu.interpolate_barycentric_coords(f, fid, bc, n)