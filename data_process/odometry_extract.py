import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry, Path
import h5py
import numpy as np
import os
from datetime import datetime

# 输入和输出路径
bag_path = "/home/hefangyuan/bag_files/trace/9/9.db3"
output_h5_path = "/home/hefangyuan/odometry_datasets/odometry_data9.h5"

if not os.path.exists(bag_path):
    print('Bag file not found')
    exit()

# 初始化数据存储结构
odometry_data = {
    'timestamps': [],
    'positions': {'x': [], 'y': [], 'z': []},
    'orientations': {'x': [], 'y': [], 'z': [], 'w': []},
    'linear_velocities': {'x': [], 'y': [], 'z': []},
    'angular_velocities': {'x': [], 'y': [], 'z': []}
}

# 打开rosbag2文件
reader = rosbag2_py.SequentialReader()
storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id="sqlite3")
reader.open(storage_options, rosbag2_py.ConverterOptions())

# 遍历消息并提取Odometry数据
while reader.has_next():
    topic, data, timestamp = reader.read_next()
    if topic == "/Odometry":  # 替换为你的实际话题名
        msg = deserialize_message(data, Odometry)
        
        # 存储时间戳(nanoseconds)
        odometry_data['timestamps'].append(timestamp)
        
        # 位置数据
        odometry_data['positions']['x'].append(msg.pose.pose.position.x)
        odometry_data['positions']['y'].append(msg.pose.pose.position.y)
        odometry_data['positions']['z'].append(msg.pose.pose.position.z)
        
        # 方向数据(四元数)
        odometry_data['orientations']['x'].append(msg.pose.pose.orientation.x)
        odometry_data['orientations']['y'].append(msg.pose.pose.orientation.y)
        odometry_data['orientations']['z'].append(msg.pose.pose.orientation.z)
        odometry_data['orientations']['w'].append(msg.pose.pose.orientation.w)
        
        # 线速度
        odometry_data['linear_velocities']['x'].append(msg.twist.twist.linear.x)
        odometry_data['linear_velocities']['y'].append(msg.twist.twist.linear.y)
        odometry_data['linear_velocities']['z'].append(msg.twist.twist.linear.z)
        
        # 角速度
        odometry_data['angular_velocities']['x'].append(msg.twist.twist.angular.x)
        odometry_data['angular_velocities']['y'].append(msg.twist.twist.angular.y)
        odometry_data['angular_velocities']['z'].append(msg.twist.twist.angular.z)

# 转换为numpy数组以提高存储效率
for key in odometry_data:
    if isinstance(odometry_data[key], dict):
        for subkey in odometry_data[key]:
            odometry_data[key][subkey] = np.array(odometry_data[key][subkey])
    else:
        odometry_data[key] = np.array(odometry_data[key])

# 保存为HDF5文件
with h5py.File(output_h5_path, 'w') as h5file:
    # 创建组结构
    pos_group = h5file.create_group('positions')
    ori_group = h5file.create_group('orientations')
    lin_vel_group = h5file.create_group('linear_velocities')
    ang_vel_group = h5file.create_group('angular_velocities')
    
    # 存储时间戳
    h5file.create_dataset('timestamps', data=odometry_data['timestamps'])
    
    # 存储位置数据
    pos_group.create_dataset('x', data=odometry_data['positions']['x'])
    pos_group.create_dataset('y', data=odometry_data['positions']['y'])
    pos_group.create_dataset('z', data=odometry_data['positions']['z'])
    
    # 存储方向数据
    ori_group.create_dataset('x', data=odometry_data['orientations']['x'])
    ori_group.create_dataset('y', data=odometry_data['orientations']['y'])
    ori_group.create_dataset('z', data=odometry_data['orientations']['z'])
    ori_group.create_dataset('w', data=odometry_data['orientations']['w'])
    
    # 存储线速度
    lin_vel_group.create_dataset('x', data=odometry_data['linear_velocities']['x'])
    lin_vel_group.create_dataset('y', data=odometry_data['linear_velocities']['y'])
    lin_vel_group.create_dataset('z', data=odometry_data['linear_velocities']['z'])
    
    # 存储角速度
    ang_vel_group.create_dataset('x', data=odometry_data['angular_velocities']['x'])
    ang_vel_group.create_dataset('y', data=odometry_data['angular_velocities']['y'])
    ang_vel_group.create_dataset('z', data=odometry_data['angular_velocities']['z'])
    
    # 添加元数据
    h5file.attrs['creation_date'] = datetime.now().isoformat()
    h5file.attrs['source_bag'] = bag_path
    h5file.attrs['description'] = 'Odometry data extracted from ROS2 bag file'

print(f"Odometry data successfully saved to {output_h5_path}")