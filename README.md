# Django Rest Framework project with Docker

In this project you can create and list Posts & comments, update and delete them. Docker is used in this project. 
To enter this application, to list, create, delete or update some posts or comments one should raise Docker-compose first. 

To raise it:
```
sudo docker-compose up
```

To list posts:
(http://0.0.0.0:8000/post/api/list)

For updating, deleting or commenting one should first register the app. After creating a superuser or user visit:
(http://0.0.0.0:8000/admin)
