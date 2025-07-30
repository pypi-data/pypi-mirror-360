class RedisKeyBuilder:
    @staticmethod
    def task_ids_key(project: str) -> str:
        return f"project:{project}:task_ids"
    
    @staticmethod
    def ip_task_map_key(project: str) -> str:
        return f"project:{project}:ip_task_map"
    
    @staticmethod
    def ip_lock_key(project: str, ip: str) -> str:
        return f"project:{project}:ip_task_lock:{ip}"
    
    @staticmethod
    def running_targets_key(project: str) -> str:
        return f"project:{project}:running_targets"