# OLMT Server

This repo stores the ELM OLMT Server, which hosts the OLMT and an API service that currently allows the API user to create met data files for OLMT/ELM. This is currently deployed as a docker container. The OLMT code has been modifed and deploying the code here will not work (because it references the main branch of OLMT). Please see the container on Docker Hub: https://hub.docker.com/r/chrisfurlong03/elm_olmt_server 

## Vercel Blob Storage

It is important to note that the API service writes large files to a Blob Storage, in this case Vercel Storage. A vercel storage python package is used to interact with Vercel Storage specifically and code will need to be modified if you intend to use a different blob storage service. 
