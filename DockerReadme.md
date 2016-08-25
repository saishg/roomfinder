Make sure  rooms.csv file contains list of rooms.
docker build -t room-finder .
docker run -d -p 5000:5000 room-finder
