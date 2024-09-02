#!/bin/bash
RESPONSE=$(docker run --rm -i --network tp0_testing_net --entrypoint sh gophernet/netcat -c 'echo "Hola mundo" | nc server 12345')

if [ "$RESPONSE" = "Hola mundo" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
