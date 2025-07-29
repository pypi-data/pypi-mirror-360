
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

#include "measurementsToolkit.hpp"

// #include <pybind11/pybind11.h>
// #include <pybind11/stl.h>
//
// namespace py = pybind11;

PYBIND11_MODULE(measurementsToolkit, m) {
    m.def("computeCorrelationFunction", &computeCorrelationFunction, "computeCorrelationFunction");
    m.def("computeCurvatures", &computeCurvatures, "computeCurvatures");
    m.def("porosityFieldBinary", &porosityFieldBinary, "porosityFieldBinary");
}
