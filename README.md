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
- fault1: insert latency at line 52
  - fault1_resize_statement_trace_42: reize function with trace at line 42 
    - data: trace data of resize_all
    - resize: reize function code
    - resize.yml: deploy yml
  - fault1_resize_statement_trace_resize_all: reize function with trace at line 42 
    - data: trace data of resize_all
    - resize: reize function code
    - resize.yml: deploy yml
```