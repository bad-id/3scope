### 3scope
The software for controlling the autofocus project in the TUe 31DAE course

### Setup project

Backend: (cd backend)
```
conda activate
conda create -n dae python=3.14.4
conda activate dae
pip install -r requirements.txt
```

If reactivating project
```
conda activate
conda activate dae
```

If any packages are added or updated, the package should be saved to requirements.txt:
```
pip freeze > requirements.txt
```

To rebuild the frontend links:
```
pyflow run -m ./ -g ../frontend/app/generated
```


Frontend: (cd frontend)
node.js version 25.9.0 (64-bit)
```
nvm install 25.9.0
nvm use 25.9.0
npm i
```

### Run project
The camera should be connected by USB to the host PC.
The PYNQ board is connected by ethernet, default connection is to 10.43.0.1:11008.