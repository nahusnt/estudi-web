# REDES

## Diagrama de red

```text
                           +-----------------------+
                           |       Internet        |
                           +-----------+-----------+
                                       |
                                       |
                              +--------v--------+
                              |  Router/Gateway |
                              +--------+--------+
                                       |
                  +--------------------+--------------------+
                  |                                         |
          +-------v-------+                         +-------v-------+
          | VLAN 10       |                         | VLAN 20       |
          | Servidores    |                         | Usuarios      |
          | 192.168.10.0/28 |                      | 192.168.20.0/24 |
          +-------+-------+                         +-------+-------+
                  |                                         |
                  |                                         |
          +-------v-------+                         +-------v-------+
          | App Flask     |                         | Cliente Web   |
          | 192.168.10.11 |                         | 192.168.20.X |
          | Puerto 5000   |                         | Navegador     |
          +---------------+                         +---------------+
                  |
                  |
                  v
          +-------------------------------+
          | MongoDB Atlas / Base de datos |
          | (Servicios en la nube)        |
          +-------------------------------+
```

### Descripción

- La aplicación Estudi Web se ejecuta localmente con Flask en el servidor de desarrollo.
- Los clientes acceden desde la red interna o desde Internet mediante el gateway.
- La capa de datos se almacena en MongoDB Atlas, por lo que la red local solo requiere acceso de salida a la base de datos remota.
- La segmentación por VLAN facilita la administración, seguridad y mantenimiento del entorno.

## Tabla de direccionamiento

| VLAN (ID y nombre) | Red / Prefijo | Máscara | Rango de hosts | Gateway | Hosts útiles |
|---|---|---|---|---|---|
| 10 – Servidores | 192.168.10.0/28 | 255.255.255.240 | 192.168.10.1 - 192.168.10.14 | 192.168.10.1 | 14 |
| 20 – Usuarios | 192.168.20.0/24 | 255.255.255.0 | 192.168.20.1 - 192.168.20.254 | 192.168.20.1 | 254 |
| 30 – Gestión | 192.168.30.0/26 | 255.255.255.192 | 192.168.30.1 - 192.168.30.62 | 192.168.30.1 | 62 |
| 40 – Wi‑Fi | 192.168.40.0/27 | 255.255.255.224 | 192.168.40.1 - 192.168.40.30 | 192.168.40.1 | 30 |

## Observaciones

- El rango útil de cada subred excluye la dirección de red y la dirección de broadcast.
- El gateway se configura en la primera dirección válida de cada VLAN.
- Los equipos de la app y de la base de datos pueden ubicarse en redes distintas si se habilita el enrutamiento y el acceso seguro.
- En un entorno real, los valores deben ajustarse al diseño específico del campus, laboratorio o infraestructura de la empresa.
