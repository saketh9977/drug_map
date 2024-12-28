source ../dev.env
BASE_DIR=$(pwd)
CONTAINER_NAME=postgres-container
    
function post_deploy(){
	psql \
		-h $POSTGRES_HOST \
		-p $POSTGRES_PORT \
		-U $POSTGRES_ROOT_USER \
		-d $POSTGRES_ROOT_DB \
		-v POSTGRES_NONROOT_DB=$POSTGRES_NONROOT_DB \
		-v POSTGRES_NONROOT_USER=$POSTGRES_NONROOT_USER \
		-v POSTGRES_NONROOT_PASSWORD=$POSTGRES_NONROOT_PASSWORD \
		-f sql/setup.sql
}

function deploy(){

	set -x
	set -e

	mkdir -p $POSTGRES_MOUNT_DIR

	docker run --name $CONTAINER_NAME \
		-p 5432:5432 \
		-e POSTGRES_PASSWORD=$POSTGRES_ROOT_PASSWORD \
		-v $POSTGRES_MOUNT_DIR:/var/lib/postgresql/data \
		-v $BASE_DIR/postgresql.conf:/etc/postgresql/postgresql.conf \
		-d postgres:16.6 \
		-c 'config_file=/etc/postgresql/postgresql.conf'

}

function clean(){

	set -x
	set +e

	docker stop $CONTAINER_NAME
	docker rm $CONTAINER_NAME
	rm -rf $POSTGRES_MOUNT_DIR
}

if [[ "$1" == "deploy" ]]; then
	deploy
elif [[ "$1" == "post_deploy" ]]; then
	post_deploy
elif [[ "$1" == "clean" ]]; then
	clean
else
	echo "pass either deploy or post_deploy or clean as argument"
	exit 1
fi
