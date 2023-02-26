import docker
import json
import time
import logging as log
from flask import Flask, render_template, request
from flask import jsonify
import datetime
#logging config
logFile = 'docker_manager.log'
log.basicConfig(filename=logFile, encoding='utf-8', level=log.DEBUG)
formatter = log.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
    
#start time 
start_time = time.time()

configData = {} 
configFile = './config.json'


def getConfig(configFile):
    # Opening JSON file
    with open(configFile) as json_file:
        data = json.load(json_file)
        return data

#Docker Utility:

def getActiveContainers(client):
    containers = client.containers.list()
    return containers

def startContainer(client,imageName):
    client.containers.run(imageName, detach=True)   
    
def stopContainer(client,hostName):
    container = client.containers.get(hostName)
    # Stop the container
    container.stop()
    
def getLogs(client,hostName):
    container = client.containers.get(hostName)
    logs = container.logs()
    return logs.decode('utf-8')
    
def get_date():
	return datetime.now().strftime('%Y-%m-%d')

def getContainerImageName(container):
    return container.attrs['Config']['Image']

def printDockerImageList(client):
    image_list = client.images.list()
    for image in image_list:
        print(image)
    
    
def getHostName(container_list,imageName):
    hostName=''
    for container in container_list:
        current_imageName = container.attrs['Config']['Image']
        if current_imageName == imageName:
            hostName = container.attrs['Config']['Hostname']
    return hostName
    
def getImageName(container_list,hostName):
    ImageName=''
    for container in container_list:
        current_hostName = container.attrs['Config']['Hostname']
        if current_hostName == hostName:
            ImageName = container.attrs['Config']['Image']
    return ImageName


#flask app
app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    logs=""
    active_container=[]
    container_list = []
    for val in configData['containers']:
        container_list.append(val['name'])
    containers = getActiveContainers(client)
    for container in containers:
        active_container.append(getContainerImageName(container))
    return render_template("index.html",containers=container_list, active_container=active_container,logs=logs)

@app.route('/logs')
def getLogsReq():
    container_name = request.args.get('container_name')
    container_list = getActiveContainers(client)
    containerHostName = getHostName(container_list,container_name)
    logs = getLogs(client,containerHostName)
    return logs

@app.route('/start')
def startContainerReq():
    container_name = request.args.get('container_name')
    startContainer(client,container_name)
    return '{} Started'.format(container_name)

@app.route('/stop')
def stopContainerReq():
    container_name = request.args.get('container_name')
    container_list = getActiveContainers(client)
    containerHostName = getHostName(container_list,container_name)
    stopContainer(client, containerHostName)
    return '{} Stopped'.format(container_name)

@app.route('/config')
def display_json():
    return jsonify(configData)


if __name__ == "__main__":
    configData = getConfig(configFile)
    
    client = docker.from_env()
    
    app.run(host="0.0.0.0")

    
    
