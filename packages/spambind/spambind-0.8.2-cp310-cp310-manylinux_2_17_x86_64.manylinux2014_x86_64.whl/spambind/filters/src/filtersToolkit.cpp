
// #include <iostream>
// #include <fstream>
// #include <sstream>
// #include <stdio.h>
// #include <math.h>
// #include <cmath>
// #include <string.h>
// #include <random>
// #include <stdio.h>
// #include <stdlib.h>
// #include <vector>
// //#include <tiffio.h>
// #include <algorithm>

#include "filtersToolkit.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(filtersToolkit, m) {
    m.def("average", &average, "average c++ function moving filters");
    m.def("variance", &variance, "variance c++ function moving filters");
    m.def("hessian", &hessian, "hessian c++ function not moving filters");
}
