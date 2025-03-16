from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController 


app=Ursina()

player = FirstPersonController()

gun = Entity(
    parent=camera.ui,
    model="cube",
    color=color.azure,
    scale=(0.2, 0.5, 1),
    position=(0.6, -0.45)
)

bullets = []

player_health = 100
health_text = Text(text=f'health: {player_health}', position=(-0.75, -0.4), scale=2, background=True)

player_score = 0
score_text = Text(text=f'Score: {player_score}', position=(-0.75, 0.45), scale=2, background=True)

class Enemy(Entity):
    def __init__(self, position=(5,1,5)):
        super().__init__(
            model='cube',
            color=color.red,
            scale=1.5,
            position=position,
            collider='box'
        )  
        self.health=3      

enemies = []
for i in range(5):
    enemy = Enemy(position=(random.uniform(0,10), 1, random.uniform(0,10)))
    enemies.append(enemy)


def input(key):
    if key == 'left mouse down':
        shoot()

def shoot():
    bullet = Entity(
        model = 'sphere',
        color=color.yellow,
        scale=0.1,
        position=camera.world_position,
        collider='sphere'
    )

    bullet.direction = camera.forward
    bullet.speed = 50
    bullets.append(bullet)

def spawn_enemy():
    enemy = Enemy(position=(random.uniform(0,10), 1, random.uniform(0,10)))
    enemies.append(enemy)

tiles = []
for z in range(30):
     for x in range(30):
          tile = Entity(
               model="cube",
               color=color.dark_gray,
               collider="box",
               ignore=False,
               position=(x, 0, z),
               parent=scene,
               origin_y=0.5,
               texture="white_cube",
               name=f'tile{x}_{z}'
          )
          tiles.append(tile)

def notice_ground():
    ray_origin = player.position + Vec3(0, 2, 0)

    hit_info = raycast(
        ray_origin,
        direction=Vec3(0, -1, 0),
        distance=5,
        ignore=[player, gun] + enemies + bullets
    )

    ground = None

    if hit_info.hit:
        ground = hit_info.entity
        for tile in tiles[:]:
            if tile.name == ground.name:
                tiles.remove(tile)
                invoke(fall_tile, tile, delay=3.5)
                break

def fall_tile(tile):
    position= tile.position
    name = tile.name

    tile.animate_position(tile.position + Vec3(0, -10, 0), duration=1)
    invoke(destroy, tile, delay=1.5)
    
    invoke(respawn_tile, position, name, delay=7)

def respawn_tile(position, name):
    new_tile = Entity(
        model="cube",
        color=color.dark_gray,
        collider="box",
        ignore=False,
        position=position, parent=scene,
        origin_y=0.5,
        texture="white_cube",
        name=name
    )
    tiles.append(new_tile)

def update():
    global player_health, player_score

    notice_ground()

    for bullet in bullets[:]:
            bullet.position += bullet.direction * bullet.speed * time.dt


            if distance(bullet.position, player.position) > 100:
                bullets.remove(bullet)
                destroy(bullet)
                continue

            for enemy in enemies[:]:
                if bullet.intersects(enemy).hit:
                    enemy.health -= 1
                    if enemy.health <=0:
                        enemies. remove(enemy)
                        destroy(enemy)
                        spawn_enemy()

                        player_score += 1
                        score_text.text = f'score: {player_score}'
                    bullets.remove(bullet)
                    destroy(bullet)
                    break

    for enemy in enemies:
            enemy.look_at(player.position)
            enemy.position += enemy.forward * time.dt * 2


            if distance(enemy.position, player.position) < 1.5:
                player_health -= 5 * time.dt
                health_text.text = f'health: {int(player_health)}'

                if player_health <= 0:
                    health_text.text = 'GAME OVER'
                    application.pause()

    if player.y < -10:
        health_text.text = 'GAME OVER'
        application.pause()



Sky()
DirectionalLight().look_at(Vec3(1,-1,-1))
app.run()

