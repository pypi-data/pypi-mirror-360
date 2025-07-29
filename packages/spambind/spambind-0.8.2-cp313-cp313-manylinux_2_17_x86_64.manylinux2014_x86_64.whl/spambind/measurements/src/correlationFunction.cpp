#include <stdio.h>
#include <math.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include "measurementsToolkit.hpp"

/* 2017-03-10 -- Emmanuel Roubin and Edward Andò -- Measurement of a correlation function on a greyscale 3D image  */

/* Inputs:
*    - 3D image
*    - Some limits in space, time, mesh of points
*
* Outputs:
*    - Correlation function Correlation Function value as a function of distance
*
* Step 1: Calculate box size from halfWindowSize and precompute unique, sorted 1D vector of all possible distances
*         within the box.
*/
#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))


void computeCorrelationFunction(py::array_t<float> volNumpy, py::array_t<double> outputNumpy, unsigned int stepCentre, unsigned int nthreads)
{

  py::buffer_info volBuf = volNumpy.request();
  py::buffer_info outputBuf = outputNumpy.request();

  float *vol = (float*) volBuf.ptr;
  double *output = (double*) outputBuf.ptr;

  unsigned int outputSize = outputBuf.shape[0];
  size_t volSizeZ = (size_t) volBuf.shape[0];
  size_t volSizeY = (size_t) volBuf.shape[1];
  size_t volSizeX = (size_t) volBuf.shape[2];

  //  The square root of the number of points asked for is a bit less
  //    than the number of unique distances
  unsigned short halfWindowSizeGuess   = pow( outputSize, 0.5 );
  std::vector<float> distances;

  // ===================================================
  // Loop until the size of the distances vector is bigger than or equal to our output size
  // ===================================================
  //std::cout << ".\t.\t Distances" << std::endl;
  while ( distances.size() <= outputSize ) {
    halfWindowSizeGuess++;
    //         std::cout << "Half window size = " << halfWindowSizeGuess << std::endl;

    // ===================================================
    // Go through measuring distances in a top corner of the box
    // ===================================================
    // TODO: Properly traverse 1/8th of the positive 1/8 of the box -- these should be the only unique distances
    distances.resize( pow( ( halfWindowSizeGuess + 1 ), 3 ) );

    unsigned int count = 0;
    /* Loop over positive 1/8th of the box */
    for ( unsigned short z = 0; z <= MIN( halfWindowSizeGuess, volSizeZ-1 ); z++ )
    {
      for ( unsigned short y = 0; y <= MIN( halfWindowSizeGuess, volSizeY-1 ); y++ )
      {
        for ( unsigned short x = 0; x <= MIN( halfWindowSizeGuess, volSizeX-1 ); x++ )
        {
          float distance = pow( z*z + y*y + x*x, 0.5 );
          if ( distance <= halfWindowSizeGuess )
          {
            distances[ count++ ] = distance;
            //                     std::cout << distances[ count-1 ] << std::endl;
          }
        }
      }
    }

    // ===================================================
    // Sorte distances and keep only unique ones
    // ===================================================
    // Unique vector sorter from: http://en.cppreference.com/w/cpp/algorithm/unique
    std::sort( distances.begin(), distances.end()); // 1 1 2 2 3 3 3 4 4 5 5 6 7
    auto last = std::unique( distances.begin(), distances.end());
    distances.erase( last, distances.end());
  }


  std::vector< unsigned short > halfWindowSize(3);
  halfWindowSize[0] = MIN( halfWindowSizeGuess, volSizeZ-1 );
  halfWindowSize[1] = MIN( halfWindowSizeGuess, volSizeY-1 );
  halfWindowSize[2] = MIN( halfWindowSizeGuess, volSizeX-1 );
  unsigned short maxHalfWindowSize = MAX( MAX( halfWindowSize[0], halfWindowSize[1] ), halfWindowSize[2] );

  // Recompute this from above
  std::vector< unsigned short > totalWindowSize(3);
  totalWindowSize[0] = 2*halfWindowSize[0]+1;
  totalWindowSize[1] = 2*halfWindowSize[1]+1;
  totalWindowSize[2] = 2*halfWindowSize[2]+1;

  std::vector< std::vector< std::vector< int > > > distanceLabels (totalWindowSize[0], std::vector<std::vector< int > >(totalWindowSize[1], std::vector< int >(totalWindowSize[2])));


  //     for (float i : distances)
  //       std::cout << i << " ";
  //     std::cout << "\n";
  //     std::cout << distances.size() << std::endl;

  // ===================================================
  // Build labelled window
  // ===================================================
  //std::cout << ".\t.\t Labels" << std::endl;
  #pragma omp parallel for num_threads(nthreads)
  for ( unsigned short z = 0; z < totalWindowSize[0]; z++ )
  {
    for ( unsigned short y = 0; y < totalWindowSize[1]; y++ )
    {
      for ( unsigned short x = 0; x < totalWindowSize[2]; x++ )
      {
        float distance = pow( ( z - halfWindowSize[0] )*( z - halfWindowSize[0] ) + ( y - halfWindowSize[1] )*( y - halfWindowSize[1] ) + ( x - halfWindowSize[2] )*( x - halfWindowSize[2] ), 0.5 );

        if ( distance <= maxHalfWindowSize )
        {
          std::vector<float>::iterator iter = std::find( distances.begin(), distances.end(), distance);
          unsigned int index = std::distance( distances.begin(), iter );
          #pragma omp critical
          distanceLabels[z][y][x] = index;
        } else {
          #pragma omp critical
          distanceLabels[z][y][x] = -1;
        }
      }
    }
  }

  // ===================================================
  // Loop image to compute covariance
  // ===================================================


  std::vector<double> covGrey( distances.size() );
  std::vector<unsigned int> nPoints( distances.size() );

  // move zyxCentre about
  //std::cout << ".\t.\t Covariance" << std::endl;
  //    unsigned short zCentre, yCentre, xCentre;
  unsigned short volSizeZminusWin = volSizeZ-halfWindowSize[0];
  unsigned short volSizeYminusWin = volSizeY-halfWindowSize[1];
  unsigned short volSizeXminusWin = volSizeX-halfWindowSize[2];
  #pragma omp parallel for num_threads(nthreads)
  for ( unsigned short zCentre = halfWindowSize[0]; zCentre < volSizeZminusWin; zCentre+=stepCentre )
  {
    //if ( volSizeZ > 1 ) printf ( "Compute Correlation Progress: %2.1f%%\n", 100 * ( zCentre - halfWindowSize[0] ) / (float)( volSizeZ - 2*halfWindowSize[0] ) );
    for ( unsigned short yCentre = halfWindowSize[1]; yCentre < volSizeYminusWin; yCentre+=stepCentre )
    {
      //if ( volSizeZ == 1 ) printf ( "Compute Correlation Progress: %2.1f%%\n", 100 * ( yCentre - halfWindowSize[1] ) / (float)( volSizeY - 2*halfWindowSize[1] ) );
      for ( unsigned short xCentre = halfWindowSize[2]; xCentre < volSizeXminusWin; xCentre+=stepCentre )
      {

        unsigned short zBot = MAX( zCentre-halfWindowSize[0],0 );
        unsigned short yBot = MAX( yCentre-halfWindowSize[1],0 );
        unsigned short xBot = MAX( xCentre-halfWindowSize[2],0 );
        unsigned short zTop = MIN( zCentre+halfWindowSize[0],volSizeZ-1 );
        unsigned short yTop = MIN( yCentre+halfWindowSize[1],volSizeY-1 );
        unsigned short xTop = MIN( xCentre+halfWindowSize[2],volSizeX-1 );

        // Get grey value of our current voxel of interest
        unsigned long voxelIndex =   zCentre  * volSizeX * volSizeY   +   yCentre * volSizeX   +  xCentre;
        float greyCentre = vol[ voxelIndex ];

        // ===================================================
        // Loop over window for this current centre, updating nPoints, covGrey
        // ===================================================
        for ( unsigned short z = zBot; z <= zTop; z++ )
        {
          for ( unsigned short y = yBot; y <= yTop; y++ )
          {
            //                         std::cout << z << " " << y << std::endl;
            for ( unsigned short x = xBot; x <= xTop; x++ )
            {
              int distanceLabel = distanceLabels[z-zBot][y-yBot][x-xBot];


              // Make sure we're in the sphere
              if ( distanceLabel != -1 )
              {
                nPoints[ distanceLabel ] += 1;

                // Build index for 3D access
                unsigned long imageIndex =   z * volSizeX * volSizeY   +   y * volSizeX   +  x;
                #pragma omp atomic
                covGrey[ distanceLabel ] += vol[ imageIndex ]*greyCentre;
              }
            }
          }
        }
      }
    }
  }

  // Exit loop moving zxyCentre

  // ===================================================
  // Compute actual covariance, update output array
  // ===================================================
  for ( unsigned short i=0; i<distances.size(); i++ )
  {
    // Fill in output only as far as we've been given
    if ( i < outputSize )
    {
      output[ i*2+1 ] = covGrey[ i ] / (float)nPoints[i];
      output[ i*2   ] = distances[ i ];
    }
  }

}
