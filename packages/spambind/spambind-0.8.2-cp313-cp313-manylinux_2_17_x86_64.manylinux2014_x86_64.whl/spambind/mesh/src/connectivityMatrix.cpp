//Define basic types from CGAL templates
#define ALPHASHAPES

#ifdef ALPHASHAPES
#include <CGAL/Alpha_shape_vertex_base_3.h>
#include <CGAL/Alpha_shape_cell_base_3.h>
#include <CGAL/Alpha_shape_3.h>
#endif

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Cartesian.h>
#include <CGAL/Regular_triangulation_3.h>
#if CGAL_VERSION_NR < CGAL_VERSION_NUMBER(4,11,0)
#include <CGAL/Regular_triangulation_euclidean_traits_3.h>
#endif

#include <CGAL/Triangulation_vertex_base_with_info_3.h>
#include <CGAL/Triangulation_cell_base_with_info_3.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/circulator.h>
#include <CGAL/number_utils.h>
#include <boost/static_assert.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "connectivityMatrix.hpp"

namespace py = pybind11;


//This include from yade let us use Eigen types
// #include <lib/base/Math.hpp>

//const unsigned facetVertices [4][3] = {{1,2,3},{0,2,3},{0,1,3},{0,1,2}};
////return the opposite edge (e.g. the opposite of {0,2} is {1,3})
//inline void revertEdge (unsigned &i,unsigned &j){
//    if (facetVertices[i][0]==j) {i=facetVertices[i][1];j=facetVertices[i][2];}
//    else if (facetVertices[i][1]==j) {i=facetVertices[i][0];j=facetVertices[i][2];}
//    else {j=facetVertices[i][1]; i=facetVertices[i][0];}
//}

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;

#if CGAL_VERSION_NR < CGAL_VERSION_NUMBER(4,11,0)
typedef CGAL::Regular_triangulation_euclidean_traits_3<K>   Traits;
#else
typedef K                                                   Traits;
#endif

typedef K::Point_3                                              Point;
#if CGAL_VERSION_NR < CGAL_VERSION_NUMBER(4,11,0)
typedef Traits::RT                                          Weight;
typedef Traits::Weighted_point                              Weighted_point;
#else
typedef Traits::FT                                          Weight;
typedef Traits::Weighted_point_3                            Weighted_point;
#endif
typedef Traits::Plane_3                                         Plane;
typedef Traits::Triangle_3                                      Triangle;
typedef Traits::Tetrahedron_3                                   Tetrahedron;

#if CGAL_VERSION_NR < CGAL_VERSION_NUMBER(4,11,0)
typedef CGAL::Triangulation_vertex_base_with_info_3<unsigned, Traits>       Vb_info;
typedef CGAL::Triangulation_cell_base_with_info_3<unsigned, Traits>         Cb_info;
#else
typedef CGAL::Regular_triangulation_vertex_base_3<K>                        Vb0;
typedef CGAL::Regular_triangulation_cell_base_3<K>                          Rcb;
typedef CGAL::Triangulation_vertex_base_with_info_3<unsigned, Traits, Vb0>  Vb_info;
typedef CGAL::Triangulation_cell_base_with_info_3<unsigned, Traits, Rcb>    Cb_info;
#endif

#ifdef ALPHASHAPES
typedef CGAL::Alpha_shape_vertex_base_3<Traits,Vb_info> Vb;
typedef CGAL::Alpha_shape_cell_base_3<Traits,Cb_info>   Fb;
typedef CGAL::Triangulation_data_structure_3<Vb, Fb>	Tds;
#else
typedef CGAL::Triangulation_data_structure_3<Vb_info, Cb_info>  Tds;
#endif
typedef CGAL::Triangulation_3<K>                                Triangulation;
typedef CGAL::Regular_triangulation_3<Traits, Tds>              RTriangulation;

