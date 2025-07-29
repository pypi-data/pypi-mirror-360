/*  Copyright 2016 Edward Ando', Felix Bertoni, Alessandro Tengattini

 *  This file is part of kalisphera_c.

    kalisphera_c is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    kalisphera_c is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with kalisphera_c.  If not, see <http://www.gnu.org/licenses/>
*/

/* FILE kalisphera_c.c BEGIN */

#include <stdio.h>
#include <math.h>
#include "kalispheraToolkit.hpp"
#include "kalisphera_ext.hpp"

#define M_PI       3.14159265358979323846   // pi


/* 2015-09-29 -- Edward Andò -- Attempt to pass kalispherea into C */
/* all comment marked (f) are done by FelixBertoni */

/* For the moment the objective is just the root of the kalisphera code
 * i.e., without the gaussian smoothing output */

/* Inputs:
 *   (all the units are in pixels)
 * Volume (box) size ( 3 scalars ) -- ideally passed as a tuple or list
 *  (f)ideally passed as a [TYPE]*, result of a C "malloc" ?
 * Centre of sphere with respect to the box  -- ideally passed as a tuple or list
 * Radius of the sphere -- scalar */

/* Practically speaking, we're going to be passed an already-allocated box, with which
 * will come its dimensions -- after that it's only the centre and the radius */


//(f) all integers coords will have to be unsigned long or long for time where img > 2kMvx will be done
//### OPTIMISATION : replace the while for the NP_wheres python by precreated vars?
//### OPTIMISATION : dont forget to set abs and sqrt and pow "inline" when in C++, or use C macros?
//### OPTIMISATION : prepare casts for integers to float for x, y and z to avoid doing it a lot ?

/* ############################################## */
/* ######## MAIN FUNCIONS IMPLEMENTATION ######## */
/* ############################################## */
/* following functions are the main body of the code
 * like iterations on each voxels and caseCubeX selection */
/* ############################################## */

float kalisphera(  py::array_t<real_t> volNumpy,
                   py::array_t<real_t> sphereCenterCoordsNumpy,
                   real_t radius)
{

  py::buffer_info volBuf = volNumpy.request();
  py::buffer_info sphereCenterCoordsBuf = sphereCenterCoordsNumpy.request();

  real_t *vol = (real_t*) volBuf.ptr;
  real_t *sphereCenterCoords = (real_t*) sphereCenterCoordsBuf.ptr;

  int volSizeZ = (int) volBuf.shape[0];
  int volSizeY = (int) volBuf.shape[1];
  int volSizeX = (int) volBuf.shape[2];


    /* "Trying to reduce the number of pixels to treat.
     *  On a first, rough approximation, we're going to only study pixels which are
     *  within a cube one pixel greater than the sphere, and a cube within the sphere
     *  Let's call this the PV (partial volume) box" - Edward */

    //sphereCenterCoords replacing Cube_coords
    real_t sphereCenterZ = sphereCenterCoords[0]+0.5;
    real_t sphereCenterY = sphereCenterCoords[1]+0.5;
    real_t sphereCenterX = sphereCenterCoords[2]+0.5;
    // loop variables for 3D search range

    sphere_ts sphere = {radius,
                        {sphereCenterX, sphereCenterY, sphereCenterZ}
                       };

    int sphereCenterZ_i, sphereCenterY_i, sphereCenterX_i, radius_i;
    // Get rounded sphere centres and radius
    sphereCenterZ_i = round( sphereCenterZ );
    sphereCenterY_i = round( sphereCenterY );
    sphereCenterX_i = round( sphereCenterX );
    radius_i  = ceil( radius  );
    /*
    printf( "Vol size is %ix%ix%i\nCenter: %f - %f - %f\n", volSizeZ, volSizeY, volSizeX, sphereCenterZ, sphereCenterY, sphereCenterX );
    printf( "Center (rounded): %i - %i - %i\n", sphereCenterZ_i, sphereCenterY_i, sphereCenterX_i );
    */

    // PV Limits : select a cube larger thant the cube containing the sphere
    int   pvLimits_i = 1;

    real_t controlSum = 0.0; //this var is the sum of all set voxel volume to calculate error on total sum

    //creation of the iteration structure
    real_t voxelCoords[3] = {0.0}; //coordinates of current voxel

    //iteration intervals
    int zBegin, zEnd;
    int yBegin, yEnd;
    int xBegin, xEnd;

    //if the interval goes out of grid, reduce it
    zBegin = sphereCenterZ_i - radius_i - pvLimits_i;
    if (zBegin < 0) zBegin = 0;

    zEnd = sphereCenterZ_i + radius_i + pvLimits_i;
    if (zEnd > volSizeZ) zEnd = volSizeZ-1;

    yBegin = sphereCenterY_i - radius_i - pvLimits_i;
    if (yBegin < 0) yBegin = 0;

    yEnd = sphereCenterY_i + radius_i + pvLimits_i;
    if (yEnd > volSizeY) yEnd = volSizeY-1;

    xBegin = sphereCenterX_i - radius_i - pvLimits_i;
    if (xBegin < 0) xBegin = 0;

    xEnd = sphereCenterX_i + radius_i + pvLimits_i;
    if (xEnd > volSizeX) xEnd = volSizeX-1;

    //linear access index
    // max val = size_x*size_y*size_z
    // on a 1500x2000x1000px 3D img, max > 2 100 000 000
    // So long type needed
    long index_i;
    real_t voxVal; //value of the voxel
    int z, y, x; //3D iteration indexes
    //for each voxel in the iteration interval
    //iteration z-y-x for better cache use
    for (z = zBegin; z <= zEnd; z++)
    {
      voxelCoords[2] = (real_t)z; //setting z coord of the voxel
      for (y = yBegin; y <= yEnd; y++)
      {
        voxelCoords[1] = (real_t)y; //setting y coord of the voxel
        for (x = xBegin; x <= xEnd; x++)
        {
          voxelCoords[0] = (real_t)x; //setting x coord of the voxel

          //calculating the linear index (need to use succession of additions to opimise?)
          index_i = x + y*volSizeX + z*volSizeY*volSizeX;
          //setting value of current voxel
          voxVal = voxelValue(voxelCoords, &sphere);
          controlSum += voxVal;
          vol[index_i] = voxVal;
        }
      }
    }

    //error returned : difference between real volume and expected volume
    //expected volume = 4/3xPIx(R^3)
    return controlSum - (4.0/3.0*M_PI*pow(radius, 3));
}


