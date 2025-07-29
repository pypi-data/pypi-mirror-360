#include <stdio.h>
#include <math.h>
#include <iostream>
#include "labelToolkit.hpp"

#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))

/* 2018-05-04 -- Edward Andò
 *  Labelling contacts between particles, with a labelled as interpixel
 *  watershed as input.
 *  This means that we don't have the luxury of having a watershed line
 *  as a vague detectio of contacts.
 */

/* This function takes in:
 *    - labelled 3D image where the object of interest are labelled as non-zero ints
 *    - an empty labelled 3D image to be filled
 *    - a vector of chars nLabels long to hold the coordination number (Z)
 *      for each particle
 *    - a "contact table" which is nLabels by 2*maxCoord number wide
 *      It contains, for each particle, pairs of [ contactingParticleLabel, contactLabel ]
 *    - a "contacting labels" matrix which contains, for each contact, the two particles that are linked
 *
 *  Function Layout:
 *    1 pass through the data in z,y,x
 *      for each non-zero voxel v@(z,y,x), check neighbours:
 *          if neighbour vN is non-zero and not the same label as v:
 *              check first Z(v) contacts to see if a contact between these
 *              two particles has already been labelled.
 *              if yes: save in contactLabel
 *              else:
 *                  Add 1 to Z(v) and Z(vN)
 *                  Add contactLabel into contact table
 *                  Add contactLabel and v, vN to contactingLabels vector
 *              outputVol(z,y,x) = contactLabel
 */

void labelContacts(    py::array_t<labels::label> volLabNumpy,
                       py::array_t<labels::contact> volContactsNumpy,
                       py::array_t<unsigned char> ZNumpy,
                       py::array_t<labels::contact> contactTableNumpy,
                       py::array_t<labels::label> contactingLabelsNumpy
                    )
{

  py::buffer_info volLabBuf = volLabNumpy.request();
  py::buffer_info volContactsBuf = volContactsNumpy.request();
  py::buffer_info ZBuf = ZNumpy.request();
  py::buffer_info contactTableBuf = contactTableNumpy.request();
  py::buffer_info contactingLabelsBuf = contactingLabelsNumpy.request();

  labels::label *volLab = (labels::label*) volLabBuf.ptr;
  labels::contact *volContacts = (labels::contact*) volContactsBuf.ptr;
  unsigned char *Z = (unsigned char*) ZBuf.ptr;
  labels::contact *contactTable = (labels::contact*) contactTableBuf.ptr;
  labels::label *contactingLabels = (labels::label*) contactingLabelsBuf.ptr;



    /* Define current contact number */
    labels::contact C = 1;

    int twoZmax = (int) contactTableBuf.shape[1];
    size_t volSizeZ1u = (size_t) volLabBuf.shape[0];
    size_t volSizeY1u = (size_t) volLabBuf.shape[1];
    size_t volSizeX1u = (size_t) volLabBuf.shape[2];


    /* 1. Start looping over spatial dimension */
    for ( size_t z = 1; z <= volSizeZ1u-2; z++ )
    {
//         printf( "\r\tContacts labelling progress: \t\t%02.1f%%\t\n", 100 * (float)(z+1) / (float)volSizeZ1-1 );

        for ( size_t y = 1; y <= volSizeY1u-2; y++ )
        {
            for ( size_t x = 1; x <= volSizeX1u-2; x++ )
            {
                size_t index_i = z  * volSizeX1u * volSizeY1u   +   y * volSizeX1u   +   x;
                labels::label pixelValue = volLab[ index_i ];

                /* Check that we are not on a label */
                if ( pixelValue != 0 )
                {
                    /* Now check the neighbours -- with +2 in the loop
                     * we are looking at the nearest 6 neighbours.
                     * Change to +1 for 27 neighbours */
                    for ( short dz = -1; dz <= 1; dz=dz+2 )
                    {
                        for ( short dy = -1; dy <= 1; dy=dy+2 )
                        {
                            for ( short dx   = -1; dx <= 1; dx=dx+2 )
                            {
//                                 printf( "%i %i %i\n", dz, dy, dx );
                                size_t index_j = (size_t)(z+dz)  * volSizeX1u * volSizeY1u   +   (size_t)(y+dy) * volSizeX1u   +   (size_t)(x+dx);
                                labels::label neighbourValue = volLab[ index_j ];

                                if ( ( neighbourValue != 0 ) && ( neighbourValue != pixelValue ) )
                                {
                                    /* This will remain zero if we do not recognise this contact */
                                    labels::contact contactLabel = 0;

                                    /* Then there is a contact. See if it is in the contact list,
                                     * check the first Z contact for this grain */
                                    for ( unsigned char contactNumber = 0; contactNumber <= Z[ pixelValue ]; contactNumber++ )
                                    {
                                        if ( contactTable[ twoZmax*pixelValue + 2*contactNumber ] == neighbourValue )
                                        {
                                            contactLabel = contactTable[ twoZmax*pixelValue + 2*contactNumber + 1 ];
                                            break;
                                        }
                                    }

                                    /* Did we find the contact? If not, define a new contact */
                                    if ( contactLabel == 0 )
                                    {
                                        /* Add one to coordination number of both particles if there is space */
                                        if ( ( Z[ pixelValue ] < twoZmax/2 ) && ( Z[ neighbourValue ] < twoZmax/2 ) )
                                        {
                                            /* Add... */
                                            Z[ pixelValue ]++;
                                            Z[ neighbourValue ]++;

                                            /* Now define new contact -- for both particles */
                                            contactTable[ twoZmax*pixelValue     + 2*( Z[ pixelValue     ] - 1 )    ] = neighbourValue;
                                            contactTable[ twoZmax*pixelValue     + 2*( Z[ pixelValue     ] - 1 ) + 1] = C;

                                            contactTable[ twoZmax*neighbourValue + 2*( Z[ neighbourValue ] - 1 )    ] = pixelValue;
                                            contactTable[ twoZmax*neighbourValue + 2*( Z[ neighbourValue ] - 1 ) + 1] = C;

                                            /* Update contactLabel for writing to volume */
                                            contactLabel = C;

                                            /* Write down which two particles, in numerical order, are linked by this labelled contact */
                                            contactingLabels[ (2*C)   ] = MIN( pixelValue, neighbourValue );
                                            contactingLabels[ (2*C)+1 ] = MAX( pixelValue, neighbourValue );

                                            /* Increment contact label */
                                            C++;
                                        }
                                        else
                                        {
                                            /* Too many contacts... not sure how to proceed */
//                                             contactLabel = -1;
                                            contactLabel = 0;
                                        }
                                    }

                                    /* Fill in the contact label into output volume */
                                    volContacts[ index_i ] = contactLabel;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

//     printf( "\n" );
}
