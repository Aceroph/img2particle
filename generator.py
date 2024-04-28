from PIL import Image
import json
import sys

img = Image.open(" ".join(sys.argv[1:])).convert("RGBA")
print(f"Image size : {img.width}x{img.height}")

density = ((img.width * img.height) ** 0.5) // 96
print(f"Density : {density}x")

with open("config.json", "r+") as cfg:
    try:
        config: dict = json.loads(cfg.read())
    except:
        config: dict = {
            "scale": 1.0,
            "width": 3.0,
            "height": 3.0,
            "tilt": "XY",
            "output": "./output.mcfunction",
            "templates": {
                "*": "particle minecraft:dust{color:[R,G,B],scale:SCALE} ~X ~Y ~Z"
            },
        }
        json.dump(config, cfg, indent=4)

posX = []
posY = []
posZ = []
colors = []

for y in range(1, img.height, int(density)):
    for x in range(1, img.width, int(density)):
        r, g, b, a = img.getpixel((x, y))
        if a != 0:
            posX.append(x * config["width"] / img.width - config["width"] / 2)

            # Render orientation
            if config["axis"] == "XZ":
                posZ.append(y * config["height"] / img.height - config["height"] / 2)
                posY.append(0)
            else:
                posY.append(y * config["height"] / img.height - config["height"] / 2)
                posZ.append(0)

            colors.append((r, g, b))


with open(config["output"], "w") as out:
    for i, x in enumerate(posX):
        r, g, b = colors[i]
        _hex = "#%02x%02x%02x" % (r, g, b)

        template: str = config["templates"].get(_hex) or config["templates"]["*"]

        command = (
            template.replace("X", format(x, ".3f"))
            .replace("Y", format(posY[::-1][i], ".3f"))
            .replace("Z", format(posZ[::-1][i], ".3f"))
            .replace("R", format(r / 255, ".2f"))
            .replace("G", format(g / 255, ".2f"))
            .replace("B", format(b / 255, ".2f"))
            .replace("SCALE", format(config["scale"]))
        )
        print(f"{i+1}/{len(posX)} | {command}")
        out.write(command + "\n")