real_t voxelValByForce(real_t voxelCoords[3], sphere_ts* sphere, int partCount, int isUpperValue){
   ///!\ Following function isn't optimised !
   //calculation of the size of a subvoxel
   real_t subSize = 1.0/((real_t)partCount);
   real_t subCoords[3];

   int x, y, z;
   int included;
   //sum of all voxels
   real_t sum = 0.0;

   for (z = 0; z < partCount; z++){
     subCoords[2] = voxelCoords[2] + ((real_t)z)*subSize;
     for (y = 0; y < partCount; y++){
       subCoords[1] = voxelCoords[1] + ((real_t)y)*subSize;
       for (x = 0; x < partCount; x++){
          subCoords[0] = voxelCoords[0] + ((real_t)x)*subSize;

          if ((included = voxelInSphere(subCoords, sphere, subSize))){

            //volume of a subvoxel inside sphere is 1/nbsubs
             if (included == -1){sum+=pow(subSize,3);}
          } else {
            if (isUpperValue){sum+=pow(subSize,3);}
          }
       }
     }
   }
   //total value
   return sum;
}

real_t voxelValue(real_t voxelCoords[3], sphere_ts* sphere){

          /* "Inner box should be at (R/2)-1 -- at the moment this case will be handled by the voxel
           * case where all eight corners intersect the sphere. For big spheres we will save time by
           * excluding this box" - Edward */


          int included = 0; //represents if voxel is in the sphere(-1), out the sphere(1), or intersecting the sphere (0)
          if ((included = voxelInSphere (voxelCoords, sphere, 1.0))) //lets look if voxel inside/outside or intersection of the sphere
          {
            /* if we're sufficiently far away... */
            if (included == 1){return 0.0;}
             /* if we're far inside */
            else {return 1.0;}
          }
          else
          {
              /* partial volume calculation */

              int voxelCorners_i = 0; //corners in counter
              int voxelCorners_a[2][2][2]; //corner in matrix
              int cornerZ_i, cornerY_i, cornerX_i; //iteration indexes

              for (cornerZ_i = 0; cornerZ_i < 2; cornerZ_i++){
                  for (cornerY_i = 0; cornerY_i < 2; cornerY_i++){
                      for (cornerX_i = 0; cornerX_i < 2; cornerX_i++){
                          //if corner in sphere
                          if ((pow(inSphereRef(voxelCoords, 0, sphere)+(real_t)cornerX_i,2)
                              +pow(inSphereRef(voxelCoords, 1, sphere)+(real_t)cornerY_i,2)
                              +pow(inSphereRef(voxelCoords, 2, sphere)+(real_t)cornerZ_i,2)
                              ) <= pow(sphere->radius,2)){
                            voxelCorners_a[cornerX_i][cornerY_i][cornerZ_i] = 1;
                            voxelCorners_i++;
                          }else {
                            voxelCorners_a[cornerX_i][cornerY_i][cornerZ_i] = 0;
                          }
                      }
                  }
              }

              return voxelIntegralCase(voxelCoords, sphere, voxelCorners_a, voxelCorners_i);

          }

}


real_t voxelIntegralCase(real_t voxelCoords[3], sphere_ts* sphere, int voxelCorners[2][2][2], int voxelCornersInNumber){
//#REMOVE here for release

              //checking wich casecube we have to use
              switch ( voxelCornersInNumber ) //OPTIMISATION : replace switch by ifs, in decreasing order of use
              {
                case 0:
                  //no corner in sphere
                  return caseCube0(voxelCoords, sphere);
                  break;

                case 1:
                  //1 corner in sphere
                  return caseCube1(voxelCoords, voxelCorners, sphere);
                  break;

                case 2:
                  //2 corners in sphere
                  return caseCube2(voxelCoords, voxelCorners, sphere);
                  break;

                case 3:
                  //3 corners in sphere
                  return caseCube3(voxelCoords, voxelCorners, sphere);
                  break;

                case 4:
                  //4 corners in sphere
                  return caseCube4(voxelCoords, voxelCorners, sphere);
                  break;

                case 5:
                  //5 corners in sphere
                  return caseCube5(voxelCoords, voxelCorners, sphere);
                  break;

                case 6:
                  //6 corners in sphere
                  return caseCube6(voxelCoords, voxelCorners, sphere);
                  break;

                case 7:
                  //7 corners in sphere
                  return caseCube7(voxelCoords, voxelCorners, sphere);
                  break;

                case 8:
                  // All for corners are inside: so the whole voxel is at 1.
                  //should no be passed through in normal conditions
                  return 1.0;
                  break;

                default:
                  //sould not be passed through in normal condition
                  return 999.999;
                  break;
              }

}

/* ############################################### */
/* ######## MAIN FUNCTIONS IMPLEMENT ENDS ######## */
/* ############################################### */

/* ################################################ */
/* ######## UTILS FUNCTIONS IMPLEMENTATION ######## */
/* ################################################ */