#ifdef ALPHASHAPES
typedef CGAL::Alpha_shape_3<RTriangulation>  			AlphaShape;
typedef typename AlphaShape::Alpha_iterator			Alpha_iterator;
typedef AlphaShape::Cell_handle                                 Cell_handle;
#endif


// extern "C"

int countTetrahedraCGAL( py::array_t<float> numTetrahedra_verticesNumpy,
        py::array_t<float> numTetrahedra_weightsNumpy,
        py::array_t<float> numTetrahedra_alphaNumpy)
        {

                py::buffer_info numTetrahedra_verticesBuf = numTetrahedra_verticesNumpy.request();
                py::buffer_info numTetrahedra_weightsBuf = numTetrahedra_weightsNumpy.request();
                py::buffer_info numTetrahedra_alphaBuf = numTetrahedra_alphaNumpy.request();

                float *numTetrahedra_vertices = (float*) numTetrahedra_verticesBuf.ptr;
                float *numTetrahedra_weights = (float*) numTetrahedra_weightsBuf.ptr;
                float *numTetrahedra_alpha = (float*) numTetrahedra_alphaBuf.ptr;

                int numTetrahedra_numVertices = (int) numTetrahedra_verticesBuf.shape[0];

                float x,y,z;
                std::vector<std::pair<Weighted_point,unsigned>> points;

                // create point pairs and delaunay triangulate
                for (int i=0; i<numTetrahedra_numVertices; i++)
                {
                        z = (float)numTetrahedra_vertices[3*i+0];
                        y = (float)numTetrahedra_vertices[3*i+1];
                        x = (float)numTetrahedra_vertices[3*i+2];
                        Point p(z,y,x);
                        Weight w=(float)numTetrahedra_weights[i];
                        // 2020-03-23: EA: Try to auto-avoid NaNs
                        if ( ! std::isnan(z) )
                        {
                            points.push_back(std::make_pair(Weighted_point(p,w),i));
                        }
                }
                RTriangulation T(points.begin(),points.end());
                if (numTetrahedra_alpha[0]!=0){
                        RTriangulation temp ( T );
                        AlphaShape as ( temp );
                        double minAlpha = as.find_alpha_solid();
                        if (numTetrahedra_alpha[0]<0||numTetrahedra_alpha[0]<minAlpha) {
                                numTetrahedra_alpha[0] = minAlpha;
                        }
                        as.set_alpha ( numTetrahedra_alpha[0] );
                        RTriangulation::Finite_cells_iterator cell_end = as.finite_cells_end();
                        uint32_t numAlpha = 0;
                        for ( RTriangulation::Finite_cells_iterator cell = as.finite_cells_begin(); cell != cell_end; cell++ ){
                                if (as.classify(cell)==AlphaShape::INTERIOR||as.classify(cell)==AlphaShape::REGULAR) {
                                        numAlpha++;
                                }
                        }
                        //std::cout << "count tets::found "<<numAlpha << " cells out of total " << as.number_of_finite_cells() << std::endl;
                        CGAL_assertion(as.number_of_vertices() == numTetrahedra_numVertices);
                        return (uint32_t) numAlpha;
                }else{
                        CGAL_assertion(T.number_of_vertices() == numTetrahedra_numVertices);
                        return (uint32_t)T.number_of_finite_cells();
                }
        }


