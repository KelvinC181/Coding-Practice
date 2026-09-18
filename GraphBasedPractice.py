# def can_message(connections, start_user, target_user):
#     current = start_user
#     x = 0
#     while current != target_user:
#         for user in connections:
#             x+=1
#             print(x)
#             if user[0] == current:
#                 current = user[1]
#                 break
#             if user == connections[-1] and user[0] != current:
#                 return False
#     return True



def toDict(conlist):
    added = []
    conDict = {}
    for points in conlist:
        if points[0] not in added:
            conDict[points[0]] = [points[1]]
            added.append(points[0])
        else:
            conDict[points[0]].append(points[1])

        if points[1] not in added:
                    conDict[points[1]] = []
                    added.append(points[1])
    return conDict

connections = [
    ["A", "B"],
    ["A", "C"],
    ["B", "D"],
    ["C", "D"],
    ["D", "E"]
]

print(toDict(connections))
    
# connections = [
#     ["Alice", "Bob"],
#     ["Bob", "Charlie"],
#     ["David", "Eve"]
# ]

# print(can_message(connections, "Alice", "Charlie"))
# print(can_message(connections, "Alice", "Eve"))

