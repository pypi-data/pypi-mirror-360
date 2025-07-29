#include <stdio.h>
#include <math.h>
#include <iostream>
#include "labelToolkit.hpp"

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

// typedef labelT;


void volumes(    py::array_t<labels::label> volLabNumpy,
                 py::array_t<unsigned short> boundingBoxesNumpy,
                 py::array_t<unsigned int> volumesNumpy
             )
{

  py::buffer_info volLabBuf = volLabNumpy.request();
  py::buffer_info boundingBoxesBuf = boundingBoxesNumpy.request();
  py::buffer_info volumesBuf = volumesNumpy.request();

  unsigned short *boundingBoxes = (unsigned short*) boundingBoxesBuf.ptr;
  labels::label *volLab = (labels::label*) volLabBuf.ptr;
  unsigned int *volumes = (unsigned int*) volumesBuf.ptr;

  int maxLabelBB = boundingBoxesBuf.shape[0];
  // size_t volSizeZu = (size_t) volLabBuf.shape[0];
  size_t volSizeYu = (size_t) volLabBuf.shape[1];
  size_t volSizeXu = (size_t) volLabBuf.shape[2];


  /*###############################################################
    ### Step 2 Get the centre of mass of each label
    ############################################################### */

    for ( labels::label label = 1; label < (labels::label)maxLabelBB; label++ )
    {
        unsigned long int pixelCount = 0;
//         printf( "\r\tVolumes progress: \t\t%02.1f%%\t", 100 * (float)(label+1) / (float)maxLabelBB );

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
                        pixelCount++;
                    }
                }
            }
        }

        /* Out of pixel loop */
        volumes[ label ] = pixelCount;
    }
//     printf( "\n" );
}
