#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <math.h>
#include <cmath>
#include <string.h>
#include <random>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
// #include <tiffio.h>
#include <algorithm>

#include "projmorpho.hpp"
#include "tetrahedron.hpp"

#define PBSTR "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
#define PBWIDTH 60
#define NEN 4

void projmorpho::print_error(std::string msg, bool ex)
{
  std::cout << "[ERROR] " << msg << std::endl;
  if (ex)
  {
    std::cout << "[ERROR] exit program" << std::endl;
    exit(EXIT_FAILURE);
  }
}

/* **** */
/* MESH */
/* **** */

projmorpho::projmorpho(std::vector<double> thresholds, std::string name, double volume_ratio_cutoff)
{
  std::cout << "<projmorpho::projmoprho" << std::endl;

  // vector of double
  _thresholds = thresholds;
  std::cout << ".\t thresholds: " << std::endl;
  if (_thresholds.size() == 1)
  {
    std::cout << ".\t .\t phase 0: (-inf; " << _thresholds[0] << "]" << std::endl;
    std::cout << ".\t .\t phase 1: ]" << _thresholds[0] << "; +inf)" << std::endl;
  }
  else if (_thresholds.size() == 2)
  {
    std::cout << ".\t .\t phase 0: (-inf; " << _thresholds[0] << "]" << std::endl;
    std::cout << ".\t .\t phase 1: ]" << _thresholds[0] << "; " << _thresholds[1] << "]" << std::endl;
    std::cout << ".\t .\t phase 2: ]" << _thresholds[1] << "; +inf)" << std::endl;
  }
  else
  {
    std::string msg = "\t wrong number of threshold: " + std::to_string(_thresholds.size()) + " (should be 1 or 2)";
    print_error(msg, true);
  }

  _file_name = name;
  std::cout << ".\t name: " << name << std::endl;
  std::cout << ">" << std::endl;
  _volume_ratio_cutoff = volume_ratio_cutoff;
  std::cout << ".\t volume ratio cutoff: " << _volume_ratio_cutoff << std::endl;
  std::cout << ">" << std::endl;
};

/* **** */
/* MESH */
/* **** */

void projmorpho::set_mesh(std::vector<std::vector<double>> c_mesh, std::vector<unsigned> a_mesh)
{
  /*
    Set mesh coordinates and adjancy matrix
  */
  std::cout << "<projmorpho::set_mesh" << std::endl;
  // get coordinates
  _c_mesh = c_mesh;
  _n_nodes = _c_mesh.size();
  std::cout << ".\t number of nodes: " << _n_nodes << std::endl;
  // get connectivity
  _a_mesh = a_mesh;
  _n_elem = _a_mesh.size() / NEN;
  std::cout << ".\t number of tetrahedra: " << _a_mesh.size() << "/4 = " << _n_elem << std::endl;
  // compute midpoints
  for (unsigned int i_elmt = 0; i_elmt < _n_elem; i_elmt++)
  {
    // std::cout << ".\t compute midpoints for element " << i_elmt << std::endl;
    std::vector<unsigned int> a_elmt(4);
    a_elmt[0] = _a_mesh[4 * i_elmt + 0];
    a_elmt[1] = _a_mesh[4 * i_elmt + 1];
    a_elmt[2] = _a_mesh[4 * i_elmt + 2];
    a_elmt[3] = _a_mesh[4 * i_elmt + 3];

    // define edge nodes permutation as per tetrahedron.cpp convention
    // n1 = 0 n2 = 1
    // n1 = 0 n2 = 3
    // n1 = 0 n2 = 2
    // n1 = 1 n2 = 3
    // n1 = 1 n2 = 2
    // n1 = 3 n2 = 2
    // local correspondence array between edges and nodes
    std::vector<std::vector<unsigned>> a_tet(6);
    for (unsigned int k = 0; k < a_tet.size(); k++)
    {
      a_tet[k].resize(2);
    }
    a_tet[0][0] = 0;
    a_tet[0][1] = 1;
    a_tet[1][0] = 0;
    a_tet[1][1] = 3;
    a_tet[2][0] = 0;
    a_tet[2][1] = 2;
    a_tet[3][0] = 1;
    a_tet[3][1] = 3;
    a_tet[4][0] = 1;
    a_tet[4][1] = 2;
    a_tet[5][0] = 3;
    a_tet[5][1] = 2;

    for (unsigned int i_edge = 0; i_edge < 6; i_edge++)
    {
      unsigned int node_1 = a_elmt[a_tet[i_edge][0]] - 1;
      unsigned int node_2 = a_elmt[a_tet[i_edge][1]] - 1;
      std::vector<double> c_node_1 = _c_mesh[node_1];
      std::vector<double> c_node_2 = _c_mesh[node_2];
      std::vector<double> c_midpoint(3);
      // std::cout << ".\t .\t edge " << i_edge << ": " << node_1 << " -> " << node_2 << std::endl;
      // compute coordinates of the middle edge
      for (unsigned i = 0; i < 3; i++)
      {
        c_midpoint[i] = 0.5 * (_c_mesh[node_1][i] + _c_mesh[node_2][i]);
      }
      _c_mesh_midpoints.push_back(c_midpoint);
      // std::cout << ".\t .\t .\t x " << _c_mesh_midpoints[6 * i_elmt + i_edge][0] << " = " << c_midpoint[0] << std::endl;
      // std::cout << ".\t .\t .\t y " << _c_mesh_midpoints[6 * i_elmt + i_edge][1] << " = " << c_midpoint[1] << std::endl;
      // std::cout << ".\t .\t .\t z " << _c_mesh_midpoints[6 * i_elmt + i_edge][2] << " = " << c_midpoint[2] << std::endl;
    }
  }
  std::cout << ".\t number of midpoints: " << _c_mesh_midpoints.size() << std::endl;

  std::cout << ">" << std::endl;
};

