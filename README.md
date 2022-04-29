# pin_conda_env

Pin conda environment to installed versions:
```python
python -m pin_conda_env environment.yml
```
will create a file `pinned.yml` identical to `environment.yml` but with currently installed version numbers included. The conda environment has to be installed for this to work.
