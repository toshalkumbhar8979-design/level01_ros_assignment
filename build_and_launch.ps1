# build_and_run.ps1
Write-Host "========================================================"
Write-Host "    ERIC Robotics Testbed - Build and Run Script        "
Write-Host "========================================================"

Write-Host "`n1. Building the Docker environment (with noVNC)..."
docker compose build

Write-Host "`n2. Starting Docker container in detached mode..."
docker compose up -d

Write-Host "`n3. Compiling the ROS2 workspace inside the container..."
docker exec testbed_navigation_env /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build"

Write-Host "`n4. Starting the Simulation and Navigation headless in the background..."
docker exec -d testbed_navigation_env /bin/bash -c "export DISPLAY=:0 && export LIBGL_ALWAYS_SOFTWARE=1 && source /workspace/install/setup.bash && ros2 launch testbed_bringup testbed_full_bringup.launch.py > /workspace/gazebo.log 2>&1"

Write-Host "Waiting 15 seconds for Gazebo and robot state publisher to load..."
Start-Sleep -Seconds 15

docker exec -d testbed_navigation_env /bin/bash -c "export DISPLAY=:0 && export LIBGL_ALWAYS_SOFTWARE=1 && source /workspace/install/setup.bash && ros2 launch testbed_navigation navigation.launch.py > /workspace/nav.log 2>&1"

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " Simulation and Navigation Stack launched in the background!" -ForegroundColor Green
Write-Host " ------------------------------------------------------------" -ForegroundColor Green
Write-Host " [SUCCESS] We have set up a full web desktop for you!" -ForegroundColor Cyan
Write-Host " Open your browser to: http://localhost:8080/vnc.html" -ForegroundColor Cyan
Write-Host " Click 'Connect' to view Gazebo and RViz directly in your browser." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green
Write-Host "To view terminal logs, use:"
Write-Host "  docker exec testbed_navigation_env tail -f /workspace/gazebo.log"
Write-Host "  docker exec testbed_navigation_env tail -f /workspace/nav.log"
Write-Host "To shut down everything, run: docker compose down"
Write-Host "========================================================"
