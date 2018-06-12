/*
    Script to extract 6 point of view images for given point 
    cloud and axes.
*/

#include <iostream>
#include <string>
#include <boost/thread/thread.hpp>
#include <boost/filesystem.hpp>
#include <pcl/io/pcd_io.h>
#include <pcl/io/vtk_lib_io.h>
#include <pcl/visualization/pcl_visualizer.h>

using namespace std;

int main(int argc, char** argv){
    /*
    Parse arguments, which are present in this order:
    [mesh file] [output directory for images] [x][y][z] [x][y][z] [x][y][z]
    where the x,y,z's are the vectors for X, Y and Z axes respectively.
    */
    if(argc != 12){
        cout << "Invalid usage.\nUsage:\t./extract_pov [mesh file] [output directory for images] [x][y][z] [x][y][z] [x][y][z]\nExample:\t./extract_pov cube_output.vtk save/ 3 4 5 3 4 5 3 4 5" << endl;
        exit(1);
    }else{
        pcl::PolygonMesh mesh;
        string save_dir(argv[2]);

        // Load point cloud from PCD file
        std::cout << "Loading mesh from " << argv[1] << endl;
        pcl::io::loadPolygonFileVTK(argv[1], mesh);
        if(!boost::filesystem::exists(save_dir)){
            boost::filesystem::create_directory(save_dir);
        }
        // Initialize PCLVisualizer
        boost::shared_ptr<pcl::visualization::PCLVisualizer> viewer(new pcl::visualization::PCLVisualizer("Point Cloud Visualizer"));
        viewer->setBackgroundColor(0, 0, 0);
        // Add polygon mesh
        viewer->addPolygonMesh(mesh);
        // Initialize camera parameters
        viewer->initCameraParameters();
        viewer->resetCamera();
        viewer->spinOnce(10);
        boost::this_thread::sleep(boost::posix_time::microseconds(10000));

        // +X
        viewer->setCameraPosition(20.0 * stof(argv[3]), 20.0 * stof(argv[4]), 20.0 * stof(argv[5]), stof(argv[9]), stof(argv[10]), stof(argv[11]));
        viewer->resetCamera();
        viewer->spinOnce(10);
        // boost::this_thread::sleep(boost::posix_time::microseconds(50000));
        viewer->saveScreenshot(save_dir + "view_0.png");
        boost::this_thread::sleep(boost::posix_time::microseconds(10000));

        // +Y
        viewer->setCameraPosition(20.0 * stof(argv[6]), 20.0 * stof(argv[7]), 20.0 * stof(argv[8]), stof(argv[9]), stof(argv[10]), stof(argv[11]));
        viewer->resetCamera();
        viewer->spinOnce(10);
        // boost::this_thread::sleep(boost::posix_time::microseconds(50000));
        viewer->saveScreenshot(save_dir + "view_1.png");
        boost::this_thread::sleep(boost::posix_time::microseconds(10000));

        // +Z
        viewer->setCameraPosition(20.0 * stof(argv[9]), 20.0 * stof(argv[10]), 20.0 * stof(argv[11]), stof(argv[6]), stof(argv[7]), stof(argv[8]));
        viewer->resetCamera();
        viewer->spinOnce(10);
        // boost::this_thread::sleep(boost::posix_time::microseconds(50000));
        viewer->saveScreenshot(save_dir + "view_2.png");
        boost::this_thread::sleep(boost::posix_time::microseconds(10000));

        // -X
        viewer->setCameraPosition(-20.0 * stof(argv[3]), -20.0 * stof(argv[4]), -20.0 * stof(argv[5]), stof(argv[9]), stof(argv[10]), stof(argv[11]));
        viewer->resetCamera();
        viewer->spinOnce(10);
        // boost::this_thread::sleep(boost::posix_time::microseconds(50000));
        viewer->saveScreenshot(save_dir + "view_3.png");
        boost::this_thread::sleep(boost::posix_time::microseconds(10000));

        // -Y
        viewer->setCameraPosition(-20.0 * stof(argv[6]), -20.0 * stof(argv[7]), -20.0 * stof(argv[8]), stof(argv[9]), stof(argv[10]), stof(argv[11]));
        viewer->resetCamera();
        viewer->spinOnce(10);
        // boost::this_thread::sleep(boost::posix_time::microseconds(50000));
        viewer->saveScreenshot(save_dir + "view_4.png");
        boost::this_thread::sleep(boost::posix_time::microseconds(10000));

        // -Z
        viewer->setCameraPosition(-20.0 * stof(argv[9]), -20.0 * stof(argv[10]), -20.0 * stof(argv[11]), stof(argv[6]), stof(argv[7]), stof(argv[8]));
        viewer->resetCamera();
        viewer->spinOnce(10);
        // boost::this_thread::sleep(boost::posix_time::microseconds(50000));
        viewer->saveScreenshot(save_dir + "view_5.png");
        boost::this_thread::sleep(boost::posix_time::microseconds(10000));

        viewer->close();
    }
}