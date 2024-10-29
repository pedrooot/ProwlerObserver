# TBD: Add more services as needed
def service_filter(service_name) -> str:
    """
    Filter the service name to a shorter version compatible with Prowler

    Parameters:
        - service_name (str): The service name to filter
    
    Returns:
        - str: The filtered service name
    """
    if service_name == "elasticloadbalancing":
        return "elb"
    if service_name == "elasticfilesystem":
        return "efs"
    return service_name