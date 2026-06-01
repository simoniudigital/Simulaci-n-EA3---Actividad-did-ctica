# Simulación de Atención Bancaria mediante Eventos Discretos

## Descripción del Proyecto

Este proyecto fue desarrollado para la asignatura **Simulación** de la Institución Universitaria Digital de Antioquia.

El objetivo consiste en modelar y analizar el comportamiento de un sistema de atención bancaria compuesto por tres cajeros, evaluando diferentes configuraciones operativas con el fin de identificar cuál ofrece mejores tiempos de espera y una utilización más eficiente de los recursos.

La simulación se implementó en Python utilizando técnicas de **simulación por eventos discretos**, permitiendo representar de forma realista la llegada de clientes, la atención en ventanilla y la formación de colas.

---

## Integrantes

* Luisa Fernanda Gomez Quiroz
* Simon Arbey Castaño Rios
* Juan Pablo Gonzalez Gil

---

## Información Académica

**Institución:** Institución Universitaria Digital de Antioquia

**Asignatura:** Simulación - PREICA2601B020049

**Docente:** Julian Andres Loaiza

**Fecha:** Mayo de 2026

---

## Objetivo

Analizar el desempeño de un banco que dispone de tres cajeros y determinar si resulta más eficiente:

* Mantener los tres cajeros atendiendo cualquier tipo de operación.
* Asignar cajeros exclusivos para retiros y pagos.
* Incorporar cambios en la distribución de recursos para optimizar la atención.

---

## Características del Modelo

La simulación considera:

* Jornada laboral de 8 horas (480 minutos).
* Tres cajeros de atención.
* Diez réplicas independientes para aumentar la confiabilidad de los resultados.
* Distribuciones exponenciales para modelar tiempos de llegada y servicio.
* Clientes con diferentes perfiles de atención.
* Política FIFO (First In, First Out) para la gestión de colas.

---

## Tipos de Operaciones

Los usuarios pueden realizar:

### Retiros

* Rápido
* Normal
* Lento
* Muy lento

### Pagos o Consignaciones

* Rápido
* Normal
* Lento
* Muy lento

Cada perfil posee:

* Tiempo promedio de servicio.
* Tiempo promedio de llegada.
* Probabilidad de ocurrencia.

---

## Escenarios Evaluados

### Escenario 1: Cajeros Mixtos

Los tres cajeros atienden cualquier tipo de transacción.

### Escenario 2: Especialización 1R + 2P

* 1 cajero exclusivo para retiros.
* 2 cajeros exclusivos para pagos.

### Escenario 3: Especialización 2R + 1P

* 2 cajeros exclusivos para retiros.
* 1 cajero exclusivo para pagos.

---

## Indicadores Analizados

El sistema calcula automáticamente:

* Tiempo promedio de servicio por cajero.
* Cantidad promedio de usuarios atendidos.
* Usuarios atendidos por réplica.
* Tiempo promedio de espera.
* Tiempo máximo de espera.
* Utilización de cada cajero.
* Necesidad de incorporar un nuevo cajero.
* Configuración recomendada.

---

## Tecnologías Utilizadas

* Python 3
* NumPy
* Pandas

---

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/usuario/simulacion-banco.git
cd simulacion-banco
```

Instalar dependencias:

```bash
pip install numpy pandas
```

---

## Ejecución

Ejecutar el programa:

```bash
python simulacion_banco.py
```

El sistema generará automáticamente los resultados estadísticos para cada escenario y mostrará una comparación final con la configuración recomendada.

---

## Resultados Obtenidos

Los experimentos realizados mostraron que:

* El esquema de tres cajeros mixtos obtuvo el menor tiempo promedio de espera.
* Los escenarios con cajeros exclusivos generaron mayores tiempos de espera debido al desbalance entre la demanda de retiros y pagos.
* La utilización de los cajeros se mantuvo dentro de niveles aceptables.
* No se identificó la necesidad de incorporar un nuevo cajero.

---

## Conclusiones

La simulación permitió analizar diferentes estrategias de atención bancaria sin intervenir el sistema real.

Los resultados evidenciaron que mantener los tres cajeros operando de forma mixta proporciona el mejor desempeño general, minimizando los tiempos de espera y distribuyendo adecuadamente la carga de trabajo.

Este proyecto demuestra la utilidad de la simulación de eventos discretos como herramienta para apoyar la toma de decisiones en procesos de atención al cliente y optimización operativa.

---

## Licencia

Proyecto desarrollado con fines académicos para la asignatura de Simulación de la Institución Universitaria Digital de Antioquia.
