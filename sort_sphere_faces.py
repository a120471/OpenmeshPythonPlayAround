import sys
import numpy as np
import openmesh as om

def face_bary(mesh, face_handle):
  debug_average = np.zeros(3)
  for v in mesh.fv(face_handle):
    debug_average += mesh.point(v)
  return debug_average / 3

def run(sphere_mesh_filepath, ordered_face_ids_filepath,
  ordered_sphere_mesh_filepath):
  mesh = om.read_trimesh(sphere_mesh_filepath)
  face_num = mesh.n_faces()

  # find upmost vertex
  upmost_v = 0
  max_y = -float('inf')
  for v in mesh.vertices():
    p = mesh.point(v)
    if p[1] > max_y:
      upmost_v = v
      max_y = p[1]

  # find the start face
  start_f = next(mesh.vf(upmost_v))

  # find the start edge
  for he in mesh.fh(start_f):
    if mesh.from_vertex_handle(he) == upmost_v:
      curr_e = he # start_e

  # iterate over top half sphere faces
  ordered_face_ids = [start_f.idx()]
  visited_face_ids = {start_f.idx()}
  while len(ordered_face_ids) < face_num:
    next_e = mesh.cw_rotated_halfedge_handle(curr_e)
    next_f = mesh.face_handle(next_e)

    while next_f.idx() in visited_face_ids:
      next_e = mesh.next_halfedge_handle(
        mesh.opposite_halfedge_handle(
        mesh.next_halfedge_handle(curr_e)))
      next_f = mesh.face_handle(next_e)
      curr_e = next_e

    ordered_face_ids.append(next_f.idx())
    visited_face_ids.add(next_f.idx())
    curr_e = next_e

    if len(ordered_face_ids) == face_num // 2:
      # export ordered face id
      np.savetxt(ordered_face_ids_filepath, ordered_face_ids, fmt='%d')

  # remove all faces, add new faces sequentially
  v_handles_list = []
  for face_id in ordered_face_ids:
    f_handle = mesh.face_handle(face_id)
    v_handles_list.append([v for v in mesh.fv(f_handle)])
    mesh.delete_face(f_handle, False)
  mesh.garbage_collection()
  for v_handles in v_handles_list:
    mesh.add_face(v_handles)
  # export ordered sphere mesh
  om.write_mesh(ordered_sphere_mesh_filepath, mesh)

if __name__ == "__main__":
  if len(sys.argv) < 4:
    print('sort_sphere_faces sphere_file output_ordered_face_ids output_ordered_sphere_file')
    exit(-1)

  run(sys.argv[1], sys.argv[2], sys.argv[3])
