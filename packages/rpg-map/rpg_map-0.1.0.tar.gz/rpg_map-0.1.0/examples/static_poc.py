from rpg_map import Travel, Map, MapType, PathStyle, PathProgressDisplayType, PathDisplayType
from PIL import Image

LOCAL_DIR = "../test_assets/map.png"
BACKGROUND_DIR = "../test_assets/background.png"
GRID_SIZE = 20
START, END = (198, 390), (330,  512)
START_X, START_Y = START


def main():
    image = Image.open(LOCAL_DIR).convert("RGBA")
    # get image bytes
    image_bytes = list(image.tobytes())
    background = Image.open(BACKGROUND_DIR).convert("RGBA")
    # get background bytes
    background_bytes = list(background.tobytes())
    map = Map(
        image_bytes,
        image.size[0],
        image.size[1],
        GRID_SIZE,
        MapType.Hidden,
        obstacles=[[(160, 240), (134, 253), (234, 257), (208, 239)]],
    )

    map.unlock_point_from_coordinates(START_X, START_Y)
    travel = Travel(map, START, END)
    path_bits =  Map.draw_background(
        map.with_dot(START_X, START_Y, (255, 0, 0, 255), 4).draw_path(
            travel,
            0.5,
            2,
            PathStyle.DottedWithOutline((255, 0, 0, 255), (255, 255, 255, 255)),
            PathDisplayType.AboveMask,
            PathProgressDisplayType.Progress,
        ),
        background_bytes
    )

    # Display the image
    image = Image.frombytes("RGBA", (image.width, image.height), path_bits)
    image.show()


if __name__ == "__main__":
    main()
