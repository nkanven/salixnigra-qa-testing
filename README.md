# salixnigra-qa-testing

Functional and Non-functional testing for Saix Nigra web application

## Launch load testing with 1000 concurrents users
locust --headless --users 1000 --spawn-rate 1 -H https://salixnigra.com/ --csv=salixnigra -t10m