# CC7711-projeto_robotica

Link do vídeo: https://www.youtube.com/watch?v=EWpE2qWwyXQ

# Visão Geral

Este projeto consiste em um robô autônomo simulado no **Webots**, utilizando o modelo **e-puck** com controlador em **Python**. O robô apresenta comportamentos de navegação autônoma, detecção de colisões, recuperação de travamentos e supervisão de objetos móveis no ambiente.

---

## Estratégia de Navegação

O robô adota a seguinte lógica:

- Avança continuamente enquanto não detecta obstáculos.
- Em caso de colisão frontal (sensores `ps0` ou `ps7`):
  1. Empurra por 0.5 segundos;
  2. Recuo equivalente a 1.0 radiano de roda;
  3. Giro de 2.4 ou 4.8 radianos.

O ângulo de giro dobra a cada 2 colisões e inverte o sentido a cada 15 colisões.

---

## Estados do Robô

| Estado          | Ação                            |
|-----------------|---------------------------------|
| `STATE_MOVING`  | Avança sem obstáculos           |
| `STATE_PUSHING` | Empurra após colisão frontal    |
| `STATE_REVERSING` | Recuo após empurrão           |
| `STATE_TURNING` | Giro no próprio eixo            |
| `STATE_FOUND`   | Celebração ao encontrar a caixa leve |

---

## Detecção de Colisão

- Utiliza os sensores de proximidade `ps0` a `ps7`.
- Colisão frontal é detectada por `ps0` e `ps7`.
- Travamentos laterais são monitorados com `ps1` a `ps6`.

---

## Mecanismo Anti-Encalhamento

- Se qualquer sensor entre `ps1` e `ps6` mantiver valor acima de 250 por 2 segundos consecutivos:
  - O robô executa a sequência de empurrar, recuar e girar.
- Utilizado para escapar de situações como:
  - Estar entre duas caixas;
  - Encostar lateralmente em uma parede.

---

## Supervisor

- O controlador utiliza a classe `Supervisor()` para monitorar objetos com `DEF` começando por `"CAIXA"`.
- Armazena a posição inicial de todas as caixas no início da simulação.
- Durante a execução, verifica se houve alteração nas coordenadas X ou Y de alguma caixa.
- Se detectar movimentação, considera que a caixa leve foi encontrada.

---

## Comportamento ao Encontrar a Caixa Leve

- Ao detectar movimentação de uma caixa:
  - Entra em `STATE_FOUND`;
  - Gira indefinidamente no próprio eixo;
  - Pisca os 10 LEDs alternadamente a cada 0.5 segundos;
  - Imprime no terminal:

---

## Parâmetros Configuráveis

Os seguintes parâmetros estão definidos no início do código e podem ser ajustados conforme necessário:
```
COLISOES_GIRO_DUPLO = 2         # Gira o dobro a cada 2 colisões
COLISOES_MUDA_DIRECAO = 15      # Inverte o sentido de rotação a cada 15 colisões
STUCK_TIMEOUT = 2000            # Tempo para considerar travamento (em ms)
PUSH_DURATION = 500             # Duração do empurrão (em ms)
TURN_ANGLE = 2.4                # Ângulo padrão de giro (em radianos)
REVERSE_ANGLE = 1.0             # Recuo após colisão (em radianos de roda)
```
