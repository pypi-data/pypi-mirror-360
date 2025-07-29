#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <math.h>
#include <cmath>
#include <string.h>
#include <random>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <iomanip>
#include <algorithm>
#include "crpacking.hpp"

#define M_PI 3.14159265358979323846 // pi

void crpacking::print_error(std::string msg, bool ex)
{
  std::cout << "[ERROR] " << msg << std::endl;
  if (ex)
  {
    std::cout << "[ERROR] exit program" << std::endl;
    exit(EXIT_FAILURE);
  }
}

/***********************************/
/*             PUBLIC              */
/***********************************/

/* CONSTRUCTOR */

crpacking::crpacking(std::vector<double> parameters,
                     std::vector<double> lengths,
                     std::vector<double> origin,
                     unsigned int inside,
                     std::string file_name,
                     std::string domain)
{
  std::cout << "<crpacking::crpacking" << std::endl;
  // set default values to the variables
  _lengths = lengths;
  _origin = origin;
  if (inside)
    _inside = true;
  else
    _inside = false;
  _domain_type = domain;
  _parameters = parameters;
  _file_name = file_name;

  // output
  std::cout << ".\t file name: " << _file_name << std::endl;
  std::cout << ".\t domain type: " << _domain_type << std::endl;
  std::cout << ".\t origin: " << _origin[0] << ", " << _origin[1] << ", " << _origin[2] << std::endl;
  std::cout << ".\t lengths: " << _lengths[0] << ", " << _lengths[1] << ", " << _lengths[2] << std::endl;
  std::string msg = (_inside) ? "True" : "False";
  std::cout << ".\t objects inside: " << msg << std::endl;
  if (_parameters.size() > 2)
  {
    if ((_parameters.size() - 2) % 4 == 0)
    { // spheres
      std::cout << ".\t parameters for spheres" << std::endl;
      for (unsigned int i = 0; i < _parameters.size(); i++)
      {
        std::cout << ".\t .\t ";
        if (i == 0)
        {
          std::cout << "total fraction volume:\t";
        }
        else if (i == 1)
        {
          std::cout << "rejection length:\t";
        }
        else if ((i - 2) % 4 == 0)
        {
          std::cout << "phase " << (int)((i - 2) / 4) << " rmin:\t\t";
        }
        else if ((i - 2) % 4 == 1)
        {
          std::cout << "phase " << (int)((i - 2) / 4) << " rmax:\t\t";
        }
        else if ((i - 2) % 4 == 2)
        {
          std::cout << "phase " << (int)((i - 2) / 4) << " volf:\t\t";
        }
        else if ((i - 2) % 4 == 3)
        {
          std::cout << "phase " << (int)((i - 2) / 4) << " valu:\t\t";
        }
        std::cout << _parameters[i] << std::endl;
      }
    }
    else if ((_parameters.size() - 2) % 5 == 0)
    { // ellipsoids
      std::cout << ".\t parameters for ellipsoids" << std::endl;
      for (unsigned int i = 0; i < _parameters.size(); i++)
      {
        std::cout << ".\t .\t ";
        if (i == 0)
        {
          std::cout << "total fraction volume:\t";
        }
        else if (i == 1)
        {
          std::cout << "rejection length:\t";
        }
        else if ((i - 2) % 5 == 0)
        {
          std::cout << "phase " << (int)((i - 2) / 5) << " rx:\t\t";
        }
        else if ((i - 2) % 5 == 1)
        {
          std::cout << "phase " << (int)((i - 2) / 5) << " ry:\t\t";
        }
        else if ((i - 2) % 5 == 2)
        {
          std::cout << "phase " << (int)((i - 2) / 5) << " rz:\t\t";
        }
        else if ((i - 2) % 5 == 3)
        {
          std::cout << "phase " << (int)((i - 2) / 5) << " volf:\t\t";
        }
        else if ((i - 2) % 5 == 4)
        {
          std::cout << "phase " << (int)((i - 2) / 5) << " valu:\t\t";
        }
        std::cout << _parameters[i] << std::endl;
      }
    }
    else
    {
      std::string msg = "param size does not fit any objects (" + std::to_string(_parameters.size()) + ")";
      print_error(msg, true);
    }
  }
  else
  {
    _parameters.resize(1);
    // std::string msg = "param needs to be initiated";
    // print_error( msg, true );
  }
  std::cout << ">" << std::endl;
}

/* ************** */
/* CREATE OBJECTS */
/* ************** */