void projmorpho::set_field(std::vector<std::vector<double>> v_mesh)
{
  /*
    Set mesh values based on known values.
    Mid points are set to be the average value between the two nodes (linear interpolation)
  */

  std::cout << "<projmorpho::set_mesh_values" << std::endl;
  if (!_n_nodes)
  {
    std::cout << ".\t it seems that the mesh is not set. Call projmorpho.set_mesh_vectors() first." << std::endl;
  }
  else
  {
    std::cout << ".\t number of phase: " << v_mesh.size() << std::endl;
    _v_mesh = v_mesh;

    // compute midpoints
    _v_mesh_midpoints.resize(v_mesh.size());
    for (unsigned int i_elmt = 0; i_elmt < _n_elem; i_elmt++)
    {
      // std::cout << ".\t compute midpoints for element " << i_elmt << std::endl;
      std::vector<unsigned int> a_elmt(4);
      a_elmt[0] = _a_mesh[4 * i_elmt + 0];
      a_elmt[1] = _a_mesh[4 * i_elmt + 1];
      a_elmt[2] = _a_mesh[4 * i_elmt + 2];
      a_elmt[3] = _a_mesh[4 * i_elmt + 3];

      // define edge nodes permutation as per tetrahedron.cpp convention
      // n1 = 0 n2 = 1
      // n1 = 0 n2 = 3
      // n1 = 0 n2 = 2
      // n1 = 1 n2 = 3
      // n1 = 1 n2 = 2
      // n1 = 3 n2 = 2
      // local correspondence array between edges and nodes
      std::vector<std::vector<unsigned>> a_tet(6);
      for (unsigned int k = 0; k < a_tet.size(); k++)
      {
        a_tet[k].resize(2);
      }
      a_tet[0][0] = 0;
      a_tet[0][1] = 1;
      a_tet[1][0] = 0;
      a_tet[1][1] = 3;
      a_tet[2][0] = 0;
      a_tet[2][1] = 2;
      a_tet[3][0] = 1;
      a_tet[3][1] = 3;
      a_tet[4][0] = 1;
      a_tet[4][1] = 2;
      a_tet[5][0] = 3;
      a_tet[5][1] = 2;

      for (unsigned int i_edge = 0; i_edge < 6; i_edge++)
      {
        unsigned int node_1 = a_elmt[a_tet[i_edge][0]] - 1;
        unsigned int node_2 = a_elmt[a_tet[i_edge][1]] - 1;

        // loop over the fields
        for (unsigned int p = 0; p < v_mesh.size(); p++)
        {
          double v_node_1 = _v_mesh[p][node_1];
          double v_node_2 = _v_mesh[p][node_2];
          _v_mesh_midpoints[p].push_back(0.5 * (v_node_1 + v_node_2));
          std::cout << ".\t .\t .\t phase " << p << " midpoint " << 6 * i_elmt + i_edge << " v1 " << v_node_1 << " v2 " << v_node_2 << " " << _v_mesh_midpoints[p][6 * i_elmt + i_edge] << std::endl;
        }
      }
    }
    for (unsigned int p = 0; p < v_mesh.size(); p++)
    {
      std::cout << ".\t .\t phase " << p << " number of midpoints values: " << _v_mesh_midpoints[p].size() << std::endl;
    }
  }
  std::cout << ">" << std::endl;
};

std::vector<std::vector<double>> projmorpho::get_mesh_coordinates()
{
  return _c_mesh;
};

std::vector<std::vector<double>> projmorpho::get_mesh_values()
{
  return _v_mesh;
};

std::vector<unsigned> projmorpho::get_mesh_connectivity()
{
  return _a_mesh;
};

std::vector<std::vector<double>> projmorpho::get_interface_coordinates()
{
  std::cout << _int_nodes.size() << "\n" << _int_nodes[0].size() << std::endl;
  return _int_nodes;
}

std::vector<std::vector<int>> projmorpho::get_interface_tri_connectivity()
{
  return  _int_a_tri;
}

std::vector<std::vector<int>> projmorpho::get_interface_qua_connectivity()
{
  return  _int_a_qua;
}

/* ******* */
/* OBJECTS */
/* ******* */

void projmorpho::set_objects(std::vector<std::vector<double>> objects)
{
  std::cout << "<projmorpho::set_objects" << std::endl;

  _objects = objects;
  std::cout << ".\t number of objects: " << _objects.size() << std::endl;
  for (unsigned int i_object = 0; i_object < _objects.size(); i_object++)
  {
    // get phase number
    unsigned int p = _objects[i_object].back();
    _phases_values.push_back(p);
  }
  std::sort(_phases_values.begin(), _phases_values.end());
  auto last = std::unique(_phases_values.begin(), _phases_values.end());
  _phases_values.erase(last, _phases_values.end());

  for (unsigned int p = 0; p < _phases_values.size(); p++)
  {
    std::cout << ".\t phase number " << p << ": " << _phases_values[p] << std::endl;
  }

  std::cout << ">" << std::endl;
}

void projmorpho::compute_field_from_objects_loop(const std::vector<std::vector<double>> c_mesh, std::vector<std::vector<double>> &v_mesh)
{
  /*
    Interpolates objects distance field at mesh nodes and midpoints.
    v_mesh is modified and can be _v_mesh or _v_mesh_midpoints
  */

  // resize v_mesh to the number of phases computed from set_objects
  v_mesh.resize(_phases_values.size());

  // resize v_mesh[p] to the number of nodes
  for (unsigned int p = 0; p < v_mesh.size(); p++)
  {
    v_mesh[p].resize(c_mesh.size());
  }

  // loop over the the nodes
  for (unsigned int i_node = 0; i_node < c_mesh.size(); i_node++)
  {

    // loop over phases
    for (unsigned int p = 0; p < v_mesh.size(); p++)
    {

      // to force initialisation of a field value
      bool first_object = true;

      // loop over the objects
      for (unsigned int i_object = 0; i_object < _objects.size(); i_object++)
      {
        std::vector<double> object = _objects[i_object];
        unsigned int phase = (unsigned int)object.back();

        // ignore if wrong phase
        if (phase != _phases_values[p])
        {
          continue;
        }

        // compute field if good phase
        std::vector<double> point(3);
        point[0] = (double)c_mesh[i_node][0];
        point[1] = (double)c_mesh[i_node][1];
        point[2] = (double)c_mesh[i_node][2];
        double field = _compute_distance_from_object(object, point, phase);

        // record field if biggest than for other objects (nearest object of the phase)
        // or if first object
        if (field > v_mesh[p][i_node] || first_object)
        {
          v_mesh[p][i_node] = field;
        }

        first_object = false;
      }
    }
  }
}

void projmorpho::compute_field_from_objects()
{
  std::cout << "<projmorpho::compute_field_from_objects" << std::endl;

  std::cout << ".\t computing mesh values... ";
  compute_field_from_objects_loop(_c_mesh, _v_mesh);
  std::cout << "done" << std::endl;
  std::cout << ".\t computing midpoints values... ";
  compute_field_from_objects_loop(_c_mesh_midpoints, _v_mesh_midpoints);
  std::cout << "done" << std::endl;

  std::cout << ">" << std::endl;
}

double projmorpho::_compute_distance_from_object(std::vector<double> object, std::vector<double> point, unsigned int phase)

{
  double field = -1.0e100;

  if (object.size() == 5)
  {
    // sphere: [r, x, y, z, p]
    double ray = object[0];
    double distance = sqrt(pow(object[1] - point[0], 2) +
                           pow(object[2] - point[1], 2) +
                           pow(object[3] - point[2], 2));
    field = (double)(phase) * (1.0 - distance / ray);
  }
  else if (object.size() == 7)
  {
    // ellipsoids
    std::cout << "ellipsoids" << std::endl;
  }
  else if (object.size() == 8)
  {
    // cylinder: [r, ox, oy, oz, nx, ny, nz, p]
    // compute distance between node and cylinder
    // d = | OM x n | / | n |
    double ox = object[1] - point[0];     // vector OM: x
    double oy = object[2] - point[1];     // vector OM: y
    double oz = object[3] - point[2];     // vector OM: z
    double nx = object[4];         // vector n: x
    double ny = object[5];         // vector n: y
    double nz = object[6];         // vector n: z
    double cx = oy * nz - oz * ny; // cross product: x
    double cy = oz * nx - ox * nz; // cross product: x
    double cz = ox * ny - oy * nx; // cross product: x
    double ray = object[0];        // disk ray
    double distance = sqrt(pow(cx, 2) + pow(cy, 2) + pow(cz, 2)) / sqrt(pow(nx, 2) + pow(ny, 2) + pow(nz, 2));
    field = (double)(phase) * (1.0 - distance / ray);
  }
  else
  {
    std::cout << "WARNING: unkown object of size " << object.size() << std::endl;
  }

  return field;
}

