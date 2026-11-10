# REDES — propuesta de topología

## Diagrama de topología

![Propuesta de topología de red para el entorno de una PyME](./images/diagrama-redes.png)

> **Alcance:** el diagrama y el direccionamiento son una propuesta académica para una red local; no describen la infraestructura desplegada de Estudi Web. El código conecta con MongoDB usando `MONGO_URI` (por defecto, MongoDB Atlas). Por tanto, la VLAN 10 de esta propuesta puede alojar el servidor de la aplicación, pero no representa la ubicación de la base de datos real.

## Diseño y justificación

La red propuesta está pensada para una PyME de desarrollo de software y consultoría. Utiliza una topología de estrella extendida con segmentación lógica por VLAN.

La topología centraliza las conexiones en el router y el switch administrable, facilita la gestión del tráfico y permite aislar fallas de los puestos finales. También permite sumar puestos sin modificar la estructura principal. El router realiza el enrutamiento entre VLAN y brinda salida a Internet; el switch se conecta al router mediante un enlace troncal.

## Componentes y segmentos

- **VLAN 10 – Servidores:** reserva direcciones estáticas para los servidores internos, por ejemplo el servidor de aplicación Flask. La base MongoDB configurada por `MONGO_URI` es un servicio externo y no se ubica en esta VLAN.
- **VLAN 20 – PCs cableadas:** conecta los puestos de trabajo por Ethernet. Las direcciones se asignan dinámicamente mediante DHCP.
- **VLAN 30 – Wi-Fi Staff:** corresponde al SSID corporativo del punto de acceso. Las direcciones se asignan mediante DHCP.
- **VLAN 40 – Wi-Fi Invitados:** corresponde al SSID para invitados, separado del tráfico corporativo. Las direcciones se asignan mediante DHCP.

El punto de acceso se conecta al switch y separa las redes inalámbricas corporativa y de invitados en sus respectivas VLAN.

## Tabla de direccionamiento

| VLAN (ID y nombre) | Red / Prefijo | Máscara | Rango de hosts | Gateway | Hosts útiles |
|---|---|---|---|---|---:|
| VLAN 10 – Servidores | 192.168.10.0/24 | 255.255.255.0 | 192.168.10.2–192.168.10.50 (estáticas) | 192.168.10.1 | 254 |
| VLAN 20 – PCs cableadas | 192.168.20.0/24 | 255.255.255.0 | 192.168.20.2–192.168.20.254 (DHCP) | 192.168.20.1 | 254 |
| VLAN 30 – Wi-Fi Staff | 192.168.30.0/24 | 255.255.255.0 | 192.168.30.2–192.168.30.254 (DHCP) | 192.168.30.1 | 254 |
| VLAN 40 – Wi-Fi Invitados | 192.168.40.0/24 | 255.255.255.0 | 192.168.40.2–192.168.40.254 (DHCP) | 192.168.40.1 | 254 |

Las subredes utilizan direcciones privadas del bloque 192.168.0.0/16, dividido en redes /24. Cada /24 ofrece 254 direcciones de host utilizables; el conteo incluye el gateway (.1). Los rangos de la tabla indican las direcciones disponibles para los dispositivos, excluyendo el gateway. En la VLAN 10 se reserva el rango .2–.50 para direcciones estáticas de los servidores internos.
