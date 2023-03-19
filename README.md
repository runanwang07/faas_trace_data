# faas_trace_data
faas_trace_data


## Deploy
```
cd resize_all

faas-cli up -f  resize.yml
```

### Load 
```
locust -f locust_file.py --host=http://33.33.33.223:31112/function/ --headless -u 5 -r 1
```

### File description
```
- resize_all: reize function with all trace point 
  - data: trace data of resize_all
  - resize: reize function code
  - resize.yml: deploy yml
- reize_47: reize function with at line 47
```