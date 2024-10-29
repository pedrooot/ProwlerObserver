def service_filter(service_name) -> str:
    if service_name == "elasticloadbalancing":
        return "elb"
    if service_name == "elasticfilesystem":
        return "efs"
    return service_name