void crpacking::create_spheres()
{
  /*
    Randomly generate spheres based on parameters
  */

  std::cout << "<crpacking::create_spheres" << std::endl;
  // STEP 1: INITIATE VARIABLES
  std::random_device r;
  std::default_random_engine generator(r());
  double dx = _lengths[0];
  double dy = _lengths[1];
  double dz = _lengths[2];
  double ox = _origin[0];
  double oy = _origin[1];
  double oz = _origin[2];
  // param[0] -> total volume fraction
  // param[1] -> rejection length
  // param[2+4*p+0] -> rmin of phase p
  // param[2+4*p+1] -> rmax of phase p
  // param[2+4*p+2] -> relative volume fraction of the phase
  // param[2+4*p+3] -> field value of the phase
  double volf_tot = _parameters[0];
  double reje_len = _parameters[1];
  if ((_parameters.size() - 2) % 4)
  {
    std::string msg = "param size = " + std::to_string(_parameters.size()) + ": size of param vector should be ( 2 + 4n ) with n the number of phase";
    print_error(msg, true);
  }
  _n_phases = (_parameters.size() - 2) / 4;
  _phases_values.resize(_n_phases);
  std::cout << ".\t total volume fraction: " << volf_tot << std::endl;
  std::cout << ".\t rejection length: " << reje_len << std::endl;
  std::cout << ".\t number of phases: " << _n_phases << std::endl;
  std::vector<unsigned int> n_spheres_per_phase(_n_phases);
  std::vector<double> volf_per_phase(_n_phases); // just for the record in order to plot summary at the end of the function
  _n_objects = 0;
  // STEP 2: LOOP 1 OVER THE PHASES (compute the number of spheres)
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double rmin = _parameters[4 * p + 2];
    double rmax = _parameters[4 * p + 3];
    double volf = _parameters[4 * p + 4] * volf_tot;
    unsigned int valu = (unsigned int)_parameters[4 * p + 5];
    _phases_values[p] = _parameters[4 * p + 5];
    volf_per_phase[p] = volf;
    double ra = 0.0;
    if (!_inside)
    {
      ra = 4. * rmax / 3.;
    } // radius added in case  inside == False
    double vol_domain = 0.0;
    if (_domain_type == "cube")
    {
      vol_domain = (dx + ra) * (dy + ra) * (dz + ra);
    }
    else if (_domain_type == "cylinder")
    {
      vol_domain = M_PI * pow(0.5 * (dx + ra), 2) * (dz + ra);
    }
    else
    {
      std::string msg = "unkown domain type \'" + _domain_type + "\'";
      print_error(msg, true);
    }
    if (rmin != rmax)
    {
      n_spheres_per_phase[p] = volf * (vol_domain)*3. * (rmax - rmin) / (M_PI * (pow(rmax, 4) - pow(rmin, 4))); // compute the number of spheres
    }
    else
    {
      n_spheres_per_phase[p] = volf * (vol_domain)*3. / (4 * M_PI * (pow(rmax, 3))); // compute the number of spheres
    }
    _n_objects += n_spheres_per_phase[p];
    std::cout << ".\t phase number: " << p << std::endl;
    std::cout << ".\t .\t rmin: " << rmin << std::endl;
    std::cout << ".\t .\t rmax: " << rmax << std::endl;
    std::cout << ".\t .\t volf: " << volf << std::endl;
    std::cout << ".\t .\t valu: " << valu << std::endl;
    // test if minimal radius rmin > rejection length
    if (rmin < reje_len)
    {
      std::string msg = "minimal radius lower than rejection length for phase " + std::to_string(p) + ": " + std::to_string(rmin) + " < " + std::to_string(reje_len);
      print_error(msg, true);
    }
    if (rmax < rmin)
    {
      std::string msg = "maximal radius lower than minimal radius for phase " + std::to_string(p) + ": " + std::to_string(rmax) + " < " + std::to_string(rmin);
      print_error(msg, true);
    }
  } // end loop 1 over phases
  // STEP 3: CREATION OF THE _objects vector
  _objects.resize(_n_objects);
  for (unsigned int i = 0; i < _n_objects; i++)
  {
    _objects[i].resize(5);
  }
  // LOOP 2 OVER THE PHASES (put the spheres randomly)
  // keep track of the indice in the global _objects vector
  unsigned int pi = 0;
  std::vector<double> volf_per_phase_real(_n_phases); // just for the record in order to plot summary at the end of the function
  double volf_tot_real = 0.0;
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double rmin = _parameters[4 * p + 2];
    double rmax = _parameters[4 * p + 3];
    unsigned int valu = (unsigned int)_parameters[4 * p + 5];
    volf_per_phase_real[p] = 0.0;
    std::uniform_real_distribution<double> u_distr_r(rmin, rmax);
    double add_r = 0.0;
    if (_inside)
    {
      add_r = rmax;
    }
    if (_domain_type == "cube")
    {
      std::uniform_real_distribution<double> u_distr_x(ox + add_r, ox + dx - add_r);
      std::uniform_real_distribution<double> u_distr_y(oy + add_r, oy + dy - add_r);
      std::uniform_real_distribution<double> u_distr_z(oz + add_r, oz + dz - add_r);
      // to compare the resulting volume fraction with the input
      double rmin_real = rmax;
      double rmax_real = rmin;
      // LOOP OVER THE SPHERES (set radius, x, y, z and field value)
      for (unsigned int i = 0; i < n_spheres_per_phase[p]; i++)
      {
        _objects[pi][0] = u_distr_r(generator); // radius
        _objects[pi][1] = u_distr_x(generator); // position x
        _objects[pi][2] = u_distr_y(generator); // position y
        _objects[pi][3] = u_distr_z(generator); // position z
        _objects[pi][4] = valu;                 // value of the field
        if (_objects[pi][0] < rmin_real)
          rmin_real = _objects[pi][0];
        if (_objects[pi][0] > rmax_real)
          rmax_real = _objects[pi][0];
        volf_per_phase_real[p] += 4. * M_PI * pow(_objects[pi][0], 3) / (3. * (dx * dy * dz));
        pi++;
      }
      volf_tot_real += volf_per_phase_real[p];
    }
    else if (_domain_type == "cylinder")
    {
      std::uniform_real_distribution<double> u_distr_z(oz + add_r, oz + dz - add_r);
      std::uniform_real_distribution<double> u_distr_d(0.0, 0.5 * dx - add_r);
      std::uniform_real_distribution<double> u_distr_theta(0.0, 2.0 * M_PI);
      // to compare the resulting volume fraction with the input
      double rmin_real = rmax;
      double rmax_real = rmin;
      // LOOP OVER THE SPHERES (set radius, x, y, z and field value)
      for (unsigned int i = 0; i < n_spheres_per_phase[p]; i++)
      {
        _objects[pi][0] = u_distr_r(generator); // radius
        double d = u_distr_d(generator);
        double theta = u_distr_theta(generator);
        _objects[pi][1] = d * cos(theta) + 0.5 * dx + ox; // position x
        _objects[pi][2] = d * sin(theta) + 0.5 * dx + oy; // position y
        _objects[pi][3] = u_distr_z(generator);           // position z
        _objects[pi][4] = valu;                           // value of the field
        if (_objects[pi][0] < rmin_real)
          rmin_real = _objects[pi][0];
        if (_objects[pi][0] > rmax_real)
          rmax_real = _objects[pi][0];
        volf_per_phase_real[p] += 4. * M_PI * pow(_objects[pi][0], 3) / (3. * (M_PI * pow(0.5 * dx, 2) * dz)); // divided by pi*r^2*h
        pi++;
      }
      volf_tot_real += volf_per_phase_real[p];
    }
    else
    {
      std::string msg = "unkown domain type \'" + _domain_type + "\'";
      print_error(msg, true);
    }
  }
  // Output VOLUME FRACTION
  std::cout << ".\t volume fraction" << std::endl;
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double a = volf_per_phase[p];
    double b = volf_per_phase_real[p];
    std::cout << std::fixed << std::setprecision(4) << ".\t .\t phase " << p << " --- target: " << a << " actual: " << b << " error: " << std::setprecision(0) << std::abs(a - b) / a * 100. << "%" << std::endl;
  }
  double a = volf_tot;
  double b = volf_tot_real;
  std::cout << std::fixed << std::setprecision(4) << ".\t .\t total ----- target: " << a << " actual: " << b << " error: " << std::setprecision(0) << std::abs(a - b) / a * 100. << "%" << std::endl;
  // Output VOLUME FRACTION
  std::cout << ".\t number of objects" << std::endl;
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double a = n_spheres_per_phase[p];
    std::cout << ".\t .\t phase " << p << ": " << a << std::endl;
  }
  std::cout << ".\t .\t total: " << _n_objects << std::endl;
  std::cout << ">" << std::endl;
}

