# Pristy Alfresco operators for Airflow


## Release

Update version in `pyproject.toml` then

```shell
TAG=0.3.2
git add pyproject.toml README
git commit -m "version $TAG"
git tag "$TAG"
git push
git push origin "tags/$TAG"
poetry build
poetry publish
```

