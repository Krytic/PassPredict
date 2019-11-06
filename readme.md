# PassPredict

PassPredict is an essential tool for any ground station. It is a fully autonomous twitter bot that monitors the skies for any satellites you are interested in, and sends you a twitter notification when it's about to happen.

Follow the University of Auckland's instance of PassPredict on twitter at [@passpredict](http://twitter.com/passpredict).

## Installation and dependencies
PassPredict requires the following libraries:
- Anaconda (Numpy, Matplotlib)
- orbit_predictor
- cartopy
- twitter

## Configuration and Operation

Default configuration is stored in `config.default.ini`. Edit this, and rename it to `config.ini` before the first run.

To run, invoke it from the command line:

    nohup python PassPredict.py &

(This runs it as a background process, use `ps aux | grep PassPredict` to monitor it, and use `vim nohup.out` to view stdout)

PassPredict will test your credentials and refuse to run if they are correct. By default PassPredict runs every 60 seconds (customisable, although is hardcoded in).

## Branch Policy
Master is considered to be bleeding-edge. Releases are tagged, please make changes on different branches and we will merge them to master as required.

We follow the [major.minor.patch](https://semver.org/) version schema, which will be introduced with version 1.0.0 (and will be tagged as such). Until then, consider this alpha software, or if you prefer a concrete version number, 0.1.0.
