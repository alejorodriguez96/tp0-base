## Mecanismos de sincronización

El objetivo de este documento es describir los mecanismos de sincronización que se utilizaron en el desarrollo del TP, especificamente durante el ejercicio 8 que involucra que el servidor atienda múltiples clientes de manera concurrente.

### Secciones críticas
El servidor tiene dos secciones críticas que deben ser protegidas para evitar race conditions:
1. Storage de apuestas

El servidor debe leer y escribir apuestas en un archivo en disco. Los métodos para realizar estas operaciones son provistos por la cátedra y no son thread-safe.

2. Cantidad de clientes que terminaron de procesar sus apuestas

El servidor solo responderá con el resultado del sorteo cuando un cliente lo solicite siempre y cuando todos los clientes hayan terminado de procesar sus apuestas. Para esto, se tiene una estructura (un array) que indica si cada cliente terminó de procesar sus apuestas.

### Mecanismos de sincronización
Para proteger las secciones críticas se utilizaron los siguientes mecanismos de sincronización:
1. Pasaje de mensajes

La escritura y lectura de las apuestas se realiza a través de un canal de mensajes. De está forma existe un StorageService que se encarga de leer y escribir las apuestas en el archivo, como solo un proceso está realizando estas operaciones a la vez, se puede garantizar que es thread-safe.

El proceso que atiende a un cliente recibe una referencia a la cola de mensajes que utilizará para enviar el pedido y un extremo de un Pipe. El StorageService usa ese extremo para enviar la respuesta al proceso que atendió al cliente.

2. Mutex

Para proteger la cantidad de clientes que terminaron de procesar sus apuestas se utilizó un mutex. Cada vez que un cliente avisa que terminó de procesar sus apuestas, se actualiza la lista. Para eso se utiliza [Array](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Array) del modulo multiprocessing de Python. Es un tipo de dato de memoria compartida que se puede compartir entre procesos. Tiene un lock interno que se adquiere automáticamente cuando se modifica el array.
