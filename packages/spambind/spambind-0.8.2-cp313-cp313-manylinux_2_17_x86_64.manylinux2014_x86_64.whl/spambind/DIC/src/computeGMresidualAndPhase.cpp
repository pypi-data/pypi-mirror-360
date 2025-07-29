#include <stdio.h>
#include <math.h>
#include <iostream>
#include "DICToolkit.hpp"


/* 2017-10-05 Emmanuel Roubin and Edward Ando
 *
 * Please refer to Tudisco et al. "An extension of Digital Image Correlation for intermodality image registration" for theoretical background.
 *
 * The GM "computeDICoperators" is for Gaussian-Mixture of two modalities
 *
 * Calculate M and A matrices to allow an external function to solve in order to get a deltaF
 *
 * Inputs (from swig):
 *   - im1 (stationary)
 *   - im2 (being progressively deformed outside this function)
 *   - im2gz (gradient of im2 in the z direction)
 *   - im2gy (gradient of im2 in the y direction)
 *   - im2gx (gradient of im2 in the x direction)
 *   - Peaks array, 6*nPeaks. order of data: phi, Muim1, Muim2, a, b, c (a coupled to im1, b coupled to im1*im2, c coupled to im2)
 *   - empty 12x12 M matrix
 *   - empty 12x1  A vector
 *   -
 * Outputs:
 *   - none (M and A are updated)
 */

/*                                  Image sizes, ZYX and images*/
void computeGMresidualAndPhase(py::array_t<float> im1Numpy,
                               py::array_t<float> im2Numpy,
                               py::array_t<unsigned char> phasesNumpy,
                               py::array_t<double> peaksNumpy,
                               py::array_t<float> residualNumpy,
                               py::array_t<unsigned char> imLabelledNumpy
                            )
{

  py::buffer_info im1Buf = im1Numpy.request();
  float *im1 = (float*) im1Buf.ptr;
  py::buffer_info im2Buf = im2Numpy.request();
  float *im2 = (float*) im2Buf.ptr;
  py::buffer_info phasesBuf = phasesNumpy.request();
  unsigned char *phases = (unsigned char*) phasesBuf.ptr;
  py::buffer_info peaksBuf = peaksNumpy.request();
  double *peaks = (double*) peaksBuf.ptr;
  py::buffer_info residualBuf = residualNumpy.request();
  float *residual = (float*) residualBuf.ptr;
  py::buffer_info imLabelledBuf = imLabelledNumpy.request();
  unsigned char *imLabelled = (unsigned char*) imLabelledBuf.ptr;

  size_t nz1 = (size_t) im1Buf.shape[0];
  size_t ny1 = (size_t) im1Buf.shape[1];
  size_t nx1 = (size_t) im1Buf.shape[2];

  size_t binsG = (size_t) phasesBuf.shape[1];
  size_t nPeaks = (size_t) peaksBuf.shape[0];


//     std::cout << "countT: " << countThreshold << std::endl;
    /* outside loop over non-deformed image 1 called im1 */
    for ( size_t z1=0; z1 < nz1; z1++ )
    {
        for ( size_t y1=0; y1 < ny1; y1++ )
        {
            for ( size_t x1=0; x1 < nx1; x1++ )
            {
                /* int variable to build index to 1D-images from x,y,z coordinates */
                size_t index1 = z1 * ny1 * nx1 + y1 * nx1 + x1;

                /* check whether this is a NaN -- This can be used to mask the image */
                if ( im2[index1] == im2[index1] )
                {
                    /* Start by finding which peak this pair of voxels corresponds to */
                    // char  thePeak = 0;
                    double phi2min = 0;
                    for ( char i=0; i < (char)nPeaks; i++ )
                    {
                        double phi   = peaks[6*i+0];
                        double Muim1 = peaks[6*i+1];
                        double Muim2 = peaks[6*i+2];
                        double a     = peaks[6*i+3];
                        double b     = peaks[6*i+4];
                        double c     = peaks[6*i+5];
                        double lambda= 0.5 * ( a*pow( im1[index1]-Muim1, 2 ) + 2.0*b*(im1[index1]-Muim1)*(im2[index1]-Muim2) + c*pow( im2[index1]-Muim2, 2 ) );
                        double phi2  = lambda - log( phi ) ;

                        if ( ( i == 0 ) || ( phi2 < phi2min ) )
                        {
                            // thePeak = i;
                            phi2min = phi2;
                        }
                    }

//                     std::cout << "phi: " << phi << " phi2: " << phi2 << " threshold: "  << log(countThreshold) << std::endl;
//
//                     if( -phi2min > log(0.0) )
//                     {
//                     }
//                     else
//                     {
// //                         std::cout << "out\n";
//                         residual[index1] = 0;
//                     }

                    int pixelF = (int)im2[index1];
                    int pixelG = (int)im1[index1];
                    int phase = phases[ pixelF + binsG*pixelG ];
                    imLabelled[index1] = phase;
                    if(phase > 0)
                    {
                        residual[index1] = (float)phi2min;
                    } else
                    {
                        residual[index1] = 0;
                    }

                } /* end NaN check */

            }
        }
    }  /* end of im1 coords loop */
}