void crpacking::create_ellipsoids()
{
  /*
    Randomly generate ellipsoids based on parameters
  */

  std::cout << "<crpacking::create_ellipsoids" << std::endl;
  // STEP 1 : INITIATE VARIABLES
  //  std::random_device r;
  //  std::default_random_engine generator( r() );
  double dx = _lengths[0];
  double dy = _lengths[1];
  double dz = _lengths[2];
  double ox = _origin[0];
  double oy = _origin[1];
  double oz = _origin[2];
  // param[0] -> total volume fraction
  // param[1] -> rejection length
  // param[2+5*p+0] -> rx
  // param[2+5*p+1] -> ry
  // param[2+5*p+2] -> rz
  // param[2+5*p+3] -> relative volume fraction of the phase
  // param[2+5*p+4] -> field value of the phase
  double volf_tot = _parameters[0];
  double reje_len = _parameters[1];
  if ((_parameters.size() - 2) % 5)
  {
    std::string msg = "param for ellipsoids: size of param vector should be 5.n+2 with n the number of phase. Here param size = " + std::to_string(_parameters.size());
    print_error(msg, true);
  }
  _n_phases = (_parameters.size() - 2) / 5;
  _phases_values.resize(_n_phases);
  std::cout << ".\t total volume fraction: " << volf_tot << std::endl;
  std::cout << ".\t rejection length: " << reje_len << std::endl;
  std::cout << ".\t number of phases: " << _n_phases << std::endl;
  std::vector<unsigned int> n_spheres_per_phase(_n_phases);
  std::vector<double> volf_per_phase(_n_phases); // just for the record in order to plot summary at the end of the function
  _n_objects = 0;
  // STEP 2 : LOOP 1 OVER THE PHASES (compute the number of spheres)
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double rx = _parameters[2 + 5 * p + 0];
    double ry = _parameters[2 + 5 * p + 1];
    double rz = _parameters[2 + 5 * p + 2];
    std::cout << ".\t rays of phase " << p << std::endl;
    std::cout << ".\t .\t rx = " << rx << std::endl;
    std::cout << ".\t .\t ry = " << ry << std::endl;
    std::cout << ".\t .\t rz = " << rz << std::endl;
    double volf = _parameters[2 + 5 * p + 3] * volf_tot;
    volf_per_phase[p] = volf;
    double rax = 0.0;
    if (!_inside)
    {
      rax = 4. * rx / 3.;
    } // radius added in case  inside == False
    double ray = 0.0;
    if (!_inside)
    {
      ray = 4. * ry / 3.;
    } // radius added in case  inside == False
    double raz = 0.0;
    if (!_inside)
    {
      raz = 4. * rz / 3.;
    }                                                                                                          // radius added in case  inside == False
    n_spheres_per_phase[p] = volf * ((dx + rax) * (dy + ray) * (dz + raz)) * 3. / (4 * M_PI * (rx * ry * rz)); // compute the number of spheres
    _n_objects += n_spheres_per_phase[p];
    // test if minimal radius rmin > rejection length
    if ((rx < reje_len) || (ry < reje_len) || (rz < reje_len))
    {
      std::string msg = "minimal radius lower than rejection length";
      print_error(msg, true);
    }
  } // end loop 1 over phases
  // STEP 3 : CREATION OF THE _objects vector
  _objects.resize(_n_objects);
  for (unsigned int i = 0; i < _n_objects; i++)
  {
    _objects[i].resize(7);
  }
  // LOOP 2 OVER THE PHASES (put the spheres randomly)
  // keep track of the indice in the global _objects vector
  unsigned int pi = 0;
  std::vector<double> volf_per_phase_real(_n_phases); // just for the record in order to plot summary at the end of the function
  double volf_tot_real = 0.0;
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double rx = _parameters[5 * p + 2 + 0];
    double ry = _parameters[5 * p + 2 + 1];
    double rz = _parameters[5 * p + 2 + 2];
    double valu = _parameters[5 * p + 2 + 4];
    _phases_values[p] = valu;
    volf_per_phase_real[p] = 0.0;
    // to compare the resulting volume fraction with the input
    std::random_device r;
    std::default_random_engine generator(r());
    std::uniform_real_distribution<double> u_distr_x(ox + rx, ox + dx - rx);
    std::uniform_real_distribution<double> u_distr_y(oy + ry, oy + dy - ry);
    std::uniform_real_distribution<double> u_distr_z(oz + rz, oz + dz - rz);
    // LOOP OVER THE SPHERES (set radius, x, y, z and field value)
    for (unsigned int i = 0; i < n_spheres_per_phase[p]; i++)
    {
      _objects[pi][0] = u_distr_x(generator); // position x
      _objects[pi][1] = u_distr_y(generator); // position y
      _objects[pi][2] = u_distr_z(generator); // position z
      _objects[pi][3] = rx;                   // radius
      _objects[pi][4] = ry;                   // radius
      _objects[pi][5] = rz;                   // radius
      _objects[pi][6] = valu;                 // value of the field
      volf_per_phase_real[p] += 4. * M_PI * _objects[pi][3] * _objects[pi][4] * _objects[pi][5] / (3. * (dx * dy * dz));
      pi++;
    }
    volf_tot_real += volf_per_phase_real[p];
  }
  // Output VOLUME FRACTION
  std::cout << ".\t volume fraction" << std::endl;
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double a = volf_per_phase[p];
    double b = volf_per_phase_real[p];
    std::cout << std::fixed << std::setprecision(4) << ".\t .\t phase " << p << " --- target: " << a << " actual: " << b << " error: " << std::setprecision(0) << std::abs(a - b) / a * 100. << "%" << std::endl;
  }
  double a = volf_tot;
  double b = volf_tot_real;
  std::cout << std::fixed << std::setprecision(4) << ".\t .\t total ----- target: " << a << " actual: " << b << " error: " << std::setprecision(0) << std::abs(a - b) / a * 100. << "%" << std::endl;
  // Output VOLUME FRACTION
  std::cout << ".\t number of ellipsoids" << std::endl;
  for (unsigned int p = 0; p < _n_phases; p++)
  {
    double a = n_spheres_per_phase[p];
    std::cout << ".\t .\t phase " << p << ": " << a << std::endl;
  }
  std::cout << ".\t .\t total  : " << _n_objects << std::endl;
  std::cout << ">" << std::endl;
}

