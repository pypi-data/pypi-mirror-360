#include <stdio.h>
#include <math.h>
#include <iostream>
#include "DICToolkit.hpp"
#include <Eigen/Dense>

/* 2017-05-12 Emmanuel Roubin and Edward Ando
 *
 * Please refer to Tudisco et al. "An extension of Digital Image Correlation for intermodality image registration" for theoretical background.
 *
 * The standard "computeDICoperators" is for same-modality registration.
 *
 * Calculate M and A matrices to allow an external function to solve in order to get a deltaF
 *
 * Inputs (from swig):
 *   - im1 (stationary)
 *   - im2 (being progressively deformed outside this function)
 *   - im1gz (gradient of im2 in the z direction)
 *   - im1gy (gradient of im2 in the y direction)
 *   - im1gx (gradient of im2 in the x direction)
 *   - empty 12x12 M matrix
 *   - empty 12x1  A vector
 * Outputs:
 *   - none (M and A are updated)
 */

#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))

/*                                  Image sizes, ZYX and images*/
void computeDICoperators(py::array_t<float> im1Numpy,
                         py::array_t<float> im2Numpy,
                         py::array_t<float> im2gzNumpy,
                         py::array_t<float> im2gyNumpy,
                         py::array_t<float> im2gxNumpy,
                         py::array_t<double> MNumpy,
                         py::array_t<double> ANumpy)
{

    py::buffer_info im1Buf = im1Numpy.request();
    float *im1 = (float *)im1Buf.ptr;

    py::buffer_info im2Buf = im2Numpy.request();
    float *im2 = (float *)im2Buf.ptr;

    py::buffer_info im2gzBuf = im2gzNumpy.request();
    float *im2gz = (float *)im2gzBuf.ptr;

    py::buffer_info im2gyBuf = im2gyNumpy.request();
    float *im2gy = (float *)im2gyBuf.ptr;

    py::buffer_info im2gxBuf = im2gxNumpy.request();
    float *im2gx = (float *)im2gxBuf.ptr;

    py::buffer_info MBuf = MNumpy.request();
    double *M = (double *)MBuf.ptr;

    py::buffer_info ABuf = ANumpy.request();
    double *A = (double *)ABuf.ptr;

    size_t nz1 = (size_t)im1Buf.shape[0];
    size_t ny1 = (size_t)im1Buf.shape[1];
    size_t nx1 = (size_t)im1Buf.shape[2];

    // 2018-07-10 EA and OS: offset to calculate dF in centre of image
    float centreOffsetZ = (nz1 - 1) / 2.0;
    float centreOffsetY = (ny1 - 1) / 2.0;
    float centreOffsetX = (nx1 - 1) / 2.0;
    // std::cout << "center = " << centreOffsetZ << std::endl;
    // std::cout << "center = " << centreOffsetY << std::endl;
    // std::cout << "center = " << centreOffsetX << std::endl;

    // set ouput matrix to 0 -- issue #105
    for (int i = 0; i < 144; i++)
    {
        M[i] = 0;
    }
    // set ouput vector to 0 -- issue #105
    for (int i = 0; i < 12; i++)
    {
        A[i] = 0;
    }

    size_t nz1us = (size_t)nz1;
    size_t ny1us = (size_t)ny1;
    size_t nx1us = (size_t)nx1;

    // std::cout << "nz1us = " << nz1us << std::endl;
    // std::cout << "ny1us = " << ny1us << std::endl;
    // std::cout << "nx1us = " << nx1us << std::endl;
    // std::cout << "type = " << typeid(nx1us).name() << std::endl;

    /* outside loop over non-deformed image 1 called im1 */
    size_t tmp = 0;
    for (size_t z1 = 0; z1 < nz1us; z1++)
    {
        for (size_t y1 = 0; y1 < ny1us; y1++)
        {
            for (size_t x1 = 0; x1 < nx1us; x1++)
            {
                /* int variable to build index to 1D-images from x,y,z coordinates */
                size_t index1 = z1 * ny1us * nx1us + y1 * nx1us + x1;

                /* check whether this is a NaN -- Check if this pixel in im1 is not NaN */
                if (im1[index1] == im1[index1] && im2[index1] == im2[index1])
                {
                    /* See comment just before equation 8 -- i(m) == iofm and j(m) == jofm
                     * These two iterators allow us to go from the 4x4 F matrix to the 12x1
                     * flattened view of F with Voigt notation.
                     *
                     * Note: i(m) goes just to 3 to avoid the last line of F which is just padding*/
                    for (int iofm = 0; iofm < 3; iofm++)
                    {
                        for (int jofm = 0; jofm < 4; jofm++)
                        {
                            /* Variable to hold current coordinate (x_j(m)) in both eq 12 and 13 */
                            double xjofm = 0.0;

                            switch (jofm)
                            {
                            case 0:
                                xjofm = z1 - centreOffsetZ;
                                break;
                            case 1:
                                xjofm = y1 - centreOffsetY;
                                break;
                            case 2:
                                xjofm = x1 - centreOffsetX;
                                break;
                            case 3:
                                xjofm = 1;
                                break;
                            }

                            /* Variable to hold current greyvalue gTilda_,i(m) which is the gradient of
                             * the deformed im2 in the ith direction which appears in both eq 12 and 13 */
                            double gradim2iofm = 0.0;
                            switch (iofm)
                            {
                            case 0:
                                gradim2iofm = im2gz[index1];
                                break;
                            case 1:
                                gradim2iofm = im2gy[index1];
                                break;
                            case 2:
                                gradim2iofm = im2gx[index1];
                                break;
                            }

                            /* Calculate 'm' from i(m) and j(m) to access A matrix */
                            /* and sum over pixels into A which is 12x1 (equation 13) */
                            int m = 4 * iofm + jofm;
                            A[m] += (im1[index1] - im2[index1]) * (xjofm * gradim2iofm);
                            tmp++;

                            // std::cout << "\n- " << tmp << " -" << std::endl;
                            // std::cout << "\tz1   = " << z1 <<     "\ty1   = " << y1 <<        "\tx1   = " << x1 << std::endl;
                            // std::cout << "\tiofm = " << iofm <<   "\tjofm = " << jofm <<      "\txjof = " << xjofm << std::endl;
                            // std::cout << "\tinde = " << index1 << "\tgrad = " << gradim2iofm << "\tA[m] = " << A[ m ] << std::endl;
                            // std::cout << "\tgraz = " << im2gz[index1] << "\tgray = " << im2gy[index1] << "\tgraz = " << im2gx[index1] << std::endl;
                            // std::cout << "\tim1   = " << im1[index1] << "\tim2 = " << im2[index1] << std::endl;
                            // if(y1==1)
                            //   return;

                            /* Second loop to fill M matrix *
                             * as before loop over 'p' i goes to 3 and j to 4 */
                            for (int iofp = 0; iofp < 3; iofp++)
                            {
                                for (int jofp = 0; jofp < 4; jofp++)
                                {
                                    /* Variable to hold current coordinate (x_j(p)) in eq 12 */
                                    double xjofp = 0.0;
                                    switch (jofp)
                                    {
                                    case 0:
                                        xjofp = z1 - centreOffsetZ;
                                        break;
                                    case 1:
                                        xjofp = y1 - centreOffsetY;
                                        break;
                                    case 2:
                                        xjofp = x1 - centreOffsetX;
                                        break;
                                    case 3:
                                        xjofp = 1;
                                        break;
                                    }

                                    /* Variable to hold current greyvalue gTilda_,i(p) which is the gradient of
                                     * the deformed im2 in the ith direction which appears in eq 12 */
                                    double gradim2iofp = 0.0;
                                    switch (iofp)
                                    {
                                    case 0:
                                        gradim2iofp = im2gz[index1];
                                        break;
                                    case 1:
                                        gradim2iofp = im2gy[index1];
                                        break;
                                    case 2:
                                        gradim2iofp = im2gx[index1];
                                        break;
                                    }

                                    /* Sum over pixels into M which is 12x12 */
                                    int p = (4 * iofp + jofp);
                                    M[p + (12 * m)] += (xjofm * gradim2iofm) * (xjofp * gradim2iofp);
                                }
                            } /* end of 'p' loops */
                        }
                    } /* end of 'm' loops */
                }     /* end NaN check */
            }
        }
    } /* end of im1 coords loop */
    // for (int i=0; i<12; i++) {
    //   std::cout << "M["<<i<<"] = "<<M[i]<<std::endl;
    // }
    // for (int i=0; i<12; i++) {
    //   std::cout << "A["<<i<<"] = "<<A[i]<<std::endl;
    // }
}

