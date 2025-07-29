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

void boundingBoxes(  py::array_t<labels::label> volLabNumpy, py::array_t<unsigned short> boundingBoxesNumpy )
{
   py::buffer_info volLabBuf = volLabNumpy.request();
   py::buffer_info boundingBoxesBuf = boundingBoxesNumpy.request();

   unsigned short *boundingBoxes = (unsigned short*) boundingBoxesBuf.ptr;
   labels::label *volLab = (labels::label*) volLabBuf.ptr;

   int maxLabel = boundingBoxesBuf.shape[0];
   size_t volSizeZu = (size_t) volLabBuf.shape[0];
   size_t volSizeYu = (size_t) volLabBuf.shape[1];
   size_t volSizeXu = (size_t) volLabBuf.shape[2];

    for ( labels::label i = 1;  i < (labels::label)maxLabel; i++)
    {
//         printf( "\rResetting label extents: \t%02.1f%%\t", 100 * (float)i / (float)maxLabel );
        boundingBoxes[i*6+0] = volSizeZu-1;
        boundingBoxes[i*6+1] = 0;
        boundingBoxes[i*6+2] = volSizeYu-1;
        boundingBoxes[i*6+3] = 0;
        boundingBoxes[i*6+4] = volSizeXu-1;
        boundingBoxes[i*6+5] = 0;
    }


  /*###############################################################
    ### Step 1 get bounding boxes for each label
    ############################################################### */

//     printf( "sizes Z: %i Y: % iX: %i\n", volSizeZ, volSizeY, volSizeX );
    /* Loop over pixels and fill it in... */
    for ( size_t z = 0; z <= volSizeZu-1; z++ )
    {
//         printf( "\r\tBounding box progress: \t\t%02.1f%%\t", 100 * (float)(z+1) / (float)volSizeZ );
        for ( size_t y = 0; y <= volSizeYu-1; y++ )
        {
            for ( size_t x = 0; x <= volSizeXu-1; x++ )
            {
                size_t index_i = z  * volSizeXu * volSizeYu   +   y * volSizeXu   +   x;

                labels::label pixelValue = volLab[ index_i ];

                if ( pixelValue != 0 )
                {
                    boundingBoxes[ pixelValue*6+0 ] = MIN( z, boundingBoxes[ pixelValue*6+0 ] );
                    boundingBoxes[ pixelValue*6+2 ] = MIN( y, boundingBoxes[ pixelValue*6+2 ] );
                    boundingBoxes[ pixelValue*6+4 ] = MIN( x, boundingBoxes[ pixelValue*6+4 ] );

                    boundingBoxes[ pixelValue*6+1 ] = MAX( z, boundingBoxes[ pixelValue*6+1 ] );
                    boundingBoxes[ pixelValue*6+3 ] = MAX( y, boundingBoxes[ pixelValue*6+3 ] );
                    boundingBoxes[ pixelValue*6+5 ] = MAX( x, boundingBoxes[ pixelValue*6+5 ] );
                }
            }
        }
    }

//     printf( "\n" );

}
