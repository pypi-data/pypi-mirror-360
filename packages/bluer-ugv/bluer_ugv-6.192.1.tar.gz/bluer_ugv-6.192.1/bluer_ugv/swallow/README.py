assets2 = "https://github.com/kamangir/assets2/blob/main/bluer-swallow"

dict_of_images = {
    "https://github.com/kamangir/assets/blob/main/bluer-ugv/bluer-light.png?raw=true": "",
    "../../diagrams/bluer-swallow/3d-design.png": "../../diagrams/bluer-swallow/3d-design.stl",
    f"{assets2}/20250605_180136.jpg?raw=true": "",
    "../../diagrams/bluer-swallow/analog.png": "../../diagrams/bluer-swallow/analog.svg",
    f"{assets2}/20250608_144453.jpg?raw=true": "",
    f"{assets2}/20250609_164433.jpg?raw=true": "",
    f"{assets2}/20250611_100917.jpg?raw=true": "",
    "../../diagrams/bluer-swallow/digital.png": "../../diagrams/bluer-swallow/digital.svg",
    f"{assets2}/20250614_114954.jpg?raw=true": "",
    f"{assets2}/20250615_192339.jpg?raw=true": "",
    f"{assets2}/20250616_134654.jpg?raw=true": "",
    f"{assets2}/20250616_145049.jpg?raw=true": "",
    f"{assets2}/20250618_122604.jpg?raw=true": "",
    f"{assets2}/20250618_102816~2_1.gif?raw=true": "",
    "../../diagrams/bluer-swallow/cover.png": "../../diagrams/bluer-swallow/cover.stl",
    f"{assets2}/20250629_123616.jpg?raw=true": "",
    f"{assets2}/20250630_214923.jpg?raw=true": "",
    f"{assets2}/20250703_153834.jpg?raw=true": "",
    "../../diagrams/bluer-swallow/steering-over-current.png": "../../diagrams/bluer-swallow/steering-over-current.svg",
    f"{assets2}/20250707_122000.jpg?raw=true": "",
}

items = [
    "[![image]({})]({})".format(image, url if url else image)
    for image, url in dict_of_images.items()
]