void crpacking::set_objects(std::vector<std::vector<double>> objects)
{
  /*
    Setup objects variables based on known list of objects
  */
  std::cout << "<crpacking::set_objects" << std::endl;
  _objects = objects;
  for (unsigned int i_object = 0; i_object < _objects.size(); i_object++)
  {
    // get phase number
    unsigned int p = _objects[i_object].back();
    _phases_values.push_back(p);
  }
  std::sort(_phases_values.begin(), _phases_values.end());
  auto last = std::unique(_phases_values.begin(), _phases_values.end());
  _phases_values.erase(last, _phases_values.end());

  _n_objects = _objects.size();
  _n_phases = _phases_values.size();
  std::cout << ".\t number of objects: " << _n_objects << std::endl;
  std::cout << ".\t number of phases: " << _n_phases << std::endl;
  std::cout << ">" << std::endl;
}

/* ************ */
/* PACK OBJECTS */
/* ************ */

void crpacking::_set_intersections(unsigned int type)
{
  /* Determines the intersections for the packing algorithms */

  _int_s.clear();
  _int_p.clear();
  _int_n = 0;
  // type == 0 -> spheres
  // type == 1 -> ellipsoids
  if (type == 0)
  {
    // computes distances if intersection
    for (unsigned int i = 0; i < _n_objects; i++)
    {
      std::vector<double> push(3);
      push[0] = 0.0;
      push[1] = 0.0;
      push[2] = 0.0;
      bool intersect = false;
      for (unsigned int j = 0; j < _n_objects; j++)
      {
        if (i != j)
        {
          double d = sqrt(pow(_objects[i][1] - _objects[j][1], 2) +
                          pow(_objects[i][2] - _objects[j][2], 2) +
                          pow(_objects[i][3] - _objects[j][3], 2));
          double rpr = _objects[i][0] + _objects[j][0];
          if (d < rpr)
          { // intersection between i and j
            intersect = true;
            double alpha = _objects[j][0] * (pow(d / rpr, 2) - 1.);
            std::vector<double> beta(3);
            for (unsigned int k = 0; k < 3; k++)
            {
              if (d > 0.0000001)
              {
                beta[k] = (_objects[j][k + 1] - _objects[i][k + 1]) / d;
              }
              else
              {
                beta[k] = 1.0;
              }
              push[k] += alpha * beta[k];
            }
            // std::cout << d << " " << alpha << " " << push[0] << " "  << push[1] << " "  << push[2] << std::endl;
          }
        }
      }
      if (intersect)
      {
        _int_n++;
        _int_s.push_back(i);    // record sphere to move
        _int_p.push_back(push); // record how to move it
      }
    }
  }
  else if (type == 1)
  {
    std::vector<double> tmp_res;
    std::vector<double> tmp_res2;
    double coeff;
    // computes distances if intersection
    for (unsigned int i = 0; i < _n_objects; i++)
    {
      std::vector<double> push(3, 0.0);
      bool intersect = false;
      for (unsigned int j = 0; j < _n_objects; j++)
      {
        if ((i != j) && (_objects[i][3] == _objects[j][3]) && (_objects[i][4] == _objects[j][4]) && (_objects[i][5] == _objects[j][5]))
        {
          tmp_res = _determine_sphero(_objects[j], _objects[i]);
          if ((tmp_res[0] > 0))
          {
            intersect = true;
            coeff = tmp_res[1] * (pow((tmp_res[3] / (tmp_res[1] + tmp_res[2])), 2) - 1);
            if ((_objects[j][0] != _objects[i][0]) || (_objects[i][1] != _objects[j][1]) || (_objects[i][2] != _objects[j][2]))
            {
              for (unsigned k = 0; k < 3; k++)
              {
                push[k] += (_objects[j][k] - _objects[i][k]) / tmp_res[3] * coeff * _objects[j][k + 3] / tmp_res[1];
              }
            }
            else
            {
              if (i > j)
              {
                for (unsigned k = 0; k < 3; k++)
                {
                  push[k] += tmp_res[2];
                }
              }
              else
              {
                for (unsigned k = 0; k < 3; k++)
                {
                  push[k] += (-1 * tmp_res[2]);
                }
              }
            }
          }
        }
        else if (i != j)
        {
          tmp_res = _determine_sphero(_objects[i], _objects[j]);
          if ((tmp_res[0] > 0))
          {
            intersect = true;
            coeff = tmp_res[1] * (pow((tmp_res[3] / (tmp_res[1] + tmp_res[2])), 2) - 1);
            if ((_objects[i][0] != _objects[j][0]) || (_objects[i][1] != _objects[j][1]) || (_objects[i][2] != _objects[j][2]))
            {
              for (unsigned k = 0; k < 3; k++)
              {
                push[k] += (_objects[j][k] - _objects[i][k]) / tmp_res[3] * coeff * _objects[j][k + 3] / tmp_res[1];
              }
            }
            else
            {
              if (i > j)
              {
                for (unsigned k = 0; k < 3; k++)
                {
                  push[k] += tmp_res[2];
                }
              }
              else
              {
                for (unsigned k = 0; k < 3; k++)
                {
                  push[k] += (-1 * tmp_res[2]);
                }
              }
            }
          }
          else
          {
            double rsphere = 0;
            if ((_objects[i][3] == _objects[i][4]) && (_objects[i][3] == _objects[i][5]))
            {
              tmp_res2 = _inter_sphero(_objects[j], _objects[i]);
              tmp_res[1] = tmp_res2[0];
              tmp_res[2] = _objects[i][4];
              rsphere = _objects[i][4];
            }
            else if ((_objects[j][3] == _objects[j][4]) && (_objects[j][3] == _objects[j][5]))
            {
              tmp_res2 = _inter_sphero(_objects[i], _objects[j]);
              tmp_res[1] = _objects[j][4];
              tmp_res[2] = tmp_res2[0];
              rsphere = _objects[j][4];
            }
            else
            {
              std::string msg = "ellipsoids packing: case with two ellipsoids of different parameters not taken into account";
              print_error(msg, true);
            }
            if (rsphere > tmp_res2[4])
            {
              intersect = true;
              coeff = tmp_res[1] * (pow((tmp_res[3] / (tmp_res[1] + tmp_res[2])), 2) - 1);
              if ((_objects[j][0] != _objects[i][0]) || (_objects[i][1] != _objects[j][1]) || (_objects[i][2] != _objects[j][2]))
              {
                for (unsigned k = 0; k < 3; k++)
                {
                  push[k] += (_objects[j][k] - _objects[i][k]) / tmp_res[3] * coeff * _objects[j][k + 3] / tmp_res[1];
                }
              }
              else
              {
                if (i > j)
                {
                  for (unsigned k = 0; k < 3; k++)
                  {
                    push[k] += tmp_res[2];
                  }
                }
                else
                {
                  for (unsigned k = 0; k < 3; k++)
                  {
                    push[k] += (-1 * tmp_res[2]);
                  }
                }
              }
            }
          }
        }
      }
      if (intersect)
      {
        _int_n++;
        _int_s.push_back(i);    // record sphere to move
        _int_p.push_back(push); // record how to move it
      }
    }
  }
  else
  {
    std::string msg = "no type \'" + std::to_string(type) + "\' implemented in crpacking::_set_intersections( unsigned int type )";
    print_error(msg, true);
  }
}

