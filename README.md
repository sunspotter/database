# Database pipeline

This repository contains the bash and python scripts to generate a sqlite database.

`pipeline.sh` needs to be called with the classifications and ranking files.

It runs only with bash and gnu versions of `sed` and `awk` are needed - I
wouldn't get into the pain to convert it so it works in a mac. Also sqlite3 is needed.

The python scripts use: `astropy`, `pandas`, `matplotlib` and `squarify`. Future
versions will work with the `orm` files so all can be done within python. That
will add a `sqlalchemy` dependency.

The sunspotter.sqlite3 produced output will 5 tables: 
- `classifcation`: Contains the comparisons done by the users (user, images compared, whether they were inverted and when)
- `fitsfiles`: Information about the fits files used to obtain the data (filename and date)
- `images`: Information about the images (filename) and the ARs (size, location, flux, flare?)
- `user`: Usernames
- `zoorank`: Information about the ranking provided by zooniverse based on their algorithm.