std::vector<double> projmorpho::_compute_normal_from_object(std::vector<double> object, std::vector<double> point)
{
  std::vector<double> interface = {0.0, 0.0, 0.0};

  if (object.size() == 5)
  {
    // sphere: [r, ox, oy, oz, p]
    double interface_norm = 0.0;
    for (unsigned int i = 0; i < 3; i++)
    {
      interface[i] = point[i] - object[i + 1];
      interface_norm += pow(interface[i], 2);
    }

    // normalize
    for (unsigned int i = 0; i < 3; i++)
    {
      interface[i] /= sqrt(interface_norm);
    }
  }
  else if (object.size() == 7)
  {
    // ellipsoids
    std::cout << "ellipsoids" << std::endl;
  }
  else if (object.size() == 8)
  {
    // cylinder: [r, ox, oy, oz, nx, ny, nz, p]
    // compute normal to the cylinder (HM)

    // STEP 1.1: compute OM
    // STEP 1.2: compute n and | n |
    std::vector<double> om(3);
    std::vector<double> n(3);
    double om_dot_n = 0.0;
    double norm_n = 0.0;
    for (unsigned int i = 0; i < 3; i++)
    {
      om[i] = point[i] - object[i + 1];
      n[i] = object[i + 4];
      om_dot_n += om[i] * n[i];
      norm_n += pow(n[i], 2);
    }
    norm_n = sqrt(norm_n);

    // STEP 2.1: compute OH as projection of OM onto line ported by n
    // OH = (OM.n) x n / |n|^2
    // STEP 2.2: compute HM = -OH + OM
    std::vector<double> oh(3);
    std::vector<double> hm(3);
    double norm_hm = 0;
    for (unsigned int i = 0; i < 3; i++)
    {
      oh[i] = om_dot_n / pow(norm_n, 2) * n[i];
      hm[i] = -oh[i] + om[i];
      norm_hm += pow(hm[i], 2);
    }
    norm_hm = sqrt(norm_hm);

    // STEP 3: compute normal as normalized HM
    // interface = HM / | HM |
    for (unsigned int i = 0; i < 3; i++)
    {
      interface[i] = hm[i] / norm_hm;
    }
  }
  else
  {
    std::cout << "WARNING: unkown object of size " << object.size() << std::endl;
  }

  return interface;
}

/* ***** */
/* IMAGE */
/* ***** */

void projmorpho::set_image(std::vector<std::vector<double>> v_image, std::vector<double> d_image, std::vector<unsigned> n_image, std::vector<double> o_image)
{
  /*
   This function interpolation fill the field values of the unstructured mesh (_v_mesh) based on an
   interpolation of the structured mesh (_v_field) using classical linear shape functions (Q8)
  */

  std::cout << "<projmorpho::set_image" << std::endl;
  _o_image = o_image; // origin
  _n_image = n_image; // number of nodes
  _d_image = d_image; // total length of the cube
  _v_image = v_image; // fields values
  std::cout << ".\t field size:\t " << _d_image[0] << " x " << _d_image[1] << " x " << _d_image[2] << std::endl;
  std::cout << ".\t field origin:\t " << _o_image[0] << " x " << _o_image[1] << " x " << _o_image[2] << std::endl;
  std::cout << ".\t field nodes:\t " << _n_image[0] << " x " << _n_image[1] << " x " << _n_image[2] << " = " << _n_image[0] * _n_image[1] * _n_image[2] << std::endl;

  _c_image.resize(_v_image[0].size());
  for (unsigned i = 0; i < _c_image.size(); i++)
  {
    _c_image[i].resize(3);
  }
  unsigned i_node = 0;
  double dx = _d_image[0] / double(_n_image[0] - 1);
  double dy = _d_image[1] / double(_n_image[1] - 1);
  double dz = _d_image[2] / double(_n_image[2] - 1);
  for (unsigned k = 0; k < _n_image[2]; k++)
  {
    for (unsigned j = 0; j < _n_image[1]; j++)
    {
      for (unsigned i = 0; i < _n_image[0]; i++)
      {
        _c_image[i_node][0] = i * dx + _o_image[0];
        _c_image[i_node][1] = j * dy + _o_image[1];
        _c_image[i_node][2] = k * dz + _o_image[2];
        i_node++;
      }
    }
  }

  unsigned n = _v_image[0].size();
  for (unsigned int f = 0; f < _v_image.size(); f++)
  {
    std::cout << ".\t field " << f + 1 << std::endl;
    std::cout << ".\t .\t node 0: " << _v_image[f][0] << std::endl;
    std::cout << ".\t .\t node 1: " << _v_image[f][1] << std::endl;
    std::cout << ".\t .\t [...] " << std::endl;
    std::cout << ".\t .\t node " << n - 2 << ": " << _v_image[f][n - 2] << std::endl;
    std::cout << ".\t .\t node " << n - 1 << ": " << _v_image[f][n - 1] << std::endl;
  }

  std::cout << ">" << std::endl;
}

