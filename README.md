
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

Frontend: (cd frontend)
node.js version 25.9.0 (64-bit)
```
nvm install 25.9.0
nvm use 25.9.0
npm i
```