real_t distance( real_t z1, real_t y1, real_t x1, real_t z2, real_t y2, real_t x2 )
{
  return sqrt( pow( z1 - z2 , 2 ) + pow( y1 - y2, 2 ) + pow( x1 - x2, 2 ) ); //just a distance calculation
}

int cornerCountSurfaceX(int xI, int D[2][2][2])
{
    return D[xI][0][0] + D[xI][0][1] + D[xI][1][0] + D[xI][1][1];  //just a count
}

int cornerCountSurfaceY(int yI, int D[2][2][2])
{
    return D[0][yI][0] + D[0][yI][1] + D[1][yI][0] + D[1][yI][1];  //just a count
}

int cornerCountSurfaceZ(int zI, int D[2][2][2])
{
    return D[0][0][zI] + D[0][1][zI] + D[1][0][zI] + D[1][1][zI];  //just a count
}

//return 0 if collision,
// 1 if no collision,
// -1 if included in sphere
// testing by projection
int voxelInSphere(real_t voxelCoords[3], sphere_ts* sphere, real_t voxSize){


    real_t xNear;
    real_t yNear;
    real_t zNear;
    //OPTIMISATION : comparison of distances with substractions ?
    //x NEAR
    //looking for the point of the voxel nearest of the sphere center
    if (voxelCoords[0] >= sphere->centerCoords[0])
         xNear = voxelCoords[0];
    else if (voxelCoords[0]+voxSize <= sphere->centerCoords[0])
         xNear = voxelCoords[0]+voxSize;
    else xNear = sphere->centerCoords[0];

    if (voxelCoords[1] >= sphere->centerCoords[1])
         yNear = voxelCoords[1];
    else if (voxelCoords[1]+voxSize <= sphere->centerCoords[1])
         yNear = voxelCoords[1]+voxSize;
    else yNear = sphere->centerCoords[1];

    if (voxelCoords[2] >= sphere->centerCoords[2])
         zNear = voxelCoords[2];
    else if (voxelCoords[2]+voxSize <= sphere->centerCoords[2])
         zNear = voxelCoords[2]+voxSize;
    else zNear = sphere->centerCoords[2];


    //check if collision
    //distance (near -> center) < R ?
    if (distance(zNear, yNear, xNear, sphere->centerCoords[2], sphere->centerCoords[1], sphere->centerCoords[0])
        < sphere->radius){

      //looking for the point of the voxel the farther from the sphere
        real_t xFar, yFar, zFar;
        //if incuded, all voxel in sphere
        if (voxelCoords[0] > sphere->centerCoords[0])
            xFar = voxelCoords[0]+voxSize;
        else if (voxelCoords[0] +voxSize < sphere->centerCoords[0])
            xFar = voxelCoords[0];
        else {
          if (fabs(voxelCoords[0] - sphere->centerCoords[0]) < fabs(voxelCoords[0] +voxSize - sphere->centerCoords[0]))
              xFar = voxelCoords[0]+voxSize;
          else xFar = voxelCoords[0];
        }

        if (voxelCoords[1] > sphere->centerCoords[1])
            yFar = voxelCoords[1]+voxSize;
        else if (voxelCoords[1] + voxSize < sphere->centerCoords[1])
            yFar = voxelCoords[1];
        else {
          if (fabs(voxelCoords[1] - sphere->centerCoords[1]) <fabs(voxelCoords[1] + voxSize - sphere->centerCoords[1]))
              yFar = voxelCoords[1]+ voxSize;
          else yFar = voxelCoords[1];
        }

        if (voxelCoords[2] > sphere->centerCoords[2])
            zFar = voxelCoords[2]+voxSize;
        else if (voxelCoords[2] + voxSize < sphere->centerCoords[2])
            zFar = voxelCoords[2];
        else {
          if (fabs(voxelCoords[2] - sphere->centerCoords[2]) < fabs(voxelCoords[2] + voxSize - sphere->centerCoords[2]))
              zFar = voxelCoords[2] + voxSize;
          else zFar = voxelCoords[2];
        }
         //check if inclusion
         //distance (far -> center) < R ?
        if (distance(zFar, yFar, xFar, sphere->centerCoords[2], sphere->centerCoords[1], sphere->centerCoords[0])
          < sphere->radius)
          return -1; //voxel in the sphere

        return 0; //voxel intersecting the sphere
    }

    return 1; //voxel out the sphere
}


//see .h for description
real_t inSphereRef(real_t voxelCoords[3], int direction,  sphere_ts* sphere){
  return voxelCoords[direction] - sphere->centerCoords[direction]; //no comment
}
//see .h for description
real_t nextSphereRef(real_t voxelCoords[3], int direction,  sphere_ts* sphere){
    return voxelCoords[direction] - sphere->centerCoords[direction] + 1.0; //no comment +1
}

/* ############################################### */
/* ####### UTILS FUNCTIONS IMPLEMENT ENDS ######## */
/* ############################################### */

/* ###################################################### */
/* ######## INTEGRATION FUNCTIONS IMPLEMENTATION ######## */
/* ###################################################### */

/*here we have the "simple" integration functions */

real_t Int_1 (real_t X, real_t R){
  //Int_(0)^(X) {(R^2-x^2)*pi/4} dx= pi/4 [R^2*x-x^3/3]_(0)^(X)
  return M_PI/4.0*(pow(R,2)*X-pow(X,3)/3);
}

real_t Int_2 (real_t X, real_t Y, real_t R){
  real_t SQRT=sqrt(fabs(pow(R,2)-pow(Y,2)-pow(X,2)));
  //Int_(0)^(X) {sqrt(R^2-Y^2-x^2)}dx= 1/2[x*sqrt(R^2-Y^2-x^2)+(R^2-Y^2)*arctan(x/(sqrt(R^2-Y^2-x^2)))]_(0)^(X)
  return (1.0/2.0)*(X*SQRT+(pow(R,2)-pow(Y,2))*atan2(X,SQRT));
}