void projmorpho::compute_field_from_images_loop(const std::vector<std::vector<double>> c_mesh, std::vector<std::vector<double>> &v_mesh)
{
  // c_mesh can be _c_mesh or _c_mesh_midpoints
  // v_mesh can be _v_mesh or _v_mesh_midpoints

  // WARNING: if unstructured and structured mesh does not have the same size a segmentation fault arises.
  // size of an field element
  std::vector<double> dx;
  dx.resize(3);
  for (unsigned i = 0; i < 3; i++)
  {
    dx[i] = _d_image[i] / double(_n_image[i] - 1);
  }

  // LOOP OVER ALL NODES OF THE MESH
  for (unsigned int i = 0; i < c_mesh.size(); i++)
  {
    double x1 = c_mesh[i][0];
    double y1 = c_mesh[i][1];
    double z1 = c_mesh[i][2];

    // get the node correpsonding to the regular mesh of the field
    int nodex1;
    int nodey1;
    int nodez1;

    if (std::abs(x1 - _d_image[0] - _o_image[0]) > 1e-8)
    {
      nodex1 = (int)((x1 - _o_image[0]) / dx[0]);
    }
    else
    {
      nodex1 = (int)_n_image[0] - 2; // number of nodes -1 (for the previous node) and -1 (for the initial 0)
    }
    if (std::abs(y1 - _d_image[1] - _o_image[1]) > 1e-8)
    {
      nodey1 = (int)((y1 - _o_image[1]) / dx[1]);
    }
    else
    {
      nodey1 = (int)_n_image[1] - 2;
    }
    if (std::abs(z1 - _d_image[2] - _o_image[2]) > 1e-8)
    {
      nodez1 = (int)((z1 - _o_image[2]) / dx[2]);
    }
    else
    {
      nodez1 = (int)_n_image[2] - 2;
    }

    // ************************************ /
    // _V_MESH Finite Element interpolation /
    // ************************************ /
    // Cube elementaire du RF
    // ^      ^
    // |y    /z
    //   ____
    //  /|* /|
    // /_|_/_|
    // | / | /  x
    // |/__|/   ->
    // ^
    // * Point of the non structured mesh: compute the field value at this point based on FE interpolation of the Q8
    // ^ node 1
    int node1 = nodex1 + _n_image[0] * nodey1 + _n_image[0] * _n_image[1] * nodez1; // node number (see drawing above)

    // Convestion from global to local coordinate (0<x1,y1,z1<1)
    x1 = 2 * (x1 - (_c_image[node1][0] + dx[0] / 2)) / dx[0];
    y1 = 2 * (y1 - (_c_image[node1][1] + dx[1] / 2)) / dx[1];
    z1 = 2 * (z1 - (_c_image[node1][2] + dx[2] / 2)) / dx[2];
    // Linare Q8 shape functions
    std::vector<double> N;
    N.resize(8);
    N[0] = (1 - x1) * (1 - y1) * (1 - z1) / 8;
    N[1] = (1 + x1) * (1 - y1) * (1 - z1) / 8;
    N[2] = (1 - x1) * (1 + y1) * (1 - z1) / 8;
    N[3] = (1 + x1) * (1 + y1) * (1 - z1) / 8;
    N[4] = (1 - x1) * (1 - y1) * (1 + z1) / 8;
    N[5] = (1 + x1) * (1 - y1) * (1 + z1) / 8;
    N[6] = (1 - x1) * (1 + y1) * (1 + z1) / 8;
    N[7] = (1 + x1) * (1 + y1) * (1 + z1) / 8;

    // deduce the the 8 node numbers based on node1
    std::vector<int> summit;
    summit.resize(8);                              // x;y;z
    summit[0] = node1;                             // 0;0;0
    summit[1] = node1 + 1;                         // 1;0;0
    summit[2] = node1 + _n_image[0];               // 0;1;0
    summit[3] = summit[2] + 1;                     // 1;1;0
    summit[4] = node1 + _n_image[0] * _n_image[1]; // 0;0;1
    summit[5] = summit[4] + 1;                     // 1;0;1
    summit[6] = summit[4] + _n_image[0];           // 0;1;1
    summit[7] = summit[6] + 1;                     // 1;1;1

    // FE interpolation
    for (unsigned int f = 0; f < v_mesh.size(); f++)
    {
      v_mesh[f][i] = 0.0;
      for (int j = 0; j < 8; j++)
      {
        v_mesh[f][i] += N[j] * _v_image[f][summit[j]];
      }
    }
  }
}

void projmorpho::compute_field_from_images()
{
  /*
   This function interpolation fill the field values of the unstructured mesh (_v_mesh) based on an
   interpolation of the structured mesh (_v_field) using classical linear shape functions (Q8)
  */

  std::cout << "<projmorpho::compute_field_from_images" << std::endl;
  std::cout << ".\t lengths: " << _d_image[0] << " x " << _d_image[1] << " x " << _d_image[2] << std::endl;
  std::cout << ".\t number of nodes: " << _n_image[0] << " x " << _n_image[1] << " x " << _n_image[2] << std::endl;
  std::cout << ".\t number of elements: " << _n_image[0] - 1 << " x " << _n_image[1] - 1 << " x " << _n_image[2] - 1 << std::endl;
  _v_mesh.resize(_v_image.size());
  _v_mesh_midpoints.resize(_v_image.size());
  for (unsigned int f = 0; f < _v_mesh.size(); f++)
  {
    _v_mesh[f].resize(_n_nodes);
    _v_mesh_midpoints[f].resize(_c_mesh_midpoints.size());
  }

  // check if mesh inside field
  // get field boundaries
  double max_image_x = -1e10;
  double min_image_x = 1e10;
  double max_image_y = -1e10;
  double min_image_y = 1e10;
  double max_image_z = -1e10;
  double min_image_z = 1e10;
  for (unsigned int i = 0; i < _c_image.size(); i++)
  {
    max_image_x = (_c_image[i][0] > max_image_x) ? _c_image[i][0] : max_image_x;
    min_image_x = (_c_image[i][0] < min_image_x) ? _c_image[i][0] : min_image_x;
    max_image_y = (_c_image[i][1] > max_image_y) ? _c_image[i][1] : max_image_y;
    min_image_y = (_c_image[i][1] < min_image_y) ? _c_image[i][1] : min_image_y;
    max_image_z = (_c_image[i][2] > max_image_z) ? _c_image[i][2] : max_image_z;
    min_image_z = (_c_image[i][2] < min_image_z) ? _c_image[i][2] : min_image_z;
  }
  std::cout << ".\t field box: " << std::endl;
  std::cout << ".\t .\t z = [" << min_image_x << " " << max_image_x << "]" << std::endl;
  std::cout << ".\t .\t y = [" << min_image_y << " " << max_image_y << "]" << std::endl;
  std::cout << ".\t .\t x = [" << min_image_z << " " << max_image_z << "]" << std::endl;

  // get mesh boundaries
  double max_mesh_x = -1e10;
  double min_mesh_x = 1e10;
  double max_mesh_y = -1e10;
  double min_mesh_y = 1e10;
  double max_mesh_z = -1e10;
  double min_mesh_z = 1e10;
  for (unsigned int i = 0; i < _c_mesh.size(); i++)
  {
    max_mesh_x = (_c_mesh[i][0] > max_mesh_x) ? _c_mesh[i][0] : max_mesh_x;
    min_mesh_x = (_c_mesh[i][0] < min_mesh_x) ? _c_mesh[i][0] : min_mesh_x;
    max_mesh_y = (_c_mesh[i][1] > max_mesh_y) ? _c_mesh[i][1] : max_mesh_y;
    min_mesh_y = (_c_mesh[i][1] < min_mesh_y) ? _c_mesh[i][1] : min_mesh_y;
    max_mesh_z = (_c_mesh[i][2] > max_mesh_z) ? _c_mesh[i][2] : max_mesh_z;
    min_mesh_z = (_c_mesh[i][2] < min_mesh_z) ? _c_mesh[i][2] : min_mesh_z;
  }
  std::cout << ".\t mesh box: " << std::endl;
  std::cout << ".\t .\t z = [" << min_mesh_x << " " << max_mesh_x << "]" << std::endl;
  std::cout << ".\t .\t y = [" << min_mesh_y << " " << max_mesh_y << "]" << std::endl;
  std::cout << ".\t .\t x = [" << min_mesh_z << " " << max_mesh_z << "]" << std::endl;

  if ((max_mesh_x > max_image_x) ||
      (max_mesh_y > max_image_y) ||
      (max_mesh_z > max_image_z) ||
      (min_mesh_x < min_image_x) ||
      (min_mesh_y < min_image_y) ||
      (min_mesh_z < min_image_z))
  {
    std::string msg = "mesh is outside the boundaries of the field";
    print_error(msg, true);
  }

  compute_field_from_images_loop(_c_mesh, _v_mesh);
  compute_field_from_images_loop(_c_mesh_midpoints, _v_mesh_midpoints);

  std::cout << ">" << std::endl;
}

std::vector<std::vector<double>> projmorpho::get_image_coordinates()
{
  return _c_image;
};

std::vector<std::vector<double>> projmorpho::get_image_values()
{
  return _v_image;
};

/* ********** */
/* PROJECTION */
/* ********** */

