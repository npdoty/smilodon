# smilodon

## Setup

Create a virtualenv, activate it, and then `pip install -r requirements.txt`. (Make sure it's a Python3 environment; some of our dependencies require it.)

Create an account with [MongoDB's cloud service](https://www.mongodb.com/cloud/atlas); it's free for a very small cluster. Set up an admin user with a separate password, create an IP whitelist and connect to the database cluster to make sure it's working. (Install `mongodb` to your machine, with Homebrew, for example.)

## Config

Update `config.py` with your MongoDB credentials/URIs (be sure to get the full URI connection string from the "Connect Your Application" dialog), your email address in the `ADMINS` list and some dummy mail server credentials.

Create a `.env` file (or otherwise configure environment variables) for your MongoDB password, API key, and other sensitive variables, based on `.env.example`. `server_name` _must_ be set to the host/port at which you'll be accessing the server; for example, for local testing you might set it to `smilodon.localhost:5000` and add `127.0.0.1 smilodon.localhost` to your `hosts` file. `server_uri` should be the full address and protocol that it will be found at, e.g. `http://smilodon.localhost:5000`. `api_uri` should also be a full address and protocol, ending in `/api` (or at a subdomain, depending on your configuration).

For local development, you may wish to disable SSLify (in `app/__init__.py`), to access the server over HTTP rather than HTTPS.

## Run it locally

Install Heroku (`brew install heroku`). (You could also use Foreman or Honcho.)

`heroku local` should run the server on your local machine. You can access the server at the server name you configured above, for example, http://smilodon.localhost:5000.

## Heroku

### Setup

Create an account on Heroku (free should be fine to start) and a single application.

`heroku login` and enter your credentials. Set up deploy via git push, following the commands listed on your Deploy tab, like: `heroku git:remote -a smilodon-app-name`.

Set configuration variables in the Settings tab, one for each variable in `.env`; update the URIs to refer to the Heroku-provided app address, e.g. `https://smilodon-app-name.herokuapp.com`. The API URI must be configured for a subdirectory, e.g. `https://smilodon-app-name.herokuapp.com/api` (unless you're running at a custom domain name with a wildcard certificate).

### Run it in the cloud

Update your master branch with `config.py` customized to you, then deploy with `git push heroku master`. Heroku will build (installing all the pip requirements, etc.) and then run your Procfile. Load `https://smilodon-app-name.herokuapp.com` to verify.