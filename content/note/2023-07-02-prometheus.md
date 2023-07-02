---
title: "Prometheus Usage"
date: 2023-07-02T01:52:18Z
draft: false
---

## Prometheus Basic




## Prometheus Admin API

* Find series contains label `uri`

```bash
curl -G 'http://localhost:9090/api/v1/series' --data-urlencode 'match[]={uri=~".+"}'

# -G, --get
#    When used, this option will make all data specified with -d, --data, --data-binary or --data-urlencode to be used in an HTTP GET request instead of the POST request that otherwise would be used.
```


* Find all the value of label `uri`

```bash
curl http://localhost:9090/api/v1/label/uri/values
```