void projmorpho::projection(bool analytical_orientation = false)
{
  std::cout << "<projmorpho::projection" << std::endl;
  // LOOP OVER THE TETRAHEDRONS
  // the goal of this loop is to fill the global elementary arrays
  // _tetra_mat
  // _tetra_sub_volumes
  // _tetra_orientation
  _tetra_mat.resize(_n_elem);
  _tetra_sub_volume.resize(_n_elem);
  _tetra_orientation.resize(_n_elem); // Define global elementary arrays
  for (unsigned int it = 0; it < _n_elem; it++)
  {
    _tetra_orientation[it].resize(3);
    _tetra_sub_volume[it] = 0.0;
    _tetra_orientation[it][0] = 1.0;
    _tetra_orientation[it][1] = 0.0;
    _tetra_orientation[it][2] = 0.0;
    _tetra_mat[it] = 0;
  }
  // and also the interface arrays
  _int_n_nodes = 0;
  _int_n_tri = 0;
  _int_n_qua = 0;

  // it will be pushed back with node coordinates
  _int_nodes.resize(3);
  _int_a_tri.resize(3);
  _int_a_qua.resize(4);
  _int_v_tri.resize(5);
  _int_v_qua.resize(5);

  // loop on fields
  for (unsigned int p = 0; p < _v_mesh.size(); p++)
  {
    std::cout << ".\t field " << p + 1 << " mesh nodes: " << _v_mesh[p].size() << " mesh mid points: " << _v_mesh_midpoints[p].size() << std::endl;

    double voltot = 0.0;
    for (unsigned int it = 0; it < _n_elem; it++)
    { // it is the iterator for each tetrahedron

      // std::cout << std::endl << "Element it = " << it << " mat = " << _tetra_mat[it] << std::endl;

      // ignore tetrahedron already treated (by another phase)
      if (_tetra_mat[it] >= 2)
      {
        continue;
        std::cout << "ignore " << it << std::endl;
      }

      unsigned int it_a = it * NEN; // it_a is the corresponding position in the 1D connectivity table

      // STEP 1 - gives default values to the global elementary arrays
      // coordinates value mesh
      std::vector<std::vector<double>> c_tet(3);
      for (unsigned int k = 0; k < 3; k++)
      {
        c_tet[k].resize(NEN);
        for (int l = 0; l < NEN; l++)
        {
          c_tet[k][l] = _c_mesh[_a_mesh[it_a + l] - 1][k];
        }
      }
      tetrahedron tet;
      voltot += tet.get_volume_tet(c_tet);

      // STEP 2 - fill the local arrays
      // (the following works only for hitting set [threshold, +infty[)
      // STEP 2.0 - Define local arrays
      //  imat and theta for each edge of the current tetrahedron

      std::vector<int> mat_edge(6);
      std::vector<double> theta_edge(6);
      for (unsigned int k = 0; k < 6; k++)
      {
        mat_edge[k] = 1;
        theta_edge[k] = 0.5;
      } // default values

      // local field value mesh
      std::vector<double> v_tet(4);
      for (unsigned int k = 0; k < 4; k++)
      {
        v_tet[k] = _v_mesh[p][_a_mesh[it_a + k] - 1];
      }

      // local field value midpoints
      std::vector<double> v_mid(6);
      for (unsigned int k = 0; k < 6; k++)
      {
        v_mid[k] = _v_mesh_midpoints[p][6 * it + k];
      }

      // local correspondancy array between edges and nodes
      std::vector<std::vector<unsigned>> a_tet(6);
      for (int k = 0; k < 6; k++)
      {
        a_tet[k].resize(2);
      }
      a_tet[0][0] = 0;
      a_tet[0][1] = 1;
      a_tet[1][0] = 0;
      a_tet[1][1] = 3;
      a_tet[2][0] = 0;
      a_tet[2][1] = 2;
      a_tet[3][0] = 1;
      a_tet[3][1] = 3;
      a_tet[4][0] = 1;
      a_tet[4][1] = 2;
      a_tet[5][0] = 3;
      a_tet[5][1] = 2;

      // STEP 2.1 - compute sums and node classifications
      int sum_t1 = 0;
      int sum_t2 = 0;
      std::vector<std::vector<double>> c_theta;
      std::vector<unsigned> l_theta;
      std::vector<std::vector<unsigned>> v_pos(4);
      for (int k = 0; k < 4; k++)
      {
        v_pos[k].resize(2);
        v_pos[k][0] = 0;
        v_pos[k][1] = 0;
      }
      for (int k = 0; k < NEN; k++)
      {
        if (_v_mesh[p][_a_mesh[it_a + k] - 1] > _thresholds[0])
        {
          sum_t1++;
          v_pos[k][0] = 1;
        }
        if (_thresholds.size() > 1)
        {
          if (_v_mesh[p][_a_mesh[it_a + k] - 1] > _thresholds[1])
          {
            sum_t2++;
            v_pos[k][1] = 1;
          }
        }
      }

      // STEP 2.2 - filling local arrays
      // STEP 2.2 - CASE 1 : one phase
      if (_thresholds.size() == 1)
      {

        // STEP 2.2.1 - define the type of material depending the sum
        _tetra_mat[it] = 3;
        if (sum_t1 == 0)
        {
          _tetra_mat[it] = 1;
        }
        if (sum_t1 == 4)
        {
          _tetra_mat[it] = 2;
        }

        if (_tetra_mat[it] == 3)
        {

          // std::cout << std::endl << "Element it = " << it << " mat = " << _tetra_mat[it] << " sum_t1 " << sum_t1 << " sum_t2 " << sum_t2 << std::endl;

          // STEP 2.2.2 - filling the arays
          // compute the coordinates if the nodes of the interface
          c_theta = tet.get_coor_intrs(c_tet, v_tet, v_mid, v_pos, 0, _thresholds[0], l_theta);

          if (c_theta[0].size() == 3)
          {
            // we have a triangle interface
            _int_a_tri[0].push_back(_int_n_nodes + 0);
            _int_a_tri[1].push_back(_int_n_nodes + 1);
            _int_a_tri[2].push_back(_int_n_nodes + 2);
            _int_n_nodes += 3;
            _int_n_tri += 1;
          }
          else
          {
            // we have a quad interface
            _int_a_qua[0].push_back(_int_n_nodes + 0);
            _int_a_qua[1].push_back(_int_n_nodes + 1);
            _int_a_qua[2].push_back(_int_n_nodes + 2);
            _int_a_qua[3].push_back(_int_n_nodes + 3);
            _int_n_nodes += 4;
            _int_n_qua += 1;
          }

          // add the node coordinates
          for (unsigned int k = 0; k < c_theta[0].size(); k++)
          {
            _int_nodes[0].push_back(c_theta[0][k]);
            _int_nodes[1].push_back(c_theta[1][k]);
            _int_nodes[2].push_back(c_theta[2][k]);
          }
        }
      }

      // STEP 2.2 - CASE 2 : two phases
      else
      {
        if ((sum_t1 == 0) && (sum_t2 == 0))
        {
          _tetra_mat[it] = 1;
        }
        else if ((sum_t1 == 4) && (sum_t2 == 0))
        {
          _tetra_mat[it] = 2;
        }
        else if (sum_t2 == 0)
        {
          _tetra_mat[it] = 3;
        }
        else if ((sum_t1 == 4) && (sum_t2 == 4))
        {
          _tetra_mat[it] = 4;
        }
        else if (sum_t1 == 4)
        {
          _tetra_mat[it] = 5;
        }
        else
        {
          _tetra_mat[it] = 6;
        }

        // STEP 2.2 - CASE 2.1 : two phases / mat 3
        if (_tetra_mat[it] == 3)
        {
          c_theta = tet.get_coor_intrs(c_tet, v_tet, v_mid, v_pos, 0, _thresholds[0], l_theta);
        }

        // STEP 2.2 - CASE 2.2 : two phases / mat 5
        else if (_tetra_mat[it] == 5)
        {
          c_theta = tet.get_coor_intrs(c_tet, v_tet, v_mid, v_pos, 1, _thresholds[1], l_theta);
        }

        // STEP 2.2 - CASE 2.3 : two phases / mat 6
        else if (_tetra_mat[it] == 6)
        {
          double temp_thresholds = (_thresholds[1] + _thresholds[0]) / 2;
          c_theta = tet.get_coor_intrs(c_tet, v_tet, v_mid, v_pos, p, temp_thresholds, l_theta);
        }

        // STEP 2.2 - CASE 2.4 : two phases / mat 7
        else if (_tetra_mat[it] == 7)
        {
          if ((sum_t1 == 3) && (sum_t2 == 1))
          {
            unsigned int node_1 = 0;
            unsigned int node_2_1 = 0;
            unsigned int node_2_2 = 0;
            unsigned int node_3 = 0;
            for (unsigned int k = 0; k < 4; k++)
            {
              if (_v_mesh[p][_a_mesh[it_a + k] - 1] < _thresholds[0])
              {
                node_1 = k;
              }
              else if (_v_mesh[p][_a_mesh[it_a + k] - 1] > _thresholds[1])
              {
                node_3 = k;
              }
              else if (node_2_1 == 0)
              {
                node_2_1 = k;
              }
              else
              {
                node_2_2 = k;
              }
            }
            for (unsigned int k = 0; k < 6; k++)
            {
              theta_edge[k] = 0.5;
              if ((a_tet[k][0] == node_1) && (a_tet[k][1] == node_3))
              {
                theta_edge[k] = 1 - (v_tet[a_tet[k][0]] - ((_thresholds[1] + _thresholds[1]) / 2)) / (v_tet[a_tet[k][0]] - v_tet[a_tet[k][1]]);
                mat_edge[k] = 3;
              }
              if ((a_tet[k][0] == node_3) && (a_tet[k][1] == node_1))
              {
                theta_edge[k] = (v_tet[a_tet[k][0]] - ((_thresholds[1] + _thresholds[1]) / 2)) / (v_tet[a_tet[k][0]] - v_tet[a_tet[k][1]]);
                mat_edge[k] = 3;
              }
              if ((a_tet[k][0] == node_1) && ((a_tet[k][1] == node_2_1) || (a_tet[k][1] == node_2_2)))
              {
                mat_edge[k] = 1;
              }
              if ((a_tet[k][1] == node_1) && ((a_tet[k][0] == node_2_1) || (a_tet[k][0] == node_2_2)))
              {
                mat_edge[k] = 1;
              }
              if (((a_tet[k][0] == node_2_1) || (a_tet[k][0] == node_2_2)) && ((a_tet[k][1] == node_2_1) || (a_tet[k][1] == node_2_2)))
              {
                mat_edge[k] = 1;
              }
              if (((a_tet[k][0] == node_2_1) || (a_tet[k][0] == node_2_2)) && (a_tet[k][1] == node_3))
              {
                theta_edge[k] = 0.0;
                mat_edge[k] = 3;
              }
              if (((a_tet[k][1] == node_2_1) || (a_tet[k][1] == node_2_2)) && (a_tet[k][0] == node_3))
              {
                theta_edge[k] = 1.0;
                mat_edge[k] = 3;
              }
            } // end for k < 6
          }   // end if sum
        }     // end if material 3, 4, 5, 6, or 7
      }       // end of STEP 2.2 (closing if case one or two phases)

      // STEP 2.3 - determine type interface parameters as function of the local variables
      if ((_tetra_mat[it] == 3) || (_tetra_mat[it] == 5) || (_tetra_mat[it] == 6))
      {
        unsigned int th = 0;
        if (_tetra_mat[it] == 5)
        {
          th = 1;
        }
        else if (_tetra_mat[it] == 6)
        {
          th = (_thresholds[1] + _thresholds[0]) / 2;
        }

        // compute interface based on node positions
        std::vector<double> interface = tet.get_interface(c_tet, c_theta, v_pos, th); // interface [nx, ny, nz, area]

        // update orientation based on analytical objects
        if (analytical_orientation && _objects.size())
        {

          // compute centroid of the tetrahedron
          std::vector<double> c_centroid = tet.get_centroid(c_tet);

          // get closest object
          double field = -1e100;
          for (unsigned int i_object = 0; i_object < _objects.size(); i_object++)
          {
            std::vector<double> object = _objects[i_object];
            unsigned int phase = (unsigned int)object.back();

            // ignore object not on current phase
            if (phase != _phases_values[p])
            {
              continue;
            }

            // get closest object
            double tmp_field = _compute_distance_from_object(object, c_centroid, phase);
            if (tmp_field > field)
            {
              field = tmp_field;
              std::vector<double> orientation = _compute_normal_from_object(object, c_centroid);
              interface[0] = orientation[0];
              interface[1] = orientation[1];
              interface[2] = orientation[2];
            }
          }
        }

        double subvolume = tet.get_sub_volume(c_tet, c_theta, th, v_pos, l_theta); // subvolume
        double totvolume = tet.get_volume_tet(c_tet);                              // total volume
        double volume_ratio = subvolume / totvolume;                               // sub volume ratio

        // Testing conditions where the subvolume is too close to zero or to the total tet volume.
        // Material type is reverted to 1 or 2 in such case. A threshold of 1% is has been set for now
        // Also testing if normal computed (in case field value falls exactly on one node (theta=0))
        double normal_norm = sqrt(pow(interface[0], 2) + pow(interface[1], 2) + pow(interface[2], 2));
        bool move_to_one = volume_ratio > (1.0 - _volume_ratio_cutoff) || (normal_norm < 1e-12 && volume_ratio >= 0.5);
        bool move_to_two = volume_ratio < _volume_ratio_cutoff || (normal_norm < 1e-12 && volume_ratio < 0.5);
        int ignored = 0;
        if (move_to_one)
        {
          _tetra_mat[it] = 1;
          ignored = (normal_norm < 1e-12) ? 2 : 1;
        }
        else if (move_to_two)
        {
          _tetra_mat[it] = 2;
          ignored = (normal_norm < 1e-12) ? 2 : 1;
        }
        else
        {
          _tetra_sub_volume[it] = subvolume;
          _tetra_orientation[it][0] = interface[0];
          _tetra_orientation[it][1] = interface[1];
          _tetra_orientation[it][2] = interface[2];
        }

        // fill the interface global vector for interface VTK
        if (c_theta[0].size() == 3)
        {
          // we have a triangle
          _int_v_tri[0].push_back(interface[0]);             // add interface vector x
          _int_v_tri[1].push_back(interface[1]);             // add interface vector y
          _int_v_tri[2].push_back(interface[2]);             // add interface vector z
          _int_v_tri[3].push_back(interface[3]);             // add area of the surface
          _int_v_tri[4].push_back(double(it));               // element ID
          _int_sub_volume_ratio_tri.push_back(volume_ratio); // sub volume ratio
          _int_ignored_tri.push_back(ignored);               // ignored interfaces (0: not ignored 1: sub volumes 2: impossible to compute normal)
        }
        else if (c_theta[0].size() == 4)
        {
          // we have a quad
          _int_v_qua[0].push_back(interface[0]);             // add interface vector x
          _int_v_qua[1].push_back(interface[1]);             // add interface vector y
          _int_v_qua[2].push_back(interface[2]);             // add interface vector z
          _int_v_qua[3].push_back(interface[3]);             // add area of the surface
          _int_v_qua[4].push_back(double(it));               // element ID
          _int_sub_volume_ratio_qua.push_back(volume_ratio); // sub volume ratio
          _int_ignored_qua.push_back(ignored);               // ignored interfaces (0: not ignored 1: sub volumes 2: impossible to compute normal)
        }
        else
        {
          std::cout << "wtf are you?" << std::endl;
        }

      } // end if _tetra_mat == 3, 5 or 6 (ie weak discontinuities)

      // STEP 3 : change material if not first field field
      // f=0: 1 -> 1 = 1
      // f=0: 2 -> 2 = 2+2*f
      // f=0: 3 -> 3 = 3+2*f
      // f=1: 1 -> 1 = 1
      // f=1: 2 -> 4 = 2+2*f
      // f=1: 3 -> 5 = 3+2*f
      // f=2: 1 -> 1 = 1
      // f=2: 2 -> 6 = 2+2*f
      // f=2: 3 -> 7 = 3+2*f
      if (_tetra_mat[it] > 1)
      {
        _tetra_mat[it] = _tetra_mat[it] + 2 * p;
      }

    } // end loop over tetrahedrons
    // std::cout << ".\t total volume: " << voltot << std::endl;
    std::cout << ".\t .\t MATE," << 1 << ": background" << std::endl;
    std::cout << ".\t .\t MATE," << 2 + 2 * p << ": phase " << p + 1 << std::endl;
    std::cout << ".\t .\t MATE," << 3 + 2 * p << ": interface phase " << p + 1 << " with background" << std::endl;

  } // end loop over fields

  std::cout << ".\t Interfaces" << std::endl;
  std::cout << ".\t .\tNumber of nodes: " << _int_n_nodes << std::endl;
  std::cout << ".\t .\tNumber of triangles: " << _int_n_tri << std::endl;
  std::cout << ".\t .\tNumber of quad: " << _int_n_qua << std::endl;
  std::cout << ".\t .\tCoordinates dim: " << _int_nodes.size() << "x" << _int_nodes[0].size() << std::endl;
  std::cout << ".\t .\tTriangles dim: " << _int_a_tri.size() << "x" << _int_a_tri[0].size() << std::endl;
  std::cout << ".\t .\tQuads dim: " << _int_a_qua.size() << "x" << _int_a_qua[0].size() << std::endl;

  std::cout << ">" << std::endl;
}

