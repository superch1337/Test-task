import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


@dataclass(frozen=True)
class Project:
    city: str
    name: str
    district: str
    category: str
    price_per_sqm: int


def load_projects(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return [
            Project(row["city"], row["name"], row["district"], row["class"],
                    int(row["price_per_sqm"]))
            for row in csv.DictReader(file)
        ]


def ask_city(cities):
    for number, city in enumerate(cities, 1):
        print(f"  {number}. {city}")
    choices = {city.casefold(): city for city in cities}
    choices.update({str(i): city for i, city in enumerate(cities, 1)})
    while True:
        answer = input("Город (номер или название): ").strip().casefold()
        if answer in choices:
            return choices[answer]
        print("Выберите город из списка.")


def ask_amount(prompt, maximum):
    while True:
        answer = "".join(input(prompt).split()).replace(",", ".")
        try:
            value = Decimal(answer)
            if value.is_finite() and 0 < value <= maximum:
                return value
        except InvalidOperation:
            pass
        print(f"Введите число больше нуля и не больше {rubles(maximum)}.")


def shortlist(projects, city, budget, area):
    estimates = [
        (project, (area * project.price_per_sqm).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP))
        for project in projects
        if project.city == city
    ]
    estimates.sort(key=lambda item: (item[1], item[0].name))
    matches = [(project, price) for project, price in estimates if price <= budget]
    return matches[:3]


def rubles(number):
    return f"{number:,.0f}".replace(",", " ")


def main():
    try:
        projects = load_projects(Path(__file__).with_name("projects.csv"))
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit(f"Не удалось прочитать projects.csv: {error}") from error

    print("Подбор новостроек")
    city = ask_city(list(dict.fromkeys(project.city for project in projects)))
    budget = ask_amount("Бюджет, руб.: ", 10**12)
    area = ask_amount("Желаемая площадь, м²: ", 10**6)
    matches = shortlist(projects, city, budget, area)

    print()
    if matches:
        print(f"Подходит под бюджет: {len(matches)} из запрошенных 3")
        for number, (project, price) in enumerate(matches, 1):
            print(f"{number}. {project.name} — ≈ {rubles(price)} руб.")
            print(f"   {project.category} · {project.district} · от {rubles(project.price_per_sqm)} руб./м²")
    else:
        print("При такой площади ни один ЖК в городе не укладывается в бюджет.")
    print("\nОценка = площадь × стартовая цена за м² из таблицы.")
    print("Наличие квартиры нужной площади и её цену уточняйте у продавца.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\nПодбор завершён.")
