#include <stdio.h>
#include <math.h>
#include <iostream>
#include "labelToolkit.hpp"
#include "checkPointInsideTetrahedron.hpp"
#include <Eigen/Dense>


/* 2016-09-09 -- Emmanuel Roubin and Edward Andò -- Image Labeller for Tetrahedra */

/* This program takes a 3D image, a tetrahedron and a list of points and decides which pixels tetrahedra are inside the tetrahedron */

/* Inputs:
 *    - 3D image
 * Practically speaking, we're going to be passed an already-allocated box, with which
 * will come its dimensions -- after that it's only the centre and the radius */
#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))



void tetPixelLabel(  py::array_t<labels::label> volNumpy,    // image
                     py::array_t<labels::label> connectivityNumpy,  // Connectivity Matrix -- should be nTetrahedra * 4
                     py::array_t<float> nodesNumpy,   // Tetrahedra Points --   should be nNodes      * 3,
                     int numThreads
                   )

{   /* Safety checks */


    py::buffer_info volBuf = volNumpy.request();
    py::buffer_info connectivityBuf = connectivityNumpy.request();
    py::buffer_info nodesBuf = nodesNumpy.request();

    labels::label *vol = (labels::label*) volBuf.ptr;
    labels::label *conne = (labels::label*) connectivityBuf.ptr;
    float *nodes = (float*) nodesBuf.ptr;

    size_t volSizeZ = (size_t) volBuf.shape[0];
    size_t volSizeY = (size_t) volBuf.shape[1];
    size_t volSizeX = (size_t) volBuf.shape[2];

    int conneSize = connectivityBuf.shape[0];

    if ( connectivityBuf.shape[1] != 4 || nodesBuf.shape[1] != 3 )
    {
      printf ("Did not get 4 nodes or 3 coords per node, exiting.\n");
      return;
    }

      /* Looping over all tetrahedra -- future parallelisation should be at this level. */
      #pragma omp parallel for num_threads(numThreads)
      for ( int nTet = 0; nTet < conneSize; nTet++ )
      {
          // std::cout << "ntet " << nTet << std::endl;
          // printf( "\r\tLabel tetrahedra progress: \t%02.1f%%\t", 100.0 * ( (float)(nTet) / (float)conneSize ) );
          /* create pTetArray Connectivity matrix and nodes List */
          Eigen::Matrix<float, 4, 3>         pTetMatrix;
          for ( unsigned char i = 0; i < 4; i++ )
          {
            for ( unsigned char j = 0; j < 3; j++ )
            {
              pTetMatrix(i,j) = nodes[ 3*conne[ 4*nTet+i ] + j ];
    //             printf("\t %i %i %i %i %i \n", i, j, 4*nTet+i, conne[ 4*nTet+i ], 3*conne[ 4*nTet+i ] + j );
            }
          }
    //         std::cout << pTetMatrix << std::endl;

          /* Find limits of the box defined by the extremities of the tetrahedron */
          /* These were doubles before */
          float Zmin = volSizeZ;
          float Ymin = volSizeY;
          float Xmin = volSizeX;
          float Zmax = 0;
          float Ymax = 0;
          float Xmax = 0;

          for ( unsigned char i = 0; i < 4; i++ )
          {
            if ( Zmin > pTetMatrix(i,0) ) Zmin = MAX( pTetMatrix(i,0),      0     );
            if ( Zmax < pTetMatrix(i,0) ) Zmax = MIN( pTetMatrix(i,0), volSizeZ-1 );
            if ( Ymin > pTetMatrix(i,1) ) Ymin = MAX( pTetMatrix(i,1),      0     );
            if ( Ymax < pTetMatrix(i,1) ) Ymax = MIN( pTetMatrix(i,1), volSizeY-1 );
            if ( Xmin > pTetMatrix(i,2) ) Xmin = MAX( pTetMatrix(i,2),      0     );
            if ( Xmax < pTetMatrix(i,2) ) Xmax = MIN( pTetMatrix(i,2), volSizeX-1 );
          }

          /* Loop over the box defined by the extremities of the tetrahedron */
          for ( size_t Z = floor(Zmin); Z <= ceil(Zmax); Z++ )
          {
              for ( size_t Y = floor(Ymin); Y <= ceil(Ymax); Y++ )
              {
                  for ( size_t X = floor(Xmin); X <= ceil(Xmax); X++ )
                  {
                      /* Build index for 3D access */
                      size_t index_i =   Z  * volSizeX * volSizeY   +   Y * volSizeX   +   X;

                      if ( checkPointInsideTetrahedron( (float)Z, (float)Y, (float)X, pTetMatrix ) == 1 )
                      {
                          vol[ index_i ] = nTet;
                      }
                  }
              }
          }
      }  // end of the tet for loop
}