std::vector<std::vector<double>> projmorpho::get_materials()
{
  std::vector<std::vector<double>> materials;
  materials.resize(_n_elem);
  for (unsigned int i = 0; i < _n_elem; i++)
  {
    materials[i].resize(5);
    materials[i][0] = _tetra_mat[i];
    materials[i][1] = _tetra_sub_volume[i];
    materials[i][2] = _tetra_orientation[i][0];
    materials[i][3] = _tetra_orientation[i][1];
    materials[i][4] = _tetra_orientation[i][2];
  }
  return materials;
};

/* ***** */
/* FILES */
/* ***** */

void projmorpho::write_feap()
{
  std::cout << "<projmorpho::write_feap" << std::endl;
  std::string feap_file_name = "I" + _file_name;
  std::string sep = ", ";

  std::ofstream feap_file;
  feap_file.open(feap_file_name, std::ios::out | std::ios::trunc);
  if (feap_file)
  {
    std::cout << ".\t feap file: " << feap_file_name << std::endl;
    // write coordinates of nodes
    feap_file << "COORdinates ! " << _n_nodes << " nodes" << std::endl;
    for (unsigned int i = 0; i < _n_nodes; i++)
    {
      feap_file << i + 1 << sep
                << 0 << sep
                << _c_mesh[i][2] << sep // !! Here switch from zyx to xyz
                << _c_mesh[i][1] << sep
                << _c_mesh[i][0] << std::endl;
    }
    feap_file << std::endl;
    // write connectivity and elements properties
    feap_file << "ELEMents ! " << _n_elem << " elements" << std::endl;
    for (unsigned int i = 0; i < _n_elem; i++)
    {
      unsigned int it_a = 4 * i;
      feap_file << i + 1 << sep                    // element number
                << 0 << sep                        // 0
                << _tetra_mat[i] << sep            // type of material
                << _a_mesh[it_a] << sep            // connectivity node 1 
                << _a_mesh[it_a + 3] << sep        // connectivity node 4 !! Here switch from zyx to xyz
                << _a_mesh[it_a + 2] << sep        // connectivity node 3
                << _a_mesh[it_a + 1] << sep        // connectivity node 2 !! Here switch from zyx to xyz 
                << _tetra_sub_volume[i] << sep     // sub volume (-)
                << _tetra_orientation[i][2] << sep // interface orientation vector !! Here switch from zyx to xyz 
                << _tetra_orientation[i][1] << sep // interface orientation vector 
                << _tetra_orientation[i][0]        // interface orientation vector 
                << std::endl;
    }
    feap_file.close();
  }
  else
  {
    std::string msg = "can\'t open feap file file \'" + feap_file_name + "\'";
    print_error(msg, true);
  }
  std::cout << ">" << std::endl;
};

