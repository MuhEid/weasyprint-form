a python tool that generates a pdf file from an html template and an api request with the required data
it utilizes Flask so run

```bash
flask run
```

to get it started on the server:
use the dockerfile inside /backend to start it

```
docker build -t phoneytech-backend .
docker run -d -p 5000:5000 --restart always --name phoneytech-backend phoneytech-backend
```
