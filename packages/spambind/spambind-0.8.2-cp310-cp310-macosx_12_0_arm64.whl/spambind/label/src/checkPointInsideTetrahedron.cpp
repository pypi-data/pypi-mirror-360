#include <stdio.h>
#include <math.h>
#include <iostream>
#include "checkPointInsideTetrahedron.hpp"
#include <Eigen/Dense>

char checkPointInsideTetrahedron( float Z, float Y, float X, Eigen::Matrix<float, 4, 3> pTetMatrix )
{
    // From: http://steve.hollasch.net/cgindex/geometry/ptintet.html
    Eigen::Matrix4f tetJac;
    Eigen::Matrix4f tmp;
    tetJac(0,0) = pTetMatrix(0,0);
    tetJac(0,1) = pTetMatrix(0,1);
    tetJac(0,2) = pTetMatrix(0,2);
    tetJac(0,3) = 1;
    tetJac(1,0) = pTetMatrix(1,0);
    tetJac(1,1) = pTetMatrix(1,1);
    tetJac(1,2) = pTetMatrix(1,2);
    tetJac(1,3) = 1;
    tetJac(2,0) = pTetMatrix(2,0);
    tetJac(2,1) = pTetMatrix(2,1);
    tetJac(2,2) = pTetMatrix(2,2);
    tetJac(2,3) = 1;
    tetJac(3,0) = pTetMatrix(3,0);
    tetJac(3,1) = pTetMatrix(3,1);
    tetJac(3,2) = pTetMatrix(3,2);
    tetJac(3,3) = 1;

    int det1s;
    det1s = sgn( tetJac.determinant() );

    for ( unsigned char i = 0; i < 4; i++ )
    {
        // replace each line with current point, and check if the determinant is a different sign,
        // if it is we're outside the tetrahedron
        tmp = tetJac;
        tmp(i,0) = Z;
        tmp(i,1) = Y;
        tmp(i,2) = X;

        float det = tmp.determinant();
        // det == 0 is a boundary case, just say it's fine, it may get overwritten by other tets sharing this edge
        // see conditions in: http://steve.hollasch.net/cgindex/geometry/ptintet.html

        // default condition for being properly inside -- unless det == 0 which means that we're on an edge
        if ( det1s != sgn( det ) && det != 0 )
        {
            return 0;
        }
    }
    return 1;
}
