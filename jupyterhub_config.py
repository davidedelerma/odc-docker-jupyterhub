import os

c = get_config()

network_name = "jupyterhub"
notebook_dir = '/home/jovyan/work'
spawn_cmd = "launch-singleuser.sh"

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
c.DockerSpawner.network_name = network_name
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.debug = True
c.DockerSpawner.volumes = {
    'jupyterhub-user-{username}': notebook_dir,
}
c.DockerSpawner.read_only_volumes = {
    '/home/ec2-user/jhub/config/datacube.conf': '/home/jovyan/.datacube.conf',
    '/home/ec2-user/jhub/config/aws_credentials': '/home/jovyan/.aws/credentials',
    'datacube-examples-volume' : '/examples',
}
c.DockerSpawner.cmd = spawn_cmd
c.DockerSpawner.remove_containers = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080
c.JupyterHub.cookie_secret_file = '/data/jupyterhub_cookie_secret'
c.JupyterHub.db_url = '/data/jupyterhub.sqlite'

# Authenticate users with GitHub OAuth
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)
