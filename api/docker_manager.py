import docker
client = docker.from_env()

def _get_managed_container(name):
    try:
        container = client.containers.get(name)

        if container.labels.get("tinycloud.managed") != "true":
            return {"error" : "Container is not managed by TinyCloud"},403
        
        return container, 200

    except docker.errors.NotFound:
        return {"error": "Container not found"}, 404

    except docker.errors.DockerException:
        return {"error": "Docker service unavailable"}, 503


def get_container(name):
    container, status_code = _get_managed_container(name)
    
    if status_code != 200:
        return container, status_code

    container.reload()

    try:
        container.reload()
        return {
            "name" : container.name, 
            "id" : container.id,
            "status" : container.status
        }, 200
    except docker.errors.NotFound:
        return {"error": "Container not found"}, 404

    except docker.errors.DockerException:
        return {"error": "Docker service unavailable"}, 503
  
  
def stop_container(name):
    container, status_code = _get_managed_container(name)
    
    if status_code != 200:
        return container, status_code
    try:
        container.reload()

    
        if container.status == "exited":
            return {"message": container.name + " has already been stopped"}, 200
        container.stop()
        return {"message": container.name + " has been stopped"}, 200

    except docker.errors.NotFound:
        return {"error": "Container not found"}, 404
    except docker.errors.DockerException:
        return {"error": "Docker service unavailable"}, 503
      
def start_container(name):
    container, status_code = _get_managed_container(name)
    if status_code != 200:
        return container, status_code

    try:
        container.reload()
        if container.status == "running":
            return {"message" : container.name + " is already running"}, 200
        container.start()
        return {"message" : container.name + " has started"}, 200

    except docker.errors.NotFound:
        return {"error": "Container not found"}, 404
    except docker.errors.DockerException:
        return {"error": "Docker service unavailable"}, 503
      
def get_containers():

    try:
        containers_list = []
        containers = client.containers.list(all=True)
        for container in containers:
            if container.labels.get("tinycloud.managed") == "true":
             containers_list.append({
            "name": container.name,
            "id": container.id,
            "status": container.status
        })
        return {"containers": containers_list}, 200
    except docker.errors.DockerException:
        return {"error": "Docker service unavailable"}, 503

def validate_container(container_id):
    container,status_code = _get_managed_container(container_id)
    if status_code != 200:
        return container, status_code
    
    return {
        "id" : container.id,
        "status": container.status
    }, 200