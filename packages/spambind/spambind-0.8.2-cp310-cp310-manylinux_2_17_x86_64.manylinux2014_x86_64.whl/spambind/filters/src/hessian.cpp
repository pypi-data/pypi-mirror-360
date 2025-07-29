#include <stdio.h>
#include <math.h>
#include <cmath>
#include <iostream>
//#include <stdlib.h> /* abs */
#include "filtersToolkit.hpp"
#include <Eigen/Dense>

/* 2017-05-23 Not Emmanuel Roubin
*

*/

/*              Image sizes, ZYX and images*/


// void hessian(   int nz1,    int ny1,     int nx1,  float *hzz,
//   int nz2,    int ny2,     int nx2,  float *hzy,
//   int nz3,    int ny3,     int nx3,  float *hzx,
//   int nz4,    int ny4,     int nx4,  float *hyz,
//   int nz5,    int ny5,     int nx5,  float *hyy,
//   int nz6,    int ny6,     int nx6,  float *hyx,
//   int nz7,    int ny7,     int nx7,  float *hxz,
//   int nz8,    int ny8,     int nx8,  float *hxy,
//   int nz9,    int ny9,     int nx9,  float *hxx,
//   int nz10,   int ny10,    int nx10, float *valA,
//   int nz11,   int ny11,    int nx11, float *valB,
//   int nz12,   int ny12,    int nx12, float *valC,
//   int nz13,   int ny13,    int nx13, float *valAz,
//   int nz14,   int ny14,    int nx14, float *valAy,
//   int nz15,   int ny15,    int nx15, float *valAx,
//   int nz16,   int ny16,    int nx16, float *valBz,
//   int nz17,   int ny17,    int nx17, float *valBy,
//   int nz18,   int ny18,    int nx18, float *valBx,
//   int nz19,   int ny19,    int nx19, float *valCz,
//   int nz20,   int ny20,    int nx20, float *valCy,
//   int nz21,   int ny21,    int nx21, float *valCx  )
void hessian(   py::array_t<float> hzzNumpy,
                py::array_t<float> hzyNumpy,
                py::array_t<float> hzxNumpy,
                py::array_t<float> hyzNumpy,
                py::array_t<float> hyyNumpy,
                py::array_t<float> hyxNumpy,
                py::array_t<float> hxzNumpy,
                py::array_t<float> hxyNumpy,
                py::array_t<float> hxxNumpy,
                py::array_t<float> valANumpy,
                py::array_t<float> valBNumpy,
                py::array_t<float> valCNumpy,
                py::array_t<float> valAzNumpy,
                py::array_t<float> valAyNumpy,
                py::array_t<float> valAxNumpy,
                py::array_t<float> valBzNumpy,
                py::array_t<float> valByNumpy,
                py::array_t<float> valBxNumpy,
                py::array_t<float> valCzNumpy,
                py::array_t<float> valCyNumpy,
                py::array_t<float> valCxNumpy )
  {

    py::buffer_info hzzBuf = hzzNumpy.request();
    py::buffer_info hzyBuf = hzyNumpy.request();
    py::buffer_info hzxBuf = hzxNumpy.request();
    py::buffer_info hyzBuf = hyzNumpy.request();
    py::buffer_info hyyBuf = hyyNumpy.request();
    py::buffer_info hyxBuf = hyxNumpy.request();
    py::buffer_info hxzBuf = hxzNumpy.request();
    py::buffer_info hxyBuf = hxyNumpy.request();
    py::buffer_info hxxBuf = hxxNumpy.request();
    py::buffer_info valABuf = valANumpy.request();
    py::buffer_info valBBuf = valBNumpy.request();
    py::buffer_info valCBuf = valCNumpy.request();
    py::buffer_info valAzBuf = valAzNumpy.request();
    py::buffer_info valAyBuf = valAyNumpy.request();
    py::buffer_info valAxBuf = valAxNumpy.request();
    py::buffer_info valBzBuf = valBzNumpy.request();
    py::buffer_info valByBuf = valByNumpy.request();
    py::buffer_info valBxBuf = valBxNumpy.request();
    py::buffer_info valCzBuf = valCzNumpy.request();
    py::buffer_info valCyBuf = valCyNumpy.request();
    py::buffer_info valCxBuf = valCxNumpy.request();

    float *hzz = (float*) hzzBuf.ptr;
    float *hzy = (float*) hzyBuf.ptr;
    float *hzx = (float*) hzxBuf.ptr;
    float *hyz = (float*) hyzBuf.ptr;
    float *hyy = (float*) hyyBuf.ptr;
    float *hyx = (float*) hyxBuf.ptr;
    float *hxz = (float*) hxzBuf.ptr;
    float *hxy = (float*) hxyBuf.ptr;
    float *hxx = (float*) hxxBuf.ptr;
    float *valA = (float*) valABuf.ptr;
    float *valB = (float*) valBBuf.ptr;
    float *valC = (float*) valCBuf.ptr;
    float *valAz = (float*) valAzBuf.ptr;
    float *valAy = (float*) valAyBuf.ptr;
    float *valAx = (float*) valAxBuf.ptr;
    float *valBz = (float*) valBzBuf.ptr;
    float *valBy = (float*) valByBuf.ptr;
    float *valBx = (float*) valBxBuf.ptr;
    float *valCz = (float*) valCzBuf.ptr;
    float *valCy = (float*) valCyBuf.ptr;
    float *valCx = (float*) valCxBuf.ptr;


    size_t nPoints = hzzBuf.shape[0] * hzzBuf.shape[1] * hzzBuf.shape[2];

    for ( size_t n=0; n<nPoints; n++ )
    {
      Eigen::Matrix3d inertiaE;
      inertiaE << hzz[n], hzy[n], hzx[n],
      hyz[n], hyy[n], hyx[n],
      hxz[n], hxy[n], hxx[n];
      Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d> eigenSolver( inertiaE );
      valA[n] = eigenSolver.eigenvalues()(2);
      valB[n] = eigenSolver.eigenvalues()(1);
      valC[n] = eigenSolver.eigenvalues()(0);
      //eigenvectors 1,2,3...
      valAz[n] = eigenSolver.eigenvectors()(0,2);
      valAy[n] = eigenSolver.eigenvectors()(1,2);
      valAx[n] = eigenSolver.eigenvectors()(2,2);
      valBz[n] = eigenSolver.eigenvectors()(0,1);
      valBy[n] = eigenSolver.eigenvectors()(1,1);
      valBx[n] = eigenSolver.eigenvectors()(2,1);
      valCz[n] = eigenSolver.eigenvectors()(0,0);
      valCy[n] = eigenSolver.eigenvectors()(1,0);
      valCx[n] = eigenSolver.eigenvectors()(2,0);
    }
  }