std::vector<std::vector<double>> crpacking::pack_spheres(bool vtk = false)
{
  // Output
  std::cout << "<crpacking::pack_spheres" << std::endl;
  // STEP: increase sphere radii by reje_len
  double reje_len = _parameters[1];
  for (unsigned int i = 0; i < _n_objects; i++)
  {
    _objects[i][0] += reje_len;
  }
  // WHILE
  _int_n = 1;           // number of intersections
  unsigned int wit = 0; // while iteration (start at 1)
  if (vtk)
  {
    std::stringstream ss;
    ss << std::setw(5) << std::setfill('0') << wit;
    std::string vtk_file = _file_name + "_" + ss.str() + ".vtk";
    write_spheres_vtk(vtk_file);
  }
  // variable for the iteratif process
  double ener_o = 1.0;
  double ener_i = 1.0;
  double phi = 1.0;
  double err = 0.0001;
  unsigned int wit_max = 2000;
  unsigned int wit_min = 1;
  std::cout << ".\t iterations" << std::endl;
  while ((phi > err && wit < wit_max) || wit < wit_min)
  {
    wit++;
    double volu_tot_moving = 0.0;
    double dist_tot_moving = 0.0;

    if (wit == 1)
    { // force all objects to be checked on first iteration
      std::vector<double> push(3);
      for (unsigned int j = 0; j < _n_objects; j++)
      {
        _int_n++;
        _int_s.push_back(j);    // record sphere to move
        _int_p.push_back(push); // record how to move it
      }
    }
    else
    {
      _set_intersections(0); // 0 for spheres
    }
    // LOOP OVER INTERSECTED SPHERES
    for (unsigned int i = 0; i < _int_s.size(); i++)
    {
      // push coming from _set_intersection
      _objects[_int_s[i]][1] += _int_p[i][0];
      _objects[_int_s[i]][2] += _int_p[i][1];
      _objects[_int_s[i]][3] += _int_p[i][2];

      // check boundaries

      // compute boundary push energy
      std::vector<double> boundary_push = {0.0, 0.0, 0.0};

      // add radius if inside
      double add_r = (_inside) ? _objects[_int_s[i]][0] : 0.0;

      // in case of a cube
      if (_domain_type == "cube")
      {
        for (unsigned int j = 0; j < 3; j++)
        {
          if ((_objects[_int_s[i]][j + 1] + add_r) > (_origin[j] + _lengths[j]))
          {
            _objects[_int_s[i]][j + 1] = _origin[j] + _lengths[j] - add_r;
            boundary_push[j] = _origin[j] + _lengths[j] - add_r;
          }
          else if ((_objects[_int_s[i]][j + 1] - add_r) < _origin[j])
          {
            _objects[_int_s[i]][j + 1] = _origin[j] + add_r;
            boundary_push[j] = _origin[j] + add_r;
          }
        }
      }
      else if (_domain_type == "cylinder")
      {                                                   // in case of a cylinder
        double x = _objects[_int_s[i]][1];                // x of center of sphere
        double y = _objects[_int_s[i]][2];                // y of center of sphere
        double z = _objects[_int_s[i]][3];                // z of center of sphere
        double r = 0.5 * _lengths[0];                     // radius of the circle
        double x0 = r + _origin[0];                       // x center of circle
        double y0 = r + _origin[1];                       // y center of circle
        double h = _lengths[2];                           // height of the cylinder
        double d = sqrt(pow(x - x0, 2) + pow(y - y0, 2)); // initial distance between center of circle and sphere
        // test over height (z direction)
        if (z + add_r > _origin[2] + h)
        {
          _objects[_int_s[i]][3] = _origin[2] + h - add_r;
          boundary_push[2] = _origin[2] + h - add_r;
        }
        else if (z - add_r < _origin[2])
        {
          _objects[_int_s[i]][3] = _origin[2] + add_r;
          boundary_push[2] = _origin[2] + add_r;
        }
        if (d + add_r > r)
        { // test > radius
          _objects[_int_s[i]][1] = (x - x0) * (r - add_r) / d + x0;
          _objects[_int_s[i]][2] = (y - y0) * (r - add_r) / d + y0;
          boundary_push[1] += (x - x0) * (r - add_r) / d + x0;
          boundary_push[2] += (y - y0) * (r - add_r) / d + y0;
        }
      }
      else
      {
        std::string msg = "unkown domain type \'" + _domain_type + "\'";
        print_error(msg, true);
      }
      // compute a kind of total energy E = \sum volume_i*distance_i / volume_domaine
      dist_tot_moving += sqrt(pow(_int_p[i][0], 2) +
                              pow(_int_p[i][1], 2) +
                              pow(_int_p[i][2], 2));

      dist_tot_moving += sqrt(pow(boundary_push[0], 2) +
                              pow(boundary_push[1], 2) +
                              pow(boundary_push[2], 2));

      volu_tot_moving += 4. * M_PI * pow(_objects[i][0] - reje_len, 3) / 3.;
    } // END LOOP OVER INTERSECTED SPHERES
    if (wit == 1)
    {
      ener_o = dist_tot_moving * volu_tot_moving;
    }
    ener_i = dist_tot_moving * volu_tot_moving;
    if (ener_o < 1e-16)
    {
      phi = 0.0;
    }
    else
    {
      phi = ener_i / ener_o;
    }
    std::cout << ".\t .\t";
    std::cout << " iter: " << std::setw(5) << std::setfill('0') << wit;
    std::cout << " phi: " << std::fixed << std::setprecision(5) << phi;
    std::cout << " n_int: " << std::setw(5) << std::setfill('0') << _int_n;
    std::cout << std::endl;
    if (vtk)
    {
      std::stringstream ss;
      ss << std::setw(5) << std::setfill('0') << wit;
      std::string vtk_file = _file_name + "_" + ss.str() + ".vtk";
      write_spheres_vtk(vtk_file);
    }
  }
  wit++;
  // STEP: decrease sphere radii by reje_len
  for (unsigned int i = 0; i < _n_objects; i++)
  {
    _objects[i][0] -= reje_len;
  }
  _set_intersections(0); // 0 for spheres
  std::cout << ".\t radius reduction                 n_int: " << _int_n << std::endl;
  if (vtk)
  {
    std::string vtk_file = _file_name + "_final.vtk";
    write_spheres_vtk(vtk_file);
  }
  std::cout << ">" << std::endl;
  return _objects;
}