/*  This is exactly the same as above, but just update the A matrix */
void computeDICjacobian(py::array_t<float> im1Numpy,
                        py::array_t<float> im2Numpy,
                        py::array_t<float> im2gzNumpy,
                        py::array_t<float> im2gyNumpy,
                        py::array_t<float> im2gxNumpy,
                        py::array_t<double> ANumpy)
{

    py::buffer_info im1Buf = im1Numpy.request();
    float *im1 = (float *)im1Buf.ptr;

    py::buffer_info im2Buf = im2Numpy.request();
    float *im2 = (float *)im2Buf.ptr;

    py::buffer_info im2gzBuf = im2gzNumpy.request();
    float *im2gz = (float *)im2gzBuf.ptr;

    py::buffer_info im2gyBuf = im2gyNumpy.request();
    float *im2gy = (float *)im2gyBuf.ptr;

    py::buffer_info im2gxBuf = im2gxNumpy.request();
    float *im2gx = (float *)im2gxBuf.ptr;

    py::buffer_info ABuf = ANumpy.request();
    double *A = (double *)ABuf.ptr;

    size_t nz1 = (size_t)im1Buf.shape[0];
    size_t ny1 = (size_t)im1Buf.shape[1];
    size_t nx1 = (size_t)im1Buf.shape[2];

    // 2018-07-10 EA and OS: offset to calculate dF in centre of image
    float centreOffsetZ = (nz1 - 1) / 2.0;
    float centreOffsetY = (ny1 - 1) / 2.0;
    float centreOffsetX = (nx1 - 1) / 2.0;

    // set ouput vector to 0 -- issue #105
    for (int i = 0; i < 12; i++)
    {
        A[i] = 0;
    }

    size_t nz1us = (size_t)nz1;
    size_t ny1us = (size_t)ny1;
    size_t nx1us = (size_t)nx1;

    /* outside loop over non-deformed image 1 called im1 */
    size_t tmp = 0;
    for (size_t z1 = 0; z1 < nz1us; z1++)
    {
        for (size_t y1 = 0; y1 < ny1us; y1++)
        {
            for (size_t x1 = 0; x1 < nx1us; x1++)
            {
                /* int variable to build index to 1D-images from x,y,z coordinates */
                size_t index1 = z1 * ny1us * nx1us + y1 * nx1us + x1;

                /* check whether this is a NaN -- Check if this pixel in im1 is not NaN */
                if (im1[index1] == im1[index1] && im2[index1] == im2[index1])
                {
                    /* See comment just before equation 8 -- i(m) == iofm and j(m) == jofm
                     * These two iterators allow us to go from the 4x4 F matrix to the 12x1
                     * flattened view of F with Voigt notation.
                     *
                     * Note: i(m) goes just to 3 to avoid the last line of F which is just padding*/
                    for (int iofm = 0; iofm < 3; iofm++)
                    {
                        for (int jofm = 0; jofm < 4; jofm++)
                        {
                            /* Variable to hold current coordinate (x_j(m)) in both eq 12 and 13 */
                            double xjofm = 0.0;

                            switch (jofm)
                            {
                            case 0:
                                xjofm = z1 - centreOffsetZ;
                                break;
                            case 1:
                                xjofm = y1 - centreOffsetY;
                                break;
                            case 2:
                                xjofm = x1 - centreOffsetX;
                                break;
                            case 3:
                                xjofm = 1;
                                break;
                            }

                            /* Variable to hold current greyvalue gTilda_,i(m) which is the gradient of
                             * the deformed im2 in the ith direction which appears in both eq 12 and 13 */
                            double gradim2iofm = 0.0;
                            switch (iofm)
                            {
                            case 0:
                                gradim2iofm = im2gz[index1];
                                break;
                            case 1:
                                gradim2iofm = im2gy[index1];
                                break;
                            case 2:
                                gradim2iofm = im2gx[index1];
                                break;
                            }

                            /* Calculate 'm' from i(m) and j(m) to access A matrix */
                            /* and sum over pixels into A which is 12x1 (equation 13) */
                            int m = 4 * iofm + jofm;
                            A[m] += (im1[index1] - im2[index1]) * (xjofm * gradim2iofm);
                            tmp++;
                        }
                    } /* end of 'm' loops */
                }     /* end NaN check */
            }
        }
    } /* end of im1 coords loop */
}

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
void computeDICoperatorsGM(py::array_t<float> im1Numpy,
                           py::array_t<float> im2Numpy,
                           py::array_t<float> im2gzNumpy,
                           py::array_t<float> im2gyNumpy,
                           py::array_t<float> im2gxNumpy,
                           py::array_t<unsigned char> phasesNumpy,
                           py::array_t<double> peaksNumpy,
                           py::array_t<double> MNumpy,
                           py::array_t<double> ANumpy)
{

    py::buffer_info im1Buf = im1Numpy.request();
    float *im1 = (float *)im1Buf.ptr;
    py::buffer_info im2Buf = im2Numpy.request();
    float *im2 = (float *)im2Buf.ptr;
    py::buffer_info im2gzBuf = im2gzNumpy.request();
    float *im2gz = (float *)im2gzBuf.ptr;
    py::buffer_info im2gyBuf = im2gyNumpy.request();
    float *im2gy = (float *)im2gyBuf.ptr;
    py::buffer_info im2gxBuf = im2gxNumpy.request();
    float *im2gx = (float *)im2gxBuf.ptr;
    py::buffer_info phasesBuf = phasesNumpy.request();
    unsigned char *phases = (unsigned char *)phasesBuf.ptr;
    py::buffer_info peaksBuf = peaksNumpy.request();
    double *peaks = (double *)peaksBuf.ptr;
    py::buffer_info MBuf = MNumpy.request();
    double *M = (double *)MBuf.ptr;
    py::buffer_info ABuf = ANumpy.request();
    double *A = (double *)ABuf.ptr;

    size_t binsF = (size_t)phasesBuf.shape[0];
    size_t binsG = (size_t)phasesBuf.shape[1];
    size_t nz1 = (size_t)im1Buf.shape[0];
    size_t ny1 = (size_t)im1Buf.shape[1];
    size_t nx1 = (size_t)im1Buf.shape[2];

    // 2018-07-10 EA and OS: offset to calculate dF in centre of image
    float centreOffsetZ = (nz1 - 1) / 2.0;
    float centreOffsetY = (ny1 - 1) / 2.0;
    float centreOffsetX = (nx1 - 1) / 2.0;

    // set ouput matrix to 0 -- issue #105
    for (int i = 0; i < 12 * 12; i++)
    {
        M[i] = 0;
    }
    // set ouput vector to 0 -- issue #105
    for (int i = 0; i < 12; i++)
    {
        A[i] = 0;
    }

    size_t nz1us = (size_t)nz1;
    size_t ny1us = (size_t)ny1;
    size_t nx1us = (size_t)nx1;

    /* outside loop over non-deformed image 1 called im1 */
    for (size_t z1 = 0; z1 < nz1us; z1++)
    {
        for (size_t y1 = 0; y1 < ny1us; y1++)
        {
            for (size_t x1 = 0; x1 < nx1us; x1++)
            {
                /* int variable to build index to 1D-images from x,y,z coordinates */
                size_t index1 = z1 * ny1us * nx1us + y1 * nx1us + x1;

                /* check whether this is a NaN -- This can be used to mask the image */
                if (im2[index1] == im2[index1])
                {
                    /* Start by finding which peak this pair of voxels corresponds to */
                    /*
                    int   thePeak = 0;
                    float phi2min = 0;
                    for ( int i=0; i < nPeaks; i++ )
                    {
                        float phi   = peaks[6*i+0];
                        float Muim1 = peaks[6*i+1];
                        float Muim2 = peaks[6*i+2];
                        float a     = peaks[6*i+3];
                        float b     = peaks[6*i+4];
                        float c     = peaks[6*i+5];
                        float lambda= 0.5 * ( a*pow( im1[index1]-Muim1, 2 ) + 2.0*b*(im1[index1]-Muim1)*(im2[index1]-Muim2) + c*pow( im2[index1]-Muim2, 2 ) );
                        float phi2  = lambda - log( phi ) ;

                        if ( ( i == 0 ) or ( phi2 < phi2min ) )
                        {
                            thePeak = i;
                            phi2min = phi2;
                        }
                    }
                    */

                    int pixelF = (int)im2[index1];
                    int pixelG = (int)im1[index1];

                    // This should be done outside here -- check that we're not going outside limits
                    if (pixelF > (int)binsF - 1)
                    {
                        pixelF = binsF - 1;
                    }
                    if (pixelF < 0)
                    {
                        pixelF = 0;
                    }
                    if (pixelG > (int)binsG - 1)
                    {
                        pixelG = binsG - 1;
                    }
                    if (pixelG < 0)
                    {
                        pixelG = 0;
                    }
                    unsigned char phase = phases[pixelF + binsG * pixelG];
                    // std::cout << pixelF << " " << binsF << " " << phase << std::endl;

                    // std::cout << phi2 << std::endl;
                    if (phase > 0)
                    {
                        // double phi   = peaks[6*(phase-1)+0]; // not used
                        double Muim1 = peaks[6 * (phase - 1) + 1];
                        double Muim2 = peaks[6 * (phase - 1) + 2];
                        // double a     = peaks[6*(phase-1)+3]; // not used
                        double b = peaks[6 * (phase - 1) + 4];
                        double c = peaks[6 * (phase - 1) + 5];

                        // std::cout << pixelF << " " << pixelG << ": "<< phase << std::endl;
                        // std::cout << Muim1 << " " << Muim2 << std::endl;

                        // See comment just before equation 8 -- i(m) == iofm and j(m) == jofm
                        // These two iterators allow us to go from the 4x4 F matrix to the 12x1
                        // flattened view of F with Voigt notation.
                        //  Note: i(m) goes just to 3 to avoid the last line of F which is just padding
                        for (int iofm = 0; iofm < 3; iofm++)
                        {
                            for (int jofm = 0; jofm < 4; jofm++)
                            {
                                /* Variable to hold current coordinate (x_j(m)) in both eq 12 and 13 */
                                double xjofm;

                                switch (jofm)
                                {
                                case 0:
                                    xjofm = z1 - centreOffsetZ;
                                    break;
                                case 1:
                                    xjofm = y1 - centreOffsetY;
                                    break;
                                case 2:
                                    xjofm = x1 - centreOffsetX;
                                    break;
                                case 3:
                                    xjofm = 1;
                                    break;
                                    // case 0: xjofm = z1; break;
                                    // case 1: xjofm = y1; break;
                                    // case 2: xjofm = x1; break;
                                    // case 3: xjofm = 1;  break;
                                }

                                /* Variable to hold current greyvalue gTilda_,i(m) which is the gradient of
                                 * the deformed im2 in the ith direction which appears in both eq 12 and 13 */
                                double gradim2iofm;
                                switch (iofm)
                                {
                                case 0:
                                    gradim2iofm = im2gz[index1];
                                    break;
                                case 1:
                                    gradim2iofm = im2gy[index1];
                                    break;
                                case 2:
                                    gradim2iofm = im2gx[index1];
                                    break;
                                }

                                /* Calculate 'm' from i(m) and j(m) to access A matrix */
                                /* and sum over pixels into A which is 12x1 (equation 13) */
                                int m = 4 * iofm + jofm;
                                A[m] -= (b * (im1[index1] - Muim1) + c * (im2[index1] - Muim2)) * (xjofm * gradim2iofm);

                                /* Second loop to fill M matrix *
                                 * as before loop over 'p' i goes to 3 and j to 4 */
                                for (int iofp = 0; iofp < 3; iofp++)
                                {
                                    for (int jofp = 0; jofp < 4; jofp++)
                                    {
                                        /* Variable to hold current coordinate (x_j(p)) in eq 12 */
                                        double xjofp;
                                        switch (jofp)
                                        {
                                        case 0:
                                            xjofp = z1 - centreOffsetZ;
                                            break;
                                        case 1:
                                            xjofp = y1 - centreOffsetY;
                                            break;
                                        case 2:
                                            xjofp = x1 - centreOffsetX;
                                            break;
                                        case 3:
                                            xjofp = 1;
                                            break;
                                            // case 0: xjofp = z1; break;
                                            // case 1: xjofp = y1; break;
                                            // case 2: xjofp = x1; break;
                                            // case 3: xjofp = 1;  break;
                                        }

                                        /* Variable to hold current greyvalue gTilda_,i(p) which is the gradient of
                                         * the deformed im2 in the ith direction which appears in eq 12 */
                                        double gradim2iofp;
                                        switch (iofp)
                                        {
                                        case 0:
                                            gradim2iofp = im2gz[index1];
                                            break;
                                        case 1:
                                            gradim2iofp = im2gy[index1];
                                            break;
                                        case 2:
                                            gradim2iofp = im2gx[index1];
                                            break;
                                        }

                                        /* Sum over pixels into M which is 12x12 */
                                        int p = (4 * iofp + jofp);
                                        M[p + (12 * m)] += c * (xjofm * gradim2iofm) * (xjofp * gradim2iofp);
                                    }
                                } /* end of 'p' loops */
                            }
                        } /* end of 'm' loops */
                    }     /* end if phi2 < threshold */
                }         /* end NaN check */
            }
        }
    } /* end of im1 coords loop */
}

