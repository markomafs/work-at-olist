from json_log_formatter import JSONFormatter


class CustomisedJSONFormatter(JSONFormatter):

    def mutate_json_record(self, json_record):
        from datetime import datetime, time, timedelta

        for attr_name in json_record:
            attr = json_record[attr_name]
            if isinstance(attr, datetime):
                json_record[attr_name] = attr.isoformat()
            elif isinstance(attr, time):
                json_record[attr_name] = attr.isoformat()
            elif isinstance(attr, timedelta):
                json_record[attr_name] = str(attr)
        return json_record

    def json_record(self, message, extra, record):
        extra = super().json_record(message, extra, record)
        return extra
