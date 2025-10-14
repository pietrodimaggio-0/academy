# Basics #

## ⚡️ 1 Run ##

### 1.1 Run an image: the simplest run ###

    docker run --name es_1_1 hello-world # docker.io/library/hello-world:latest

### 1.2 Containers are transient by default ###

    docker run -it --name es_1_2 ubuntu bash

- Make a change inside the current container (apt update & apt install python3)

### 1.3 Run an image: the simplest run (2) ###

    docker run --name es_1_3 nginx # what should you do to have your shell free of nginx's output?
    docker ps

### 1.4 How about reaching my container? ###

    docker run -d -p 8080:80 --name es_1_4 nginx
    docker ps

example output:
    d27b80af565f  docker.io/library/nginx:latest  nginx
    -g daemon o...
    4 seconds ago  Up 4 seconds  0.0.0.0:8080->80/tcp  es_1_4

Check your container
wget -O- <http://localhost:8080>

### 1.5  Inspect a running container ###
    docker inspect -f 'Image: {{ .Config.Image }}’ es_1_4
    docker inspect -f 'Command: {{ .Config.Cmd }}' es_1_4
    docker inspect -f 'Entrypoint: {{ .Config.Entrypoint }}' es_1_4

### 1.6 Jumping into a running container ###

    docker exec -it es_1_5 bash

Modify the index.html

    echo yourname > /usr/share/nginx/html/index.html

Leave the shell

    exit

Stop and Start es_1_5

🙋🏼‍♂️ Question

- Does the index.html retain your last update?
- Try to remove the container and then create a new one, what happens to index.html?

### 1.7 Get container log ###

    docker logs es_1_5

### 1.8 A Postgres container

The `postgres` image on the Docker Hub starts a relational database server on TCP port 5432:

    docker run --name es_1_8 -p 5432:5432 -e POSTGRES_PASSWORD=1234 postgres

This will create a default database called `postgres`, an admin login role called `postgres` with login password 1234.

Now open DBeaver, add a Postgres connection with all the needed parameters and see if you are able to view the default database.

## 👷🏽 2 Building images ##

### 2.1 Customize you first image ###

You can start from a base image

    FROM nginx

and RUN commands to make changes

    RUN echo yourname > /usr/share/nginx/html/index.html

Write a Dockerfile with the above instructions
Execute

    docker build -t img_es_2_1 .

or with label option

    docker build -t img_es_2_1 --label=env=academy  .

Check your image exists

    docker images img_es_2_1

or

    docker images -f "label=env=academy"

### 2.2 A more complex task ###

Use the alpine image to create a new python application based on "app.py" example.
Alpine is a super lightweight Linux base image, so it doesn’t include Python by default.
You can install it using apk, Alpine’s package manager.

    FROM alpine

    #Install python
    RUN apk add --no-cache python3 py3-pip

    #Copy "app.py" into "app" folder ,
    WORKDIR /app
    COPY app.py .

    #Add a starting command
    CMD ["python3", "app.py"]

Build your image with tag "img_es_2_2" and then run

    docker run --name es_2_2 img_es_2_2

### 2.3 Understanding ENTRYPOINT vs CMD ###

Both instructions define what runs when a container starts, but they behave differently:

 • ENTRYPOINT → sets the main executable for the container.

 • CMD → provides default arguments (or a default command if no ENTRYPOINT is set).

They can be combined:

 • ENTRYPOINT defines what to run

 • CMD defines how to run it (defaults).

Try to execute:

    docker run --name es_2_3 img_es_2_2 ls

What happened?

Make the image run python3 app.py as main executable with default parameter

    ENTRYPOINT ["python3", "app.py"]
    CMD ["world]

Modify app.py:

    import sys

    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "world"

    print(f"Hello, {name}!")

## ꙮ 3 Multi-stage builds ##

A multi-stage build means using multiple FROM statements in a single Dockerfile.
Each FROM starts a new build stage, and you can copy only what you need from earlier stages.

    ## ---------------------
    ## Stage 1: Builder
    ## ---------------------

    FROM node:20 AS builder

    WORKDIR /app

    ## Copy and install dependencies

    COPY package*.json ./
    RUN npm install --production

    ## Copy source code

    COPY . .

    ## ---------------------
    ## Stage 2: Runtime
    ## ---------------------
    FROM node:20-alpine AS runtime

    WORKDIR /app

    ## Copy only what’s needed from the builder stage
    COPY --from=builder /app ./

    ## Expose the application port
    EXPOSE 3000

    ## Run the app
    CMD ["npm", "start"]

⚙️ How it Works 💡

 1. The first stage (builder) uses the full Node image (with npm and compilers) to install dependencies.

 2. The second stage starts from a lightweight base (node:20-alpine) and copies only the /app folder from stage 1.

 3. The final image is small, clean, and ready to run — no build tools included.

    docker build -t img_es_3_1 .
    docker run -p 3000:3000 --name es_3_1 img_es_3_1

🔍 Compare Image Sizes

Try building with and without multi-stage:

    docker images | grep img_es_3_1

Compare image sizes with and without multi-stage

## ✅ 4 Persistent Data and Volumes ##

Containers are transient — when they stop, changes inside them are lost.
Docker volumes allow you to persist or share data between containers.

### 4.1 VOLUME Hands-On ###

We will create a simple Python app that writes logs into a directory.

    app.py
        from datetime import datetime
        import time
        while True:
            with open("/data/logs/app.log", "a") as f:
                f.write(f"{datetime.now()} - App is running\n")
            time.sleep(5)

Dockerfile

    FROM python:3.11-slim
    WORKDIR /app
    COPY app.py .
    VOLUME ["/data/logs"]
    CMD ["python", "app.py"]

Build and run your container:

    docker build -t img_es_4_1 .

Mount a volume, it will be create automatically

    docker run --name es_4_1 -d --mount type=volume,src=myvolume,dst=/data/logs img_es_4_1

or

    docker run --name es_4_1 -d -v myvolume:/data/logs img_es_4_1

List volumes to see the volume created:

    docker volume ls

Check that the log file exists inside the container:

    docker exec -it es_4_1 ls /data/logs

    docker exec -it es_4_1 tail /data/logs/app.log

🙋🏼‍♂️ Question:

- What happens to the logs if you remove the container and run a new one with the same -v mount?
- What happens if you run one more container myapplog2 with the same -v mount?

### 4.2 Binding host ###

Stop and remove the container, then run again with a host bind mount:

    mkdir -p ./mylogs
    docker run -d --name es_4_2 -v ./mylogs:/data/logs img_es_4_1

Check that logs are now written in your local directory:

    tail -f mylogs/app.log
