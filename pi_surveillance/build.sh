sudo apt-get update && sudo apt-get upgrade -y

sudo apt-get install -y libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt-get install -y libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libjasper-dev
sudo apt autoremove -y

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
