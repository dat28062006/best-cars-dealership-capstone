# Full Stack Application Development Capstone Project

## Repository name

`best-cars-dealership-capstone`

## Project name

**Best Cars Dealership Review Portal**

Best Cars is a full-stack Django and React capstone application for browsing
dealerships across the United States, filtering branches by state, reading
customer reviews, and posting authenticated reviews with sentiment analysis.

## Run locally

```bash
cd server/frontend
npm install
npm run build
cd ../..
python -m pip install -r server/requirements.txt
python server/manage.py migrate
python server/manage.py runserver
```

The site is then available at `http://127.0.0.1:8000/`.
