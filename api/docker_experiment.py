import docker

client = docker.from_env()

# List all containers
containers = client.containers.list(all=True)


def get_container(name):
    try:
        container = client.containers.get(name)
        return {"name" : container.name, "id": container.id, "status": container.status}, 200

    except docker.errors.NotFound:
        return {"error" : "Not found"},404

container = client.containers.get("tinycloud-managed-demo")

print(container.labels)
print(container.labels.get("tinycloud.managed"))

def start_container(name):
    try:
        container = client.containers.get(name)

        if container.labels.get("tinycloud.managed") == "true":
            container.reload()
            if container.status == "running":
                return {"message" : container.name + " is already running"}, 200
            container.reload()
            container.start()
            return {"message" : container.name + " has started"}, 200
        else:
            return {"error" : container.name + " is not managed by tinycloud"}, 403

    except docker.errors.NotFound:
        return {"error": "Container not found"}, 404

print(start_container("tinycloud-managed-demo"))
print(start_container("tinycloud-managed-demo"))
print("DEBUG STATUS:", container.status)

def stop_container(name):
    try:
        container = client.containers.get(name)

        if container.labels.get("tinycloud.managed") == "true":
            container.reload()
            if container.status == "exited":
                return {"message": container.name + " has already been stopped"}, 200
            container.stop()
            return {"message": container.name + " has been stopped"}, 200
        else:
             return {"error": container.name + " is not managed by TinyCloud"}, 403

    except docker.errors.NotFound:
        return {"error": "Container not found"}, 404

print(stop_container("tinycloud-managed-demo"))
print(stop_container("tinycloud-managed-demo"))
print("DEBUG STATUS:", container.status)

print(get_container("fake-container"))
print(start_container("fake container"))
print(stop_container("fake-container"))