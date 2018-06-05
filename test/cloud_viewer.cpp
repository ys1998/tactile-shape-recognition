#include <pcl/visualization/cloud_viewer.h>
#include <iostream>
#include <pcl/io/io.h>
#include <pcl/io/pcd_io.h>
#include <pcl/common/centroid.h>
    
int user_data;
    
void viewerOneOff (pcl::visualization::PCLVisualizer& viewer)
{
    viewer.setBackgroundColor (1.0, 1.0, 1.0);
    // viewer.addSphere (o, 0.25, "sphere", 0);
    // std::cout << "i only run once" << std::endl;
    
}
    
void viewerPsycho (pcl::visualization::PCLVisualizer& viewer)
{
    static unsigned count = 0;
    std::stringstream ss;
    ss << "Once per viewer loop: " << count++;
    viewer.removeShape ("text", 0);
    viewer.addText (ss.str(), 200, 300, "text", 0);
    
    //FIXME: possible race condition here:
    // user_data++;
}
    
int main ()
{
    pcl::PointCloud<pcl::PointXYZRGBA>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZRGBA>);
    pcl::io::loadPCDFile ("model.pcd", *cloud);

    float x=0.0, y=0.0, z=0.0;
    for (size_t i = 0; i < cloud->size(); ++i)
    {
        x += cloud->points[i].x;
        y += cloud->points[i].y;
        z += cloud->points[i].z;
    }

    // Shift point cloud to its centroid
    int cnt = cloud->size();
    for (size_t i = 0; i < cloud->size(); ++i){
        cloud->points[i].x -= x/cnt;
        cloud->points[i].y -= y/cnt;
        cloud->points[i].z -= z/cnt;
    }

    pcl::visualization::CloudViewer viewer("Point Cloud Visualization");
    
    //blocks until the cloud is actually rendered
    viewer.showCloud(cloud);

    // //blocks until the cloud is actually rendered
    // viewer.showCloud(cloud);
    
    //use the following functions to get access to the underlying more advanced/powerful
    //PCLVisualizer
    
    //This will only get called once
    viewer.runOnVisualizationThreadOnce (viewerOneOff);
    
    //This will get called once per visualization iteration
    // viewer.runOnVisualizationThread (viewerPsycho);
    while (!viewer.wasStopped ())
    {
    //you can also do cool processing here
    //FIXME: Note that this is running in a separate thread from viewerPsycho
    //and you should guard against race conditions yourself...
    // user_data++;
    }
    return 0;
}