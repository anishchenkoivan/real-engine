# Real engine(3d engine)

## Demo

![demo](assets/demo.jpg)

![shrek](assets/shrek.png)

Blender 3d models support isn't merged into master as it's only PoC at the moment.
You can find it in feature/shrek branch.

## Setup

Create venv

    python3 -m venv .env
    . ./.env/bin/activate

Install dependencies

    pip3 install -r requirements.txt

## Run

Activate venv and run

    . ./.env/bin/activate
    cd engine
    python3 main.py

## Features

- Gpu acceleration
- Transparrent materials
- Rough materials
- Light dispertion and chromatic aberration
- Sampling (reduces noise by calculating mean color of all frames since last move for each pixel)
- Sky texture

PoC only

- Blender 3d models support
- Light sources

## More pictures

![rough floor](assets/rough-floor.jpg)
![rough floor](assets/rough-floor2.jpg)
![rough floor](assets/transparrent-spheres.jpg)
![rough floor](assets/transparrent-spheres2.jpg)
![rough floor](assets/rough-spheres.jpg)
![rough floor](assets/light.jpg)