real_t Int_3 (real_t X, real_t R){
  real_t SQRT;
  real_t sum = pow(R,2)-pow(X,2);

  if (sum <= 0.0) {SQRT = 0;}
  else {SQRT=sqrt(sum);}

  return 1.0/2.0*(X*SQRT+(pow(R,2)*atan2(X,SQRT)));
}

real_t Int_4 (real_t X, real_t Y, real_t R){
  real_t SQRT;
  real_t sum = pow(R,2)-pow(Y,2)-pow(X,2);

  if (sum <= 0.0) {SQRT = 0;}
  else {SQRT=sqrt(sum);}

  return 1.0/12.0*
    (X*Y*SQRT+ Y*
      (3*pow(R,2)+pow(Y,2))
      *atan2(X,SQRT)
      +(6*pow(R,2)*X-2*pow(X,3))*atan2(Y,SQRT)
        -4*pow(R,3)*atan2((X*Y),(R*SQRT)));

}

real_t Int_5 (real_t X, real_t Y, real_t R){
  //#to solve issues with 'Indeterminate form' of atan2((0+)/0)
  if (Y==0.0)Y+= ZERO_PLUS_CONST;
  //folowing lines are equivalent to (SQRT=sqrt(...)).real in python
  real_t SQRT;
  real_t sum = pow(R,2)-pow(Y,2)-pow(X,2);
  if (sum <= 0.0) {SQRT = 0;}
  else {SQRT=sqrt(sum);}

  return 1.0/12.0*(-X*Y*SQRT+6*pow(R,2)*X*atan2((SQRT),Y)
  -Y*(3*pow(R,2)+pow(Y,2))*atan2(X,(SQRT))-2*pow(X,3)*atan2((SQRT),Y)
  +4*pow(R,3)*atan2(X*Y,(R*SQRT)));
}

/* Following are the Group Integration functions */

real_t integralGroup1(real_t Xm, real_t R){
  return 4*(Int_1(R,R)-Int_1(Xm,R));
}

real_t integralGroup2(real_t Xm, real_t XM, real_t Ym, real_t R){
  return 2*(Int_1(XM,R)-Int_1(Xm,R))
        -2*(Int_2(XM,Ym,R)-Int_2(Xm,Ym,R))
        -2*(Int_4(XM,Ym,R)-Int_4(Xm,Ym,R));
}

real_t integralGroup3(real_t Xm, real_t XM, real_t Ym, real_t Zm, real_t R){
  return -0.5*Zm*(Int_2(XM,Zm,R)-Int_2(Xm,Zm,R))
  +(Int_5(XM,Zm,R)-Int_5(Xm,Zm,R))-0.5*Ym*(Int_2(XM,Ym,R)-Int_2(Xm,Ym,R))
  -(Int_4(XM,Ym,R)-Int_4(Xm,Ym,R))+Zm*Ym*XM-Zm*Ym*Xm;
}

real_t integralGroup4(real_t Xm, real_t XM, real_t Ym, real_t YM, real_t Zm, real_t R){
  real_t a = 0.5*YM*(Int_2(XM,YM,R)-Int_2(Xm,YM,R));
  real_t b = 0.5*Ym*(Int_2(XM,Ym,R)-Int_2(Xm,Ym,R));
  real_t c = (Int_4(XM,YM,R)-Int_4(Xm,YM,R));
  real_t d = (Int_4(XM,Ym,R)-Int_4(Xm,Ym,R));
  real_t e = (Zm*YM*XM-Zm*YM*Xm);
  real_t f = (Zm*Ym*XM-Zm*Ym*Xm);
  return a - b + c - d - e + f;
}

/* ###################################################### */
/* ######## INTEGRATION FUNCTIONS IMPLEMENT ENDS ######## */
/* ###################################################### */


/* #################################################### */
/* ######## CASE CUBE FUNCTIONS IMPLEMENTATION ######## */
/* #################################################### */
/*
 FOR ALL FOLLOWING CASES :
 function do the same row of actions
    => analysing corners in sphere (voxelCorners param) to find integation direction
    => computing integration interval
    => computing integral
    => returning value

    sometimes, np.where from python is replaced by research optimised as pre-declared variables with impossible values

 */


real_t caseCube0 (real_t voxelCoords[3], sphere_ts* sphere)
{

  int otherFirst = -1; //position et and count by impossible value
  int otherSecond = -1;
  int direction;
  //OPTIMISATION : max 2, on met un While ? => il y a mult
  for (direction = 0; direction < 3 && otherSecond == -1; direction++)
  {
    if (inSphereRef(voxelCoords, direction, sphere)*nextSphereRef(voxelCoords, direction, sphere)>0.0)
    {
      if (otherFirst == -1) {otherFirst = direction;}
      else {otherSecond = direction;}
    }
  }
 //python : if len(onthezero[np.where(onthezero==0)])==2:
  if (otherSecond == -1){
    real_t Xm = fmin(fabs(inSphereRef(voxelCoords, otherFirst, sphere)),fabs(nextSphereRef(voxelCoords, otherFirst, sphere)));
    return integralGroup1(Xm,sphere->radius);
  } else {
    //TOTEST
    real_t bottom_cube_Lim_1=fmin(fabs(inSphereRef(voxelCoords, otherFirst, sphere)),fabs(nextSphereRef(voxelCoords, otherFirst, sphere)));
    real_t bottom_cube_Lim_2=fmin(fabs(inSphereRef(voxelCoords, otherSecond, sphere)),fabs(nextSphereRef(voxelCoords, otherSecond, sphere)));
    real_t bottom_max=fmax(bottom_cube_Lim_1,bottom_cube_Lim_2);
    real_t bottom_min=fmin(bottom_cube_Lim_1,bottom_cube_Lim_2);

    real_t XM;
    real_t sum = pow(sphere->radius,2)-pow(bottom_min,2);
    if (sum < 0.0){XM = 0.0;}
    else {XM=sqrt(sum);}

    return fabs(integralGroup2(bottom_max,XM,bottom_min,sphere->radius));
  }
}

