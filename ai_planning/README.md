To run the AI planning service [metric-ff](https://fai.cs.uni-saarland.de/hoffmann/metric-ff.html) needs to be installed, so the ff executable is placed at ```./build/ff```.
Afterwards the system can be started by executing the following commands: 

```
python3 ai_planning_service.py
```
if the ff executable is located somewhere else, you can provide the path as the first argument to the programm:
```
python3 ai_planning_service.py /some/path/build/ff
```