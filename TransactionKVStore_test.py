import pytest

class TransactionKVStore:
    def __init__(self):
        self.global_store = {}
        self.transactions = []
        # Unique tombstone marker for deletions
        self.DELETED = object()

    def set(self, key: str, value):
        # TODO: Implement SET logic
        if self.transactions:
            self.transactions[-1][key] = value
            return
        self.global_store[key] = value
            
    def get(self, key: str):
        # TODO: Implement GET logic (top to bottom search)
        for transaction in reversed(self.transactions):
            if key in transaction:
                return None if transaction[key] == self.DELETED else transaction[key]
        if key in self.global_store:
            return None if self.global_store[key] == self.DELETED else self.global_store[key]
        return None

    def delete(self, key: str) -> bool:
        # TODO: Implement DELETE logic
        for transaction in reversed(self.transactions):
            if key in transaction:
                if transaction[key] == self.DELETED:
                    return False  
                else:
                    transaction[key] = self.DELETED
                    return True            

        if not self.transactions:
            if key in self.global_store:
                self.global_store.pop(key, None)
                return True

        if key in self.global_store:
            self.transactions[-1][key] = self.DELETED
            return True
            
        return False
    
    def begin(self):
        # TODO: Implement BEGIN logic
        self.transactions.append({})

    def rollback(self) -> bool:
        # TODO: Implement ROLLBACK logic
        if not self.transactions:
            return False
        else:
            self.transactions.clear()
            return True

    def commit(self) -> bool:
        # TODO: Implement COMMIT logic
        if not self.transactions:
            return False
        for transaction in self.transactions:
            for key in transaction:
                if transaction[key] == self.DELETED:
                    self.global_store.pop(key)
                else:
                    self.global_store[key] = transaction[key]
        self.transactions = []
        return True



#test written by ai


# Assuming TransactionKVStore is defined in the same file or imported

def test_basic_set_get_delete():
    kv = TransactionKVStore()
    kv.set("a", 100)
    assert kv.get("a") == 100
    assert kv.get("b") is None

    assert kv.delete("a") is True
    assert kv.get("a") is None
    assert kv.delete("a") is False


def test_single_transaction_rollback():
    kv = TransactionKVStore()
    kv.set("a", 10)
    
    kv.begin()
    kv.set("a", 20)
    kv.set("b", 30)
    assert kv.get("a") == 20
    assert kv.get("b") == 30
    
    assert kv.rollback() is True
    assert kv.get("a") == 10
    assert kv.get("b") is None


def test_single_transaction_commit():
    kv = TransactionKVStore()
    kv.set("a", 10)
    
    kv.begin()
    kv.set("a", 20)
    kv.set("b", 30)
    assert kv.commit() is True
    
    assert kv.get("a") == 20
    assert kv.get("b") == 30
    assert kv.rollback() is False  # No transaction to rollback anymore


def test_deletion_inside_transaction():
    kv = TransactionKVStore()
    kv.set("a", 50)
    
    kv.begin()
    assert kv.delete("a") is True
    assert kv.get("a") is None  # Must NOT fall through to global store!
    
    kv.rollback()
    assert kv.get("a") == 50   # Restored after rollback


def test_nested_transactions_complex():
    kv = TransactionKVStore()
    kv.set("key1", "val1")
    
    kv.begin()                  # Layer 1
    kv.set("key1", "layer1_val")
    kv.delete("key2")
    
    kv.begin()                  # Layer 2
    kv.set("key2", "layer2_val")
    assert kv.get("key1") == "layer1_val"
    assert kv.get("key2") == "layer2_val"
    
    kv.rollback()               # Discards Layer 2
    assert kv.get("key2") is None  # Back to Layer 1 state (key2 deleted)
    assert kv.get("key1") == "layer1_val"
    
    kv.commit()                 # Commits Layer 1
    assert kv.get("key1") == "layer1_val"
    assert kv.get("key2") is None


def test_rollback_and_commit_returns_false_when_empty():
    kv = TransactionKVStore()
    assert kv.rollback() is False
    assert kv.commit() is False