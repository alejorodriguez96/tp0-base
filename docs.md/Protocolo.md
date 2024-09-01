### Protocolo de comunicación para agencias de lotería nacional
#### 1. Introducción
En este documento se describe el protocolo de comunicación que se utilizará 
para la comunicación entre clientes y servidor de un sistema de agencias de
lotería nacional desarrollado como TP0 de la matería Sistemas Distribuidos.

#### 2. Formato de los mensajes
Los mensajes intercambiados entre el cliente y el servidor tendrán el siguiente
formato:
```
<Tipo de mensaje | 1 byte><Largo del payload | 4 bytes><Payload | Longitud variable>
```
El campo `Tipo de mensaje` indica el tipo de mensaje que se está enviando. Los
tipos de mensajes posibles son:
- `0x01`: *Apuesta* - El cliente envía una apuesta al servidor.
- `0x02`: *Apuestas en batch* - El cliente envía varias apuestas al servidor.
- `0x03`: *Error* - El servidor envía un mensaje de error al cliente.
- `0x04`: *ACK* - El servidor envía un mensaje de confirmación al cliente.
- `0x05`: *END* - El cliente envía un mensaje de finalización al servidor.
- `0x06`: *Solicitud Resultado* - El cliente solicita el resultado de un sorteo.
- `0x07`: *Resultado Sorteo* - El servidor envía el resultado de un sorteo al cliente.
- `0x08`: *Sorteo en proceso* - El servidor envía un mensaje al cliente indicando que el sorteo está en proceso.

El campo `Largo del payload` indica la longitud del campo `Payload` en bytes.
El campo `Payload` contiene la información específica de cada tipo de mensaje.

#### 3. Mensajes
##### 3.1. Apuesta
El payload de un mensaje de tipo `Apuesta` tiene 6 campos separados por `0x1F`:
- `ID de la agencia` - Entero
- `Nombre del jugador` - String
- `Apellido del jugador` - String
- `Número de DNI del jugador` - Entero
- `Fecha de nacimiento del jugador` - String
- `Número apostado` - Entero
Entonces, por ejemplo, un mensaje de tipo `Apuesta` con los siguientes valores:
- `ID de la agencia`: 1
- `Nombre del jugador`: "Juan"
- `Apellido del jugador`: "Perez"
- `Número de DNI del jugador`: 12345678
- `Fecha de nacimiento del jugador`: "1990-01-01"
- `Número apostado`: 4245
Tendría el siguiente formato:
```
0x01 <longitud> 0x01 0x1F Juan 0x1F Perez 0x1F 12345678 0x1F 1990-01-01 0x1F 4245
```
__Nota: Los espacios son solo para claridad, no forman parte del mensaje.__

##### 3.2. Apuestas en batch
El payload de un mensaje de tipo `Apuestas en batch` tiene multiples apuestas, donde
cada apuesta tiene el mismo formato que el mensaje de tipo `Apuesta`, y están separadas
por `0x1E`. Por ejemplo, un mensaje de tipo `Apuestas en batch` podría tener el siguiente
formato:
```
0x02 <longitud> 0x01 0x1F Juan 0x1F Perez 0x1F 12345678 0x1F 1990-01-01 0x1F 4245 0x1E 0x01 0x1F Maria 0x1F Lopez 0x1F 87654321 0x1F 1980-02-02 0x1F 1234
```
__Nota: Los espacios son solo para claridad, no forman parte del mensaje.__

##### 3.3. Error
El payload de un mensaje de tipo `Error` tiene un campo con el mensaje de error. Por ejemplo,
un mensaje de tipo `Error` con el siguiente mensaje:
- `Mensaje de error`: "Error al procesar la apuesta"
Tendría el siguiente formato:
```
0x03 <longitud> Error al procesar la apuesta
```

##### 3.4. ACK
El payload de un mensaje de tipo `ACK` puede ser vacío o contener un mensaje de confirmación, pero
no se espera que el cliente haga nada con el mensaje de confirmación. Por ejemplo, un mensaje de tipo
`ACK` podría ser simplemente:
```
0x04 0x00
```
O podría tener un mensaje de confirmación:
```
0x04 <longitud> Apuesta procesada correctamente
```

##### 3.5. END
El payload de un mensaje de tipo `END` es vacío. Por ejemplo, un mensaje de tipo `END` podría ser simplemente:
```
0x05 0x00
```

##### 3.6. Solicitud Resultado
El payload de un mensaje de tipo `Solicitud Resultado` tiene un campo con el número de agencia que solicita
el resultado. Por ejemplo, un mensaje de tipo `Solicitud Resultado` con el siguiente número de agencia:
- `Número de agencia`: 1
Tendría el siguiente formato:
```
0x06 0x01 1
```

##### 3.7. Resultado Sorteo
El payload de un mensaje de tipo `Resultado Sorteo` tiene un único campo con el número de DNI del ganador, pero una cantidad variable de ganadores. Por ejemplo, un mensaje de tipo `Resultado Sorteo` con los siguientes números de documento:
- `Números de documento`: 12345678, 87654321
Tendría el siguiente formato:
```
0x07 <longitud> 12345678 0x1E 87654321
```

#### 3.8. Sorteo en proceso
El payload de un mensaje de tipo `Sorteo en proceso` es vacío. Por ejemplo, un mensaje de tipo `Sorteo en proceso` podría ser simplemente:
```
0x08 0x00
```
