/* Adapted from http://pointclouds.org/documentation/tutorials/pcl_visualizer.php#pcl-visualizer */

#include <iostream>

#include <boost/thread/thread.hpp>
#include <pcl/common/common_headers.h>
#include <pcl/features/normal_3d.h>
#include <pcl/io/pcd_io.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/console/parse.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/surface/gp3.h>

void keyboardEventOccurred(const pcl::visualization::KeyboardEvent &, void *);
pcl::PointCloud<pcl::PointXYZ>::Ptr basic_cloud_ptr(new pcl::PointCloud<pcl::PointXYZ>);

// Usage instructions
void printUsage(const char *progName)
{
  std::cout << "Usage: \n"<<progName<<" [PCD data file]"<<endl;
}

boost::shared_ptr<pcl::visualization::PCLVisualizer> init_visualizer (pcl::PointCloud<pcl::PointXYZ>::ConstPtr cloud)
{
  // Open 3D viewer
  boost::shared_ptr<pcl::visualization::PCLVisualizer> viewer (new pcl::visualization::PCLVisualizer ("Point Cloud Visualizer"));
  viewer->setBackgroundColor (0, 0, 0);
  // Add callback function for keyboard events
  viewer->registerKeyboardCallback(keyboardEventOccurred, (void *)viewer.get());
  // Add point cloud
  viewer->addPointCloud<pcl::PointXYZ> (cloud, "Point Cloud");
  viewer->setPointCloudRenderingProperties (pcl::visualization::PCL_VISUALIZER_POINT_SIZE, 1, "Point Cloud");
  viewer->initCameraParameters ();
  return (viewer);
}

void keyboardEventOccurred (const pcl::visualization::KeyboardEvent &event, void* viewer_void){
  pcl::visualization::PCLVisualizer *viewer = static_cast<pcl::visualization::PCLVisualizer *>(viewer_void);
  if (event.getKeySym () == "r" && event.keyDown ()){
    std::cout << "Reconstructing surface." << std::endl;
    /* Surface reconstruction routine */
    // Normal estimation*
    pcl::NormalEstimation<pcl::PointXYZ, pcl::Normal> n;
    pcl::PointCloud<pcl::Normal>::Ptr normals(new pcl::PointCloud<pcl::Normal>);
    pcl::search::KdTree<pcl::PointXYZ>::Ptr tree(new pcl::search::KdTree<pcl::PointXYZ>);
    tree->setInputCloud(basic_cloud_ptr);
    n.setInputCloud(basic_cloud_ptr);
    n.setSearchMethod(tree);
    n.setKSearch(20);
    n.compute(*normals);
    //* normals should not contain the point normals + surface curvatures

    // Concatenate the XYZ and normal fields*
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud_with_normals(new pcl::PointCloud<pcl::PointNormal>);
    pcl::concatenateFields(*basic_cloud_ptr, *normals, *cloud_with_normals);
    //* cloud_with_normals = cloud + normals

    // Create search tree*
    pcl::search::KdTree<pcl::PointNormal>::Ptr tree2(new pcl::search::KdTree<pcl::PointNormal>);
    tree2->setInputCloud(cloud_with_normals);

    // Initialize objects
    pcl::GreedyProjectionTriangulation<pcl::PointNormal> gp3;
    pcl::PolygonMesh triangles;

    // Set the maximum distance between connected points (maximum edge length)
    gp3.setSearchRadius(0.005);

    // Set typical values for the parameters
    gp3.setMu(2.5);
    gp3.setMaximumNearestNeighbors(1000);
    gp3.setMaximumSurfaceAngle(M_PI / 4); // 45 degrees
    gp3.setMinimumAngle(M_PI / 18);       // 10 degrees
    gp3.setMaximumAngle(2 * M_PI / 3);    // 120 degrees
    gp3.setNormalConsistency(false);

    // Get result
    gp3.setInputCloud(cloud_with_normals);
    gp3.setSearchMethod(tree2);
    gp3.reconstruct(triangles);

    viewer->addPolygonMesh(triangles);
  }
  else if (event.getKeySym() == "n" && event.keyDown())
  {
    std::cout << "Constructing normals." << std::endl;
    // Normal construction routine
  }
  else if (event.getKeySym() == "c" && event.keyDown())
  {
    std::cout << "Reseting back to original." << std::endl;
    // Reset
  }
}

int main (int argc, char** argv){
  
  // Parse command line arguments
  if (argc != 2){
    printUsage (argv[0]);
    return 0;
  }

  // Load point cloud from PCD file
  std::cout << "Loading point cloud from "<<argv[1]<<endl;
  pcl::io::loadPCDFile(argv[1], *basic_cloud_ptr);
  
  // basic_cloud_ptr->width = (int) basic_cloud_ptr->points.size ();
  // basic_cloud_ptr->height = 1;
  // point_cloud_ptr->width = (int) point_cloud_ptr->points.size ();
  // point_cloud_ptr->height = 1;

  // // ----------------------------------------------------------------
  // // -----Calculate surface normals with a search radius of 0.05-----
  // // ----------------------------------------------------------------
  // pcl::NormalEstimation<pcl::PointXYZRGB, pcl::Normal> ne;
  // ne.setInputCloud (point_cloud_ptr);
  // pcl::search::KdTree<pcl::PointXYZRGB>::Ptr tree (new pcl::search::KdTree<pcl::PointXYZRGB> ());
  // ne.setSearchMethod (tree);
  // pcl::PointCloud<pcl::Normal>::Ptr cloud_normals1 (new pcl::PointCloud<pcl::Normal>);
  // ne.setRadiusSearch (0.05);
  // ne.compute (*cloud_normals1);

  // // ---------------------------------------------------------------
  // // -----Calculate surface normals with a search radius of 0.1-----
  // // ---------------------------------------------------------------
  // pcl::PointCloud<pcl::Normal>::Ptr cloud_normals2 (new pcl::PointCloud<pcl::Normal>);
  // ne.setRadiusSearch (0.1);
  // ne.compute (*cloud_normals2);

  boost::shared_ptr<pcl::visualization::PCLVisualizer> viewer;
  viewer = init_visualizer(basic_cloud_ptr);

  while (!viewer->wasStopped ())
  {
    viewer->spinOnce (100);
    boost::this_thread::sleep (boost::posix_time::microseconds (100000));
  }
}