std::vector<double> crpacking::_determine_sphero(const std::vector<double> &s1, const std::vector<double> &s2)
{
  /* determines the ellipsoids spherocity for the ellopsoids packing algorithm */

  double k1 = 1.0 / sqrt(pow((s1[0] - s2[0]) / s1[3], 2) + pow((s1[1] - s2[1]) / s1[4], 2) + pow((s1[2] - s2[2]) / s1[5], 2));
  double k2 = 1.0 / sqrt(pow((s1[0] - s2[0]) / s2[3], 2) + pow((s1[1] - s2[1]) / s2[4], 2) + pow((s1[2] - s2[2]) / s2[5], 2));
  double d1 = sqrt(pow(s1[0] - ((s2[0] - s1[0]) * k1 + s1[0]), 2) + pow(s1[1] - ((s2[1] - s1[1]) * k1 + s1[1]), 2) + pow(s1[2] - ((s2[2] - s1[2]) * k1 + s1[2]), 2));
  double d2 = sqrt(pow(s2[0] - ((s1[0] - s2[0]) * k2 + s2[0]), 2) + pow(s2[1] - ((s1[1] - s2[1]) * k2 + s2[1]), 2) + pow(s2[2] - ((s1[2] - s2[2]) * k2 + s2[2]), 2));
  double d3 = sqrt(pow(s1[0] - s2[0], 2) + pow(s1[1] - s2[1], 2) + pow(s1[2] - s2[2], 2));
  double dist = 0;
  if (d1 + d2 > d3)
  {
    dist = sqrt(pow((s2[0] - s1[0]) * k1 + s1[0] - (s1[0] - s2[0]) * k2 - s2[0], 2) + pow((s2[1] - s1[1]) * k1 + s1[1] - (s1[1] - s2[1]) * k2 - s2[1], 2) + pow((s2[2] - s1[2]) * k1 + s1[2] - (s1[2] - s2[2]) * k2 - s2[2], 2));
  }
  std::vector<double> result(4);
  result[0] = dist;
  result[1] = d1;
  result[2] = d2;
  result[3] = d3;
  return result;
}

