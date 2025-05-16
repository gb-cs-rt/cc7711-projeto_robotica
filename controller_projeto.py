from controller import Supervisor, DistanceSensor, Motor, LED

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

# === Parâmetros configuráveis ===
COLISOES_GIRO_DUPLO = 2      # a cada X colisões, gira o dobro
COLISOES_MUDA_DIRECAO = 15   # a cada X colisões, muda o sentido do giro
STUCK_TIMEOUT = 2000        # tempo em ms até considerar "preso" com sensor lateral

# === Constantes fixas ===
VELOCITY = 6.28
REVERSE_SPEED = -3.0
SENSOR_THRESHOLD = 250
TURN_ANGLE = 2.4
REVERSE_ANGLE = 1.0
MOVE_THRESHOLD = 0.01
PUSH_DURATION = 500  # ms

# Motores
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

# Encoders
left_encoder = robot.getDevice('left wheel sensor')
left_encoder.enable(timestep)

# LEDs
leds = [robot.getDevice(f'led{i}') for i in range(10)]
led_state = 0
led_timer = 0

# Sensores
sensor_names = [f"ps{i}" for i in range(8)]
sensors = [robot.getDevice(name) for name in sensor_names]
for s in sensors:
    s.enable(timestep)

# Estados
STATE_MOVING = 0
STATE_PUSHING = 1
STATE_REVERSING = 2
STATE_TURNING = 3
STATE_FOUND = 4

state = STATE_MOVING
reverse_start_angle = 0
turn_start_angle = 0
light_box_found = False
push_timer = 0

# Colisão e rotação
collision_count = 0
turn_angle = TURN_ANGLE
turn_direction = 1

# Lógica de stuck
stuck_timer = 0
is_stuck = False

# Buscar caixas com DEF "CAIXA*"
caixas = []
caixas_pos_inicial = []
root_children = robot.getRoot().getField("children")

for i in range(root_children.getCount()):
    node = root_children.getMFNode(i)
    def_name = node.getDef()
    if def_name and def_name.startswith("CAIXA"):
        caixas.append((def_name, node))
        caixas_pos_inicial.append(node.getPosition())

# Loop principal
while robot.step(timestep) != -1:
    # Detectar se alguma caixa foi movida
    if not light_box_found:
        for i, (def_name, caixa) in enumerate(caixas):
            pos = caixa.getPosition()
            pos_inicial = caixas_pos_inicial[i]
            dx = abs(pos[0] - pos_inicial[0])
            dy = abs(pos[1] - pos_inicial[1])
            if dx >= MOVE_THRESHOLD or dy >= MOVE_THRESHOLD:
                light_box_found = True
                state = STATE_FOUND
                print(f"encontrei a caixa leve: {def_name}")
                break

    sensor_values = [sensor.getValue() for sensor in sensors]
    left_pos = left_encoder.getValue()

    # Verificação de encalhamento lateral (ps1 a ps6)
    if state == STATE_MOVING:
        lateral_stuck = any(sensor_values[i] > SENSOR_THRESHOLD for i in range(1, 7))
        if lateral_stuck:
            stuck_timer += timestep
        else:
            stuck_timer = 0

        if stuck_timer >= STUCK_TIMEOUT:
            # Considera preso: inicia escape como se fosse colisão frontal
            stuck_timer = 0
            is_stuck = True
            push_timer = 0
            state = STATE_PUSHING
            left_motor.setVelocity(VELOCITY)
            right_motor.setVelocity(VELOCITY)
            continue

    if state == STATE_MOVING:
        if sensor_values[0] > SENSOR_THRESHOLD or sensor_values[7] > SENSOR_THRESHOLD:
            push_timer = 0
            state = STATE_PUSHING
            left_motor.setVelocity(VELOCITY)
            right_motor.setVelocity(VELOCITY)
        else:
            left_motor.setVelocity(VELOCITY)
            right_motor.setVelocity(VELOCITY)

    elif state == STATE_PUSHING:
        push_timer += timestep
        left_motor.setVelocity(VELOCITY)
        right_motor.setVelocity(VELOCITY)
        if push_timer >= PUSH_DURATION:
            reverse_start_angle = left_pos
            state = STATE_REVERSING
            collision_count += 1

            if collision_count % COLISOES_MUDA_DIRECAO == 0:
                turn_direction *= -1

            turn_angle = TURN_ANGLE * 2 if collision_count % COLISOES_GIRO_DUPLO == 0 else TURN_ANGLE

            left_motor.setVelocity(REVERSE_SPEED)
            right_motor.setVelocity(REVERSE_SPEED)

    elif state == STATE_REVERSING:
        delta = abs(left_pos - reverse_start_angle)
        if delta >= REVERSE_ANGLE:
            turn_start_angle = left_encoder.getValue()
            state = STATE_TURNING
            left_motor.setVelocity(turn_direction * -VELOCITY)
            right_motor.setVelocity(turn_direction * VELOCITY)

    elif state == STATE_TURNING:
        delta = abs(left_encoder.getValue() - turn_start_angle)
        if delta >= turn_angle:
            state = STATE_MOVING
            left_motor.setVelocity(VELOCITY)
            right_motor.setVelocity(VELOCITY)
        else:
            left_motor.setVelocity(turn_direction * -VELOCITY)
            right_motor.setVelocity(turn_direction * VELOCITY)

    elif state == STATE_FOUND:
        left_motor.setVelocity(-VELOCITY)
        right_motor.setVelocity(VELOCITY)
        led_timer += timestep
        if led_timer >= 500:
            led_state = 1 - led_state
            for led in leds:
                led.set(led_state)
            led_timer = 0