real_t caseCube1 (real_t voxelCoords[3], int voxelCorners[2][2][2], sphere_ts* sphere)
{
  //find XYZ coords of that corner
  int found = 0;
  int x_i;
  int y_i;
  int z_i = 0;

  //setting x, y and z to the value of the coords of the corner in
  while (z_i < 2 && !found){
    y_i = 0;
    while (y_i < 2 && !found){
      x_i = 0;
      while (x_i < 2 && !found){
        found = voxelCorners[x_i][y_i][z_i];
        x_i++;
      }
      y_i++;
    }
    z_i++;
  }
  x_i--; y_i--; z_i--;

  real_t Xm = fabs(inSphereRef(voxelCoords, 0, sphere)+x_i);
  real_t Ym = fabs(inSphereRef(voxelCoords, 1, sphere)+y_i);
  real_t Zm = fabs(inSphereRef(voxelCoords, 2, sphere)+z_i);

  real_t sum = pow(sphere->radius, 2)-pow(Zm, 2)-pow(Ym, 2);
  real_t XM;
  //OPTIMISATION : remove if statement?
  if (sum < 0.0){XM = 0;}
  else {XM = sqrt(sum);}
  return integralGroup3(Xm, XM, Ym, Zm, sphere->radius);
}

/*return partial volume value in case 2
 * x : x coord of voxel
 * y : y coord of voxel
 * z : z coord of voxel
 * voxelCorners : represents the corners of the voxel in or not the sphere
 * R : radius of the sphere
 */
real_t caseCube2 (real_t voxelCoords[3], int voxelCorners[2][2][2], sphere_ts* sphere)
{
    int dirEqual[3] = {1,1,1};


    int x_i;
    int y_i;
    int z_i = 0;
    int cornerPosition[2][3];
    int cornerRank = 0;

    //looking for the corners
     while (cornerRank < 2 && z_i < 2){
      y_i = 0;
      while (cornerRank < 2 && y_i < 2){
        x_i = 0;
        while (cornerRank < 2 && x_i < 2){
           if (voxelCorners[x_i][y_i][z_i] == 1){
              cornerPosition[cornerRank][0] = x_i;
              cornerPosition[cornerRank][1] = y_i;
              cornerPosition[cornerRank][2] = z_i;
              cornerRank++;
           }
           x_i++;
        }
        y_i++;
      }
      z_i++;
    }

    int direction;
    for (direction = 0; direction < 3; direction++){
        if (cornerPosition[0][direction] != cornerPosition[1][direction]){
          dirEqual[direction] = 0;
          break;
        }
    }
    int dirEq1 = 0;
    int dirEq2 = 0;
    int xDir = 0;

   //direction of the integration
    if (dirEqual[0] == 0){
        xDir = 0;
        dirEq1 = 1;
        dirEq2 = 2;
   } else {
     dirEq1 = 0;
     if (dirEqual[1] == 0){
        xDir = 1; //1
        dirEq2 = 2; //2
     } else {
        dirEq2 = 1; //1
        xDir = 2;  //2
     }
   }

  real_t Zm = fmin(fabs(inSphereRef(voxelCoords, dirEq1, sphere)),fabs(nextSphereRef(voxelCoords, dirEq1, sphere)));
  real_t Ym = fmin(fabs(inSphereRef(voxelCoords, dirEq2, sphere)),fabs(nextSphereRef(voxelCoords, dirEq2, sphere)));
  real_t Xm = fmin(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));
  real_t XM = fmax(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));


  return fabs(integralGroup3(Xm, XM, Ym, Zm, sphere->radius));
}

real_t caseCube3 (real_t voxelCoords[3], int voxelCorners[2][2][2], sphere_ts* sphere)
{

    int basePlane[3] = {0};
    int cornerPosition[3][3];

    int x_i;
    int y_i;
    int z_i = 0;
    int cornerRank = 0;

    //seeking the three corners in
    //OPTIMISATION : would a "for" parse better?
     while (cornerRank < 3 && z_i < 2){
      y_i = 0;
      while (cornerRank < 3 && y_i < 2){
        x_i = 0;
        while (cornerRank < 3 && x_i < 2){
           if (voxelCorners[x_i][y_i][z_i] == 1){
              cornerPosition[cornerRank][0] = x_i;
              cornerPosition[cornerRank][1] = y_i;
              cornerPosition[cornerRank][2] = z_i;
              cornerRank++;
           }
           x_i++;
        }
        y_i++;
      }
      z_i++;
    }
    int direction;
    for (direction = 0; direction < 3; direction++){
          if (cornerPosition[0][direction] == cornerPosition[1][direction]
            && cornerPosition[0][direction] == cornerPosition[2][direction])
            {
              basePlane[direction] = 1;
            }
    }




   int xDir;
   int yDir;
   int zDir;
   //direction of integral
    if (basePlane[0] == 1){

        zDir = 0;
        xDir = 1;
        yDir = 2;
   } else {

     xDir = 0;
     if (basePlane [1] == 1){

        zDir = 1;
        yDir = 2;
     } else {

        yDir = 1;
        zDir = 2;
     }
   }


  real_t Zm1=fmin(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
   real_t Ym1=fmin(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));
   real_t Xm1=fmin(fabs(inSphereRef(voxelCoords, xDir, sphere)),fabs(nextSphereRef(voxelCoords, xDir, sphere)));
   real_t XM1=fmax(fabs(inSphereRef(voxelCoords, xDir, sphere)),fabs(nextSphereRef(voxelCoords, xDir, sphere)));

   real_t macroPiece = integralGroup3(Xm1,XM1,Ym1,Zm1,sphere->radius);
   //optimisation : remplacer les X = X2 dans les formules
   real_t Xm2=Xm1;
   real_t Ym2=fmax(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));
   real_t Zm2=Zm1;

   //OPIMISATION : verif necessaire?
   real_t sum = pow(sphere->radius,2)-pow(Zm2,2)-pow(Ym2,2);
   real_t XM2;
   if (sum < 0.0){XM2 = 0.0;}
   else {XM2=sqrt(sum);}
   real_t leftoverToSubstract = integralGroup3(Xm2,XM2,Ym2,Zm2,sphere->radius);
   return macroPiece - leftoverToSubstract;
}

