mog-cli [![Stories in Ready](https://badge.waffle.io/mogproject/mog-cli.png?label=ready)](http://waffle.io/mogproject/mog-cli)
=======

Command Line Interface for CSA Shogi Client

## Requirements

* Python (>= 3.0)


## Testing with Docker

* Run docker host

  (If you are using Vagrant, use ```docker-host``` Vagrantfile in 
https://github.com/mogproject/mog-infra)

* Run the shogi-server container on the docker host.  

  ```
  $ docker run -d -p 4081:4081 mogproject/shogi-server
  ```

  (Further information here - https://index.docker.io/u/mogproject/shogi-server/)

