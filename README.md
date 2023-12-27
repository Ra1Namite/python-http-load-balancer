
# Http-Load-balancer

Python based load balancer developed using test driven development (TDD) method. It is used for intelligently distributing network traffic across multiple servers in order to horizontally scale web-based applications.

## Features
* Host name and path based routing.

* Configured from yaml file.


* Check health of available servers.

* Manipulate HTTP headers, query parameters, POST data, cookies and rewrite urls.

* Uses Least connections load balancing algorithm to distribute network traffic.

* Firewall: IP based and path based blocking.


## Run Locally

Clone the project

```bash
  git clone git@github.com:Ra1Namite/python-http-load-balancer.git
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Build test app's Docker image
```bash
  docker build -t server -f Dockerfile-test .
```
Start test app's servers

```bash
  docker compose up -d
```
Start the load balancer server

```bash
  FLASK_APP=src/loadbalancer.py flask run

```


## Running Tests

To run tests, run the following command

```bash
  make test
```