real_t caseCube4(real_t voxelCoords[3], int voxelCorners[2][2][2], sphere_ts* sphere)
{

    int basePlane[3] = {0};
    int cornerPosition[4][3];
    int x_i;
    int y_i;
    int z_i = 0;
    int cornerRank = 0;

    //seeking the three corners in
    //OPTIMISATION : would be a "for" parse better?
     while (cornerRank < 4 && z_i < 2){
      y_i = 0;
      while (cornerRank < 4 && y_i < 2){
        x_i = 0;
        while (cornerRank < 4 && x_i < 2){
           if (voxelCorners[x_i][y_i][z_i] == 1){
              cornerPosition[cornerRank][0] = x_i;
              cornerPosition[cornerRank][1] = y_i;
              cornerPosition[cornerRank][2] = z_i;
              cornerRank++;
           }
           x_i++;
        }
        y_i++;
      }
      z_i++;
    }


    int direction;
    int basePlaneSet = 0;
    for (direction = 0; direction < 3; direction++){
          if (cornerPosition[0][direction] == cornerPosition[1][direction]
            && cornerPosition[0][direction] == cornerPosition[2][direction]
            && cornerPosition[0][direction] == cornerPosition[3][direction])
            {
              basePlane[direction] = 1;
              basePlaneSet = 1;
            }
    }

    if (basePlaneSet){

        int xDir = -1;
        int yDir = -1;
        int zDir = -1;
        for (direction = 0; direction < 3; direction++){
            if (basePlane[direction] == 0){
              if(xDir == -1){xDir = direction;}
              else {yDir = direction;}
            } else {
              zDir = direction;
            }
         }

        real_t Zm=fmin(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
        real_t ZM=fmax(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
        real_t Ym=fmin(inSphereRef(voxelCoords, yDir, sphere), nextSphereRef(voxelCoords, yDir, sphere));
        real_t YM=fmax(inSphereRef(voxelCoords, yDir, sphere), nextSphereRef(voxelCoords, yDir, sphere));
        real_t Xm=fmin(inSphereRef(voxelCoords, xDir, sphere), nextSphereRef(voxelCoords, xDir, sphere));
        real_t XM=fmax(inSphereRef(voxelCoords, xDir, sphere), nextSphereRef(voxelCoords, xDir, sphere));


         //int onthezero[3] = {0};
         real_t pieceToRemove = 0.0;
         int onTheZeroCount = 0;
         int dirTouching = -1;

         //OPTIMISATION : something to do here?
         for (direction = 0; direction < 3; direction++){
            if (inSphereRef(voxelCoords, direction, sphere)*nextSphereRef(voxelCoords, direction, sphere)<0.0){
              //onthezero[direction] = 1;
              onTheZeroCount++;
            } else {
               if (direction != zDir){
                 dirTouching = direction;
               }
            }
         }


          if (onTheZeroCount == 2 && ZM < sphere->radius){
              pieceToRemove = integralGroup1(ZM,sphere->radius);

          } else if(onTheZeroCount == 1){
  //onthezero[zDir]=1;
              real_t minDirTouch =fmin(inSphereRef(voxelCoords, dirTouching, sphere), nextSphereRef(voxelCoords, dirTouching, sphere));
              //OPTIMISATION : if statement useless if sum always >= 0
              real_t maxR;
              real_t sum = pow(sphere->radius,2)-pow(minDirTouch,2);
              if(sum < 0.0){maxR = 0.0;}
              else {maxR = sqrt(sum);}

              if (maxR>ZM){
                 pieceToRemove = fabs(integralGroup2(ZM,maxR,minDirTouch,sphere->radius));
              }
          }

          return fabs(integralGroup4(Xm,XM,Ym,YM,Zm,sphere->radius))-pieceToRemove;


    } else {

        //OPTIMISATION : replace max and min by comp?
        real_t Xm1=fmin(fabs(inSphereRef(voxelCoords, 0, sphere)),fabs(nextSphereRef(voxelCoords, 0, sphere)));
        real_t XM1=fmax(fabs(inSphereRef(voxelCoords, 0, sphere)),fabs(nextSphereRef(voxelCoords, 0, sphere)));

        real_t Ym1=fmin(fabs(inSphereRef(voxelCoords, 1, sphere)),fabs(nextSphereRef(voxelCoords, 1, sphere)));
        real_t YM1=fmax(fabs(inSphereRef(voxelCoords, 1, sphere)),fabs(nextSphereRef(voxelCoords, 1, sphere)));

        real_t Zm1=fmin(fabs(inSphereRef(voxelCoords, 2, sphere)),fabs(nextSphereRef(voxelCoords, 2, sphere)));
        real_t ZM1=fmax(fabs(inSphereRef(voxelCoords, 2, sphere)),fabs(nextSphereRef(voxelCoords, 2, sphere)));

        real_t macroPiece= integralGroup3(Xm1,XM1,Ym1,Zm1,sphere->radius);

        real_t Xm2=fabs(YM1);
        real_t Ym2=fabs(Xm1);
        real_t Zm2=fabs(Zm1);
         //OPTIMISATION : if statement useless if sum always >= 0
        real_t XM2;
        real_t sum = pow(sphere->radius,2)-pow(Ym2,2)-pow(Zm2,2);

        if(sum < 0.0){
           XM2 = 0.0;
        } else {
          XM2 = sqrt(sum);
        }

        real_t leftoverToSubstract1 = integralGroup3(Xm2,XM2,Ym2,Zm2,sphere->radius);

        real_t Xm3=fabs(ZM1);
        real_t Ym3=fabs(Ym1);
        real_t Zm3=fabs(Xm1);
         //OPTIMISATION : if statement useless if sum always >= 0
        real_t XM3;
        sum = pow(sphere->radius,2)-pow(Ym3,2)-pow(Zm3,2);
        if(sum < 0.0){
           XM3 = 0.0;
        } else {
          XM3 = sqrt(sum);
        }

        real_t leftoverToSubstract2 = integralGroup3(Xm3,XM3,Ym3,Zm3,sphere->radius);
        return macroPiece-leftoverToSubstract1 - leftoverToSubstract2;
    }

}

real_t caseCube5(real_t voxelCoords[3], int voxelCorners[2][2][2], sphere_ts* sphere)
{

   int xDir = 0;
   int yDir = 1;
   int zDir = 2;

   if (cornerCountSurfaceX(0, voxelCorners) == 4 || cornerCountSurfaceX(1, voxelCorners) == 4)
    {

       xDir = 1;
       yDir = 2;
       zDir = 0;
    }
    else if (cornerCountSurfaceY(0, voxelCorners) == 4 || cornerCountSurfaceY(1, voxelCorners) == 4)
    {
       xDir = 0;
       yDir = 2;
       zDir = 1;
    }
//if (cornerCountSurfaceX(0, voxelCorners) == 4 || cornerCountSurfaceX(1, voxelCorners))
//done on init

    real_t Zm=fmin(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
    real_t ZM=fmax(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));

    real_t Ym=fmin(inSphereRef(voxelCoords, yDir, sphere), nextSphereRef(voxelCoords, yDir, sphere));
    real_t YM=fmax(inSphereRef(voxelCoords, yDir, sphere), nextSphereRef(voxelCoords, yDir, sphere));

    real_t Xm=fmin(inSphereRef(voxelCoords, xDir, sphere), nextSphereRef(voxelCoords, xDir, sphere));
    real_t XM=fmax(inSphereRef(voxelCoords, xDir, sphere), nextSphereRef(voxelCoords, xDir, sphere));

    real_t mainPiece=fabs(integralGroup4(Xm,XM,Ym,YM,Zm,sphere->radius));

    real_t Xm2=fabs(ZM); //OPTIMISATION, enlever le fabs car deja positif?

    real_t Ym2=fmin(fabs(inSphereRef(voxelCoords, xDir, sphere)),fabs(nextSphereRef(voxelCoords, xDir, sphere)));
    real_t Zm2=fmin(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));

    real_t sum = pow(sphere->radius,2)-pow(Ym2,2)-pow(Zm2,2); //OPTIMISATION : need test?
    real_t XM2;
    if (sum < 0.0){XM2 = 0.0;}
    else {XM2=sqrt(sum);}

    real_t leftoverToSubstract1= integralGroup3(Xm2,XM2,Ym2,Zm2,sphere->radius);

    return mainPiece - leftoverToSubstract1;
}

real_t caseCube6 (real_t voxelCoords[3], int voxelCorners[2][2][2], sphere_ts* sphere)
{


  int xDir;
  int yDir;
  int zDir;
  //#REMOVE test #if
  //OPIMISATION : MEDIC MEDIC, too much If statements?
  //finding the 6 corners in the sphere
  if (cornerCountSurfaceX(0, voxelCorners) == 4)
  {
    zDir = 0;
    if ((voxelCorners[1][0][0]== 1 && voxelCorners[1][0][1]==1)
     || (voxelCorners[1][1][0]==1 && voxelCorners[1][1][1]==1)){
          xDir = 2;
          yDir = 1;

    } else {

        xDir = 1;
        yDir = 2;
    }
  }
  else  if (cornerCountSurfaceX(1, voxelCorners) == 4)
  {
      zDir = 0;
      if ((voxelCorners[0][0][0] == 1 && voxelCorners[0][0][1] == 1)
        ||(voxelCorners[0][1][0] == 1 && voxelCorners[0][1][1] == 1)){
        xDir = 2;
          yDir = 1;

      } else {

        xDir = 1;
        yDir = 2;
      }

  } else if (voxelCorners[0][0][0]== 1
          && voxelCorners[0][0][1]== 1
          && voxelCorners[1][0][0]== 1
          && voxelCorners[1][0][1]== 1)
  {

       zDir = 1;
       if ((voxelCorners[0][1][0] == 1 && voxelCorners[0][1][1] == 1)
         ||(voxelCorners[1][1][0] == 1 && voxelCorners[1][1][1] == 1))
        {

           xDir = 2;
           yDir = 0;
        } else {

           xDir = 0;
           yDir = 2;
        }

  } else if (voxelCorners[0][1][0]== 1
          && voxelCorners[0][1][1]== 1
          && voxelCorners[1][1][0]== 1
          && voxelCorners[1][1][1]== 1)
  {

        zDir = 1;
        if((voxelCorners[0][0][0]== 1 && voxelCorners[0][0][1]==1 )
          || (voxelCorners[1][0][0]==1 && voxelCorners[1][0][1]==1))
        {

          xDir = 2;
          yDir = 0;
        } else {

          xDir = 0;
          yDir = 2;
        }

  } else if (voxelCorners[0][0][0]==1
          && voxelCorners[0][1][0]==1
          && voxelCorners[1][0][0]==1
          && voxelCorners[1][1][0]==1)
  {
      zDir = 2;
      if ((voxelCorners[0][0][1]== 1 && voxelCorners[1][0][1]==1)
       || (voxelCorners[0][1][1]== 1 && voxelCorners[1][1][1]==1))
      {
         xDir = 0;
         yDir = 1;

      } else {

         xDir = 1;
         yDir = 0;
      }

  } else {
      zDir = 2;
      if ((voxelCorners[0][0][0]== 1 && voxelCorners[1][0][0]==1)
       || (voxelCorners[0][1][0]== 1 && voxelCorners[1][1][0]==1))
      {

        xDir = 0;
        yDir = 1;
      } else {

        xDir = 1;
        yDir = 0;
      }
  }


  //integration interval...
  real_t Zm=fmin(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
  real_t ZM=fmax(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));

  real_t Ym=fmin(inSphereRef(voxelCoords, yDir, sphere),nextSphereRef(voxelCoords, yDir, sphere));
  real_t YM=fmax(inSphereRef(voxelCoords, yDir, sphere),nextSphereRef(voxelCoords, yDir, sphere));

  real_t Xm=fmin(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));
  real_t XM=fmax(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));

  real_t mainPiece=fabs(integralGroup4(Xm,XM,Ym,YM,Zm,sphere->radius));

  real_t Xm2=Xm; //OPIMISATION : virer et remplacer dans les appels pareil Zm2 et XM2
  real_t Ym2=fmin(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));
  real_t Zm2=ZM;
  real_t XM2=XM;
  real_t leftoverToSubstract1= fabs(integralGroup3(Xm2,XM2,Ym2,Zm2,sphere->radius));
  return mainPiece-leftoverToSubstract1;
}


