# Google Doc Clone
## Distributed-Computing-Project 

Project to develop a multi user shared text editor, where many users can open a document and any edit that user make appears to all the other users who are viewing this specific document. 
Fault tolerance was also implemented through a load balancer and workers. Caching was implemented using hash tables to improve response time.

## Follow the following steps to run the program:

 - Install dependencies
 - npm start -> in cmd of front directory to open front end
 - python load_balncer.py -> in cmd of back directory to open load balancer 
 - python app.py -> in cmd of back directory to open worker
Can open more than one app.py to have more than one worker.

Link of drive with video: https://drive.google.com/drive/folders/19qDpHhg1gFaszUHR6mxdAY5JPXf7jUyd
