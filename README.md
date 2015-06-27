# Tropixel Sinbiota Scrapers

We've found Sinbiota data awesome, but hard to get.
Scrapy came to rescue -- get all data as JSON or CSV!

## How to setup

### Ubuntu

First of all, install Git, Python and some other dependencies:

    sudo apt-get install git libxml2-dev libxslt-dev python-dev python-pip python-virtualenv

Then checkout this project:

    git clone https://github.com/barraponto/tropixel.git
    cd tropixel

Setup a virtual environment for this project:

    virtualenv tropixel-env
    source tropixel-env/bin/activate

And finally, install the requirements:

    pip install -r requirements.txt

## How to run

Make sure you are in the repository folder and the source is active.

    source tropixel-env/bin/activate

Then run a scrapy crawl to get all of Ubatuba's data:

    scrapy crawl sinbiota -t json -o ubatuba.json

Alternatively, choose the sinbiotachoose spider to pick your own municipality.

    scrapy crawl sinbiotachoose -t json -o mymunicipalty.json

It will prompt you to type your municipality, then present you with fuzzy options.
Choose your option by typing the number and pressing enter.

### Useful addons

The above commands have `-t json -o myfile.json` but it could just as well have
`-t csv -o myfile.csv` for a CSV export. We also recommend enabling HTTP cache,
to avoid re-requesting data from the server:

    scrapy crawl --set=HTTPCACHE_ENABLED=1 sinbiota -t json -o myfile.json

Anyway, this is a scrapy project, you can go nuts with the options :)
