#!/bin/bash

set -e
source ../dev.env
source utils.sh
BASE_DIR=$(pwd)
CONTAINER_NAME=postgres-container
FILE_NAME=$(basename $0)

function clean(){

	set -x
	set +e

	docker stop $CONTAINER_NAME
	docker rm $CONTAINER_NAME
	rm -rf $POSTGRES_MOUNT_DIR

	set -e
}

function deploy(){

	set -x
	set -e

	mkdir -p $POSTGRES_MOUNT_DIR

	docker run \
		--name $CONTAINER_NAME \
		-p 5432:5432 \
		-e POSTGRES_PASSWORD=$POSTGRES_ROOT_PASSWORD \
		-v $POSTGRES_MOUNT_DIR:/var/lib/postgresql/data \
		-v $BASE_DIR/postgresql.conf:/etc/postgresql/postgresql.conf \
		-d postgres:16.6 \
		-c 'config_file=/etc/postgresql/postgresql.conf'

	set +x
	wait_for_container_to_start_running $CONTAINER_NAME
	set +x

	# wait for postgres-container to accept connections
	while true; do
		
		set +e
		res_pg=$(docker exec $CONTAINER_NAME pg_isready -U $POSTGRES_ROOT_USER)
		set -e
		
		echo "$FILE_NAME|$LINENO|$res_pg"

		if [[ "$res_pg" == *"- no response"* ]]; then
			echo "$FILE_NAME|$LINENO|waiting for container $CONTAINER_NAME to accept connections..."
			sleep 3
			continue
		fi

		if [[ "$res_pg" == *"- accepting connections"* ]]; then
			echo "$FILE_NAME|$LINENO|container $CONTAINER_NAME is accepting connections"
			break
		fi

		echo "$FILE_NAME|$LINENO|unexpected response: |$res_pg|"
		exit 1
	done
	# --------------------------------------------------------
	
	set -x
}

function post_deploy(){
	set -x
	set -e

	export PGHOST=$POSTGRES_HOST
	export PGPORT=$POSTGRES_PORT
	export PGUSER=$POSTGRES_ROOT_USER
	export PGPASSWORD=$POSTGRES_ROOT_PASSWORD
	export PGDATABASE=$POSTGRES_ROOT_DB
	
	psql \
		-v POSTGRES_NONROOT_DB=$POSTGRES_NONROOT_DB \
		-v POSTGRES_NONROOT_USER=$POSTGRES_NONROOT_USER \
		-v POSTGRES_NONROOT_PASSWORD=$POSTGRES_NONROOT_PASSWORD \
		-f sql/setup.sql
}

if [[ "$1" == "clean" ]]; then
	clean
elif [[ "$1" == "deploy" ]]; then
	deploy
elif [[ "$1" == "post_deploy" ]]; then
	post_deploy
else
	echo "$FILE_NAME|$LINENO|pass either deploy or post_deploy or clean as argument"
	exit 1
fi
