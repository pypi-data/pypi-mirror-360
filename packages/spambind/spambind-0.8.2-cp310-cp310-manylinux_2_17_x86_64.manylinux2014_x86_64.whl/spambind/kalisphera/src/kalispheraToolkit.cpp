#include "kalispheraToolkit.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

PYBIND11_MODULE(kalispheraToolkit, m) {
  m.def("kalisphera", &kalisphera, "kalisphera c++ function");
    }
