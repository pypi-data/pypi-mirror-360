#include <stdio.h>
#include <math.h>
#include <iostream>
#include "DICToolkit.hpp"

/* 2017-05-12 Emmanuel Roubin and Edward Ando
 *
 * We should receive a small im1 and a larger im2, and we are going to compute similarities of im1
 * in different integer positions of im2 while looking for the best correlation coefficient
 */

float InvSqrt(float x)
{
    float xhalf = 0.5f * x;
    int i = *(int*)&x;              // get bits for floating value
    i = 0x5f375a86 - (i >> 1);      // gives initial guess y0 -- what the fuck?!
    x = *(float*)&i;                // convert bits back to float
    x = x * (1.5f - xhalf * x * x); // Newton step, repeating increases accuracy
    return x;
}


/*                                  Image sizes, ZYX and images*/
void pixelSearch(py::array_t<float> im1Numpy,
                 py::array_t<float> im2Numpy,
                 py::array_t<float> argoutdataNumpy )
{

  py::buffer_info im1Buf = im1Numpy.request();
  float *im1 = (float*) im1Buf.ptr;
  py::buffer_info im2Buf = im2Numpy.request();
  float *im2 = (float*) im2Buf.ptr;
  py::buffer_info argoutdataBuf = argoutdataNumpy.request();
  float *argoutdata = (float*) argoutdataBuf.ptr;

  size_t im1z = (size_t) im1Buf.shape[0];
  size_t im1y = (size_t) im1Buf.shape[1];
  size_t im1x = (size_t) im1Buf.shape[2];
  size_t im2z = (size_t) im2Buf.shape[0];
  size_t im2y = (size_t) im2Buf.shape[1];
  size_t im2x = (size_t) im2Buf.shape[2];


    /* size_t variable to build index to 1D-images from x,y,z coordinates */
//     size_t index1, index2;

    /* loop variables for 3D search range */
    size_t zTop, yTop, xTop;

    /* loop variables for 3D CC calculation */
    unsigned int z, y, x;


    /* empty variables for each pixel of our 3D image */
    float im1px, im2px;

    /* Variable to assemble NCC into. */
    double cc;
    double ccMax;
    ccMax = 0;

    /* Maximum variables, for tracking the best NCC so far... */
    int zMax, yMax, xMax;
    zMax = yMax = xMax = 0;


    /* calculate half-window size of image1, we will use it a lot */
//     unsigned short im1zHalf, im1yHalf, im1xHalf;
//     im1zHalf = im1z/2;
//     im1yHalf = im1y/2;
//     im1xHalf = im1x/2;

    /* Pre-calculate slice dimension for faster indexing */
    long im1yXim1x, im2yXim2x;
    im1yXim1x = im1y*im1x;
    im2yXim2x = im2y*im2x;

//     std::cout << im1zHalf << " " << im1yHalf << " " << im1xHalf << "\n" << std::endl;
    /* Go through search range in im2 -- z, y, x positions are offsets of the window,
            Consequently the first iteration here at z=y=x=0, is comparing im1 with the top
            Corner of im2 */

//     std::cout << "start pos:" << startPos[0] << " " << startPos[1] << " " << startPos[2] << std::endl;

    // coordinates of the top corner of im1 in the coordinates of im2
    for ( zTop=0; zTop <= im2z-im1z; zTop++ )
    {
        for ( yTop = 0; yTop <= im2y-im1y; yTop++ )
        {
            for ( xTop = 0; xTop <= im2x-im1x; xTop++ )
            {
//                 std::cout << zTop << " " << yTop << " " << xTop << std::endl;

                /* reset calculations */
                /* three components to our NCC calculation (see documentation/C-remi.odt) */
                float a,b,c;
                a = b = c = 0;

                /* CC calculation Loop z-first (for numpy) */
                for ( z=0; z<im1z; z++ )
                {
                    /* More speedups, precalculate slice offset*/
                    size_t zOffset1 =  z      *im1yXim1x;
                    size_t zOffset2 = (z+zTop)*im2yXim2x;

                    for ( y=0; y<im1y; y++ )
                    {
                        /* More speedups, precalculate column offset*/
                        size_t yOffset1 =  y      *im1x;
                        size_t yOffset2 = (y+yTop)*im2x;

                        for ( x=0; x<im1x; x++ )
                        {
                            /* build index to 1D image1 */
                            size_t index1 =  zOffset1 + yOffset1 + x;

                            /* build index to 1D image2 */
                            size_t index2 = zOffset2 + yOffset2 + (x+xTop);

                            /* 2015-10-22: EA -- skip NaNs in the reference image
                                *   NaNs in C are not even equal to themselves, so we'll use this simple check. */
                            if ( im1[ index1 ] == im1[ index1 ] &&  im2[ index2 ] == im2[ index2 ] )
                            {
                                // fetch 1 pixel from both images
                                im1px = im1[ index1 ];
                                im2px = im2[ index2 ];

                                // Our little bits of the NCC
                                a = a + im1px * im2px;
                                b = b + im1px * im1px;
                                c = c + im2px * im2px;
                            }
                        }
                    }
                }
                /* End CC calculation loop */

                /* once the sums are done, add up and sqrt
                * assemble bits and calculate CC */

                cc = a * InvSqrt( b * c );
//                     cc = a / std::sqrt( b * c );

//                     printf( "\tC: pixel_search: cc = %f\n", cc );
//                     printf( "\t-> CC@(z=%i,y=%i,x=%i) = %f\n", z, y, x, cc );

                /* If this cc is higher than the previous best, update our best... */
                if ( cc > ccMax )
                {
                    xMax   = xTop;
                    yMax   = yTop;
                    zMax   = zTop;
                    ccMax  = cc;
//                         printf("##### CC UPDATED #####");
//                         printf( "\t-> New CC_max@(z=%i,y=%i,x=%i) = %f\n", zMax, yMax, xMax, cc );
                }
            }
        }
    }

    argoutdata[ 0 ] = (float) zMax;
    argoutdata[ 1 ] = (float) yMax;
    argoutdata[ 2 ] = (float) xMax;
    argoutdata[ 3 ] = (float) ccMax;
}
