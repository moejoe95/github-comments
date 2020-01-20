# github-comments

Comments are important to understand and maintain source code. The goal of this project is to
compare commenting styles in Java and Python projects by analyzing comments in Java and Python
projects on GitHub.

## How-To

### Data extraction

Extract and save comments from a python project to a pandas dataframe:
```
python main.py keras-team/keras --lang py
```

Extract and save comments from a java project to a pandas dataframe:
```
python main.py spring-projects/spring-boot --lang java
```

Clone and extract data of the 100 most popular GitHub repositories written in Java and Python:
```
python main.py --top 100 -rm
```

The `-rm` flag removes the cloned repository right after the data is extracted and saved to our dataframe.

### Data visualization

To make some analysis on the dataframe:
```
python analyzer.py
```
