class BootsrapViaAuthenticationToken:
    def __init__(self, token, group, configurations):
        self.secret_value = None
        self.device_id = None
        self.enrollment_method = None
        self.configurations = configurations
        self.token = token
        self.group = group

    def __repr__(self):
        return f"BootstrapViaAuthenticationToken(token={self.token})"

    def to_dict(self):
        return {
            "type": "BootstrapViaAuthenticationToken",
            "input": {
                "token": {
                    "secretValue": self.secret_value
                },
                "deviceId": self.device_id,
                "enrollmentMethod": "admin",
                "configurations": self.configurations 
            }
        }
    

class BootstrapViaJsonFile:
    def __init__(self, file_location):
        self.file_location = file_location

    def __repr__(self):
        return f"BootstrapViaJsonFile(file_location={self.file_location})"

    def to_dict(self):
        return {
            "type": "BootstrapViaJsonFile",
             "input": {
                    "file": self.file_location
            }
        }

class RemoveDeviceOwnership:
    def __init__(self):
        pass

    def __repr__(self):
        return f"RemoveDeviceOwnership()"
    
    def to_dict(self):
        return {
            "type": "RemoveDeviceOwnership",
            "input": None
        }