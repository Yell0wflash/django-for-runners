# Django-ForRunners

![Logo](https://github.com/Yell0wflash/django-for-runners/raw/main/for_runners/static/Django-ForRunners128.png "Logo") Store your GPX tracks of your running (or other sports activity) in django.

[![pytest](https://github.com/Yell0wflash/django-for-runners/workflows/test/badge.svg?branch=main)](https://github.com/Yell0wflash/django-for-runners/actions)
[![Coverage Status on codecov.io](https://codecov.io/gh/Yell0wflash/django-for-runners/branch/main/graph/badge.svg)](https://codecov.io/gh/Yell0wflash/django-for-runners)
[![django_yunohost_integration @ PyPi](https://img.shields.io/pypi/v/django_yunohost_integration?label=django_yunohost_integration%20%40%20PyPi)](https://pypi.org/project/django_yunohost_integration/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django_yunohost_integration)](https://github.com/Yell0wflash/django-for-runners/blob/main/pyproject.toml)
[![License GPL](https://img.shields.io/pypi/l/django_yunohost_integration)](https://github.com/Yell0wflash/django-for-runners/blob/main/LICENSE)

(The name **Django-ForRunners** has the origin from the great Android tracking app **ForRunners** by Benoît Hervier: [http://rvier.fr/#forrunners](http://rvier.fr/#forrunners) )

[![Install Django-ForRunners with YunoHost](https://install-app.yunohost.org/install-with-yunohost.svg)](https://install-app.yunohost.org/?app=django-for-runners_ynh)

> [django-for-runners_ynh](https://github.com/YunoHost-Apps/django-for-runners_ynh) allows you to install Django-ForRunners quickly and simply on a YunoHost server. If you don't have YunoHost, please consult [the guide](https://yunohost.org/#/install) to learn how to install it.

## Features:


* GPX track management:
  * Upload GPX tracks
  * Import GPX tracks from commandline
  * Track analysis:
    * basics: Track length / Duration / Pace / Hart rate Up-/Downhill
    * Display route on OpenStreetMap map
    * Graphs with elevation / heart rate / cadence (if available in GPX data)
  * Data that is automatically extracted from the web:
    * Start/finish Address from OpenStreetMap
    * Start/finish weather information from metaweather.com
  * Store additional data:
    * Ideal track distance (for easier grouping/filtering tracks)
* sports competitions Management:
  * Create a List of Sport Events
    * Add participation to a event
    * link GPX track with a event participation
    * Store you event participation:
      * official track length
      * measured finisher time
      * Number of participants who have finished in your discipline
    * Add links to webpages relatet to this event
    * Record costs (entry fee, T-shirt etc.)
* common
  * Multiple user support (However: no rights management and currently only suitable for a handful of users)


## Developer information

### prepare

To start hacking: Just clone the project and start `./manage.py` to bootstrap a virtual environment:

```bash
# Install base requirements for bootstraping:
~$ sudo apt install python3-pip python3-venv

# Get the sources:
~$ git clone https://github.com/Yell0wflash/django-for-runners.git
~$ cd django-for-runners/

# Just call manage.py:
~/django-for-runners$ ./manage.py --help
...
[manage_django_project]
    code_style
    coverage
    install
    project_info
    publish
    run_dev_server
    safety
    tox
    update_req
...
```
This bootstrap is realized with: https://github.com/Yell0wflash/manage_django_project



Start Django's dev server:
```bash
~/django-for-runners$ ./manage.py run_dev_server
````
The web page is available in Port 8000, e.g.: `http://127.0.0.1:8000/`


Run tests, e.g.:
```bash
~/django-for-runners$ ./manage.py test
# or with coverage
~/django-for-runners$ ./manage.py coverage
# or via tox:
~/django-for-runners$ ./manage.py tox
````



### import GPX files

e.g.:
```
~/django-for-runners$ ./manage.py import_gpx --username <django_username> ~/backups/gpx_files
```

**Note:** It is no problem to start **import_gpx** with the same GPX files: Duplicate entries are avoided. The start/finish (time/latitude/longitude) are compared.

### backup

Create a backup into `.../backups/<timestamp>/` e.g.:
```
~/django-for-runners$ ./manage.py backup
```

The backup does:


* backup the database
* export all GPX tracks
* generate .csv files:
* a complete file with all running tracks
* one file for every user

## some notes

### GPX storage

Currently we store the unchanged GPX data in a TextField.

### static files

We collect some JavaScript files, for easier startup. These files are:

| Project Homepage                      | License                                                                                   | storage directory                                                                                                   |
| ------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [leafletjs.com](http://leafletjs.com) | [Leaflet licensed under BSD](https://github.com/Leaflet/Leaflet/blob/master/LICENSE)      | [for_runners/static/leaflet/](https://github.com/Yell0wflash/django-for-runners/tree/master/for_runners/static/leaflet)   |
| [dygraphs.com](http://dygraphs.com)   | [dygraphs licensed under MIT](https://github.com/danvk/dygraphs/blob/master/LICENSE.txt)  | [for_runners/static/dygraphs/](https://github.com/Yell0wflash/django-for-runners/tree/master/for_runners/static/dygraphs) |
| [chartjs.org](http://www.chartjs.org) | [Chart.js licensed under MIT](https://github.com/chartjs/Chart.js/blob/master/LICENSE.md) | [for_runners/static/chartjs/](https://github.com/Yell0wflash/django-for-runners/tree/master/for_runners/static/chartjs)   |

### Precision of coordinates

GPX files from Garmin (can) contain:


* latitude with 29 decimal places
* longitude with 28 decimal places
* elevation with 19 decimal places

The route on OpenStreetMap does not look more detailed, with more than 5 decimal places.

See also: [https://wiki.openstreetmap.org/wiki/Precision_of_coordinates](https://wiki.openstreetmap.org/wiki/Precision_of_coordinates)

## Django compatibility

| django-for-runners | django version | python              |
|--------------------|----------------|---------------------|
| >=v0.16.0          | 4.1            | 3.9, 3.10, 3.11     |
| >=v0.15.0          | 3.2, 4.0, 4.1  | 3.7, 3.8, 3.9, 3.10 |
| >=v0.14.0          | 3.2            | 3.7, 3.8, 3.9, 3.10 |
| >=v0.12.0          | 2.2            | 3.7, 3.8, 3.9, 3.10 |
| >=v0.11.0          | 2.2            | 3.7, 3.8, 3.9       |
| >=v0.7.1           | 2.1            | 3.5, 3.6, 3.7       |
| v0.5.x             | 2.0            | 3.5, 3.6, 3.7       |

(See also combinations in [tox settings in pyproject.toml](https://github.com/Yell0wflash/django-for-runners/blob/main/pyproject.toml) and [github actions](https://github.com/Yell0wflash/django-for-runners/blob/main/.github/workflows/tests.yml))


## Backwards-incompatible changes


### v0.16.0

We switched from Poetry to pip-tools and https://github.com/Yell0wflash/manage_django_project
Just remove the old Poetry venv and bootstrap by call the `./manage.py`, see above.

We also remove different Django Versions from test matrix and just use the current newest version.
Because this is a project and not really a reuse-able-app ;)


## links

| Homepage | [http://github.com/Yell0wflash/django-for-runners](http://github.com/Yell0wflash/django-for-runners)     |
| PyPi     | [https://pypi.org/project/django-for-runners/](https://pypi.org/project/django-for-runners/) |

### activity exporter

It's sometimes hard to find a working project for exporting activities.
So here tools that i use currently:


* [Garmin-Connect-Export](https://github.com/rsjrny/Garmin-Connect-Export) from rsjrny

### alternatives (OpenSource only)


* [https://github.com/pytrainer/pytrainer](https://github.com/pytrainer/pytrainer) (Desktop Program)
* [https://github.com/GoldenCheetah/GoldenCheetah/](https://github.com/GoldenCheetah/GoldenCheetah/) (Desktop Program)

Online tools:


* [https://www.j-berkemeier.de/ShowGPX.html](https://www.j-berkemeier.de/ShowGPX.html) (de)

## credits

The whole thing is based on many excellent projects. Especially the following:


* [gpxpy](https://pypi.org/project/gpxpy/) GPX file parser
* [Leaflet JS](https://leafletjs.com) A JS library for interactive maps used to render the track on [OpenStreetMap](https://openstreetmap.org/)
* [dygraphs](http://dygraphs.com) open source JavaScript charting library
* [Chart.js](https://www.chartjs.org) HTML5 Charts
* [geopy](https://pypi.org/project/geopy/) Get geo location names of the GPX track start/end point
* [matplotlib](https://pypi.org/project/matplotlib/) plotting 2D graphics
* [autotask](https://pypi.org/project/autotask/) schedule background jobs
* [svgwrite](https://pypi.org/project/svgwrite/) Generating SVG file