void projmorpho::write_vtk()
{
  std::cout << "<projmorpho::write_vtk" << std::endl;
  std::string vtk_file_name = _file_name + ".vtk";
  std::ofstream vtk_file;
  vtk_file.open(vtk_file_name, std::ios::out | std::ios::trunc);
  std::string sep = " ";
  if (vtk_file)
  {
    std::cout << ".\t vtk file: " << vtk_file_name << std::endl;
    // STEP 1 - write header
    vtk_file << "# vtk DataFile Version 2.0" << std::endl;
    vtk_file << "VTK file from projmorpho: " << vtk_file_name << std::endl;
    vtk_file << "ASCII" << std::endl;
    vtk_file << "DATASET UNSTRUCTURED_GRID" << std::endl;
    vtk_file << std::endl;
    // STEP 2 - write coordinates of nodes
    vtk_file << "POINTS " << _n_nodes << " double" << std::endl;
    for (unsigned int i = 0; i < _n_nodes; i++)
    {
      vtk_file << _c_mesh[i][2] << sep
               << _c_mesh[i][1] << sep
               << _c_mesh[i][0] << std::endl;
    }
    vtk_file << std::endl;
    // STEP 3 - write connectivity and elements properties
    vtk_file << "CELLS " << _n_elem << " " << 5 * _n_elem << std::endl;
    for (unsigned int i = 0; i < _n_elem; i++)
    {
      unsigned int it_a = 4 * i;
      vtk_file << 4 << sep                     // number of nodes / cell
               << _a_mesh[it_a] - 1 << sep     // connectivity node 1
               << _a_mesh[it_a + 1] - 1 << sep // connectivity node 2
               << _a_mesh[it_a + 2] - 1 << sep // connectivity node 3
               << _a_mesh[it_a + 3] - 1 << sep // connectivity node 4
               << std::endl;
    }
    // STEP 4 - write type of cell
    vtk_file << "CELL_TYPES " << _n_elem << std::endl;
    for (unsigned int i = 0; i < _n_elem; i++)
    {
      vtk_file << 10 << std::endl;
    }
    vtk_file << std::endl;
    // STEP 3 - write cell datas
    vtk_file << "CELL_DATA " << _n_elem << std::endl;
    vtk_file << "SCALARS Material int" << std::endl;
    vtk_file << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _n_elem; i++)
    {
      vtk_file << _tetra_mat[i] << std::endl;
    }
    vtk_file << std::endl;
    vtk_file << "VECTORS InterfaceVector double" << std::endl;
    for (unsigned int i = 0; i < _n_elem; i++)
    {
      vtk_file << _tetra_orientation[i][2] << sep
               << _tetra_orientation[i][1] << sep
               << _tetra_orientation[i][0] << sep
               << std::endl;
    }
    vtk_file << std::endl;

    vtk_file << "POINT_DATA " << _n_nodes << std::endl;
    for (unsigned int f = 0; f < _v_mesh.size(); f++)
    {
      // STEP 4 - write nodes values (interpolated field)
      vtk_file << "SCALARS InterpolatedField" << f + 1 << " double" << std::endl;
      vtk_file << "LOOKUP_TABLE default" << std::endl;
      for (unsigned int i = 0; i < _n_nodes; i++)
      {
        vtk_file << _v_mesh[f][i] << std::endl;
      }
      vtk_file << std::endl;
    }

    vtk_file.close();
  }
  else
  {
    std::string msg = "can\'t open vtk file file \'" + vtk_file_name + "\'";
    print_error(msg, true);
  }
  std::cout << ">" << std::endl;
};

