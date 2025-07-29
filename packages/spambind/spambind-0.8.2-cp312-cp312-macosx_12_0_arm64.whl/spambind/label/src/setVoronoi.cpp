#include <stdio.h>
#include <math.h>
#include <iostream>
#include "labelToolkit.hpp"

#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))


/* 2018-03-27 -- Edward Andò and Takashi Matsishima
 *  Approximate set Voronoi calculator
 *
 * This function takes in:
 *    - labelled 3D image where the object of interest are labelled as non-zero labels::label
 *    - a float image of the same size representing an EDT of the pores -- this can come from:
 *          scipy.ndimage.morphology.distance_transform_edt( lab == 0 ).astype( '<f4' )
 *    - a labels::label 3D array out for the labelled voxels
 */


void setVoronoi(    py::array_t<labels::label> volLabNumpy,
                    py::array_t<float> poreEDTNumpy,
                    py::array_t<labels::label> volLabOutNumpy,
                    py::array_t<int> indicesSortedNumpy,
                    py::array_t<int> indicesNumpy
//                     float distThresh
                    )
{


  py::buffer_info volLabBuf = volLabNumpy.request();
  py::buffer_info poreEDTBuf = poreEDTNumpy.request();
  py::buffer_info volLabOutBuf = volLabOutNumpy.request();
  py::buffer_info indicesSortedBuf = indicesSortedNumpy.request();
  py::buffer_info indicesBuf = indicesNumpy.request();

  labels::label *volLab = (labels::label*) volLabBuf.ptr;
  float *poreEDT = (float*) poreEDTBuf.ptr;
  labels::label *volLabOut = (labels::label*) volLabOutBuf.ptr;
  int *indicesSorted = (int*) indicesSortedBuf.ptr;
  int *indices = (int*) indicesBuf.ptr;

  size_t volSizeZ1u = (size_t) volLabBuf.shape[0];
  size_t volSizeY1u = (size_t) volLabBuf.shape[1];
  size_t volSizeX1u = (size_t) volLabBuf.shape[2];

    float distThresh = (float) indicesBuf.shape[0] - 1;
    unsigned short distThreshUS = (unsigned short) distThresh;

    for ( size_t z = distThreshUS; z <= volSizeZ1u-1-distThreshUS; z++ )
    {
//         printf( "\r\tSet Voronoi progress: \t\t%02.1f%%\t", 100 * (float)(z-distThreshUS+1) / (float)(volSizeZ1-2*distThreshUS) );

        # pragma omp parallel
        # pragma omp for
        for ( size_t y = distThreshUS; y <= volSizeY1u-1-distThreshUS; y++ )
        {
            for ( size_t x = distThreshUS; x <= volSizeX1u-1-distThreshUS; x++ )
            {
                size_t index_i = z  * volSizeX1u * volSizeY1u   +   y * volSizeX1u   +   x;

                float EDTval = poreEDT[ index_i ];

                unsigned int radiusMin = floor( EDTval );
                unsigned int radiusMax = ceil(  EDTval );

                /* In case we're on a perfect int */
                if ( radiusMin == radiusMax ) radiusMax++;

                /* If value of the pore's EDT is smaller than our time-saving threshold and is not zero */
                if ( EDTval < distThresh && EDTval > 0)
                {
                    /* Previous we raster scanned, now used sorted distances to
                     *  access elements in the right order.
                     *
                     * First of all: use the indices matrix to figure out our entry point and
                     *  end point for our scan */
                    for ( int distIndex = indices[radiusMin]; distIndex <= indices[radiusMax]; distIndex++ )
                    {
                        int Zrel = indicesSorted[ 3*distIndex + 0 ];
                        int Yrel = indicesSorted[ 3*distIndex + 1 ];
                        int Xrel = indicesSorted[ 3*distIndex + 2 ];
                        unsigned long int index_l = (z+Zrel)  * volSizeX1u * volSizeY1u   +   (y+Yrel) * volSizeX1u   +   (x+Xrel);
                        if ( volLab[ index_l ] != 0 )
                        {
                            volLabOut[ index_i ] = volLab[ index_l ];
                            break;
                        }
                    }

//                     /* Local loop around + and - radiusMax */
//                     for ( int Z = -radiusMax; Z <= radiusMax; Z++ )
//                     {
//                         for ( int Y = -radiusMax; Y <= radiusMax; Y++ )
//                         {
//                             for ( int X = -radiusMax; X <= radiusMax; X++ )
//                             {
//                                 /* Compute distance to central voxel -- keep it squared to avoid slow sqrt*/
//                                 float distSq = ( Z * Z ) + ( Y * Y ) + ( X * X );
//
//                                 /* if within radii coniditions*/
//                                 if ( distSq > radiusMin &&  distSq < closestDistanceSq )
//                                 {
//                                     unsigned long int index_l = (z+Z)  * volSizeX1 * volSizeY1   +   (y+Y) * volSizeX1   +   (x+X);
//                                     if ( volLab[ index_l ] != 0 && distSq < closestDistanceSq )
//                                     {
//                                         closestDistanceSq = distSq;
//                                         labelOut = volLab[ index_l ];
//                                     }
//                                 }
//                             }
//                         }
//                     }
//                     volLabOut[ index_i ] = labelOut;
                }

                /* We're already inside a given label, just copy it */
                if ( EDTval == 0 )
                {
                    volLabOut[ index_i ] = volLab[ index_i ];
                }
            }
        }
    }

//     printf( "\n" );
}
