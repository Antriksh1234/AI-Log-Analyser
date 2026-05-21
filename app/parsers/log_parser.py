def parse_log(line):

    parts = line.split()

    if len(parts) < 5:
        return None

    severity = parts[2]
    service = parts[3]

    message = " ".join(parts[4:])

    return {
        "severity": severity,
        "service": service,
        "message": message
    }


def group_logs_by_service(parsed_logs):

    service_groups = {}

    for log in parsed_logs:

        service = log["service"]

        formatted_message = (
            f'{log["severity"]} {log["message"]}'
        )

        if service not in service_groups:

            service_groups[service] = {
                "logs": [],
                "severity": log["severity"]
            }

        service_groups[service]["logs"].append(
            formatted_message
        )

        # Track highest severity
        if log["severity"] == "ERROR":

            service_groups[service][
                "severity"
            ] = "ERROR"

        elif (
            log["severity"] == "WARN"
            and service_groups[service][
                "severity"
            ] != "ERROR"
        ):

            service_groups[service][
                "severity"
            ] = "WARN"

    return service_groups


def create_incident_chunks(service_groups):

    chunks = []

    for service, data in service_groups.items():

        combined_logs = "\n".join(
            data["logs"]
        )

        incident_text = (
            f"Service: {service}\n\n"
            f"{combined_logs}"
        )

        chunks.append({
            "service": service,
            "severity": data["severity"],
            "incident": incident_text
        })

    return chunks