/* ========================================================= */
/* ===  Global DVC no sorry DIC starts here              === */
/* ========================================================= */

/* ******************** */
/* Elementary functions */
/* ******************** */

Eigen::Matrix<double, 4, 4> shapeFunc(Eigen::Matrix<double, 4, 3> pTetMatrix)
{
    /* This function takes four nodes that a tetrahedron, and calculates the four coefficients of the four shape functions, see tetra.pdf */
    /* by the way, since this is C and nothing is easy, we are recieving a pre-allocated 4x4 matrix */
    Eigen::Matrix<double, 4, 4> coeffMatrix;

    /* Fill in jacTet and padd first column with zeros */
    Eigen::Matrix<double, 4, 4> jacTet;
    jacTet(0, 0) = 1;
    jacTet(1, 0) = 1;
    jacTet(2, 0) = 1;
    jacTet(3, 0) = 1;
    /* fill in jacTet, which is the jacobian of the tetrahedron (first row padded with ones) */
    for (unsigned char i = 0; i < 4; i++)
    {
        for (unsigned char j = 0; j < 3; j++)
        {
            jacTet(i, j + 1) = pTetMatrix(i, j);
        }
    }

    double sixVee = jacTet.determinant();

    /* define 3x3 matrix to calculate determinant */
    Eigen::Matrix3f tmp;

    /* from tetra.pdf */
    /* a1 */
    tmp(0, 0) = jacTet(1, 1);
    tmp(0, 1) = jacTet(1, 2);
    tmp(0, 2) = jacTet(1, 3);
    tmp(1, 0) = jacTet(2, 1);
    tmp(1, 1) = jacTet(2, 2);
    tmp(1, 2) = jacTet(2, 3);
    tmp(2, 0) = jacTet(3, 1);
    tmp(2, 1) = jacTet(3, 2);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(0, 0) = tmp.determinant() / sixVee;

    /* a2 */
    tmp(0, 0) = jacTet(0, 1);
    tmp(0, 1) = jacTet(0, 2);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(2, 1);
    tmp(1, 1) = jacTet(2, 2);
    tmp(1, 2) = jacTet(2, 3);
    tmp(2, 0) = jacTet(3, 1);
    tmp(2, 1) = jacTet(3, 2);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(1, 0) = -tmp.determinant() / sixVee;

    /* a3 */
    tmp(0, 0) = jacTet(0, 1);
    tmp(0, 1) = jacTet(0, 2);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(1, 1);
    tmp(1, 1) = jacTet(1, 2);
    tmp(1, 2) = jacTet(1, 3);
    tmp(2, 0) = jacTet(3, 1);
    tmp(2, 1) = jacTet(3, 2);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(2, 0) = tmp.determinant() / sixVee;

    /* a4 */
    tmp(0, 0) = jacTet(0, 1);
    tmp(0, 1) = jacTet(0, 2);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(1, 1);
    tmp(1, 1) = jacTet(1, 2);
    tmp(1, 2) = jacTet(1, 3);
    tmp(2, 0) = jacTet(2, 1);
    tmp(2, 1) = jacTet(2, 2);
    tmp(2, 2) = jacTet(2, 3);
    coeffMatrix(3, 0) = -tmp.determinant() / sixVee;

    /* b1 */
    tmp(0, 0) = jacTet(1, 0);
    tmp(0, 1) = jacTet(1, 2);
    tmp(0, 2) = jacTet(1, 3);
    tmp(1, 0) = jacTet(2, 0);
    tmp(1, 1) = jacTet(2, 2);
    tmp(1, 2) = jacTet(2, 3);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 2);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(0, 1) = -tmp.determinant() / sixVee;

    /* b2 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 2);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(2, 0);
    tmp(1, 1) = jacTet(2, 2);
    tmp(1, 2) = jacTet(2, 3);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 2);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(1, 1) = tmp.determinant() / sixVee;

    /* b3 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 2);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(1, 0);
    tmp(1, 1) = jacTet(1, 2);
    tmp(1, 2) = jacTet(1, 3);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 2);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(2, 1) = -tmp.determinant() / sixVee;

    /* b4 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 2);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(1, 0);
    tmp(1, 1) = jacTet(1, 2);
    tmp(1, 2) = jacTet(1, 3);
    tmp(2, 0) = jacTet(2, 0);
    tmp(2, 1) = jacTet(2, 2);
    tmp(2, 2) = jacTet(2, 3);
    coeffMatrix(3, 1) = tmp.determinant() / sixVee;

    /* c1 */
    tmp(0, 0) = jacTet(1, 0);
    tmp(0, 1) = jacTet(1, 1);
    tmp(0, 2) = jacTet(1, 3);
    tmp(1, 0) = jacTet(2, 0);
    tmp(1, 1) = jacTet(2, 1);
    tmp(1, 2) = jacTet(2, 3);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 1);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(0, 2) = tmp.determinant() / sixVee;

    /* c2 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 1);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(2, 0);
    tmp(1, 1) = jacTet(2, 1);
    tmp(1, 2) = jacTet(2, 3);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 1);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(1, 2) = -tmp.determinant() / sixVee;

    /* c3 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 1);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(1, 0);
    tmp(1, 1) = jacTet(1, 1);
    tmp(1, 2) = jacTet(1, 3);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 1);
    tmp(2, 2) = jacTet(3, 3);
    coeffMatrix(2, 2) = tmp.determinant() / sixVee;

    /* c4 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 1);
    tmp(0, 2) = jacTet(0, 3);
    tmp(1, 0) = jacTet(1, 0);
    tmp(1, 1) = jacTet(1, 1);
    tmp(1, 2) = jacTet(1, 3);
    tmp(2, 0) = jacTet(2, 0);
    tmp(2, 1) = jacTet(2, 1);
    tmp(2, 2) = jacTet(2, 3);
    coeffMatrix(3, 2) = -tmp.determinant() / sixVee;

    /* d1 */
    tmp(0, 0) = jacTet(1, 0);
    tmp(0, 1) = jacTet(1, 1);
    tmp(0, 2) = jacTet(1, 2);
    tmp(1, 0) = jacTet(2, 0);
    tmp(1, 1) = jacTet(2, 1);
    tmp(1, 2) = jacTet(2, 2);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 1);
    tmp(2, 2) = jacTet(3, 2);
    coeffMatrix(0, 3) = -tmp.determinant() / sixVee;

    /* d2 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 1);
    tmp(0, 2) = jacTet(0, 2);
    tmp(1, 0) = jacTet(2, 0);
    tmp(1, 1) = jacTet(2, 1);
    tmp(1, 2) = jacTet(2, 2);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 1);
    tmp(2, 2) = jacTet(3, 2);
    coeffMatrix(1, 3) = tmp.determinant() / sixVee;

    /* d3 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 1);
    tmp(0, 2) = jacTet(0, 2);
    tmp(1, 0) = jacTet(1, 0);
    tmp(1, 1) = jacTet(1, 1);
    tmp(1, 2) = jacTet(1, 2);
    tmp(2, 0) = jacTet(3, 0);
    tmp(2, 1) = jacTet(3, 1);
    tmp(2, 2) = jacTet(3, 2);
    coeffMatrix(2, 3) = -tmp.determinant() / sixVee;

    /* d4 */
    tmp(0, 0) = jacTet(0, 0);
    tmp(0, 1) = jacTet(0, 1);
    tmp(0, 2) = jacTet(0, 2);
    tmp(1, 0) = jacTet(1, 0);
    tmp(1, 1) = jacTet(1, 1);
    tmp(1, 2) = jacTet(1, 2);
    tmp(2, 0) = jacTet(2, 0);
    tmp(2, 1) = jacTet(2, 1);
    tmp(2, 2) = jacTet(2, 2);
    coeffMatrix(3, 3) = tmp.determinant() / sixVee;

    return coeffMatrix;
}

