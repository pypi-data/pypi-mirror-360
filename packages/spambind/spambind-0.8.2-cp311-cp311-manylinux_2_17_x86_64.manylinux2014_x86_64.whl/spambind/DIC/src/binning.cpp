#include <stdio.h>
#include <math.h>
#include <iostream>
#include "DICToolkit.hpp"

// #include <Eigen/Dense>

/* 2017-05-12 Emmanuel Roubin and Edward Ando
 *
 *  Apply a 4x4 transformation matrix F to a subset of a 3D image.
 *
 * Inputs:
 *   - F (4x4)
 *   - im
 *   - subim (allocated but empty)
 *   - origin of subim
 *
 * Outputs:
 *   - ???
 *
 * Approach:
 *   1.
 */

#define MIN(x, y) (((x) < (y)) ? (x) : (y))

/*                                  Image sizes, ZYX and images*/
void binningFloat(  py::array_t<float> imNumpy,
                    py::array_t<float> imBinNumpy,
                    py::array_t<int> offsetNumpy,
                    int binning )
{

  py::buffer_info imBuf = imNumpy.request();
  float *im = (float*) imBuf.ptr;
  py::buffer_info imBinBuf = imBinNumpy.request();
  float *imBin = (float*) imBinBuf.ptr;
  py::buffer_info offsetBuf = offsetNumpy.request();
  int *offset = (int*) offsetBuf.ptr;

  size_t ny1u = (size_t) imBuf.shape[1];
  size_t nx1u = (size_t) imBuf.shape[2];
  size_t nzbu = (size_t) imBinBuf.shape[0];
  size_t nybu = (size_t) imBinBuf.shape[1];
  size_t nxbu = (size_t) imBinBuf.shape[2];


    size_t binningzu = (size_t) MIN(binning, imBuf.shape[0]);
    size_t binningyu = (size_t) MIN(binning, imBuf.shape[1]);
    size_t binningxu = (size_t) MIN(binning, imBuf.shape[2]);

    size_t zo = offset[0];
    size_t yo = offset[1];
    size_t xo = offset[2];

//     printf("Offsets (ZYX): %i %i %i", zo, yo, xo);

//     #pragma omp parallel for simd
    /* iterate over binned image */
    for ( size_t zb=0; zb < nzbu; zb++ )
    {
        for ( size_t yb=0; yb < nybu; yb++ )
        {
            for ( size_t xb=0; xb < nxbu; xb++ )
            {
                /* int variable to build index to 1D-images from x,y,z coordinates */
                size_t indexB = zb * nybu * nxbu + yb * nxbu + xb;

                float sum = 0;
                int count = 0;
                /* now loop over large image */
                for ( size_t zl=0; zl < binningzu; zl++ )
                {
                    for ( size_t yl=0; yl < binningyu; yl++ )
                    {
                        for ( size_t xl=0; xl < binningxu; xl++ )
                        {
                            size_t index1 = ( binningzu*zb + zo + zl) * ny1u * nx1u + ( binningyu*yb + yo + yl) * nx1u + ( binningxu*xb + xo + xl);
                            sum += im[ index1 ];
                            count++;
                        }
                    }
                }
                imBin[indexB] = sum / count;
             }
        }
    }
}

