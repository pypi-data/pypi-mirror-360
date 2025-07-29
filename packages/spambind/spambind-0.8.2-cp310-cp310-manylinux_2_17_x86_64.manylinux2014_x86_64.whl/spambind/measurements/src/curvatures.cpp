#include <stdio.h>
#include <math.h>
#include <iostream>
#include <vector>
#include <algorithm>

#include "measurementsToolkit.hpp"

/* 2018-06 -- Yue Sun -- Measurement of a curvatures based on [http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.24.3427&rep=rep1&type=pdf ]  */

/* Inputs:
* verts : The coordinates (x,y,z) of the points
* faces : Table of connectivity, which gives the vertex ID of each triangle
*     Attention : The points of each triangle are in counter-clockwise order from 1 to 3
*
* Outputs:
*  mean_gauss_area : Three values are given at each points - mean curvature ; gauss curvature and the mixed area
*
*
 */


std::vector<std::vector<double> > computeCurvatures( const std::vector<std::vector<unsigned int> >& faces, const std::vector<std::vector<double> >& verts)
{

  std::vector<std::vector<double> > mean_gauss_area(verts.size());
  for(unsigned i=0; i<verts.size(); i++ )
    {
      mean_gauss_area[i].resize(3);
    }

  int nb_tri = faces.size();  // count nomber of triangles
  int nb_p = verts.size();  // count nomber of nodes
  double temp=0.0 ;
  double sum=0.0;
  double wi=0.0;
  unsigned point;
  int kk;
  int ll;

  /*  declare two vector temp */
  std::vector<double> mc_vec(3);
  std::vector<double> n_vec(3);
  /*  declare matrix of size nb_tri*3 */
  std::vector<std::vector<double>> f_normal(nb_tri);// normal vector for each triangle
  std::vector<std::vector<double>> p1(nb_tri);
  std::vector<std::vector<double>> p2(nb_tri);
  std::vector<std::vector<double>> n(nb_tri);
  std::vector<std::vector<double>> l_edg(nb_tri);
  std::vector<std::vector<double>> ang_tri(nb_tri);
  std::vector<std::vector<double>> f_center(nb_tri);
  std::vector<std::vector<double>> v0(nb_tri);
  std::vector<std::vector<double>> v1(nb_tri);
  std::vector<std::vector<double>> v2(nb_tri);

  for (unsigned i=0; i<faces.size(); i++ ){
    f_normal[i].resize(3);
    p1[i].resize(3);
    p2[i].resize(3);
    n[i].resize(3);
    l_edg[i].resize(3);
    ang_tri[i].resize(3);
    f_center[i].resize(3);
    v0[i].resize(3);
    v1[i].resize(3);
    v2[i].resize(3);
  }

  /*  declare vector of size nb_tri*1 */
  std::vector<double> norm(nb_tri);
  std::vector<double> p(nb_tri);
  std::vector<double> area_tri(nb_tri);
  std::vector<double> tempp(3);

  /*  declare vector of size nb_tri*1 */
  std::vector<double> alf(nb_p);

  for( int i = 0; i < nb_tri; i++ ) {
    /*  normal vector */
    for ( int j=0; j<3; j++){
      p1[i][j]=verts[faces[i][0]][j]-verts[faces[i][1]][j];
      p2[i][j]=verts[faces[i][0]][j]-verts[faces[i][2]][j];
    }

    for ( int j=0; j<3; j++){
      n[i][0]=p1[i][1]*p2[i][2]-p1[i][2]*p2[i][1];
      n[i][1]=p1[i][2]*p2[i][0]-p1[i][0]*p2[i][2];
      n[i][2]=p1[i][0]*p2[i][1]-p1[i][1]*p2[i][0];
    }

    norm[i]=sqrt(pow(n[i][0],2)+pow(n[i][1],2)+pow(n[i][2],2));
    for ( int j=0; j<3; j++){
        f_normal[i][j]=n[i][j]/norm[i];
    }

    /*  edges */
    for ( int j=0; j<3; j++){
      v0[i][j]=verts[faces[i][1]][j]-verts[faces[i][0]][j];
      v1[i][j]=verts[faces[i][2]][j]-verts[faces[i][1]][j];
      v2[i][j]=verts[faces[i][0]][j]-verts[faces[i][2]][j];
    }

    /*  length of edges   */
    l_edg[i][0]=sqrt(pow(v0[i][0],2)+pow(v0[i][1],2)+pow(v0[i][2],2));
    l_edg[i][1]=sqrt(pow(v1[i][0],2)+pow(v1[i][1],2)+pow(v1[i][2],2));
    l_edg[i][2]=sqrt(pow(v2[i][0],2)+pow(v2[i][1],2)+pow(v2[i][2],2));

    /*  length of edges   */
    temp=0.0;
    for ( int j=0; j<3; j++){
      temp=temp+(v0[i][j]/l_edg[i][0])*((-v2[i][j])/l_edg[i][2]);
    }
    ang_tri[i][0]=acos(temp);

    temp=0.0;
    for ( int j=0; j<3; j++){
      temp=temp+((-v0[i][j]/l_edg[i][0]))*((v1[i][j])/l_edg[i][1]);
    }
    ang_tri[i][1]=acos(temp);
    ang_tri[i][2]=3.1415926-ang_tri[i][0]-ang_tri[i][1];

    /*  incenter  */
    p[i]=l_edg[i][0]+l_edg[i][1]+l_edg[i][2];
    f_center[i][0]=(l_edg[i][0]*verts[faces[i][2]][0]+l_edg[i][1]*verts[faces[i][0]][0]+l_edg[i][2]*verts[faces[i][1]][0])/p[i];
    f_center[i][1]=(l_edg[i][0]*verts[faces[i][2]][1]+l_edg[i][1]*verts[faces[i][0]][1]+l_edg[i][2]*verts[faces[i][1]][1])/p[i];
    f_center[i][2]=(l_edg[i][0]*verts[faces[i][2]][2]+l_edg[i][1]*verts[faces[i][0]][2]+l_edg[i][2]*verts[faces[i][1]][2])/p[i];

    /*  surface  */
    tempp[0]=v0[i][1]*v1[i][2]-v0[i][2]*v1[i][1];
    tempp[1]=v0[i][2]*v1[i][0]-v0[i][0]*v1[i][2];
    tempp[2]=v0[i][0]*v1[i][1]-v0[i][1]*v1[i][0];
    area_tri[i]=sqrt(pow(tempp[0],2)+pow(tempp[1],2)+pow(tempp[2],2))/2.0;
  }

  for (unsigned i=0; i<verts.size(); i++){
    for ( int j=0; j<3; j++){
      mc_vec[j]=0.0;
      n_vec[j]=0.0;
    }

    /* neib_tri vector unknown size */
    std::vector<unsigned> neib_tri;
    for ( int j=0; j<nb_tri; j++){
      if(faces[j][0]==i || faces[j][1]==i || faces[j][2]==i ){
        neib_tri.push_back(j);
      }
    }

    for (unsigned j=0; j<neib_tri.size(); j++){
      point=neib_tri[j];  // point -> neib
      /*sum of angles around point i ==>GC */
      kk=0;
      for ( int k=0; k<3; k++){
        if (faces[point][k]==i){
          alf[i]=alf[i]+ang_tri[point][k];
          kk=k;
          break;
        }
      }

      /* mean curvature operator */
      if (kk==0){
        for ( int k=0; k<3; k++){
          mc_vec[k]=mc_vec[k]+(v0[point][k]/tan(ang_tri[point][2])-v2[point][k]/tan(ang_tri[point][1]));
        }
      }
      else if (kk==1){
        for ( int k=0; k<3; k++){
          mc_vec[k]=mc_vec[k]+(v1[point][k]/tan(ang_tri[point][0])-v0[point][k]/tan(ang_tri[point][2]));
        }
      }

      else if (kk==2){
        for ( int k=0; k<3; k++){
          mc_vec[k]=mc_vec[k]+(v2[point][k]/tan(ang_tri[point][1])-v1[point][k]/tan(ang_tri[point][0]));
        }
      }

      /*A_mixed calculation (a_mixed=mean_gauss_area[:][2]) */
      if (ang_tri[point][kk]>=3.1415/2.0){
        mean_gauss_area[i][2]=mean_gauss_area[i][2]+area_tri[point]/2.0;
      }
      else{
        if (ang_tri[point][0]>=3.1415/2.0 || ang_tri[point][1]>=3.1415/2.0 || ang_tri[point][2]>=3.1415/2.0){
          mean_gauss_area[i][2]=mean_gauss_area[i][2]+area_tri[point]/4.0;
        }
        else{
          sum=0.0;
          for ( int m=0; m<3; m++){
            if (m!=kk){
              ll=m+1;
              if (ll==3){
                ll=0;
              }
              sum=sum+(pow(l_edg[point][ll],2)/tan(ang_tri[point][m]));
            }
          }
          mean_gauss_area[i][2]=mean_gauss_area[i][2]+sum/8.0;
        }
      }

      /* normal vector at each vertex */
      /* weighted average of normal vectors of neighbour triangles */
      for( int k=0; k<3; k++){
        tempp[k]=f_center[point][k]-verts[i][k];
        }
      wi=1.0/(sqrt(pow(tempp[0],2)+pow(tempp[1],2)+pow(tempp[2],2)));
      for( int k=0; k<3; k++){
        n_vec[k]=n_vec[k]+wi*f_normal[point][k];
      }
    }
    mean_gauss_area[i][1]=(2.0*3.1415-alf[i])/mean_gauss_area[i][2];
    temp=sqrt(pow(n_vec[0],2)+pow(n_vec[1],2)+pow(n_vec[2],2));
    for ( int m=0; m<3; m++){
      mc_vec[m]=0.25*mc_vec[m]/mean_gauss_area[i][2];
      n_vec[m]=n_vec[m]/temp;
    }
    /*  sign of MC   (MC=mean_gauss_area[:][0])*/
    if ((mc_vec[0]*n_vec[0]+mc_vec[1]*n_vec[1]+mc_vec[2]*n_vec[2])<0){
      mean_gauss_area[i][0]=-sqrt(pow(mc_vec[0],2)+pow(mc_vec[1],2)+pow(mc_vec[2],2));
    }
    else {
      mean_gauss_area[i][0]=sqrt(pow(mc_vec[0],2)+pow(mc_vec[1],2)+pow(mc_vec[2],2));
    }
  }

  return mean_gauss_area;
};