std::vector<double> elementaryGradient(unsigned int *volLab, size_t volSizeZ, size_t volSizeY, size_t volSizeX, // image
                                       float *vol4DGrad,
                                       Eigen::Matrix<double, 4, 3> pTetMatrix, // 4*3 points of the tetrahedron
                                       size_t nTet)
{
    /* Initialise individual element matrix */
    std::vector<double> gV{0.0, 0.0, 0.0};

    /* Find limits of the box defined by the extremities of the tetrahedron */
    double Zmin = volSizeZ;
    double Ymin = volSizeY;
    double Xmin = volSizeX;
    double Zmax = 0;
    double Ymax = 0;
    double Xmax = 0;

    for (unsigned char i = 0; i < 4; i++)
    {
        if (Zmin > pTetMatrix(i, 0))
            Zmin = MAX(pTetMatrix(i, 0), 0);
        if (Zmax < pTetMatrix(i, 0))
            Zmax = MIN(pTetMatrix(i, 0), volSizeZ - 1);
        if (Ymin > pTetMatrix(i, 1))
            Ymin = MAX(pTetMatrix(i, 1), 0);
        if (Ymax < pTetMatrix(i, 1))
            Ymax = MIN(pTetMatrix(i, 1), volSizeY - 1);
        if (Xmin > pTetMatrix(i, 2))
            Xmin = MAX(pTetMatrix(i, 2), 0);
        if (Xmax < pTetMatrix(i, 2))
            Xmax = MIN(pTetMatrix(i, 2), volSizeX - 1);
    }

    // divide gradient by the number of voxel
    unsigned int totalVox = 0;

    /* Loop over the pixels of the box defined by the extremities of the tetrahedron */
    for (size_t Z = floor(Zmin); Z <= ceil(Zmax); Z++)
    {
        for (size_t Y = floor(Ymin); Y <= ceil(Ymax); Y++)
        {
            for (size_t X = floor(Xmin); X <= ceil(Xmax); X++)
            {
                /* Build index for 3D access */
                size_t index_i = Z * volSizeX * volSizeY + Y * volSizeX + X;

                /* If our pixel is labelled with this tet number, then continue...*/
                // printf( "checking whether this pixel has the correct label at index_i = %i lab %i (%i %i %i) [%i %i %i].\n", index_i, volLab[index_i], Z, Y, X, volSizeZ, volSizeY, volSizeX  );
                if (volLab[index_i] == (unsigned int)nTet)
                {

                    totalVox += 1;

                    for (unsigned short alpha = 0; alpha < 3; alpha++)
                    {

                        size_t indexGradAlpha = index_i + (size_t)(alpha * volSizeZ * volSizeY * volSizeX);
                        gV[alpha] += vol4DGrad[indexGradAlpha];
                        // std::cout << alpha << " " << vol4DGrad[indexGradAlpha] << std::endl;
                    }
                }
            }
        }
    }

    // normalize gV by the number of voxels
    for (unsigned short alpha = 0; alpha < 3; alpha++)
    {
        // gV[alpha] = totalVox;
        gV[alpha] /= totalVox;
    }
    // std::cout << gV[0] << " " << gV[1] << " " << gV[2] << " " << totalVox<< std::endl;

    return gV;
}

