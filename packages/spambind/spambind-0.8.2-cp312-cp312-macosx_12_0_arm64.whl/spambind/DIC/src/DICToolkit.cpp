#include "DICToolkit.hpp"

PYBIND11_MODULE(DICToolkit, m)
{
    // applyPhi.cpp
    m.def("applyPhi", &applyPhi, "applyPhi c++ function");
    // binning.cpp
    m.def("binningChar", &binningChar, "binningChar c++ function");
    m.def("binningUInt", &binningUInt, "binningUInt c++ function");
    m.def("binningFloat", &binningFloat, "binningFloat c++ function");
    // computeDICoperators.cpp
    m.def("computeDICoperators", &computeDICoperators, "computeDICoperators c++ function");
    m.def("computeDICjacobian", &computeDICjacobian, "computeDICjacobian c++ function");
    m.def("computeDICoperatorsGM", &computeDICoperatorsGM, "computeDICoperatorsGM c++ function");
    m.def("applyMeshTransformation", &applyMeshTransformation, "applyMeshTransformation c++ function");
    m.def("computeGradientPerTet", &computeGradientPerTet, "computeGradientPerTet c++ function");
    m.def("computeDICglobalMatrix", &computeDICglobalMatrix, "computeDICglobalMatrix c++ function");
    m.def("computeDICglobalVector", &computeDICglobalVector, "computeDICglobalVector c++ function");
    // computeGMresidualAndPhase.cpp
    m.def("computeGMresidualAndPhase", &computeGMresidualAndPhase, "computeGMresidualAndPhase c++ function");
    // pixelSearchGC.cpp
    m.def("pixelSearch", &pixelSearch, "pixelSearch c++ function");
}
