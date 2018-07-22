# Environment Documentation

## [Setup Environment](#setup-env)

Install dependencies:
* [docker](https://docs.docker.com/install/)
* [docker-compose](https://docs.docker.com/compose/install/)
* [git](https://git-scm.com/downloads)


### Installing

```bash
git clone git@github.com:markomafs/work-at-olist.git 
cd work-at-olist
```

## [Running Local](#local-run)

```bash
docker-compose up -d
```

## [Deployment](#deployment) 

All deployment process is automated by Heroku whenever master changes,
that means you should only merge pull-requests to deploy to `staging` as DEBUG 
environment and `production`.
 
#### Staging 

https://staging-markomafs-work-at-olis.herokuapp.com/

#### Production

https://markomafs-work-at-olist.herokuapp.com/

