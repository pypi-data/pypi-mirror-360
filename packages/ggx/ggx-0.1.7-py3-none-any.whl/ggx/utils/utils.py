from loguru import logger






class Utils:
    
    def __init__(self):
        pass
    
    
    
    def skip_calculator(
        self, time: int, skip_type: list[str] = None
        ) -> list[str]:
        
        
        all_skip_values = [(86400, "MS7"), (18000, "MS6"), (3600, "MS5"), (1800, "MS4"), (600, "MS3"), (300, "MS2"), (60, "MS1")]
        
        if skip_type:
            skip_values = [(sec, lbl) for sec, lbl in all_skip_values if lbl in skip_type]
            if not skip_values:
                logger.error("Your skips are not allowed!")
                
        else:
            skip_values = all_skip_values
            
        minutes = time // 60
        skip_minutes = [(sec // 60, label) for sec, label in all_skip_values]
        INF = float('inf')
        dp = [INF] * (minutes + 1)
        prev = [None] * (minutes + 1)
        dp[0] = 0
        
        for i in range(1, minutes + 1):
            for m, label in skip_minutes:
                if i >= m and dp[i - m] + 1 < dp[i]:
                    dp[i] = dp[i - m] + 1
                    prev[i] = (i - m, label)
        skips = []
        cur = minutes
        while cur > 0 and prev[cur]:
            j, label = prev[cur]
            skips.append(label)
            cur = j
        used = sum(sec * skips.count(lbl) for sec, lbl in all_skip_values)
        rem = time - used
        if rem > 0:
            for sec, label in sorted(all_skip_values, key=lambda x: x[0]):
                if sec >= rem:
                    skips.append(label)
                    break
        
        return skips
    
    
    
    