void projmorpho::write_interfaces_vtk()
{
  std::cout << "<projmorpho::write_interfaces_vtk" << std::endl;
  std::string vtk_file_name = _file_name + "_interfaces.vtk";
  std::ofstream vtk_file;
  vtk_file.open(vtk_file_name, std::ios::out | std::ios::trunc);
  std::string sep = " ";
  if (vtk_file)
  {
    std::cout << ".\t vtk file: " << vtk_file_name << std::endl;
    // STEP 1 - write header
    vtk_file << "# vtk DataFile Version 2.0" << std::endl;
    vtk_file << "VTK file from projmorpho: " << vtk_file_name << std::endl;
    vtk_file << "ASCII" << std::endl;
    vtk_file << "DATASET UNSTRUCTURED_GRID" << std::endl;
    vtk_file << std::endl;
    // STEP 2 - write coordinates of nodes
    vtk_file << "POINTS " << _int_n_nodes << " double" << std::endl;
    for (unsigned int i = 0; i < _int_n_nodes; i++)
    {
      vtk_file << _int_nodes[2][i] << sep
               << _int_nodes[1][i] << sep
               << _int_nodes[0][i] << std::endl;
    }
    vtk_file << std::endl;

    // STEP 3 - write connectivity and elements properties
    vtk_file << "CELLS " << _int_n_tri + _int_n_qua << " " << (4 * _int_n_tri) + (5 * _int_n_qua) << std::endl;
    // loop over the triangles
    for (unsigned int i = 0; i < _int_n_tri; i++)
    {
      vtk_file << 3 << sep                // number of nodes / cell
               << _int_a_tri[0][i] << sep // connectivity node 1
               << _int_a_tri[1][i] << sep // connectivity node 2
               << _int_a_tri[2][i] << sep // connectivity node 3
               << std::endl;
    }
    // loop over the quads
    for (unsigned int i = 0; i < _int_n_qua; i++)
    {
      vtk_file << 4 << sep                // number of nodes / cell
               << _int_a_qua[0][i] << sep // connectivity node 1
               << _int_a_qua[1][i] << sep // connectivity node 2
               << _int_a_qua[2][i] << sep // connectivity node 3
               << _int_a_qua[3][i] << sep // connectivity node 4
               << std::endl;
    }
    vtk_file << std::endl;

    // STEP 4 - write type of cell
    vtk_file << "CELL_TYPES " << _int_n_tri + _int_n_qua << std::endl;
    for (unsigned int i = 0; i < _int_n_tri; i++)
    {
      vtk_file << 5 << std::endl;
    }
    for (unsigned int i = 0; i < _int_n_qua; i++)
    {
      vtk_file << 9 << std::endl;
    }
    vtk_file << std::endl;

    // STEP 5 - write cell datas
    vtk_file << "CELL_DATA " << _int_n_tri + _int_n_qua << std::endl;
    vtk_file << "SCALARS ElementID int" << std::endl;
    vtk_file << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _int_n_tri; i++)
    {
      vtk_file << int(_int_v_tri[4][i]) << std::endl;
    }
    for (unsigned int i = 0; i < _int_n_qua; i++)
    {
      vtk_file << int(_int_v_qua[4][i]) << std::endl;
    }
    vtk_file << std::endl;
    vtk_file << "SCALARS Area double" << std::endl;
    vtk_file << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _int_n_tri; i++)
    {
      vtk_file << _int_v_tri[3][i] << std::endl;
    }
    for (unsigned int i = 0; i < _int_n_qua; i++)
    {
      vtk_file << _int_v_qua[3][i] << std::endl;
    }
    vtk_file << std::endl;

    vtk_file << "SCALARS SubVolumeRatio double" << std::endl;
    vtk_file << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _int_n_tri; i++)
    {
      vtk_file << _int_sub_volume_ratio_tri[i] << std::endl;
    }
    for (unsigned int i = 0; i < _int_n_qua; i++)
    {
      vtk_file << _int_sub_volume_ratio_qua[i] << std::endl;
    }
    vtk_file << std::endl;

    vtk_file << "SCALARS Ignored int" << std::endl;
    vtk_file << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _int_n_tri; i++)
    {
      vtk_file << _int_ignored_tri[i] << std::endl;
    }
    for (unsigned int i = 0; i < _int_n_qua; i++)
    {
      vtk_file << _int_ignored_qua[i] << std::endl;
    }
    vtk_file << std::endl;

    vtk_file << "VECTORS InterfaceVector double" << std::endl;
    for (unsigned int i = 0; i < _int_n_tri; i++)
    {
      vtk_file << _int_v_tri[2][i] << sep
               << _int_v_tri[1][i] << sep
               << _int_v_tri[0][i] << sep
               << std::endl;
    }
    for (unsigned int i = 0; i < _int_n_qua; i++)
    {
      vtk_file << _int_v_qua[2][i] << sep
               << _int_v_qua[1][i] << sep
               << _int_v_qua[0][i] << sep
               << std::endl;
    }
    vtk_file << std::endl;

    vtk_file.close();
  }
  else
  {
    std::string msg = "can\'t open vtk file file \'" + vtk_file_name + "\'";
    print_error(msg, true);
  }
  std::cout << ">" << std::endl;
};
