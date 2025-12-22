score = 0

with open(
'names.txt', 'r', encoding = 'utf-8'
) as file:
    for name in file:
        if name == 'Катя':
            score += 1

print(score)