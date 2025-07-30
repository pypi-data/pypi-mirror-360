# Test file for basic TODO detection patterns
# Expected detections: 6 high-confidence items

def calculate_metrics():
    # TODO: Add error handling for division by zero
    total = sum(values)
    return total / count

class DataProcessor:
    def __init__(self):
        # FIXME: Memory leak in batch processing
        self.cache = {}
    
    def process_batch(self, items):
        # BUG: Race condition when processing concurrent batches
        for item in items:
            self.cache[item.id] = item.data
            
    def cleanup(self):
        # TODO: Implement proper resource cleanup
        pass

# FIXME: This entire class needs refactoring for performance
class LegacyHandler:
    def handle_request(self):
        # BUG: SQL injection vulnerability in query builder
        return "processed"