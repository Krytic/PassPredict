# PassPredict

Intelligent twitter bot to track and identify satellites that are passing overhead. Follow it on twitter at [@passpredict](http://twitter.com/passpredict)

## Installation and dependencies
PassPredict requires the following libraries:
- Anaconda (Numpy, Matplotlib + Basemap, Scipy)
- [Skyfield](https://rhodesmill.org/skyfield)
- [Python-Twitter](https://github.com/bear/python-twitter)

To install, download a fork into your folder. Create a file called `config.txt` with the following contents:

    consumer_key=<CONSUMER_KEY>
    consumer_secret=<CONSUMER_SECRET>
    access_token_key=<TOKEN>
    access_token_secret=<SECRET_KEY>

To run, invoke it from the command line:

    python PassPredict.py

PassPredict will test your credentials and refuse to run if they are correct. By default PassPredict runs every 60 seconds (customisable) and detects passes close to [The University of Auckland](http://auckland.ac.nz) (also customisable).

## Branch Policy
Master is considered to be bleeding-edge. Releases are tagged, please make changes on different branches and we will merge them to master as required.

We follow the [major.minor.patch](https://semver.org/) version schema, which will be introduced with version 1.0.0 (and will be tagged as such). Until then, consider this alpha software, or if you prefer a concrete version number, 0.1.0.
