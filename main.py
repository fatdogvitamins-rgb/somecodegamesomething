def spin_entity(entity, amount=1):
    entity.rotation_x += amount
    entity.rotation_y += amount
    entity.rotation_z += amount


def run_cube_game():
    try:
        from ursina import EditorCamera, Entity, Ursina, color
    except ModuleNotFoundError:
        print("Ursina is not installed yet. Run: pip install ursina")
        return

    app = Ursina()

    otherthing = Entity(
        model="cube",
        color=color.azure,
        scale=(1, 1, 1),
        position=(0, 0, 0),
    )
    otherthing.update = lambda: spin_entity(otherthing, 1)

    mything = Entity(
        model="cube",
        color=color.red,
        scale=(3, 1, 2),
        position=(9, 8, 6),
    )
    mything.update = lambda: spin_entity(mything, 1)

    EditorCamera()
    app.run()


if __name__ == "__main__":
    run_cube_game()
