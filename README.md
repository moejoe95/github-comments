# github-comments

Comments are important to understand and maintain source code. The goal of this project is to
compare commenting styles in Java and Python projects by analyzing comments in Java and Python
projects on GitHub.

## How-To

Extract and save comments from a python project to a pandas dataframe:
```
python main.py keras-team/keras --lang py
```

Extract and save comments from a java project to a pandas dataframe:
```
python main.py spring-projects/spring-boot --lang java
```

To make some analysis on the dataframe:
```
python analyzer.py
```
