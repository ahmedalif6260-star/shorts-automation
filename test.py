name: Shorts Automation Test

on:
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Pillow
        run: |
          pip install pillow

      - name: Install FFmpeg and Voice Tools
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg espeak-ng

      - name: Run Shorts generator
        run: |
          python generate_short.py

      - name: Upload generated video
        uses: actions/upload-artifact@v4
        with:
          name: generated-short
          path: output/short.mp4
