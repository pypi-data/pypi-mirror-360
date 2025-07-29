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
//#include <tiffio.h>
#include <algorithm>

#include "crpacking.hpp"
#include "projmorpho.hpp"
#include "connectivityMatrix.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(meshToolkit, m) {
  py::class_<crpacking>(m, "crpacking")
  .def(py::init<std::vector<double>, std::vector<double>, std::vector<double>, unsigned int, std::string, std::string>())
    .def("writeSpheresVTK", &crpacking::write_spheres_vtk, "write spheres VTK", py::arg("name") = "")
    .def("createSpheres", &crpacking::create_spheres, "create spheres")
    .def("packSpheres", &crpacking::pack_spheres, "pack spheres", py::arg("vtk") = false)
    .def("getObjects", &crpacking::get_objects, "get objects")
    .def("setObjects", &crpacking::set_objects, "set objects");

    py::class_<projmorpho>(m, "projmorpho")
    .def(py::init<const std::vector<double>, std::string, double>(), py::arg("thresholds") = std::vector<double> {0.0}, py::arg("name") = "projmorpho", py::arg("cutoff") = 1e-6)
      .def("setMesh", &projmorpho::set_mesh, "set mesh")
      .def("setField", &projmorpho::set_field, "set field (bypass computation of distance field)")
      .def("setObjects", &projmorpho::set_objects, "set objects")
      .def("computeFieldFromObjects", &projmorpho::compute_field_from_objects, "compute field from objects")
      .def("setImage", &projmorpho::set_image, "set image")
      .def("computeFieldFromImages", &projmorpho::compute_field_from_images, "compute field from images")
      .def("projection", &projmorpho::projection, "projection", py::arg("analytical_orientation") = false)
      .def("getMaterials", &projmorpho::get_materials, "get materials")
      .def("getConnectivity", &projmorpho::get_mesh_connectivity, "get connectivity")
      .def("getInterfaceCoordinates", &projmorpho::get_interface_coordinates, "get interface coordinates")
      .def("getInterfaceTriConnectivity", &projmorpho::get_interface_tri_connectivity, "get interface connectivity")
      .def("getInterfaceQuaConnectivity", &projmorpho::get_interface_qua_connectivity, "get interface connectivity")
      .def("writeFEAP", &projmorpho::write_feap, "write feap")
      .def("writeVTK", &projmorpho::write_vtk, "write vtk")
      .def("writeInterfacesVTK", &projmorpho::write_interfaces_vtk, "write mesh interfaces");

    m.def("countTetrahedraCGAL", &countTetrahedraCGAL, "countTetrahedraCGAL");
    m.def("triangulateCGAL", &triangulateCGAL, "triangulateCGAL");
    }
