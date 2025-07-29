#include <stdio.h>
#include <math.h>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "labelToolkit.hpp"

namespace py = pybind11;

#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))

/* 2016-11-09 -- Edward Andò and Max Wiebicke
 *  Moment of Interia tensor calculation
 */

/* This function takes in:
 *    - labelled 3D image where the object of interest are labelled as non-zero short ints
 *    - a numpy array containing the labels to work on in numerical order (total length nLabels)
 *    - an nLabelsx3x3 float array for output
 *
 *  Function Layout: This has 3 passes through the data:
 *    1. Bounding Boxes
 *    2. Centre-of-mass
 *    3. Moment-of-inertia
 */

void centresOfMass( py::array_t<labels::label> volLabNumpy,
                    py::array_t<unsigned short> boundingBoxesNumpy,
                    py::array_t<float> centresOfMassNumpy,
                    int minVolFiltVX )
{
  /*###############################################################
    ### Step 2 Get the centre of mass of each label
    ############################################################### */

    py::buffer_info volLabBuf = volLabNumpy.request();
    py::buffer_info boundingBoxesBuf = boundingBoxesNumpy.request();
    py::buffer_info centresOfMassBuf = centresOfMassNumpy.request();

    labels::label *volLab = (labels::label*) volLabBuf.ptr;
    unsigned short *boundingBoxes = (unsigned short*) boundingBoxesBuf.ptr;
    float *centresOfMass = (float*) centresOfMassBuf.ptr;

    labels::label maxLabelBB = (labels::label) boundingBoxesBuf.shape[0];
    // size_t volSizeZu = (size_t) volLabBuf.shape[0];
    size_t volSizeYu = (size_t) volLabBuf.shape[1];
    size_t volSizeXu = (size_t) volLabBuf.shape[2];

    for ( labels::label label = 1; label < (labels::label)maxLabelBB; label++ )
    {
        long int zSum = 0;
        long int ySum = 0;
        long int xSum = 0;
        long int pixelCount = 0;
//         printf( "\r\tCentres of mass progress: \t%02.1f%%\t", 100 * (float)(label+1) / (float)maxLabelBB );

        for ( size_t z = boundingBoxes[ 6*label ]; z <= boundingBoxes[ 6*label+1 ]; z++ )
        {
            for ( size_t y = boundingBoxes[ 6*label+2 ]; y <= boundingBoxes[ 6*label+3 ]; y++ )
            {
                for ( size_t x = boundingBoxes[ 6*label+4 ]; x <= boundingBoxes[ 6*label+5 ]; x++ )
                {
                    size_t index_i = z  * volSizeXu * volSizeYu   +   y * volSizeXu   +   x;

                    labels::label pixelValue = volLab[ index_i ];

                    if ( pixelValue == label )
                    {
                        zSum += z;
                        ySum += y;
                        xSum += x;
                        pixelCount++;
                    }
                }
            }
        }

        /* Out of pixel loop */
        if ( pixelCount >= minVolFiltVX )
        {
            centresOfMass[ 3*label+0 ] = double(zSum) / double(pixelCount);
            centresOfMass[ 3*label+1 ] = double(ySum) / double(pixelCount);
            centresOfMass[ 3*label+2 ] = double(xSum) / double(pixelCount);
        }
        else
        {
            /* write zeros */
            centresOfMass[ 3*label+0 ] = 0;
            centresOfMass[ 3*label+1 ] = 0;
            centresOfMass[ 3*label+2 ] = 0;
//             /* make a cheap nan */
//             centresOfMass[ 3*label+0 ] = sqrt(-1);
//             centresOfMass[ 3*label+1 ] = sqrt(-1);
//             centresOfMass[ 3*label+2 ] = sqrt(-1);
        }

    }
//     printf( "\n" );
}
