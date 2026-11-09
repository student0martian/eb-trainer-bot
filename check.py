import json

ANSWERS = {
    "1":  [1,1,2,4,2,3,2,1,5,2],
    "2":  [1,2,3,1,3,4,4,3,4,2],
    "3":  [3,4,2,1,3,3,3,1,3,2],
    "4":  [2,2,2,2,4,1,4,4,2,2],
    "5":  [2,3,2,2,3,3,1,4,3,1],
    "6":  [2,4,4,4,5,1,2,2,3,4],
    "7":  [3,4,4,2,1,1,2,1,2,2],
    "8":  [4,2,2,2,3,2,3,2,4,3],
    "9":  [3,1,5,5,4,3,1,5,5,2],
    "10": [2,4,4,3,5,4,2,2,5,2],
    "11": [3,2,2,1,3,3,4,1,5,3],
    "12": [2,3,1,4,4,5,1,5,4,4],
    "13": [2,3,2,4,1,1,4,2,4,4],
    "14": [1,5,3,4,3,1,2,4,4,5],
    "15": [1,3,2,1,1,5,2,4,1,2],
    "16": [2,2,1,3,4,2,3,4,1,3],
    "17": [1,2,2,2,4,4,3,5,3,5],
    "18": [4,1,3,2,4,1,4,2,4,1],
    "19": [4,3,2,1,2,2,1,4,1,2],
    "20": [1,2,2,3,3,1,1,5,3,1],
    "21": [4,2,2,1,2,2,3,2,1,3],
    "22": [1,3,4,2,4,2,5,4,4,4],
    "23": [4,2,3,5,4,1,3,2,5,1],
    "24": [3,1,4,4,3,3,2,2,4,4],
    "25": [3,2,1,3,1,3,4,2,2,1],
    "26": [2,3,1,3,2,2,4,3,5,2],
    "27": [2,4,3,2,4,2,1,4,4,3],
    "28": [3,5,3,4,2,2,2,2,5,4],
    "29": [3,1,2,1,2,2,1,4,1,4],
    "30": [4,1,2,1,1,2,3,4,3,2],
}

errors = 0

for n in range(1, 31):
    path = f"test{n:02d}.json"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"{path}: файл не найден")
        errors += 1
        continue

    if data["ticket_id"] != n:
        print(f"{path}: ticket_id = {data['ticket_id']}, а не {n}")
        errors += 1

    questions = data["questions"]
    expected = ANSWERS[str(n)]

    if len(questions) != len(expected):
        print(f"{path}: вопросов {len(questions)}, а не {len(expected)}")
        errors += 1

    for q in questions:
        qid = q["question_id"]
        aid = q["answer_id"]

        if aid not in q["options"]:
            print(f"{path}, вопрос {qid}: answer_id нет в options")
            errors += 1
        elif q["options"][aid] != q["answer"]:
            print(f"{path}, вопрос {qid}: answer не совпадает с options")
            errors += 1

        if qid <= len(expected) and aid != str(expected[qid - 1]):
            print(f"{path}, вопрос {qid}: answer_id = {aid}, по таблице {expected[qid - 1]}")
            errors += 1

print("Ошибок:", errors)