void triangulateCGAL(   py::array_t<float> connectivityMatrix_verticesNumpy,
        py::array_t<float> connectivityMatrix_weightsNumpy,
        py::array_t<unsigned int> connectivityMatrix_connectivityNumpy,
        py::array_t<float> numTetrahedra_alphaNumpy)
        {

                py::buffer_info connectivityMatrix_verticesBuf = connectivityMatrix_verticesNumpy.request();
                py::buffer_info connectivityMatrix_weightsBuf = connectivityMatrix_weightsNumpy.request();
                py::buffer_info connectivityMatrix_connectivityBuf = connectivityMatrix_connectivityNumpy.request();
                py::buffer_info numTetrahedra_alphaBuf = numTetrahedra_alphaNumpy.request();

                float *connectivityMatrix_vertices = (float*) connectivityMatrix_verticesBuf.ptr;
                float *connectivityMatrix_weights = (float*) connectivityMatrix_weightsBuf.ptr;
                unsigned int *connectivityMatrix_connectivity = (unsigned int*) connectivityMatrix_connectivityBuf.ptr;
                float *numTetrahedra_alpha = (float*) numTetrahedra_alphaBuf.ptr;

                int connectivityMatrix_numVertices = (int) connectivityMatrix_verticesBuf.shape[0];

                float x,y,z;
                std::vector<std::pair<Weighted_point,unsigned>> points;

                // create point pairs and delaunay triangulate
                for (int i=0; i<connectivityMatrix_numVertices; i++)
                {
                        z = (float)connectivityMatrix_vertices[3*i+0];
                        y = (float)connectivityMatrix_vertices[3*i+1];
                        x = (float)connectivityMatrix_vertices[3*i+2];
                        Point p(z,y,x);
                        Weight w=(float)connectivityMatrix_weights[i];
                        // 2020-03-23: EA: Try to auto-avoid NaNs
                        if ( ! std::isnan(z) )
                        {
                            points.push_back(std::make_pair(Weighted_point(p,w),i));
                            //std::cout<<"Point made "<<x << " " << " " << y << " " << z << " id " << i << std::endl;
                        }
                }
                RTriangulation T(points.begin(),points.end());
                std::vector<bool> fullCellList(T.number_of_finite_cells(),false);
                //std::cout << " len of fullcelllist " << fullCellList.size() << std::endl;

                if (numTetrahedra_alpha[0]!=0){
                        RTriangulation temp ( T );
                        AlphaShape as ( temp );
                        //std::cout << "running alpha mode with alpha" << numTetrahedra_alpha[0] << std::endl;
                        double minAlpha = as.find_alpha_solid();
                        if (numTetrahedra_alpha[0]<0||numTetrahedra_alpha[0]<minAlpha) {
//                                 std::cerr<<"User passed negative value for alpha (or alpha<minValue for continous solid), letting CGAL automatically select the minimum alpha for a continous solid (swiss cheese mesh likely, consider increasing alpha)"<<std::endl;
                                numTetrahedra_alpha[0] = minAlpha;
                        }
                        as.set_alpha ( numTetrahedra_alpha[0] );
                        CGAL_assertion(as.number_of_vertices() == numTetrahedra_numVertices);
                        int numAlpha = 0; int i= 0;
                        RTriangulation::Finite_cells_iterator cell_end = as.finite_cells_end();
                        for ( RTriangulation::Finite_cells_iterator cell = as.finite_cells_begin(); cell != cell_end; cell++ ){
                                if (as.classify(cell)==AlphaShape::INTERIOR||as.classify(cell)==AlphaShape::REGULAR) {
                                        fullCellList[i] = true;
                                        numAlpha += 1;
                                }
                                i++;
                        }
                        //std::cout << "triangulate::using "<<numAlpha << " alpha cells out of the total " << as.number_of_finite_cells() << std::endl;

                }else{
                        // std::cout << "running in standard mode" << std::endl;
                        CGAL_assertion(T.number_of_vertices() == numTetrahedra_numVertices);
                }

                RTriangulation::Finite_cells_iterator cit; uint32_t tetNumber = 0; uint32_t cellNumber = 0;
                for (cit = T.finite_cells_begin(); cit != T.finite_cells_end(); cit++)
                {
                        //std::cout << "tet number "<<tetNumber<<std::endl;
                        if (numTetrahedra_alpha[0]!=0 && !fullCellList[cellNumber]) { cellNumber++; continue; } // if it is an external of the alpha, we don't add it to conn
                        for (uint32_t i=0;i<4;i++)
                        {
                                connectivityMatrix_connectivity[4*tetNumber+i] = (uint32_t) cit->vertex(i)->info();
                        }
                        tetNumber++; cellNumber++;
                }
        }
