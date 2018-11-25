# ohio
This repository will house our property records application. More to come!


# Scrapy

This project uses Scrapy to download updates from each site. 
If you're still new to Scrapy, reviewing the 
<a target="_blank" href="https://doc.scrapy.org/en/latest/topics/architecture.html">Architecture Overview</a>
provides a helpful look at how Scrapy operates. 

# Test Driven Development
This application has been tested as it was developed. Keep tabs on tests here: https://travis-ci.org/ludstuen90/ohio

# Installing a new instance of this application. 
- Scraping in this application depends on Twisted, which <a href="https://twistedmatrix.com/trac/wiki/Downloads">has a few requirements to install before-hand</a>. 
- Users will need to set up a PostgreSQL database instance, and provide the database parameters to the application via environment variables.


# Environment Variables
The following environment variables are required: 

`SECRET_KEY`

`DEBUG`

`PSQL_DATABASE_NAME`

`PSQL_DATABASE_USER`

`PSQL_DATABASE_USER_PASSWORD`

`WARREN_MORTGAGE_SITE`

