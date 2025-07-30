# giga_auto

cd existing_repo
git remote add origin https://git2.oristand.com/qa/other/giga_auto.git
git branch -M main
git push -uf origin main
```

CMD:
 python setup.py sdist bdist_wheel
 twine upload dist/*
