#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <cmath>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>

#include "tetrahedron.hpp"

// Feb/2020: Current functions
// Jan/2023: Point to (-)
// Feb/2023: Order 2 interpolation

std::vector<double> tetrahedron::_cprod(std::vector<double> a, std::vector<double> b)
{
  std::vector<double> res(3);
  res[0] = a[1] * b[2] - a[2] * b[1];
  res[1] = a[2] * b[0] - a[0] * b[2];
  res[2] = a[0] * b[1] - a[1] * b[0];
  return res;
}
double tetrahedron::_dprod(std::vector<double> a, std::vector<double> b)
{
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

std::vector<std::vector<double>> tetrahedron::get_coor_intrs(std::vector<std::vector<double>> c_tet,
                                                             std::vector<double> v_tet, std::vector<double> v_mid, std::vector<std::vector<unsigned>> v_pos,
                                                             unsigned int ph, double thresh,
                                                             std::vector<unsigned> &l_theta)
{
  // Calculation of intersections between the plane and the tetrahedron
  unsigned int n1;
  unsigned int n2;
  double theta;
  std::vector<std::vector<double>> c_theta(3);

  // std::cout << "vtet " << v_tet[0] << " " << v_tet[1] << " " << v_tet[2] << " " << v_tet[3] << std::endl;

  // local correspondence array between edges and nodes
  std::vector<std::vector<unsigned>> a_tet(6);
  for (unsigned int k = 0; k < a_tet.size(); k++)
  {
    a_tet[k].resize(2);
  }
  a_tet[0][0] = 0; a_tet[0][1] = 1;
  a_tet[1][0] = 0; a_tet[1][1] = 3;
  a_tet[2][0] = 0; a_tet[2][1] = 2;
  a_tet[3][0] = 1; a_tet[3][1] = 3;
  a_tet[4][0] = 1; a_tet[4][1] = 2;
  a_tet[5][0] = 3; a_tet[5][1] = 2;

  for (unsigned int k = 0; k < 6; k++)
  {
    n1 = a_tet[k][0];
    n2 = a_tet[k][1];
    if (v_pos[n1][ph] != v_pos[n2][ph])
    {
      // a interpolation ratio based on distance field values is taken to locate the
      // coordinates of intersections in all directions.
      // std::cout << "v_tet = " << v_tet[n1] << " " << v_tet[n2] << " v_mid " << v_mid[k] << std::endl;

      // determine quadratic equation given 3 points
      double P0 = v_tet[n1];
      double P1 = v_mid[k];
      double P2 = v_tet[n2];

      double a = 2 * (P2 + P0) - 4 * P1;
      double b = -P2 - 3 * P0 + 4 * P1;
      double c = P0 - thresh;
      double delta = b * b - 4 * a * c;
      if( abs(a) < 1e-12 )
      {
        // std::cout << "linear interpolation is safer delta = " << delta << " a = " << a << std::endl;
        theta = (v_tet[n1] - thresh) / (v_tet[n1] - v_tet[n2]);
      }
      else if( delta < 0 )
      {
        std::cout << "WARNING : Delta < 0 (" << delta << "), no intersection found (that shouldn't happen)."  << std::endl;
        theta = (v_tet[n1] - thresh) / (v_tet[n1] - v_tet[n2]);
      }
      else
      {
        theta = (- b + sqrt(delta)) / (2 * a);
        if (theta > 1 || theta < 0) {
          theta = (- b - sqrt(delta)) / (2 * a);
          if (theta > 1 || theta < 0) {
            std::cout << "WARNING : theta is not between 0 and 1 (" << theta << "), no intersection found (that shouldn't happen)."  << std::endl;
            theta = (v_tet[n1] - thresh) / (v_tet[n1] - v_tet[n2]);
          }
        }
        // std::cout << "quadratic interpolation theta = " << theta << " linear " << (v_tet[n1] - thresh) / (v_tet[n1] - v_tet[n2]) << std::endl;
      }

      // force linear interpolation
      // theta = (v_tet[n1] - thresh) / (v_tet[n1] - v_tet[n2]);
      // std::cout << "theta" << k << " = " << theta << " vtet1 = " << v_tet[n1] << " vtet2 = " << v_tet[n2]<< std::endl;

      for (unsigned int j = 0; j < 3; j++)
      {
        c_theta[j].push_back(c_tet[j][n1] + (c_tet[j][n2] - c_tet[j][n1]) * theta);
      }
      l_theta.push_back(k); // the tet edge associated with each intersection is stored. It is useful later.
    }

    // check orientation of the connectivity
    if (c_theta[0].size() == 4)
    {
      // Compute V_02 v01 and V03
      // check that V_02xV_01 is not the same direction as V_02xV_03 to have 0-2 the diag
      // so if not, switch 1 and 2

      // STEP 0: save original c_theta
      std::vector<std::vector<double>> tmp;
      std::vector<unsigned> ltmp;
      tmp = c_theta;
      ltmp = l_theta;

      // STEP 1: first trial we spam 1 & 2
      std::vector<double> v01(3);
      v01[0] = c_theta[0][1] - c_theta[0][0];
      v01[1] = c_theta[1][1] - c_theta[1][0];
      v01[2] = c_theta[2][1] - c_theta[2][0];
      std::vector<double> v02(3);
      v02[0] = c_theta[0][2] - c_theta[0][0];
      v02[1] = c_theta[1][2] - c_theta[1][0];
      v02[2] = c_theta[2][2] - c_theta[2][0];
      std::vector<double> v03(3);
      v03[0] = c_theta[0][3] - c_theta[0][0];
      v03[1] = c_theta[1][3] - c_theta[1][0];
      v03[2] = c_theta[2][3] - c_theta[2][0];
      std::vector<double> cp21(3);
      std::vector<double> cp23(3);
      cp21 = _cprod(v02, v01);
      cp23 = _cprod(v02, v03);
      if (_dprod(cp21, cp23) > 0)
      {
        // swap 1 and 2
        c_theta[0][1] = tmp[0][2];
        c_theta[1][1] = tmp[1][2];
        c_theta[2][1] = tmp[2][2];
        c_theta[0][2] = tmp[0][1];
        c_theta[1][2] = tmp[1][1];
        c_theta[2][2] = tmp[2][1];
        l_theta[1] = ltmp[2];
        l_theta[2] = ltmp[1];
      }

      // STEP 3: second trial if still wrong we should have have swapped 1 & 3
      v01[0] = c_theta[0][1] - c_theta[0][0];
      v01[1] = c_theta[1][1] - c_theta[1][0];
      v01[2] = c_theta[2][1] - c_theta[2][0];
      v02[0] = c_theta[0][2] - c_theta[0][0];
      v02[1] = c_theta[1][2] - c_theta[1][0];
      v02[2] = c_theta[2][2] - c_theta[2][0];
      v03[0] = c_theta[0][3] - c_theta[0][0];
      v03[1] = c_theta[1][3] - c_theta[1][0];
      v03[2] = c_theta[2][3] - c_theta[2][0];
      cp21 = _cprod(v02, v01);
      cp23 = _cprod(v02, v03);
      if (_dprod(cp21, cp23) > 0)
      {
        // back to origin
        c_theta[0][1] = tmp[0][1];
        c_theta[1][1] = tmp[1][1];
        c_theta[2][1] = tmp[2][1];
        l_theta[1] = ltmp[1];
        // c_theta[0][2] = tmp[0][2];
        // c_theta[1][2] = tmp[1][2];
        // c_theta[2][2] = tmp[2][2];
        // swap 1 & 3
        c_theta[0][2] = tmp[0][3];
        c_theta[1][2] = tmp[1][3];
        c_theta[2][2] = tmp[2][3];
        c_theta[0][3] = tmp[0][2];
        c_theta[1][3] = tmp[1][2];
        c_theta[2][3] = tmp[2][2];
        l_theta[2] = ltmp[3];
        l_theta[3] = ltmp[2];
      }
    }
  }

  return c_theta;
}

std::vector<double> tetrahedron::get_interface(std::vector<std::vector<double>> c_tet, std::vector<std::vector<double>> c_theta,
                                               std::vector<std::vector<unsigned>> v_pos, unsigned int fd)
{
  // Calculation of interface orientation
  double u1, u2, u3, v1, v2, v3, n1, n2, n3;
  n1 = 1.0;
  n2 = 0.0;
  n3 = 0.0;
  double w1, w2, w3, ntst;

  // normal obtained through cross product having 2 vectors describing the cutting plane.
  u1 = c_theta[0][1] - c_theta[0][0];
  u2 = c_theta[1][1] - c_theta[1][0];
  u3 = c_theta[2][1] - c_theta[2][0];
  v1 = c_theta[0][2] - c_theta[0][0];
  v2 = c_theta[1][2] - c_theta[1][0];
  v3 = c_theta[2][2] - c_theta[2][0];
  n1 = u2 * v3 - u3 * v2;
  n2 = u3 * v1 - u1 * v3;
  n3 = u1 * v2 - u2 * v1;

  // this normal must point out to the (-) domain. A test node on the tet is taken to assess this and to correct if needed.
  // we loop over tetrahedral nodes until w != 0 (in case c_tet == c_theta)
  for(unsigned int a=0; a<4; a++) {
    w1 = c_tet[0][a] - c_theta[0][0];
    w2 = c_tet[1][a] - c_theta[1][0];
    w3 = c_tet[2][a] - c_theta[2][0];
    ntst = w1 * n1 + w2 * n2 + w3 * n3;
    if (!(((v_pos[a][fd] > 0) && (ntst <= 0.0)) || ((v_pos[a][fd] == 0) && (ntst >= 0.0))))
    {
      n1 = -n1;
      n2 = -n2;
      n3 = -n3;
    }

    // if w != 0 we exit the loop
    if(pow(w1, 2) + pow(w2, 2) + pow(w3, 2) > 1e-12)
    {
      continue;
    }
  }

  double norm = sqrt(pow(n1, 2) + pow(n2, 2) + pow(n3, 2));

  std::vector<double> interface = {0.0, 0.0, 0.0, 0.0}; // [n1, n2, n3, area]
  if(norm > 1e-12)
  {
    // check if norm != 0
    // it can happen if one field value is exactly at the threshold
    // two c_theta can be the same which leads seomtimes to u and/or v = 0
    interface[0] = n1 / norm;
    interface[1] = n2 / norm;
    interface[2] = n3 / norm;
  }
  else
  {
    std::cout << "warning: a normal vector is null. element is ignored." << std::endl;
  }

  // compute the surface
  if (c_theta[0].size() == 3)
  {
    // surface is 0.5 times cross product of 2 vecotrs

    // YES we know we computed it already just above... but it's fiiiine
    double u1_1 = c_theta[0][1] - c_theta[0][0];
    double u2_1 = c_theta[1][1] - c_theta[1][0];
    double u3_1 = c_theta[2][1] - c_theta[2][0];
    double v1_1 = c_theta[0][2] - c_theta[0][0];
    double v2_1 = c_theta[1][2] - c_theta[1][0];
    double v3_1 = c_theta[2][2] - c_theta[2][0];
    double n1_1 = u2_1 * v3_1 - u3_1 * v2_1;
    double n2_1 = u3_1 * v1_1 - u1_1 * v3_1;
    double n3_1 = u1_1 * v2_1 - u2_1 * v1_1;

    double s1 = 0.5 * sqrt(pow(n1_1, 2) + pow(n2_1, 2) + pow(n3_1, 2));

    interface[3] = s1;
  }
  else if (c_theta[0].size() == 4)
  {
    // split surface in 2 triangles

    double u1_1 = c_theta[0][1] - c_theta[0][0];
    double u2_1 = c_theta[1][1] - c_theta[1][0];
    double u3_1 = c_theta[2][1] - c_theta[2][0];
    double v1_1 = c_theta[0][2] - c_theta[0][0];
    double v2_1 = c_theta[1][2] - c_theta[1][0];
    double v3_1 = c_theta[2][2] - c_theta[2][0];
    double n1_1 = u2_1 * v3_1 - u3_1 * v2_1;
    double n2_1 = u3_1 * v1_1 - u1_1 * v3_1;
    double n3_1 = u1_1 * v2_1 - u2_1 * v1_1;

    double s1 = 0.5 * sqrt(pow(n1_1, 2) + pow(n2_1, 2) + pow(n3_1, 2));

    double u1_2 = c_theta[0][1] - c_theta[0][3];
    double u2_2 = c_theta[1][1] - c_theta[1][3];
    double u3_2 = c_theta[2][1] - c_theta[2][3];
    double v1_2 = c_theta[0][2] - c_theta[0][3];
    double v2_2 = c_theta[1][2] - c_theta[1][3];
    double v3_2 = c_theta[2][2] - c_theta[2][3];
    double n1_2 = u2_2 * v3_2 - u3_2 * v2_2;
    double n2_2 = u3_2 * v1_2 - u1_2 * v3_2;
    double n3_2 = u1_2 * v2_2 - u2_2 * v1_2;

    double s2 = 0.5 * sqrt(pow(n1_2, 2) + pow(n2_2, 2) + pow(n3_2, 2));

    interface[3] = s1 + s2;
  }
  else
  {
    std::cout << "wtf??? how many points to you want in your intersection? " << c_theta[0].size() << " given" << std::endl;
    interface[3] = -1.0;
  }

  return interface;
}

double tetrahedron::get_sub_volume(std::vector<std::vector<double>> c_tet, std::vector<std::vector<double>> c_theta,
                                   unsigned int fd, std::vector<std::vector<unsigned>> v_pos, std::vector<unsigned> l_theta)
{
  // Unified routine for tet subvolume calculation
  std::vector<std::vector<double>> tet_ref(3);
  std::vector<unsigned> np;
  std::vector<unsigned> nm;
  std::vector<std::vector<unsigned>> prmsh(3);
  double vm = 0.0;
  unsigned int ii = 0, jj = 0;

  // Recovering node position on +, - domains
  for (unsigned int k = 0; k < 4; k++)
  {
    if (v_pos[k][fd] > 0)
    {
      np.push_back(k);
    }
    else
    {
      nm.push_back(k);
    }
  }
  std::vector<std::vector<unsigned>> vx_tet(4);
  for (unsigned int k = 0; k < vx_tet.size(); k++)
  {
    vx_tet[k].resize(3);
  }
  vx_tet[0][0] = 0;
  vx_tet[0][1] = 2;
  vx_tet[0][2] = 1;
  vx_tet[1][0] = 0;
  vx_tet[1][1] = 3;
  vx_tet[1][2] = 4;
  vx_tet[2][0] = 2;
  vx_tet[2][1] = 4;
  vx_tet[2][2] = 5;
  vx_tet[3][0] = 1;
  vx_tet[3][1] = 3;
  vx_tet[3][2] = 5;

  // 3 plane intersections case : subtet + irregular triangular prism scenario / 3-1 node partition
  // Approach: form a tet by gathering the three intersection nodes of the cutting surface
  // and the solitary tet node. if the solitary node is on the (-) domain, this is the desired volume.
  // If not, the desired volume is obtained by simple substraction to the big tet volume.
  if (c_theta[0].size() == 3)
  {
    for (unsigned int j = 0; j < 3; j++)
    {
      for (unsigned int k = 0; k < 3; k++)
      {
        tet_ref[k].push_back(c_theta[k][j]);
      }
    }
    if (nm.size() == 1)
    {
      for (unsigned int k = 0; k < 3; k++)
      {
        tet_ref[k].push_back(c_tet[k][nm[0]]);
      }
      vm = get_volume_tet(tet_ref);
    }
    else
    {
      for (unsigned int k = 0; k < 3; k++)
      {
        tet_ref[k].push_back(c_tet[k][np[0]]);
      }
      vm = get_volume_tet(c_tet) - get_volume_tet(tet_ref);
    }
  }
  else
  {
    // 4 plane intersections case : 2 irregular triangular prisms scenario / 2-2 node partition
    // Approach: the irregular prism on (-) is to be meshed with three tets (Euclid book XII, prop. 7)
    // The prmsh[tet#][node#] vector contains the node ordering for each tet *beware, it mixes numbering
    // from the big tet nodes and local quadrilateral cutting surface nodes knowing beforehand*
    // One of the diagonals of the quadrilateral cut surface must be identified for this purpose.
    prmsh[0].push_back(nm[0]);
    prmsh[1].push_back(nm[1]);
    prmsh[2].push_back(nm[0]);
    prmsh[2].push_back(nm[1]);
    for (unsigned int k = 0; k < 4; k++)
    {
      for (unsigned int j = 0; j < 3; j++)
      {
        if (l_theta[k] == vx_tet[nm[0]][j])
        {
          prmsh[0].push_back(k);
          for (unsigned int i = 0; i < 3; i++)
          {
            if (l_theta[k] == vx_tet[np[0]][i])
            {
              ii = k;
            } // Saving diagonal vertex
          }
        }
        else if (l_theta[k] == vx_tet[nm[1]][j])
        {
          prmsh[1].push_back(k);
          for (unsigned int i = 0; i < 3; i++)
          {
            if (l_theta[k] == vx_tet[np[1]][i])
            {
              jj = k;
            } // Saving diagonal vertex
          }
        }
      }
    }
    prmsh[1].push_back(ii);
    prmsh[0].push_back(jj);
    prmsh[2].push_back(ii);
    prmsh[2].push_back(jj);

    // Coordinates are retrieved to build a dummy tet: tet_ref[][], using prmsh[][]
    // 1st tet processing
    for (unsigned int i = 0; i < 3; i++)
    {
      tet_ref[i].push_back(c_tet[i][prmsh[0][0]]);
    }
    for (unsigned int k = 0; k < 3; k++)
    {
      for (unsigned int j = 0; j < 3; j++)
      {
        tet_ref[j].push_back(c_theta[j][prmsh[0][k + 1]]);
      }
    }
    vm += get_volume_tet(tet_ref);
    // 2nd tet processing
    for (unsigned int i = 0; i < 3; i++)
    {
      tet_ref[i][0] = c_tet[i][prmsh[1][0]];
    }
    for (unsigned int k = 0; k < 3; k++)
    {
      for (unsigned int j = 0; j < 3; j++)
      {
        tet_ref[j][k + 1] = c_theta[j][prmsh[1][k + 1]];
      }
    }
    vm += get_volume_tet(tet_ref);
    // 3nd tet processing
    for (unsigned int k = 0; k < 2; k++)
    {
      for (unsigned int j = 0; j < 3; j++)
      {
        tet_ref[j][k] = c_tet[j][prmsh[2][k]];
      }
    }
    for (unsigned int k = 0; k < 2; k++)
    {
      for (unsigned int j = 0; j < 3; j++)
      {
        tet_ref[j][k + 2] = c_theta[j][prmsh[2][k + 2]];
      }
    }
    vm += get_volume_tet(tet_ref);
  }

  // std::cout << "Volume:  " << vm << " ";
  // std::cout << "Sub volume:  " << vm << std::endl;

  return vm;
}

double tetrahedron::get_volume_tet(std::vector<std::vector<double>> c_tet)
{
  double xa = c_tet[0][0];
  double ya = c_tet[1][0];
  double za = c_tet[2][0];
  double xb = c_tet[0][1];
  double yb = c_tet[1][1];
  double zb = c_tet[2][1];
  double xc = c_tet[0][2];
  double yc = c_tet[1][2];
  double zc = c_tet[2][2];
  double xd = c_tet[0][3];
  double yd = c_tet[1][3];
  double zd = c_tet[2][3];
  double ax = xd - xa;
  double bx = xd - xb;
  double cx = xd - xc;
  double ay = yd - ya;
  double by = yd - yb;
  double cy = yd - yc;
  double az = zd - za;
  double bz = zd - zb;
  double cz = zd - zc;
  double pvx = by * cz - bz * cy;
  double pvy = bz * cx - bx * cz;
  double pvz = bx * cy - by * cx;
  // std::cout << "volu: " << std::abs(ax*pvx+ay*pvy+az*pvz)/6.0 << std::endl;
  return std::abs(ax * pvx + ay * pvy + az * pvz) / 6.0;
}

std::vector<double> tetrahedron::get_centroid(std::vector<std::vector<double>> c_tet)
{
  std::vector<double> centroid(3);

  // loop over x, y, z
  for(unsigned int i = 0; i < 3; i++)
  {
    // step 0: coordinates of the triangle
    double a = c_tet[i][0];
    double b = c_tet[i][1];
    double c = c_tet[i][2];
    double d = c_tet[i][3];

    // step 1: midpoint of AB
    double mid_ab = a + (b - a) / 2.0;

    // step 2: face centroid (1/3 of mid_ab -> c)
    double face_centroid = mid_ab + (c - mid_ab) / 3.0;

    // step 3: tetrahedron centroid (1/4 of face centroid -> d)
    centroid[i] = face_centroid + (d - face_centroid) / 4.0;
  }

  return centroid;
}
