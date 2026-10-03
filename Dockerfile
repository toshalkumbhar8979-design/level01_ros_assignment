FROM osrf/ros:humble-desktop

# Install basic tools and dependencies
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-xacro \
    ros-humble-rmw-cyclonedds-cpp \
    nano \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fluxbox \
    && rm -rf /var/lib/apt/lists/*

# Add a script to start noVNC
RUN echo '#!/bin/bash\n\
export DISPLAY=:0\n\
export RESOLUTION=1920x1080x24\n\
Xvfb :0 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &\n\
sleep 2\n\
fluxbox &\n\
sleep 1\n\
x11vnc -display :0 -nopw -xkb -forever -shared -bg\n\
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 8080 &\n\
echo "noVNC running on port 8080. Connect via http://localhost:8080/vnc.html"\n\
exec "$@"' > /start_novnc.sh && chmod +x /start_novnc.sh

ENTRYPOINT ["/start_novnc.sh"]

# Set up environment variables
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV ROS_DOMAIN_ID=30

WORKDIR /workspace

# Source ROS2 setup in bashrc
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "if [ -f /workspace/install/setup.bash ]; then source /workspace/install/setup.bash; fi" >> ~/.bashrc

CMD ["/bin/bash"]
