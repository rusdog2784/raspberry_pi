chmod +x build.sh

./build.sh

source venv/bin/activate

python web_streaming.py --ip 0.0.0.0 --port 5000
