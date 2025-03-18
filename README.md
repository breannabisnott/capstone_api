# Fire Alarm API

To Update Server:
```bash
git pull
sudo docker build -t firealarm .
sudo docker run -d -p 8000:8000 --name firealarm firealarm
```

To Stop Container:
```bash
sudo docker stop firealarm
```

To Delete Container:
```bash
sudo docker rm firealarm
```

To List running containers:
```bash
sudo docker ps
```