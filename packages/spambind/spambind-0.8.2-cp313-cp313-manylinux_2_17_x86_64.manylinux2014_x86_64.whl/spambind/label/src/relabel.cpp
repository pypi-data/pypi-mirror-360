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
 *    - a numpy array containing a 1D array of floats to replace each label
 *    - and empty float array of same size and input label
 *
 * We will just do a single pass through the data, a flat view of the 3D data...
 *
 */

// typedef labelT;

void relabel(         py::array_t<labels::label> volLabNumpy,
                      py::array_t<labels::label> labelMapNumpy
                    )
{

  py::buffer_info volLabBuf = volLabNumpy.request();
  py::buffer_info labelMapBuf = labelMapNumpy.request();

  labels::label *volLab = (labels::label*) volLabBuf.ptr;
  labels::label *labelMap = (labels::label*) labelMapBuf.ptr;

  int maxLabel = labelMapBuf.shape[0];
  size_t volSizeZin = (size_t) volLabBuf.shape[0];
  size_t volSizeYin = (size_t) volLabBuf.shape[1];
  size_t volSizeXin = (size_t) volLabBuf.shape[2];


//     # pragma omp parallel
//     # pragma omp for
    /* Loop over pixels and fill it in... */
    for ( size_t indexFlat = 0; indexFlat < (size_t)volSizeZin*volSizeYin*volSizeXin; indexFlat++ )
    {
        labels::label labPixelValue = volLab[ indexFlat ];

        /* If it's not zero, in the map range and useful to update */
        if ( labPixelValue != 0 && labPixelValue <= (labels::label)maxLabel && labPixelValue != labelMap[ labPixelValue ] )
        {
            /* Overwrite with updated value */
//             printf("Overwriting %i with %i\n", labPixelValue, labelMap[ labPixelValue ] );
            volLab[ indexFlat ] = labelMap[ labPixelValue ];
        }
    }
}
