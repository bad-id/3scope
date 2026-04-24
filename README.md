
### Setup project
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