rsync -avz Questions.py deployadmin@ec2-174-129-148-44.compute-1.amazonaws.com:remoteTools/tools
ssh deployadmin@ec2-174-129-148-44.compute-1.amazonaws.com '/remoteTools/tools/Questions.py $*' 