std::vector<double> crpacking::_inter_sphero(const std::vector<double> &s1, const std::vector<double> &s2)
{
  /* determines the ellipsoids intersection spherocity for the ellopsoids packing algorithm */

  double x0 = 0;
  double x1 = 0.1;
  int count = 0;
  while (fabs((x1 - x0) / x1) > 0.001)
  {
    x0 = x1;
    double sum1 = pow(1.0 / s1[3], 2) * (s2[0] - s1[0]) * (s2[0] - s1[0]) / pow(1 + x0 * pow(1.0 / s1[3], 2), 2);
    sum1 += pow(1.0 / s1[4], 2) * (s2[1] - s1[1]) * (s2[1] - s1[1]) / pow(1 + x0 * pow(1.0 / s1[4], 2), 2);
    sum1 += pow(1.0 / s1[5], 2) * (s2[2] - s1[2]) * (s2[2] - s1[2]) / pow(1 + x0 * pow(1.0 / s1[5], 2), 2);
    double sum2 = pow(1.0 / s1[3], 4) * (s2[0] - s1[0]) * (s2[0] - s1[0]) / pow(1 + x0 * pow(1.0 / s1[3], 2), 3);
    sum2 += pow(1.0 / s1[4], 4) * (s2[1] - s1[1]) * (s2[1] - s1[1]) / pow(1 + x0 * pow(1.0 / s1[4], 2), 3);
    sum2 += pow(1.0 / s1[5], 4) * (s2[2] - s1[2]) * (s2[2] - s1[2]) / pow(1 + x0 * pow(1.0 / s1[5], 2), 3);
    x1 = x0 - (sum1 - 1) / (-2 * sum2);
    count++;
    if (count > 1000)
    {
      std::cout << "Trop d'iteration dans le calcul de la distance minimum\n\n";
      break;
    }
  }
  std::vector<double> z(5);
  z[1] = (s2[0] - s1[0]) / (1 + x1 * pow(1.0 / s1[3], 2)) + s1[0];
  z[2] = (s2[1] - s1[1]) / (1 + x1 * pow(1.0 / s1[4], 2)) + s1[1];
  z[3] = (s2[2] - s1[2]) / (1 + x1 * pow(1.0 / s1[5], 2)) + s1[2];
  z[0] = sqrt(pow(s1[0] - z[1], 2) + pow(s1[1] - z[2], 2) + pow(s1[2] - z[3], 2));
  z[4] = sqrt(pow(s2[0] - z[1], 2) + pow(s2[1] - z[2], 2) + pow(s2[2] - z[3], 2));
  return z;
}

