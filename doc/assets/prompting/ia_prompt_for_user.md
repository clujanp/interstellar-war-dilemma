# ¡Crea tu Estrategia en el Interstellar War Dilemma! 🪐🚀⚔️

En este juego intergaláctico, cada jugador diseña una **estrategia** para liderar a su civilización. No te preocupes si no sabes programar, un **asistente inteligente** te guiará para crear tu propia estrategia en Python, ¡sin necesidad de experiencia! 


## ¿Cómo funciona? 🛠️

1. **Nombra tu estrategia**: ¿Cómo quieres que se llame?
2. **Decide el comportamiento**: ¿Tu civilización será agresiva, cooperativa o algo intermedio? Aquí decides las reglas.
3. **Factores clave**: La estrategia tomará en cuenta:
   - **Planeta**: Donde ocurre la escaramuza (puede tener un costo alto, medio, bajo o ninguno).
   - **Oponente**: ¿Cómo te has enfrentado a ellos en el pasado?
   - **Recursos**: ¿Quieres ser más agresivo si tienes muchos recursos o más cuidadoso si tienes pocos?


## ¡Tu misión! 🎯

Define cuándo **cooperar** o **atacar** basándote en estos factores. El asistente se encargará de convertir tus decisiones en código Python para que no tengas que preocuparte por programar.

### Ejemplo sencillo de estrategia:

```python
def estrategia(memories, planet, opponent, resources):
    if memories.aggressions(opponent).percent > 80:
        return False  # Atacar si el oponente fue muy agresivo.
    return True  # Cooperar si no fue muy agresivo.
```


## ¿Listo para diseñar tu civilización? 🚀
Responde estas preguntas para crear tu estrategia:

1. **¿Cómo debería comportarse tu civilización** (agresiva, cooperativa, mixta)**?**
2. **¿Qué factores influyen en la decisión** (recursos, comportamiento del oponente, planeta)**?**
3. **¿Cuándo cooperar y cuándo atacar?**
4. **¿Te gustaría inspirarte en una estrategia existente** (cooperación siempre, agresión siempre, aleatoria)**?**


## Ejemplo de creación de estrategia 💡

1. **¿Cómo debería comportarse tu civilización (agresiva, cooperativa, mixta)?**
   - Mi civilización será **mixta**, dependiendo del comportamiento previo de mi oponente.

2. **¿Qué factores influyen en la decisión (recursos, comportamiento del oponente, planeta)?**
   - Si tengo **recursos** altos, seré más agresivo. Si tengo pocos, cooperaré. También, si el **oponente** fue muy agresivo en el pasado, atacaré más. El **costo del planeta** influirá: en planetas con costo bajo, seré más agresivo.

3. **¿Cuándo cooperar y cuándo atacar?**
   - **Cooperaré** si el oponente ha sido cooperativo en las últimas rondas, o si no tengo suficientes recursos.
   - **Atacaré** si el oponente ha sido agresivo más del 50% del tiempo, o si tengo recursos suficientes para arriesgarme.

4. **¿Te gustaría inspirarte en una estrategia existente (cooperación siempre, agresión siempre, aleatoria)?**
   - Me basaré en una estrategia tipo **Tit-for-Tat** (ojo por ojo), pero adaptada a los recursos y comportamiento del oponente.

### Código generado:

```python
from . import Cost, Position


def estrategia(opponent, planet, memories, resources):
    # Si el planeta es barato, atacaré más.
    if planet.cost == Cost.LOW:
        return Position.AGGRESSION

    # Reviso si el oponente ha sido muy agresivo (>50% del tiempo).
    if memories.aggressions(opponent).percent > 50:
        return Position.AGGRESSION

    # Si tengo menos de 3 recursos, cooperaré para no perderlos.
    if resources < 3:
        return Position.COOPERATION

    # Si el oponente ha sido cooperativo en las últimas 2 rondas.
    if (
        memories.last_positions(opponent, 2)
        == [Position.COOPERATION, Position.COOPERATION]
    ):
        return Position.COOPERATION

    # Si no se cumple ninguna de las anteriores, cooperaré por defecto.
    return Position.COOPERATION
```

Con esta guía, puedes ajustar tu estrategia según las respuestas! Si tienes dudas, el asistente te ayudará a convertir tus ideas en código efectivo. ¡A jugar! 🎮 🌌


## Anexo: estrategias por pre fabricadas 🤖
TODO: Agregar estrategias pre fabricadas con descripcion y tabla de simulacion.