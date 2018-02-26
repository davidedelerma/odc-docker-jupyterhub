# odc-docker-jupyterhub
Scripts to deploy ODC + Jupyterhub with Github OAuth using Docker


# config

Plan is to move towards one file config, but for now this is what needs to happen. Replace `my.example.com` and `user@example.com` with proper values.

File `config/common.env`

```
DOMAIN=my.example.com
```

File `config/oauth.env`

```
OAUTH_CLIENT_ID=<bunch of numbers from github>
OAUTH_CLIENT_SECRET=<bunch of numbers from github>
OAUTH_CALLBACK_URL=https://my.example.com/hub/oauth_callback
```

File `config/userlist`

```
<your github login> admin
```

File `config/jhub-vhost.yml`

```
letsencrypt:
  email: user@example.com

# this part is optional
duckdns:
  token: <bunch of numbers from duckdns>
```

Create folder `user_folder`, content of this folder will be used as a template for creating new user volumes. At the very least you need to create `user_folder/.datacube.conf` with the following content:

```
[default]
db_database: datacube
db_hostname: datacube-db
db_username: postgres
db_password: todo_generate_me
```
