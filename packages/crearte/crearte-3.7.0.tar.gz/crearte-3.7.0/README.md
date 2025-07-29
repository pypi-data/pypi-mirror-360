# Crearte

[![GHCR](https://img.shields.io/badge/GHCR-Crearte-blue?logo=docker)](https://github.com/Uchida16104/Crearte/pkgs/container/crearte)
[![pypi version](https://img.shields.io/pypi/v/crearte.svg)](https://pypi.org/project/crearte)
[![homebrew](https://img.shields.io/badge/homebrew-crearte-orange?logo=homebrew)](https://github.com/Uchida16104/homebrew-crearte)
[![Debian](https://img.shields.io/badge/debian-crearte-red?logo=debian)](https://github.com/Uchida16104/Crearte/releases/latest)
[![npm version](https://img.shields.io/npm/v/crearte.svg)](https://www.npmjs.com/package/crearte)

<img src="https://raw.githubusercontent.com/Uchida16104/Crearte/refs/heads/main/Crearte.png" alt="Crearte" />

Crearte is software that helps to create musical scores using music generated from images and poems. The etymology of Crearte comes from the combination of "create" and "art".The directory contains sample .mid files, .wav files, .png files, and .txt files.

## Features
- It can import images, poems, and dances into music.
- It uses simple shapes and math to create graphic scores.
- You can also move your body to make sound in real time.

## Requirements
- Python
- Java / Processing
- SuperCollider
- Node.js
- Browser software

## Usage
1. ``` cd Crearte ```
2. ``` source scripts/install.sh ``` (First time)
3. ``` python3 -m venv venv ```
4. ``` source venv/bin/activate ```
5. ``` open crearte/hydra/launch.sh ```
6. edit and run script.js on [hydra](https://hydra.ojack.xyz)
7. save and generate input.png from hydra by screencap() function
8. move input.png to Crearte directory
9. edit and save image_notes.txt and gesture_notes.txt
10. ``` python3 image2score/image2score.py ```
11. ``` python3 text2midi/text2midi.py ```
12. run crearte/bin/crearte.pde
13. ``` python3 crearte/converter/convert_midi_to_txt.py ```
14. perform with crearte/player/player.scd, hydra-processing-bridge/index.html, and score_output.mid.

## Completed output file image

<img src="https://raw.githubusercontent.com/Uchida16104/Crearte/refs/heads/main/output_full_score.png" alt="Score" />

Hirotoshi Uchida