void binningUInt(py::array_t<unsigned short> imNumpy,
                 py::array_t<unsigned short> imBinNumpy,
                 py::array_t<int> offsetNumpy,
                 int binning )
{

    py::buffer_info imBuf = imNumpy.request();
    unsigned short *im = (unsigned short*) imBuf.ptr;
    py::buffer_info imBinBuf = imBinNumpy.request();
    unsigned short *imBin = (unsigned short*) imBinBuf.ptr;
    py::buffer_info offsetBuf = offsetNumpy.request();
    int *offset = (int*) offsetBuf.ptr;

    size_t ny1u = (size_t) imBuf.shape[1];
    size_t nx1u = (size_t) imBuf.shape[2];
    size_t nzbu = (size_t) imBinBuf.shape[0];
    size_t nybu = (size_t) imBinBuf.shape[1];
    size_t nxbu = (size_t) imBinBuf.shape[2];

    size_t binningzu = (size_t) MIN(binning, imBuf.shape[0]);
    size_t binningyu = (size_t) MIN(binning, imBuf.shape[1]);
    size_t binningxu = (size_t) MIN(binning, imBuf.shape[2]);

    size_t zo = offset[0];
    size_t yo = offset[1];
    size_t xo = offset[2];

//     printf("Offsets (ZYX): %i %i %i", zo, yo, xo);

//     #pragma omp parallel for simd
    /* iterate over binned image */
    for ( size_t zb=0; zb < nzbu; zb++ )
    {
        for ( size_t yb=0; yb < nybu; yb++ )
        {
            for ( size_t xb=0; xb < nxbu; xb++ )
            {
                /* int variable to build index to 1D-images from x,y,z coordinates */
                size_t indexB = zb * nybu * nxbu + yb * nxbu + xb;

                size_t sum = 0;
                int count = 0;
                /* now loop over large image */
                for ( size_t zl=0; zl < binningzu; zl++ )
                {
                    for ( size_t yl=0; yl < binningyu; yl++ )
                    {
                        for ( size_t xl=0; xl < binningxu; xl++ )
                        {
                            size_t index1 = ( binningzu*zb + zo + zl) * ny1u * nx1u + ( binningyu*yb + yo + yl) * nx1u + ( binningxu*xb + xo + xl);
                            sum += im[ index1 ];
                            count++;
                        }
                    }
                }
                imBin[indexB] = sum/count;
             }
        }
    }
}


void binningChar(py::array_t<unsigned char> imNumpy,
                 py::array_t<unsigned char> imBinNumpy,
                 py::array_t<int> offsetNumpy,
                 int binning )
{

    py::buffer_info imBuf = imNumpy.request();
    unsigned char *im = (unsigned char*) imBuf.ptr;
    py::buffer_info imBinBuf = imBinNumpy.request();
    unsigned char *imBin = (unsigned char*) imBinBuf.ptr;
    py::buffer_info offsetBuf = offsetNumpy.request();
    int *offset = (int*) offsetBuf.ptr;

    size_t ny1u = (size_t) imBuf.shape[1];
    size_t nx1u = (size_t) imBuf.shape[2];
    size_t nzbu = (size_t) imBinBuf.shape[0];
    size_t nybu = (size_t) imBinBuf.shape[1];
    size_t nxbu = (size_t) imBinBuf.shape[2];

    size_t binningzu = (size_t) MIN(binning, imBuf.shape[0]);
    size_t binningyu = (size_t) MIN(binning, imBuf.shape[1]);
    size_t binningxu = (size_t) MIN(binning, imBuf.shape[2]);

    size_t zo = offset[0];
    size_t yo = offset[1];
    size_t xo = offset[2];

//     printf("Offsets (ZYX): %i %i %i", zo, yo, xo);

//     #pragma omp parallel for simd
    /* iterate over binned image */
    for ( size_t zb=0; zb < nzbu; zb++ )
    {
        for ( size_t yb=0; yb < nybu; yb++ )
        {
            for ( size_t xb=0; xb < nxbu; xb++ )
            {
                /* int variable to build index to 1D-images from x,y,z coordinates */
                size_t indexB = zb * nybu * nxbu + yb * nxbu + xb;

                size_t sum = 0;
                int count = 0;
                /* now loop over large image */
                for ( size_t zl=0; zl < binningzu; zl++ )
                {
                    for ( size_t yl=0; yl < binningyu; yl++ )
                    {
                        for ( size_t xl=0; xl < binningxu; xl++ )
                        {
                            size_t index1 = ( binningzu*zb + zo + zl) * ny1u * nx1u + ( binningyu*yb + yo + yl) * nx1u + ( binningxu*xb + xo + xl);
                            sum += im[ index1 ];
                            count++;
                        }
                    }
                }
                imBin[indexB] = sum/count;
            }
        }
    }
}
