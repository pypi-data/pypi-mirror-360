#include "labelToolkit.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(labelToolkit, m) {
    m.def("boundingBoxes", &boundingBoxes, "boundingBoxes c++ function");
    m.def("centresOfMass", &centresOfMass, "centresOfMass c++ function");
    m.def("volumes", &volumes, "volumes c++ function");
    m.def("momentOfInertia", &momentOfInertia, "momentOfInertia c++ function");
    m.def("labelToFloat", &labelToFloat, "labelToFloat c++ function");
    m.def("relabel", &relabel, "relabel c++ function");
    m.def("tetPixelLabel", &tetPixelLabel, "tetPixelLabel c++ function");
    m.def("setVoronoi", &setVoronoi, "setVoronoi c++ function");
    m.def("labelContacts", &labelContacts, "labelContacts c++ function");
}
