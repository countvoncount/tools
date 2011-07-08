rsync -avz --exclude="*git" --exclude="*.pkl" --exclude="config.yml" ~/vurve/code/sophie/sophie deployadmin@ec2-174-129-148-44.compute-1.amazonaws.com:code/sophie
rsync -avz --exclude="*git" --exclude="*.pkl" ~/vurve/tools deployadmin@ec2-174-129-148-44.compute-1.amazonaws.com:remoteTools