real_t caseCube7 (real_t voxelCoords[3], int voxelCorners[2][2][2], sphere_ts* sphere){

  int haveInversion = 0;
  int firstOne = -1;
  int firstZero = -1;
  int other;

  //OPTIMISATION : replace other one by two pairs tat impossible values?
  int direction;
  for (direction = 0; direction < 3; direction++){
    if (inSphereRef(voxelCoords, direction, sphere)*nextSphereRef(voxelCoords, direction, sphere)<0){
        if (firstOne == -1){firstOne = direction;}
        else {other = direction;}
        haveInversion++;
     } else {

        if (firstZero == -1){firstZero = direction;}
        else {other = direction;}
     }
  }

  int xDir=0;
  int yDir=1;
  int zDir=2;

  real_t Zm;
  real_t ZM;
  real_t Ym;
  real_t YM;
  real_t Xm;
  real_t XM;
  //OPTIMISATION : replace xDiryz by raw first_oz and other
  if (haveInversion == 0){

    Zm=fmin(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
    ZM=fmax(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));

    Ym=fmin(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));
    YM=fmax(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));

    Xm=fmin(fabs(inSphereRef(voxelCoords, xDir, sphere)),fabs(nextSphereRef(voxelCoords, xDir, sphere)));
    XM=fmax(fabs(inSphereRef(voxelCoords, xDir, sphere)),fabs(nextSphereRef(voxelCoords, xDir, sphere)));

  } else if (haveInversion == 1){

    xDir = firstOne;
    yDir = firstZero;
    zDir = other;

    Zm=fmin(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
    ZM=fmax(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));

    Ym=fmin(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));
    YM=fmax(fabs(inSphereRef(voxelCoords, yDir, sphere)),fabs(nextSphereRef(voxelCoords, yDir, sphere)));


    Xm=fmin(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));
    XM=fmax(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));


  } else {

    xDir = firstOne;
    yDir = other;
    zDir = firstZero;

    Zm=fmin(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));
    ZM=fmax(fabs(inSphereRef(voxelCoords, zDir, sphere)),fabs(nextSphereRef(voxelCoords, zDir, sphere)));

    Ym=fmin(inSphereRef(voxelCoords, yDir, sphere),nextSphereRef(voxelCoords, yDir, sphere));
    YM=fmax(inSphereRef(voxelCoords, yDir, sphere),nextSphereRef(voxelCoords, yDir, sphere));

    Xm=fmin(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));
    XM=fmax(inSphereRef(voxelCoords, xDir, sphere),nextSphereRef(voxelCoords, xDir, sphere));

  }

    real_t mainPiece=fabs(integralGroup4(Xm,XM,Ym,YM,Zm,sphere->radius));
    //OPTIMISATION : replace xmx by raw in calls xm
    real_t Zm1=ZM;
    real_t Ym1=Ym;
    real_t Xm1=Xm;
    real_t XM1=XM;
    real_t macroPiecepieceToRemove=fabs(integralGroup3(Xm1,XM1,Ym1,Zm1,sphere->radius));

    real_t Xm2=YM;
    real_t Ym2=fabs(Xm);
    real_t Zm2=ZM;
    //OPTIMISATION : if statement useless if sum always >= 0
    real_t XM2;
    real_t sum = pow(sphere->radius,2)-pow(Zm2,2)-pow(Ym2,2);
    if (sum < 0.0){XM2 = 0.0;}
    else {XM2 = sqrt(sum);}

   real_t PieceToSubFromRemovedPiece = fabs(integralGroup3(Xm2,XM2,Ym2,Zm2,sphere->radius));

   return mainPiece-(macroPiecepieceToRemove-PieceToSubFromRemovedPiece);

}

/* #################################################### */
/* ######## CASE CUBE FUNCTIONS IMPLEMENT ENDS ######## */
/* #################################################### */

/* FILE kalisphera_c.c ENDS */
