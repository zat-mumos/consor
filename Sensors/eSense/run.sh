#!/bin/bash

bash_filepath="/home/user/<path to consor>/consor/main.sh"
python_filepath="./<path to ros_pub.py>/ros_pub.py"


kill_python_process(){
pid_=$(ps aux | grep python3 | grep user | grep ros_pub.py | tr -s ' ' | cut -d ' ' -f 2)
# https://stackoverflow.com/questions/48261038/shell-script-how-to-check-if-variable-is-null-or-no
echo "--------------------- PID: $pid"
if [[ -n "$pid_" ]]; then
	echo $pid_
	kill $pid_
	echo "Process killed"
fi

kill $python_background
echo "done"
}


trap kill_python_process SIGINT SIGTERM EXIT

cd
cd zat_ws

source /opt/ros/foxy/setup.bash

colcon build --packages-select <name of ROS2 package>
source install/setup.bash

python3 $python_filepath &

# https://stackoverflow.com/questions/1908610/how-to-get-process-id-of-background-process
python_background=$!

echo "Background PID: $python_background"

bash $bash_filepath | python3 $python_filepath

