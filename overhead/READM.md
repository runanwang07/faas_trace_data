## Overhead

### Cal overhead
```
 python3 cal_overhead.py 


faas_trace_data/overhead/resize_statement_trace_overhead_1/data 28853.78184281843
faas_trace_data/overhead/resize_statement_trace_overhead_2/data 29004.346967559944
faas_trace_data/overhead/resize_statement_trace_overhead_3/data 29124.865937072504
faas_trace_data/overhead/resize_statement_trace_overhead_4/data 29536.93490304709
faas_trace_data/overhead/resize_statement_trace_overhead_5/data 29646.708333333332
faas_trace_data/overhead/resize_statement_trace_overhead_6/data 30024.839684625495
faas_trace_data/overhead/resize_statement_trace_overhead_7/data 30305.32037533512
```




|  Trace Point   |  Latency (microsecond)  | Compare with 1 point | 
|  ----          |  ----  | ----  |
| 1              | 28853 |   -    |
| 2              | 29004 |  0.5%  |
| 3              | 29124 |  0.9%  |
| 4              | 29536 |  2.3%  |
| 5              | 29646 |  2.7%  |
| 6              | 30024 |  4%    |
| 7              | 30305 |  5%    |

(30305-28853)/28853 = 0.05 

7 Trace points will generate 5% more latency than 1 Trace point.