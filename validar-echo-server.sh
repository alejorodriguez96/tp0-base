#!/bin/bash
RESPONSE=$(docker exec -i server bash -c 'echo -n "Hola mundo" | nc server 12345')

if [ "$RESPONSE" = "Hola mundo" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
