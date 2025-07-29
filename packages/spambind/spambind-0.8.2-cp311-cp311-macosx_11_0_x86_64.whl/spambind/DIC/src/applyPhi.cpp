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

/*                                  Image sizes, ZYX and images*/
void applyPhi(  py::array_t<float> imNumpy,
                py::array_t<float> imDefNumpy,
                py::array_t<float> FinvNumpy,
                py::array_t<float> FpointNumpy,
                int interpOrder )
{


  py::buffer_info imBuf = imNumpy.request();
  float *im = (float*) imBuf.ptr;
  py::buffer_info imDefBuf = imDefNumpy.request();
  float *imDef = (float*) imDefBuf.ptr;
  py::buffer_info FinvBuf = FinvNumpy.request();
  float *Finv = (float*) FinvBuf.ptr;
  py::buffer_info FpointBuf = FpointNumpy.request();
  float *Fpoint = (float*) FpointBuf.ptr;

  size_t nz1 = (size_t) imBuf.shape[0];
  size_t ny1 = (size_t) imBuf.shape[1];
  size_t nx1 = (size_t) imBuf.shape[2];
  size_t nz2 = (size_t) imDefBuf.shape[0];
  size_t ny2 = (size_t) imDefBuf.shape[1];
  size_t nx2 = (size_t) imDefBuf.shape[2];

    /* Loop over size of subimage in global coordinates, also update a linear access to imDef */
    unsigned long indexImSub = 0;

    //unsigned long zOffset = 0; // unused
    //unsigned long yOffset = 0; // unused

    float zo = Fpoint[0];
    float yo = Fpoint[1];
    float xo = Fpoint[2];

//     #pragma omp parallel for simd
    for (size_t z=0; z<nz2+0; z++ )
    {
        for (size_t y=0; y<ny2+0; y++ )
        {
            for (size_t x=0; x<nx2+0; x++ )
            {
                /* Apply F to global coordinates z,y,x */
                float zTransf = Finv[ 0]*(z-zo) + Finv[1]*(y-yo) + Finv[ 2]*(x-xo) + Finv[ 3] + zo;
                float yTransf = Finv[ 4]*(z-zo) + Finv[5]*(y-yo) + Finv[ 6]*(x-xo) + Finv[ 7] + yo;
                float xTransf = Finv[ 8]*(z-zo) + Finv[9]*(y-yo) + Finv[10]*(x-xo) + Finv[11] + xo;

                /* Check that transformed coordinates do not go outside boundaries + order for interpolation
                *   imDef should be initialised to zero, so we can drop it */
                if ( zTransf >= interpOrder && zTransf < nz1 - interpOrder &&
                     yTransf >= interpOrder && yTransf < ny1 - interpOrder &&
                     xTransf >= interpOrder && xTransf < nx1 - interpOrder )
                {

                    /* Nearest neighbour interpolation */
                    if ( interpOrder == 0 )
                    {
                        /* Round coordinates and look them up on the fly */
                        size_t indexIm = round(zTransf)* ny1 * nx1 + round(yTransf) * nx1 + round(xTransf);

                        /* Update imDef */
                        imDef[ indexImSub ] = im[ indexIm ];
                    }

                    /* Tri-Linear interpolation */
                    else if ( interpOrder == 1 )
                    {
                        double zTransfFloor = floor( zTransf );
                        double yTransfFloor = floor( yTransf );
                        double xTransfFloor = floor( xTransf );

                        double zTransfRel   = zTransf - zTransfFloor;
                        double yTransfRel   = yTransf - yTransfFloor;
                        double xTransfRel   = xTransf - xTransfFloor;

                        /* Trilinear interpolation see Eddy Phd page 128-129 */
                        double grey = 0.0;
                        double dZ, dY, dX;
                        for ( size_t zSmall = 0; zSmall <= 1; zSmall++ )
                        {
                            for ( size_t ySmall = 0; ySmall <= 1; ySmall++ )
                            {
                                for ( size_t xSmall = 0; xSmall <= 1; xSmall++ )
                                {
                                    /* Build index for 3D access */
                                    size_t index =   ( zSmall + zTransfFloor ) * ny1 * nx1  +  ( ySmall + yTransfFloor ) * nx1   +   ( xSmall + xTransfFloor );

                                    /* switch cases for the corners of the cube */
                                    if ( zSmall == 0) dZ = 1 - zTransfRel;
                                    else              dZ =     zTransfRel;
                                    if ( ySmall == 0) dY = 1 - yTransfRel;
                                    else              dY =     yTransfRel;
                                    if ( xSmall == 0) dX = 1 - xTransfRel;
                                    else              dX =     xTransfRel;

                                    /* Add recursively to current greyscale value */
                                    grey += im[index]*dZ*dY*dX;
                                }
                            }
                        }
                        /* Update imDef */
                        imDef[ indexImSub ] = (float)grey;
                    }
                    else
                    {
                        std::cout << "applyPhi(): Interpolation Order = " << interpOrder << " Not implemented, exiting.\n";
//                         return;
                    }
                }

                /* Move onto next voxel in imDef */
                indexImSub++;
            }
        }
    }
}
