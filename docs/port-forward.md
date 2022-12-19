
## `kubectl port-forward`

> Syntax

```bash
kubectl -n <NAMESPACE> port-forward svc/<SERVICE> <LOCAL-PORT>:<SERVICE-PORT>
```

<br>

> Example

```bash
kubectl -n monitoring svc/prometheus-server 8080:80
```


<br>

To know more => https://stackoverflow.com/questions/51468491/how-kubectl-port-forward-works
