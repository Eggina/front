gunicorn main:app &
ssh -R 8000:localhost:8000 ec2 &&
fg
