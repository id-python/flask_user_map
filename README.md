User Map
========

A simple flask application for creating user community maps.

To run in debug mode (which will also serve up static content), use the -d
flag.

``python runserver.py -d``


If running under pycharm, remember to edit the run configuration and add the
``-d`` to the parameters.

Deployment using Docker
=======================

If you are using docker, you can create a Docker image for this app easily as
follows:

```
wget -O Dockerfile https://raw.github.com/timlinux/user_map/master/docker/Dockerfile
wget -O sources.list https://raw.github.com/timlinux/user_map/master/docker/sources.list
wget -O post-setup.sh https://raw.github.com/timlinux/user_map/master/docker/post-setup.sh
chmod +x post-setup.sh

docker build -t linfiniti/user_map:base .
docker run -d -p 8099:80 -t linfiniti/user_map:base -n user_map -D
```

If you are on a Hetzner server, consider replacing the second line above with:

```
wget -O sources.list https://raw.github.com/timlinux/user_map/master/docker/hetzner-sources.list
```

Authors
=======

Tim Sutton and Akbar Gumbira
