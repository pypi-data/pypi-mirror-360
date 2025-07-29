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

void labelToFloat(   py::array_t<labels::label> volLabNumpy,
                     py::array_t<float> labelFloatsNumpy,
                     py::array_t<float> volOutputNumpy
                    )
{
    // if ( volSizeZin != volSizeZout && volSizeYin != volSizeYout && volSizeXin != volSizeXout )
    // {
    //     std::cout << "C++ labelToolkit.labelToFloat(): In and out dimensions not the same" << std::endl;
    //     return;
    // }

    py::buffer_info volLabBuf = volLabNumpy.request();
    py::buffer_info labelFloatsBuf = labelFloatsNumpy.request();
    py::buffer_info volOutputBuf = volOutputNumpy.request();

    labels::label *volLab = (labels::label*) volLabBuf.ptr;
    float *labelFloats = (float*) labelFloatsBuf.ptr;
    float *volOutput = (float*) volOutputBuf.ptr;

    int maxLabel = labelFloatsBuf.shape[0];
    size_t volSizeZin = (size_t) volLabBuf.shape[0];
    size_t volSizeYin = (size_t) volLabBuf.shape[1];
    size_t volSizeXin = (size_t) volLabBuf.shape[2];



    # pragma omp parallel
    # pragma omp for
    /* Loop over pixels and fill it in... */
    for ( size_t indexFlat = 0; indexFlat < (size_t)volSizeZin*volSizeYin*volSizeXin; indexFlat++ )
    {
        labels::label labPixelValue = volLab[ indexFlat ];

//         printf( "%i\n", labPixelValue  );
        if ( labPixelValue != 0 && labPixelValue <= (labels::label)maxLabel )
        {
            volOutput[ indexFlat ] = labelFloats[ labPixelValue ];
//             printf( "%i\t%i\t", indexFlat, labPixelValue );
//             printf( "%f\n", volOutput[ indexFlat ] );
        }
    }
}