void crpacking::pack_ellipsoids()
{
  // Output
  std::cout << "<crpacking::pack_ellipsoids" << std::endl;
  // STEP : increase sphere radii by reje_len
  double reje_len = _parameters[1];
  for (unsigned int i = 0; i < _n_objects; i++)
  {
    _objects[i][3] += reje_len / 2.0;
    _objects[i][4] += reje_len / 2.0;
    _objects[i][5] += reje_len / 2.0;
  }
  // WHILE
  _int_n = 1;           // number of intersections
  unsigned int wit = 0; // while iteration (start at 1)
  // variable for the iteratif process
  double ener_o = 1.0;
  double ener_i = 1.0;
  double phi = 1.0;
  double err = 0.00001;
  unsigned int wit_max = 2000;
  unsigned int wit_min = 1;
  std::cout << ".\t iterations" << std::endl;
  while ((phi > err && wit < wit_max) || wit < wit_min)
  {
    wit++;
    double volu_tot_moving = 0.0;
    double dist_tot_moving = 0.0;
    // computes distances if intersection
    _set_intersections(1); // 1 for ellipsoids
    // LOOP OVER INTERSECTED SPHERES
    for (unsigned int i = 0; i < _int_s.size(); i++)
    {
      _objects[_int_s[i]][0] += _int_p[i][0];
      _objects[_int_s[i]][1] += _int_p[i][1];
      _objects[_int_s[i]][2] += _int_p[i][2];
      // check if it does not go out of the domain
      std::vector<double> add_r(3, 0.0);
      if (_inside)
      {
        add_r[0] = _objects[_int_s[i]][3] - reje_len / 2.0;
        add_r[1] = _objects[_int_s[i]][4] - reje_len / 2.0;
        add_r[2] = _objects[_int_s[i]][5] - reje_len / 2.0;
      } // add radius if inside
      for (unsigned int j = 0; j < 3; j++)
      {
        if ((_objects[_int_s[i]][j] + (add_r[j])) > (_origin[j] + _lengths[j]))
        {
          _objects[_int_s[i]][j] = _origin[j] + _lengths[j] - add_r[j];
        }
        else if ((_objects[_int_s[i]][j] - add_r[j]) < _origin[j])
        {
          _objects[_int_s[i]][j] = _origin[j] + add_r[j];
        }
      }
      // compute a kind of total energy E = \sum volume_i*distance_i / volume_domaine
      dist_tot_moving += sqrt(pow(_int_p[i][0], 2) +
                              pow(_int_p[i][1], 2) +
                              pow(_int_p[i][2], 2));
      volu_tot_moving += 4. * M_PI * (_objects[i][3] - reje_len / 2.0) * (_objects[i][4] - reje_len / 2.0) * (_objects[i][5] - reje_len / 2.0) / 3.;
    } // END LOOP OVER INTERSECTED SPHERES
    if (wit == 1)
    {
      ener_o = dist_tot_moving * volu_tot_moving;
    }
    ener_i = dist_tot_moving * volu_tot_moving;
    if (ener_o < 1e-16)
    {
      phi = 0.0;
    }
    else
    {
      phi = ener_i / ener_o;
    }
    std::cout << ".\t .\t iter: ";
    std::cout << std::setw(5) << std::setfill('0') << wit;
    std::cout << std::fixed << std::setprecision(5) << " phi: " << phi << " n_int: " << _int_n << std::endl;
  }
  wit++;
  // STEP : decrease sphere radii by reje_len
  for (unsigned int i = 0; i < _n_objects; i++)
  {
    _objects[i][3] -= reje_len / 2.0;
    _objects[i][4] -= reje_len / 2.0;
    _objects[i][5] -= reje_len / 2.0;
  }
  _set_intersections(1); // 1 for ellipsoids
  std::cout << ".\t radius reduction           n_int: " << _int_n << std::endl;
  std::cout << ">" << std::endl;
}

/* *** */
/* GET */
/* *** */

std::vector<std::vector<double>> crpacking::get_objects() { return _objects; }

/* ********* */
/* WRITE VTK */
/* ********* */

void crpacking::write_spheres_vtk(std::string file_name)
{
  if (file_name.empty())
  {
    file_name = _file_name + ".vtk";
  }

  std::ofstream pfile;
  pfile.open(file_name, std::ios::out | std::ios::trunc);
  std::string sep = " ";
  if (pfile)
  {
    // write headers
    pfile << "# vtk DataFile Version 2.0" << std::endl;
    pfile << "Unstructured grid legacy vtk file with point scalar data" << std::endl;
    pfile << "ASCII" << std::endl;
    pfile << std::endl;
    // centers
    pfile << "DATASET UNSTRUCTURED_GRID" << std::endl;
    pfile << "POINTS " << _n_objects << " float" << std::endl;
    for (unsigned int i = 0; i < _n_objects; i++)
    {
      pfile << _objects[i][3] << sep
            << _objects[i][2] << sep
            << _objects[i][1] << std::endl;
    }
    pfile << std::endl;
    // radii
    pfile << "POINT_DATA " << _n_objects << std::endl;
    pfile << "SCALARS sphereID int" << std::endl;
    pfile << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _n_objects; i++)
    {
      pfile << i << std::endl;
    }
    pfile << std::endl;
    pfile << "SCALARS radii float" << std::endl;
    pfile << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _n_objects; i++)
    {
      pfile << _objects[i][0] << std::endl;
    }
    pfile << std::endl;
    // radii
    pfile << "SCALARS field float" << std::endl;
    pfile << "LOOKUP_TABLE default" << std::endl;
    for (unsigned int i = 0; i < _n_objects; i++)
    {
      pfile << _objects[i][4] << std::endl;
    }
    pfile << std::endl;
    pfile.close();
  }
  else
  {
    std::string msg = "can\'t open vtk file file \'" + file_name + "\'";
    print_error(msg, true);
  }
}
