"""
MOCK TASK 2 — Transactional Data Management        (suggested time: ~40 min)
=============================================================================

PROBLEM: Command-Stream Transactional Key-Value Store

Implement `solve(operations: list[tuple]) -> list` that processes a list of
operation tuples against an in-memory key-value store supporting nested
transactions, and returns the output of every operation that produces one.

SUPPORTED OPERATIONS  (op, *args)

  ("SET", key, value)      -> no output. Writes key=value in the current
                               scope (inside the innermost open transaction
                               if one is active, otherwise straight to the
                               committed store).
  ("GET", key)             -> output: the current value, or None if the key
                               doesn't exist / was deleted.
  ("DELETE", key)          -> output: True if the key existed and was
                               removed, False if it didn't exist.
  ("BEGIN",)               -> no output. Opens a new nested transaction.
  ("COMMIT",)               -> output: True if a transaction was open and
                               got committed, False if there was nothing to
                               commit. Commits only the innermost transaction
                               (merges it into the layer below).
  ("ROLLBACK",)            -> output: True if a transaction was open and got
                               discarded, False if there was nothing to roll
                               back. Discards only the innermost transaction.
  ("EXISTS", key)           -> output: True/False — is this key currently
                               visible (accounting for any open transactions),
                               WITHOUT it counting as a "read" that affects
                               anything else. (This is the twist: think about
                               whether this can just reuse your GET logic.)
  ("DEPTH",)                -> output: an int — how many transactions are
                               currently open (0 if none).

EXAMPLE

  operations = [
      ("SET", "a", 5),
      ("BEGIN",),
      ("SET", "a", 10),
      ("DEPTH",),          # -> 1
      ("GET", "a"),        # -> 10
      ("BEGIN",),
      ("DELETE", "a"),     # -> True
      ("EXISTS", "a"),     # -> False
      ("DEPTH",),          # -> 2
      ("ROLLBACK",),       # -> True  (undoes the delete only)
      ("GET", "a"),        # -> 10
      ("COMMIT",),          # -> True  (commits "a"=10 into the outer scope)
      ("GET", "a"),         # -> 10
  ]
  expected output = [1, 10, True, False, 2, True, 10, True, 10]

EDGE CASES TO THINK ABOUT:
  - COMMIT / ROLLBACK / DEPTH with no transaction ever opened
  - Deleting a key inside a transaction, then rolling back just that
    transaction — does the outer scope's value come back correctly?
  - EXISTS on a key that was deleted in an inner transaction but still
    exists in an outer one
"""
class TranKVStore:
    def __init__(self):
        self.global_store = {}
        self.transactions = []
        self.DELETED = object()

    def set(self, key, value):
        if not self.transactions:
            self.global_store[key] = value
            return
        self.transactions[-1][key] = value
        return

    def get(self, key):
        if self.transactions:
            for trasaction in reversed(self.transactions):
                if key in trasaction:
                    return None if trasaction[key]==self.DELETED else trasaction[key]
        if key in self.global_store:
            return None if self.global_store[key]==self.DELETED else self.global_store[key]
        return None

    def delete(self, key):
        if self.transactions:
            for trasaction in reversed(self.transactions):
                if key in trasaction:
                    if trasaction[key]==self.DELETED:
                        return False 
                    self.transactions[-1][key] = self.DELETED
                    return True
        if key in self.global_store:
            if self.global_store[key]==self.DELETED:
                return False
            self.transactions[-1][key] = self.DELETED
            return True
        return False

    def begin(self):
        self.transactions.append({})

    def commit(self):
        if not self.transactions:
            return False
        try:
            for key in self.transactions[-1]:
                self.transactions[-2][key] = self.transactions[-1][key]
                self.transactions.pop(-1)
                return True
        except:
            for key in self.transactions[-1]:
                self.global_store[key] = self.transactions[-1][key]
                self.transactions.pop(-1)
                return True

    def rollback(self):
        if not self.transactions:
            return False
        self.transactions.pop(-1)
        return True

    def exists(self, key):
        if self.transactions:
            for trasaction in reversed(self.transactions):
                if key in trasaction:
                    return False if trasaction[key]==self.DELETED else True
        if key in self.global_store:
            return False if self.global_store[key]==self.DELETED else True
        return False
        

    def depth(self):
        count = 0
        if not self.transactions:
            return count
        count += len(self.transactions)
        return count
        

    

def solve(operations: list[tuple]) -> list:
    # TODO: implement (build whatever internal store/class you want)
    store = TranKVStore()
    results = []
    for operation in operations:
        action = operation[0]
        match action:
            case "SET":
                store.set(operation[1],operation[2])
            case "GET":
                results.append(store.get(operation[1]))
            case "DELETE":
                results.append(store.delete(operation[1]))
            case "BEGIN":
                store.begin()
            case "COMMIT":
                results.append(store.commit())
            case "ROLLBACK":
                results.append(store.rollback())
            case "EXISTS":
                results.append(store.exists(operation[1]))
            case "DEPTH":
                results.append(store.depth())
            case _:
                results.append("invalid input")

    return results





# ---------------------------------------------------------------------
# Self-check harness
# ---------------------------------------------------------------------

def _run():
    results = []

    def check(name, ops, expected):
        try:
            got = solve(ops)
            results.append((name, "PASS" if got == expected else f"FAIL (got {got}, expected {expected})"))
        except NotImplementedError:
            results.append((name, "NOT IMPLEMENTED"))
        except Exception as e:
            results.append((name, f"ERROR: {e}"))

    check("readme_example", [
        ("SET", "a", 5), ("BEGIN",), ("SET", "a", 10), ("DEPTH",), ("GET", "a"),
        ("BEGIN",), ("DELETE", "a"), ("EXISTS", "a"), ("DEPTH",), ("ROLLBACK",),
        ("GET", "a"), ("COMMIT",), ("GET", "a"),
    ], [1, 10, True, False, 2, True, 10, True, 10])

    check("basic_set_get", [("SET", "x", 1), ("GET", "x")], [1])

    check("get_missing_key", [("GET", "nope")], [None])

    check("delete_missing_key", [("DELETE", "nope")], [False])

    check("rollback_with_nothing_open", [("ROLLBACK",)], [False])

    check("commit_with_nothing_open", [("COMMIT",)], [False])

    check("depth_tracks_nesting", [
        ("DEPTH",), ("BEGIN",), ("DEPTH",), ("BEGIN",), ("DEPTH",),
        ("ROLLBACK",), ("DEPTH",), ("ROLLBACK",), ("DEPTH",),
    ], [0, 1, 2, True, 1, True, 0])

    check("delete_in_outer_survives_inner_rollback", [
        ("SET", "k", 1), ("BEGIN",), ("DELETE", "k"), ("BEGIN",),
        ("SET", "junk", 99), ("ROLLBACK",),          # only undoes the inner txn
        ("EXISTS", "k"),                              # should still be False (delete survives)
        ("ROLLBACK",),                                # now undo the delete too
        ("EXISTS", "k"),                              # should be True again
    ], [True, True, False, True, True])

    check("exists_after_commit", [
        ("BEGIN",), ("SET", "z", 1), ("COMMIT",), ("EXISTS", "z"),
    ], [True, True])

    for name, result in results:
        print(f"{name:45} {result}")


if __name__ == "__main__":
    _run()
