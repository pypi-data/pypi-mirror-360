#include <stdio.h>
#include <math.h>
#include <cmath>
#include <iostream>
#include "filtersToolkit.hpp"

/* 2017-05-23 Emmanuel Roubin */

/* Image sizes, ZYX and images*/
void average(py::array_t<float> imInNumpy, py::array_t<float> imOuNumpy, py::array_t<float> stElNumpy ) {
    py::buffer_info imInBuf = imInNumpy.request();
    py::buffer_info imOuBuf = imOuNumpy.request();
    py::buffer_info stElBuf = stElNumpy.request();

    float *imIn = (float*) imInBuf.ptr;
    float *imOu = (float*) imOuBuf.ptr;
    float *stEl = (float*) stElBuf.ptr;

    size_t nz1 = (size_t) imInBuf.shape[0];
    size_t ny1 = (size_t) imInBuf.shape[1];
    size_t nx1 = (size_t) imInBuf.shape[2];
    size_t nz3 = (size_t) stElBuf.shape[0];
    size_t ny3 = (size_t) stElBuf.shape[1];
    size_t nx3 = (size_t) stElBuf.shape[2];

    // int variable to build index to 1D-images from x,y,z coordinates

    // get the box of the image
    size_t zMin = nz3/2; size_t zMax = nz1-nz3/2;
    size_t yMin = ny3/2; size_t yMax = ny1-ny3/2;
    size_t xMin = nx3/2; size_t xMax = nx1-nx3/2;

    // std::cout << "START C++ moving average" << std::endl;
    // std::cout << "z range: " << zMin << " - " << zMax << std::endl;
    // std::cout << "y range: " << yMin << " - " << yMax << std::endl;
    // std::cout << "x range: " << xMin << " - " << xMax << std::endl;
    // std::cout << "z image size: " << nz1 << std::endl;
    // std::cout << "y image size: " << ny1 << std::endl;
    // std::cout << "x image size: " << nx1 << std::endl;
    // std::cout << "z structuring element size: " << nz3 << std::endl;
    // std::cout << "y structuring element size: " << ny3 << std::endl;
    // std::cout << "x structuring element size: " << nx3 << std::endl;


    /* loop over the structural element to get the sum */
    size_t idSt = 0;
    float stEl_sum = 0.0;
    // std::cout << "z loop from: " << -(int)nz3/2 << " to " << nz3/2 << std::endl;
    // std::cout << "y loop from: " << -(int)ny3/2 << " to " << ny3/2 << std::endl;
    // std::cout << "x loop from: " << -(int)nx3/2 << " to " << nx3/2 << std::endl;
    for( int k=-(int)nz3/2; k<=(int)nz3/2; k++ ) {
      for( int j=-(int)ny3/2; j<=(int)ny3/2; j++ ) {
        for( int i=-(int)nx3/2; i<=(int)nx3/2; i++ ) {
          stEl_sum += stEl[ idSt ];
          idSt++;
        }
      }
    }
    // std::cout << "sum of structural element: " << stEl_sum << std::endl;


    // loop over the image
    for( size_t z=zMin; z<zMax; z++ ) {
      for( size_t y=yMin; y<yMax; y++ ) {
        for( size_t x=xMin; x<xMax; x++ ) {

          // index of output image
          size_t idImOu = z * ny1 * nx1 + y * nx1 + x;

          // tmp voxel values of the output and
          float im_sum = 0.0;
          //float im_sum2 = 0.0;

          // loop over the structural element
          size_t idSt = 0;
          for( int k=-(int)nz3/2; k<=(int)nz3/2; k++ ) {
            for( int j=-(int)ny3/2; j<=(int)ny3/2; j++ ) {
              for( int i=-(int)nx3/2; i<=(int)nx3/2; i++ ) {
                size_t idImIn = ( z+k ) * ny1 * nx1 + ( y+j ) * nx1 + ( x+i );
                im_sum += stEl[ idSt ] * imIn[ idImIn ];
                //im_sum2 += (stEl[ idSt ] * imIn[ idImIn ])*(stEl[ idSt ] * imIn[ idImIn ]);
                idSt++;
              }
            }
          }

          imOu[ idImOu ] = im_sum/stEl_sum;
          //imOu[ idImOu ] = (im_sum2 - im_sum * im_sum/stEl_sum)/stEl_sum;

        }
      }
    }

    // std::cout << "STOP C++ moving average" << std::endl;
  }


  //int  sgn(double d){
  // float eps = 0.0000000000000000000001;
  // return d<-eps?-1:d>eps;
  // }


  void variance(  py::array_t<float> imInNumpy, py::array_t<float> imOuNumpy, py::array_t<float> stElNumpy ) {
      py::buffer_info imInBuf = imInNumpy.request();
      py::buffer_info imOuBuf = imOuNumpy.request();
      py::buffer_info stElBuf = stElNumpy.request();

      float *imIn = (float*) imInBuf.ptr;
      float *imOu = (float*) imOuBuf.ptr;
      float *stEl = (float*) stElBuf.ptr;

      size_t nz1 = (size_t) imInBuf.shape[0];
      size_t ny1 = (size_t) imInBuf.shape[1];
      size_t nx1 = (size_t) imInBuf.shape[2];
      size_t nz3 = (size_t) stElBuf.shape[0];
      size_t ny3 = (size_t) stElBuf.shape[1];
      size_t nx3 = (size_t) stElBuf.shape[2];


      // int variable to build index to 1D-images from x,y,z coordinates

      // get the box of the image
      size_t zMin = nz3/2; size_t zMax = nz1-nz3/2;
      size_t yMin = ny3/2; size_t yMax = ny1-ny3/2;
      size_t xMin = nx3/2; size_t xMax = nx1-nx3/2;

      /* loop over the structural element to get the sum */
      size_t idSt = 0;
      float stEl_sum = 0.0;
      for( int k=-(int)nz3/2; k<=(int)nz3/2; k++ ) {
        for( int j=-(int)ny3/2; j<=(int)ny3/2; j++ ) {
          for( int i=-(int)nx3/2; i<=(int)nx3/2; i++ ) {
            stEl_sum += stEl[ idSt ];
            idSt++;
          }
        }
      }

      // loop over the image
      for( size_t z=zMin; z<zMax; z++ ) {
        for( size_t y=yMin; y<yMax; y++ ) {
          for( size_t x=xMin; x<xMax; x++ ) {

            // index of output image
            size_t idImOu = z * ny1 * nx1 + y * nx1 + x;

            // tmp voxel values of the output and
            float im_sum = 0.0;
            float im_sum2 = 0.0;

            // loop over the structural element
            size_t idSt = 0;
            for( int k=-(int)nz3/2; k<=(int)nz3/2; k++ ) {
              for( int j=-(int)ny3/2; j<=(int)ny3/2; j++ ) {
                for( int i=-(int)nx3/2; i<=(int)nx3/2; i++ ) {
                  size_t idImIn = ( z+k ) * ny1 * nx1 + ( y+j ) * nx1 + ( x+i );
                  im_sum += stEl[ idSt ] * imIn[ idImIn ];
                  im_sum2 += (stEl[ idSt ] * imIn[ idImIn ])*(stEl[ idSt ] * imIn[ idImIn ]);
                  idSt++;
                }
              }
            }

            imOu[ idImOu ] = (im_sum2 - im_sum * im_sum/stEl_sum)/stEl_sum;
          }
        }
      }

      // std::cout << "STOP C++ moving variance" << std::endl;
      // std::cout << "abs(-min) = " << std::abs(-4.62e-07) << std::endl;
      // std::cout << " \n*** that was Olga's 1rst C++ function :) " << std::endl;
    }