Eigen::Matrix<double, 12, 12> elementaryMatrix(unsigned int *volLab, size_t volSizeZ, size_t volSizeY, size_t volSizeX, // image
                                               float *vol4DGrad,                                                        // gradient
                                               Eigen::Matrix<double, 4, 3> pTetMatrix,                                  // 4*3 points of the tetrahedron
                                               size_t nTet)
{
    /* Initialise individual element matrix */
    Eigen::Matrix<double, 12, 12> Me;
    for (unsigned char i = 0; i < 12; i++)
    {
        for (unsigned char j = 0; j < 12; j++)
        {
            Me(i, j) = 0;
        }
    }

    /* calculate Shape function coefficient matrix */
    Eigen::Matrix<double, 4, 4> coeffMatrix = shapeFunc(pTetMatrix);

    /* Find limits of the box defined by the extremities of the tetrahedron */
    double Zmin = volSizeZ;
    double Ymin = volSizeY;
    double Xmin = volSizeX;
    double Zmax = 0;
    double Ymax = 0;
    double Xmax = 0;

    for (unsigned char i = 0; i < 4; i++)
    {
        if (Zmin > pTetMatrix(i, 0))
            Zmin = MAX(pTetMatrix(i, 0), 0);
        if (Zmax < pTetMatrix(i, 0))
            Zmax = MIN(pTetMatrix(i, 0), volSizeZ - 1);
        if (Ymin > pTetMatrix(i, 1))
            Ymin = MAX(pTetMatrix(i, 1), 0);
        if (Ymax < pTetMatrix(i, 1))
            Ymax = MIN(pTetMatrix(i, 1), volSizeY - 1);
        if (Xmin > pTetMatrix(i, 2))
            Xmin = MAX(pTetMatrix(i, 2), 0);
        if (Xmax < pTetMatrix(i, 2))
            Xmax = MIN(pTetMatrix(i, 2), volSizeX - 1);
    }

    /* Loop over the pixels of the box defined by the extremities of the tetrahedron */
    for (size_t Z = floor(Zmin); Z <= ceil(Zmax); Z++)
    {
        for (size_t Y = floor(Ymin); Y <= ceil(Ymax); Y++)
        {
            for (size_t X = floor(Xmin); X <= ceil(Xmax); X++)
            {
                /* Build index for 3D access */
                size_t index_i = Z * volSizeX * volSizeY + Y * volSizeX + X;

                /* If our pixel is labelled with this tet number, then continue...*/
                //                 printf( "checking whether this pixel has the correct label at index_i = %i (%i %i %i) [%i %i %i].\n", index_i, Z, Y, X, volSizeZ, volSizeY, volSizeX  );
                if (volLab[index_i] == (unsigned int)nTet)
                {

                    /* Loop over the combinations of the nodes -- 4x4 loop, N.B. b=a to fill in the top symmetric part equation 2.2 (10) in g-dic.pdf */
                    /* Said differently the a and b subindices are the Me subindices on the right hand side of the = in equation 18 in g-dic.pdf */
                    for (unsigned short a = 0; a < 4; a++)
                    {
                        //                         for ( unsigned short b=a; b < 4; b++ )
                        for (unsigned short b = 0; b < 4; b++)
                        {
                            /* looping over dimensions in the submatrices of Me -- fx fy in equation 19 in g-dic.pdf */
                            for (unsigned short alpha = 0; alpha < 3; alpha++)
                            {

                                for (unsigned short beta = 0; beta < 3; beta++)
                                {
                                    double Na = (coeffMatrix(a, 0) * 1.0 + coeffMatrix(a, 1) * (double)Z + coeffMatrix(a, 2) * (double)Y + coeffMatrix(a, 3) * (double)X);
                                    double Nb = (coeffMatrix(b, 0) * 1.0 + coeffMatrix(b, 1) * (double)Z + coeffMatrix(b, 2) * (double)Y + coeffMatrix(b, 3) * (double)X);
                                    /* if you're crazy about performance put this in the loop above */
                                    /* create the access index to the 4D grad volume by adding an offset to the current poistion in the image */
                                    size_t indexGradAlpha = index_i + (size_t)(alpha * volSizeZ * volSizeY * volSizeX);
                                    size_t indexGradBeta = index_i + (size_t)(beta * volSizeZ * volSizeY * volSizeX);

                                    /* Look up the gradient in the alpha and beta direction * the shape function,
                                     * fill in the correct sub-me with an a and b offset */
                                    Me(3 * a + alpha, 3 * b + beta) += vol4DGrad[indexGradAlpha] * vol4DGrad[indexGradBeta] * Na * Nb;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return Me;
}

Eigen::Matrix<double, 12, 1> elementaryVector(unsigned int *volLab, unsigned int volSizeZ, unsigned int volSizeY, unsigned int volSizeX, // image
                                              float *vol4DGrad,
                                              float *vol1,
                                              float *vol2,
                                              Eigen::Matrix<double, 4, 3> pTetMatrix, // 4*3 points of the tetrahedron
                                              int nTet)
{
    /* Initialise individual element matrix */
    Eigen::Matrix<double, 12, 1> Fe;
    for (unsigned char i = 0; i < 12; i++)
        Fe(i) = 0;

    /* calculate Shape function coefficient matrix */
    Eigen::Matrix<double, 4, 4> coeffMatrix = shapeFunc(pTetMatrix);

    /* Find limits of the box defined by the extremities of the tetrahedron */
    double Zmin = volSizeZ;
    double Ymin = volSizeY;
    double Xmin = volSizeX;
    double Zmax = 0;
    double Ymax = 0;
    double Xmax = 0;

    for (unsigned char i = 0; i < 4; i++)
    {
        if (Zmin > pTetMatrix(i, 0))
            Zmin = MAX(pTetMatrix(i, 0), 0);
        if (Zmax < pTetMatrix(i, 0))
            Zmax = MIN(pTetMatrix(i, 0), volSizeZ - 1);
        if (Ymin > pTetMatrix(i, 1))
            Ymin = MAX(pTetMatrix(i, 1), 0);
        if (Ymax < pTetMatrix(i, 1))
            Ymax = MIN(pTetMatrix(i, 1), volSizeY - 1);
        if (Xmin > pTetMatrix(i, 2))
            Xmin = MAX(pTetMatrix(i, 2), 0);
        if (Xmax < pTetMatrix(i, 2))
            Xmax = MIN(pTetMatrix(i, 2), volSizeX - 1);
    }

    /* Loop over the pixels of the box defined by the extremities of the tetrahedron */
    for (size_t Z = floor(Zmin); Z < ceil(Zmax); Z++)
    {
        for (size_t Y = floor(Ymin); Y < ceil(Ymax); Y++)
        {
            for (size_t X = floor(Xmin); X < ceil(Xmax); X++)
            {
                /* Build index for 3D access */
                size_t index_i = Z * volSizeX * volSizeY + Y * volSizeX + X;

                /* If our pixel is labelled with this tet number, then continue...*/
                //                 printf( "checking whether this pixel has the correct label at index_i = %i (%i %i %i) [%i %i %i].\n", index_i, Z, Y, X, volSizeZ, volSizeY, volSizeX  );
                if (volLab[index_i] == (unsigned int)nTet)
                {

                    /* Loop over the combinations of the nodes -- 4x4 loop, N.B. b=a to fill in the top symmetric part equation 2.2 (10) in g-dic.pdf */
                    /* Said differently the a and b subindices are the Me subindices on the right hand side of the = in equation 18 in g-dic.pdf */
                    for (unsigned short a = 0; a < 4; a++)
                    {
                        /* looping over dimensions in the submatrices of Me -- fx fy in equation 19 in g-dic.pdf */
                        for (unsigned short alpha = 0; alpha < 3; alpha++)
                        {
                            double Na = (coeffMatrix(a, 0) * 1.0 + coeffMatrix(a, 1) * (double)Z + coeffMatrix(a, 2) * (double)Y + coeffMatrix(a, 3) * (double)X);
                            /* if you're crazy about performance put this in the loop above */
                            /* create the access index to the 4D grad volume by adding an offset to the current poistion in the image */
                            unsigned long indexGradAlpha = index_i + (alpha * volSizeZ * volSizeY * volSizeX);

                            /* Look up the gradient in the alpha and beta direction * the shape function,
                             * fill in the correct sub-me with an a and b offset */
                            Fe(3 * a + alpha) += (vol1[index_i] - vol2[index_i]) * Na * vol4DGrad[indexGradAlpha];
                        }
                    }
                }
            }
        }
    }

    //     std::cout << Fe << std::endl;
    return Fe;
}

/* ************** */
/* Transform mesh */
/* ************** */

void applyMeshTransformation(py::array_t<float> volGreyNumpy, // image
                             py::array_t<unsigned int> volLabNumpy,
                             py::array_t<float> volOutNumpy,
                             py::array_t<unsigned int> conneNumpy, // Connectivity Matrix      -- should be nTetrahedra * 4
                             py::array_t<double> nodesNumpy,       // Tetrahedra Points        -- should be nNodes      * 3
                             py::array_t<double> displNumpy,       // Tetrahedra Displacement  -- should be nNodes      * 3
                             int numThreads)
{

    py::buffer_info volGreyBuf = volGreyNumpy.request();
    float *volGrey = (float *)volGreyBuf.ptr;
    py::buffer_info volLabBuf = volLabNumpy.request();
    unsigned int *volLab = (unsigned int *)volLabBuf.ptr;
    py::buffer_info volOutBuf = volOutNumpy.request();
    float *volOut = (float *)volOutBuf.ptr;
    py::buffer_info conneBuf = conneNumpy.request();
    unsigned int *conne = (unsigned int *)conneBuf.ptr;
    py::buffer_info nodesBuf = nodesNumpy.request();
    double *nodes = (double *)nodesBuf.ptr;
    py::buffer_info displBuf = displNumpy.request();
    double *displ = (double *)displBuf.ptr;

    size_t conneSize = (size_t)conneBuf.shape[0];

    size_t volSizeZ = (size_t)volGreyBuf.shape[0];
    size_t volSizeY = (size_t)volGreyBuf.shape[1];
    size_t volSizeX = (size_t)volGreyBuf.shape[2];

    //     printf("interpolateMeshVoxels in C starting up\n");
/* Safety checks */
// if ( connSizeTet != 4 || pTetSizeDim != 3 )
// {
//     printf ("Did not get 4 nodes or 3 coords per node, exiting.\n");
//     return;
// }

/* Looping over all tetrahedra -- future parallelisation should be at this level. */
#pragma omp parallel for num_threads(numThreads)
    for (size_t nTet = 0; nTet < conneSize; nTet++)
    {
        //         if ( nTet%(conneSize/100) == 0) printf("\r\t(%2.1f%%) %i of %i", 100.0*(float)(nTet+1)/(float)conneSize, nTet+1, conneSize );

        /* create pTetArray Connectivity matrix and nodes List */
        Eigen::Matrix<double, 4, 3> pTetMatrix;
        /* same as above for nodal displacements */
        Eigen::Matrix<double, 4, 3> dispMatrix;
        for (size_t i = 0; i < 4; i++)
        {
            for (size_t j = 0; j < 3; j++)
            {
                size_t index_t = 3 * conne[4 * nTet + i] + j;
                pTetMatrix(i, j) = nodes[index_t];
                dispMatrix(i, j) = displ[index_t];
            }
        }

        /* calculate Shape function coefficient matrix */
        Eigen::Matrix<double, 4, 4> coeffMatrix = shapeFunc(pTetMatrix);

        /* Find limits of the box defined by the extremities of the tetrahedron */
        double Zmin = volSizeZ;
        double Ymin = volSizeY;
        double Xmin = volSizeX;
        double Zmax = 0;
        double Ymax = 0;
        double Xmax = 0;

        for (unsigned char i = 0; i < 4; i++)
        {
            if (Zmin > pTetMatrix(i, 0))
                Zmin = MAX(pTetMatrix(i, 0), 0);
            if (Zmax < pTetMatrix(i, 0))
                Zmax = MIN(pTetMatrix(i, 0), volSizeZ - 1);
            if (Ymin > pTetMatrix(i, 1))
                Ymin = MAX(pTetMatrix(i, 1), 0);
            if (Ymax < pTetMatrix(i, 1))
                Ymax = MIN(pTetMatrix(i, 1), volSizeY - 1);
            if (Xmin > pTetMatrix(i, 2))
                Xmin = MAX(pTetMatrix(i, 2), 0);
            if (Xmax < pTetMatrix(i, 2))
                Xmax = MIN(pTetMatrix(i, 2), volSizeX - 1);
        }

        /* Loop over the box defined by the extremities of the tetrahedron */
        for (size_t Z = floor(Zmin); Z <= ceil(Zmax); Z++)
        {
            for (size_t Y = floor(Ymin); Y <= ceil(Ymax); Y++)
            {
                for (size_t X = floor(Xmin); X <= ceil(Xmax); X++)
                {
                    /* Build index for 3D access */
                    size_t index_i = Z * volSizeX * volSizeY + Y * volSizeX + X;

                    /* If our pixel is labelled with this tet number, then continue...*/
                    //                 printf( "checking whether this pixel has the correct label at index_i = %i (%i %i %i) [%i %i %i].\n", index_i, Z, Y, X, volSizeZ, volSizeY, volSizeX  );
                    if (volLab[index_i] == (unsigned int)nTet)
                    {
                        double dispPixRel[3];
                        dispPixRel[0] = 0.0;
                        dispPixRel[1] = 0.0;
                        dispPixRel[2] = 0.0;

                        /* Loop over nodes of this tetrahedron */
                        for (unsigned short a = 0; a < 4; a++)
                        {
                            for (unsigned short dim = 0; dim < 3; dim++)
                            {
                                dispPixRel[dim] += (coeffMatrix(a, 0) * 1.0 + coeffMatrix(a, 1) * (double)Z + coeffMatrix(a, 2) * (double)Y + coeffMatrix(a, 3) * (double)X) * dispMatrix(a, dim);
                            }
                        }

                        /* this could be negative */
                        //                     /* start only needed for nearest neighbour interpolation */
                        //                     int displacedPosR[3];
                        //                     displacedPosR[0] = round( (double)Z-dispPixRel[0] );
                        //                     displacedPosR[1] = round( (double)Y-dispPixRel[1] );
                        //                     displacedPosR[2] = round( (double)X-dispPixRel[2] );
                        //                     /* end only needed for nearest neighbour interpolation */

                        int displacedPosF[3];
                        displacedPosF[0] = floor((double)Z - dispPixRel[0]);
                        displacedPosF[1] = floor((double)Y - dispPixRel[1]);
                        displacedPosF[2] = floor((double)X - dispPixRel[2]);

                        double displacedPosRel[3];
                        displacedPosRel[0] = (double)Z - dispPixRel[0] - (double)displacedPosF[0];
                        displacedPosRel[1] = (double)Y - dispPixRel[1] - (double)displacedPosF[1];
                        displacedPosRel[2] = (double)X - dispPixRel[2] - (double)displacedPosF[2];

                        /* check if the position + rev displacement goes outside our data -- if so, do not interpolate and give this pixel 0.0 */
                        if (displacedPosF[0] > 0 && displacedPosF[0] < (int)(volSizeZ - 1) &&
                            displacedPosF[1] > 0 && displacedPosF[1] < (int)(volSizeY - 1) &&
                            displacedPosF[2] > 0 && displacedPosF[2] < (int)(volSizeX - 1))
                        {
                            //                         /* nearest neighbour interpolation */
                            //                         unsigned int index_disp =   displacedPosR[0]  * volSizeX * volSizeY   +   displacedPosR[1] * volSizeX   +   displacedPosR[2];
                            //                         volOut[index_i] = volGrey[index_disp];
                            //                         /* endnearest neighbour interpolation */

                            /* Trilinear interpolation see Eddy Phd page 128-129 */
                            double grey = 0.0;
                            double dZ, dY, dX;
                            for (unsigned char z = 0; z <= 1; z++)
                            {
                                for (unsigned char y = 0; y <= 1; y++)
                                {
                                    for (unsigned char x = 0; x <= 1; x++)
                                    {
                                        /* Build index for 3D access */
                                        size_t index_g = (size_t)(z + displacedPosF[0]) * volSizeX * volSizeY + (size_t)(y + displacedPosF[1]) * volSizeX + (size_t)(x + displacedPosF[2]);

                                        /* switch cases for the corners of the cube */
                                        if (z == 0)
                                            dZ = 1 - displacedPosRel[0];
                                        else
                                            dZ = displacedPosRel[0];
                                        if (y == 0)
                                            dY = 1 - displacedPosRel[1];
                                        else
                                            dY = displacedPosRel[1];
                                        if (x == 0)
                                            dX = 1 - displacedPosRel[2];
                                        else
                                            dX = displacedPosRel[2];

                                        /* Add recursively to current greyscale value */
                                        grey += volGrey[index_g] * dZ * dY * dX;
                                    }
                                }
                            }
                            volOut[index_i] = grey;
                            /* End Trilinear interpolation see Eddy Phd page 128-129 */
                        }
                        // else
                        // {
                        //     volOut[index_i] = 0.0;  // it used to be 0 now we let it be
                        //     volOut[index_i] = 2.0;  // for debug purposes
                        //     std::cout << "id out: (2) " << displacedPosF[0] << " " << displacedPosF[1] << " " << displacedPosF[2] << std::endl;
                        // }
                    }
                }
            }
        }
    }
}

/* **************** */
/* Global functions */
/* **************** */

void computeGradientPerTet(py::array_t<unsigned int> volLabelNumpy, // image
                           py::array_t<float> vol4DGradNumpy,
                           py::array_t<unsigned int> conneNumpy, // Connectivity Matrix -- should be nTetrahedra * 4
                           py::array_t<double> nodesNumpy,       // Tetrahedra Points --   should be nNodes      * 3)
                           py::array_t<double> matOutNumpy)
{

    py::buffer_info volLabelBuf = volLabelNumpy.request();
    unsigned int *volLabel = (unsigned int *)volLabelBuf.ptr;
    py::buffer_info vol4DGradBuf = vol4DGradNumpy.request();
    float *vol4DGrad = (float *)vol4DGradBuf.ptr;
    py::buffer_info conneBuf = conneNumpy.request();
    unsigned int *conne = (unsigned int *)conneBuf.ptr;
    py::buffer_info nodesBuf = nodesNumpy.request();
    double *nodes = (double *)nodesBuf.ptr;
    py::buffer_info matOutBuf = matOutNumpy.request();
    double *matOut = (double *)matOutBuf.ptr;

    size_t conneSize = (size_t)conneBuf.shape[0];

    size_t volSizeZ = (size_t)volLabelBuf.shape[0];
    size_t volSizeY = (size_t)volLabelBuf.shape[1];
    size_t volSizeX = (size_t)volLabelBuf.shape[2];

    size_t n1 = (size_t)matOutBuf.shape[0];
    size_t n2 = (size_t)matOutBuf.shape[1];

    // n1 should be conneSize
    // n2 should be 3

    //  Allocate & mapping global matrix
    for (size_t i = 0; i < n1 * n2; i++)
    {
        matOut[i] = 0;
    }

// Looping over all tetrahedra
#pragma omp parallel
#pragma omp for
    for (size_t nTet = 0; nTet < conneSize; nTet++)
    // for (size_t nTet = 0; nTet < 1; nTet++)
    {
        // std::cout << "nTet " << nTet << std::endl;

        // create pTetArray Connectivity matrix and nodes List for the current tetrahedra
        Eigen::Matrix<double, 4, 3> pTetMatrix;
        for (unsigned char i = 0; i < 4; i++)
        {
            for (unsigned char j = 0; j < 3; j++)
            {
                unsigned int index_t = 3 * conne[4 * nTet + i] + j;
                pTetMatrix(i, j) = nodes[index_t];
            }
        }

        // Call elementary function and print result for now
        std::vector<double> gV = elementaryGradient(volLabel,
                                                    volSizeZ,
                                                    volSizeY,
                                                    volSizeX,
                                                    vol4DGrad,
                                                    pTetMatrix,
                                                    nTet);
        // std::cout << gV[0] << " " << gV[1] << " " << gV[2] << std::endl;
        //  Add this into the global matrix, looking up node numbers
        for (unsigned short alpha = 0; alpha < 3; alpha++)
        {
            matOut[3 * nTet + alpha] = gV[alpha];
            // std::cout << "nTet = " << nTet << " alpha = " << alpha << " i = " << 3 * nTet + alpha << " gV = " << gV[alpha] << std::endl;
        }
    }
    // std::cout << "done" << std::endl;
}

void computeDICglobalMatrix(py::array_t<unsigned int> volLabelNumpy, // image
                            py::array_t<float> vol4DGradNumpy,
                            py::array_t<unsigned int> conneNumpy, // Connectivity Matrix -- should be nTetrahedra * 4
                            py::array_t<double> nodesNumpy,       // Tetrahedra Points --   should be nNodes      * 3)
                            py::array_t<double> matOutNumpy)
{

    py::buffer_info volLabelBuf = volLabelNumpy.request();
    unsigned int *volLabel = (unsigned int *)volLabelBuf.ptr;
    py::buffer_info vol4DGradBuf = vol4DGradNumpy.request();
    float *vol4DGrad = (float *)vol4DGradBuf.ptr;
    py::buffer_info conneBuf = conneNumpy.request();
    unsigned int *conne = (unsigned int *)conneBuf.ptr;
    py::buffer_info nodesBuf = nodesNumpy.request();
    double *nodes = (double *)nodesBuf.ptr;
    py::buffer_info matOutBuf = matOutNumpy.request();
    double *matOut = (double *)matOutBuf.ptr;

    size_t conneSize = (size_t)conneBuf.shape[0];
    size_t nodesSize = (size_t)nodesBuf.shape[0];

    size_t volSizeZ = (size_t)volLabelBuf.shape[0];
    size_t volSizeY = (size_t)volLabelBuf.shape[1];
    size_t volSizeX = (size_t)volLabelBuf.shape[2];

    size_t dof1 = (size_t)matOutBuf.shape[0];
    size_t dof2 = (size_t)matOutBuf.shape[1];

    //  Allocate & mapping global matrix
    const unsigned int dof = nodesSize * 3;
    for (size_t i = 0; i < dof1 * dof2; i++)
    {
        matOut[i] = 0;
    }
    Eigen::Map<Eigen::MatrixXd> globalMatrix(matOut, dof, dof);

//  Looping over all tetrahedra
#pragma omp parallel
#pragma omp for
    for (size_t nTet = 0; nTet < conneSize; nTet++)
    {
        // create pTetArray Connectivity matrix and nodes List for the current tetrahedra
        Eigen::Matrix<double, 4, 3> pTetMatrix;
        Eigen::Matrix<double, 4, 1> nodeNumbers;
        for (unsigned char i = 0; i < 4; i++)
        {
            // record global convention node number for reassembly
            nodeNumbers(i) = conne[4 * nTet + i];

            for (unsigned char j = 0; j < 3; j++)
            {
                unsigned int index_t = 3 * conne[4 * nTet + i] + j;
                pTetMatrix(i, j) = nodes[index_t];
            }
        }

        // Call elementary function and print result for now
        Eigen::Matrix<double, 12, 12> Me = elementaryMatrix(volLabel,
                                                            volSizeZ,
                                                            volSizeY,
                                                            volSizeX,
                                                            vol4DGrad,
                                                            pTetMatrix,
                                                            nTet);

        //  Add this into the global matrix, looking up node numbers
        //  Loop over the combinations of the nodes -- 4x4 loop, N.B. b=a to fill in the top symmetric part equation 2.2 (10) in g-dic.pdf
        //  Said differently the a and b subindices are the Me subindices on the right hand side of the = in equation 18 in g-dic.pdf
        for (unsigned short a = 0; a < 4; a++)
        {
            for (unsigned short b = 0; b < 4; b++)
            {
                unsigned int nodeA = nodeNumbers(a);
                unsigned int nodeB = nodeNumbers(b);
                globalMatrix.block<3, 3>(nodeA * 3, nodeB * 3) += Me.block<3, 3>(3 * a, 3 * b);
            }
        }
    }
}

void computeDICglobalVector(py::array_t<unsigned int> volLabelNumpy, // image
                            py::array_t<float> vol4DGradNumpy,
                            py::array_t<float> vol1Numpy,
                            py::array_t<float> vol2Numpy,
                            py::array_t<unsigned int> conneNumpy, // Connectivity Matrix -- should be nTetrahedra * 4
                            py::array_t<double> nodesNumpy,       // Tetrahedra Points --   should be nNodes      * 3)
                            py::array_t<double> vecOutNumpy)
{

    py::buffer_info volLabelBuf = volLabelNumpy.request();
    unsigned int *volLabel = (unsigned int *)volLabelBuf.ptr;
    py::buffer_info vol4DGradBuf = vol4DGradNumpy.request();
    float *vol4DGrad = (float *)vol4DGradBuf.ptr;
    py::buffer_info vol1Buf = vol1Numpy.request();
    float *vol1 = (float *)vol1Buf.ptr;
    py::buffer_info vol2Buf = vol2Numpy.request();
    float *vol2 = (float *)vol2Buf.ptr;
    py::buffer_info conneBuf = conneNumpy.request();
    unsigned int *conne = (unsigned int *)conneBuf.ptr;
    py::buffer_info nodesBuf = nodesNumpy.request();
    double *nodes = (double *)nodesBuf.ptr;
    py::buffer_info vecOutBuf = vecOutNumpy.request();
    double *vecOut = (double *)vecOutBuf.ptr;

    size_t conneSize = (size_t)conneBuf.shape[0];
    size_t nodesSize = (size_t)nodesBuf.shape[0];

    size_t volSizeZ = (size_t)volLabelBuf.shape[0];
    size_t volSizeY = (size_t)volLabelBuf.shape[1];
    size_t volSizeX = (size_t)volLabelBuf.shape[2];

    size_t dof3 = (size_t)vecOutBuf.shape[0];

    /* Safety checks */
    // if ( connSizeTet != 4 || pTetSizeDim != 3 )
    // {
    //     printf ("Did not get 4 nodes or 3 coords per node, exiting.\n");
    //     return;
    // }

    // set ouput matrix to 0
    for (size_t i = 0; i < dof3; i++)
    {
        vecOut[i] = 0;
    }

    /* Allocate global matrix*/
    const unsigned int dof = nodesSize * 3;

    Eigen::Map<Eigen::MatrixXd> globalVector(vecOut, dof, 1);

#pragma omp parallel
#pragma omp for
    /* Looping over all tetrahedra -- future parallelisation should be at this level. */
    for (size_t nTet = 0; nTet < conneSize; nTet++)
    {
        //         if ( nTet%(conneSize/100) == 0) printf("\r\t(%2.1f%%) %i of %i", 100.0*(float)(nTet+1)/(float)conneSize, nTet+1, conneSize );

        /* create pTetArray Connectivity matrix and nodes List */
        Eigen::Matrix<double, 4, 3> pTetMatrix;
        Eigen::Matrix<double, 4, 1> nodeNumbers;
        /* same as above for nodal displacements */
        for (size_t i = 0; i < 4; i++)
        {
            /* record global convention node number for reassembly */
            nodeNumbers(i) = conne[4 * nTet + i];

            for (size_t j = 0; j < 3; j++)
            {
                size_t index_t = 3 * conne[4 * nTet + i] + j;
                pTetMatrix(i, j) = nodes[index_t];
            }
        }

        //         std::cout << nodeNumbers << std::endl;
        //         printf( "\n\n" );

        /* Call elementary function and print result for now */
        Eigen::Matrix<double, 12, 1> Fe = elementaryVector(volLabel, volSizeZ, volSizeY, volSizeX,
                                                           vol4DGrad,
                                                           vol1,
                                                           vol2,
                                                           pTetMatrix,
                                                           nTet);

        /* Add this into the global matrix, looking up node numbers */
        /* Loop over the combinations of the nodes -- 4x4 loop, N.B. b=a to fill in the top symmetric part equation 2.2 (10) in g-dic.pdf */
        /* Said differently the a and b subindices are the Me subindices on the right hand side of the = in equation 18 in g-dic.pdf */
        for (unsigned short a = 0; a < 4; a++)
        {
            unsigned int nodeA = nodeNumbers(a);
            globalVector(nodeA * 3 + 0) += Fe(3 * a + 0);
            globalVector(nodeA * 3 + 1) += Fe(3 * a + 1);
            globalVector(nodeA * 3 + 2) += Fe(3 * a + 2);
        }
    }
}
