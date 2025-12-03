# Developer Guide

## Getting Started

### 1. Setup Dev Environment
run this every time you pull latest
```bash
bash ./dev_scripts/setup_dev_env.sh
```

this script will:
- create the python virtual environment
- install python dependencies
- setup the db
- run the db migrations
- run the tests
- ingest comments from `./data/comments.json`

### 2. Run Dev Servers
run this to serve the ui as you develop

```bash
bash ./dev_scripts/run_dev_env.sh
```

starts both vite and django:
- Vite frontend: http://localhost:5173 talking to Django listening to http://127.0.0.1:8000

### Ingesting the comments file
The raw comments file lives at `./data/comments.json`.  To re-ingest this file, execute

```bash
bash ./dev_scripts/reingest_comment.sh
```


## Tests

```bash
cd backend
python manage.py test
```

## Tech Stack

### Backend
- **psql** 
- **django** 

### Frontend
- **react** 
- **vite** 
- **sass**

## Monorepo Structure
```
monorepo/
├── .env                 # all env vars here
├── data/                # dir to hold arbitrary data files
├── backend/             # django / orm
│   └── api/             
│       └── <django stuff>.py    
├── frontend/            # react/vite/sass
│   ├── src/
│   │   ├── <ui>.jsx     
│   │   └── lib/*.js     # common front end utils   
│   └── vite.config.js
├── dev_scripts/           
│   └── setup_dev_env.sh  # setup the dev env
│   └── run_dev_env.sh    # run the dev servers
```

## If I had more time, I'd
- sort out the csrf cookie and get rid of the @csrf_exempt decorators
- implement automated tests for the react side
- put it all in a container to make local dev and debugging more consistent
