FILE_NAME=$(basename $0)

function wait_for_container_to_start_running(){

	set +x
    set -e
	
	container_name=$1

    while true; do
        status=$(docker inspect -f '{{.State.Status}}' $container_name)
        if [ "$status" == "restarting" ]; then
            echo "$FILE_NAME|$LINENO|waiting for container $container_name to reach State=Running..."
            sleep 3
            continue
        fi

        echo "$FILE_NAME|$LINENO|container $container_name status=$status"
        if [ "$status" != "running" ]; then
            echo "$FILE_NAME|$LINENO|container $container_name failed to reach status=running"
            exit 1
        fi
        break
    done	

	set -x
}