COMUNICACION MULTICAST EN GRUPO
==============================

¿QUE HACE EL PROGRAMA?

Permite que tres computadoras reciban mensajes enviados a un grupo
multicast. Una cuarta computadora puede enviar mensajes a un coordinador,
que los reenvia al grupo.

ROLES

1. Nodos del grupo
   Cada nodo se suscribe al mismo grupo multicast: 239.10.10.10, puerto
   5007. Se queda esperando y muestra los mensajes que recibe.

2. Coordinador
   Escucha mensajes externos en el puerto UDP 5008. Cuando recibe uno,
   le agrega un identificador, un numero de secuencia y la fecha, y luego
   lo envia al grupo multicast.

3. Equipo externo
   Es la cuarta computadora. Escribe un mensaje y se lo envia al
   coordinador usando la IP de esa computadora.

ANALOGIA SENCILLA

Imagina un edificio con tres personas suscriptas a un altavoz compartido.
Ese altavoz representa el grupo multicast: cuando se anuncia algo, los
tres nodos pueden escucharlo al mismo tiempo.

El coordinador es la recepcion del edificio. La cuarta computadora no
puede hablar directamente por el altavoz: le entrega su mensaje a
recepcion, y recepcion lo anuncia al grupo y le asigna un numero.

En el codigo, cada mensaje se prepara como un objeto JSON y se envia en
un unico datagrama UDP. Esto mantiene los limites entre mensajes: cada
datagrama recibido se procesa como un mensaje separado. Sin embargo,
UDP no confirma que el mensaje haya llegado ni lo vuelve a enviar si se
pierde en la red.

COMO EJECUTARLO

Se necesita Python instalado en las cuatro computadoras y el archivo
multicast_grupo.py disponible en cada una.

1. En una computadora del grupo, iniciar el coordinador:

   python multicast_grupo.py coordinador

   Anotar la direccion IP de esa computadora en la red local. Por ejemplo:
   192.168.1.100

2. En cada una de las tres computadoras que formaran el grupo, abrir una
   terminal distinta y ejecutar:

   python multicast_grupo.py nodo Nodo1
   python multicast_grupo.py nodo Nodo2
   python multicast_grupo.py nodo Nodo3

   Se puede ejecutar el coordinador y uno de los nodos en la misma
   computadora, usando dos terminales diferentes.

3. En la cuarta computadora, ejecutar el programa con la IP del
   coordinador:

   python multicast_grupo.py externo 192.168.1.100

   Escribir un mensaje y presionar Enter. Para salir, escribir:

   salir

REQUISITOS DE RED

- Los cuatro equipos deben poder comunicarse entre si por la red.
- La red debe permitir trafico multicast para el grupo 239.10.10.10.
- El firewall debe permitir UDP en los puertos 5007 y 5008.
- Si se usa otra red, puede ser necesario configurar el router o la
  interfaz de red para permitir multicast.
- La IP que se pasa al modo "externo" debe ser la IP del coordinador,
  no la direccion multicast.

RESUMEN DE LOS MODOS

python multicast_grupo.py nodo Nombre
    Se une al grupo y recibe sus mensajes.

python multicast_grupo.py coordinador
    Recibe mensajes externos y los distribuye al grupo.

python multicast_grupo.py externo IP_DEL_COORDINADOR
    Envia mensajes al coordinador desde una computadora externa al grupo.
