from datetime import datetime, date, timedelta
from typing import List, Optional


class Goal:
    VALID_CATEGORIES = ["Работа", "Здоровье", "Путешествия", "Образование", "Дом", "Другое"]

    def __init__(self, name: str, target_amount: float, category: str, due_date: Optional[date] = None):
        if category not in self.VALID_CATEGORIES:
            raise ValueError("Недопустимая категория. Выберите из: " + ", ".join(self.VALID_CATEGORIES))
        if target_amount <= 0:
            raise ValueError("Итоговая сумма должна быть больше 0.")

        self.name = name
        self.target_amount = target_amount
        self.current_balance = 0.0
        self.category = category
        self.status = "активна"
        self.due_date = due_date
        self.history: List[str] = []
        self.deposits: List[tuple[float, date]] = []

        self._log("Цель создана: {}, целевая сумма: {}, категория: {}".format(
            self.name, self.target_amount, self.category) +
            (" , дедлайн: {}".format(self.due_date) if self.due_date else ""))

    def _log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append("[{}] {}".format(timestamp, message))

    @property
    def progress_percent(self) -> float:
        if self.target_amount == 0:
            return 0.0
        return min(100.0, (self.current_balance / self.target_amount) * 100)

    def change_balance(self, delta: float) -> bool:
        new_balance = self.current_balance + delta

        if new_balance > self.target_amount and delta > 0:
            print("Предупреждение: нельзя превысить целевую сумму {}. Максимум можно добавить {:.2f}.".format(
                self.target_amount, self.target_amount - self.current_balance))
            return False

        self.current_balance = new_balance
        self._log("Баланс изменён на {:.2f}. Новый баланс: {:.2f}".format(delta, self.current_balance))

        if delta > 0:
            self.deposits.append((delta, date.today()))
            if len(self.deposits) > 10:
                self.deposits.pop(0)

        if self.current_balance >= self.target_amount and self.status != "выполнена":
            self.status = "выполнена"
            self._log("Цель достигнута: статус изменён на 'выполнена'.")

        return True

    def set_due_date(self, new_due_date: date) -> bool:
        self.due_date = new_due_date
        self._log("Дата завершения обновлена на {}".format(new_due_date))
        return True

    def set_category(self, new_category: str) -> bool:
        if new_category not in self.VALID_CATEGORIES:
            print("Ошибка: недопустимая категория. Доступные: {}".format(", ".join(self.VALID_CATEGORIES)))
            return False
        old_category = self.category
        self.category = new_category
        self._log("Категория изменена с '{}' на '{}'".format(old_category, new_category))
        return True

    def estimate_completion_date(self) -> Optional[date]:
        if not self.deposits or self.status == "выполнена":
            return None

        total_deposited = sum(amount for amount, _ in self.deposits)
        first_date = min(d for _, d in self.deposits)
        last_date = max(d for _, d in self.deposits)

        days_span = (last_date - first_date).days
        if days_span == 0:
            days_span = 1

        avg_daily = total_deposited / days_span

        if avg_daily <= 0:
            return None

        remaining = self.target_amount - self.current_balance
        days_needed = max(1, int(remaining / avg_daily) + 1)
        return date.today() + timedelta(days=days_needed)

    def get_reminder_status(self) -> str:
        if self.status == "выполнена":
            return "выполнена"

        if not self.due_date:
            return "без дедлайна"

        today = date.today()
        delta_days = (self.due_date - today).days

        if delta_days < 0:
            return "просрочена"
        elif delta_days <= 3:
            return "срочно (осталось <= 3 дня)"
        elif delta_days <= 7:
            return "скоро дедлайн (<= 7 дней)"
        else:
            return "в норме"

    def get_history(self) -> List[str]:
        return self.history

    def __str__(self):
        percent = self.progress_percent
        due_str = "Дедлайн: {}".format(self.due_date) if self.due_date else "Дедлайн: не установлен"
        est_str = ""
        est = self.estimate_completion_date()
        if est:
            est_str = "\nПрогноз завершения: {}".format(est)

        reminder = self.get_reminder_status()

        return ("Цель: {} | Категория: {} | Статус: {}\n"
                "{} {}\n"
                "Целевая сумма: {:.2f} | Текущий баланс: {:.2f}\n"
                "Прогресс: {:.1f}%\n"
                "Статус напоминания: {}").format(
            self.name, self.category, self.status,
            due_str, est_str,
            self.target_amount, self.current_balance,
            percent,
            reminder)


class PiggyBank:
    def __init__(self):
        self.goals: List[Goal] = []

    def add_goal(self, name: str, target_amount: float, category: str,
                 due_date: Optional[date] = None) -> Optional[Goal]:
        try:
            goal = Goal(name, target_amount, category, due_date)
            self.goals.append(goal)
            print("Цель успешно добавлена.")
            return goal
        except ValueError as e:
            print("Не удалось создать цель: {}".format(e))
            return None

    def find_goal_by_name(self, name: str) -> Optional[Goal]:
        for goal in self.goals:
            if goal.name.lower() == name.lower():
                return goal
        return None

    def remove_goal(self, name: str) -> bool:
        goal = self.find_goal_by_name(name)
        if goal is None:
            print("Цель не найдена.")
            return False
        self.goals.remove(goal)
        print("Цель '{}' удалена.".format(name))
        return True

    def list_goals(self):
        if not self.goals:
            print("Нет ни одной цели.")
            return
        for i, goal in enumerate(self.goals, 1):
            print("\n--- Цель #{} ---".format(i))
            print(goal)

    def get_goal_history(self, name: str):
        goal = self.find_goal_by_name(name)
        if goal is None:
            print("Цель не найдена.")
            return
        print("\nИстория изменений для цели '{}':".format(goal.name))
        if not goal.history:
            print("История пуста.")
        else:
            for entry in goal.history:
                print(entry)

    def show_reminders(self):
        today = date.today()
        urgent_goals = []

        for g in self.goals:
            status = g.get_reminder_status()
            if status in ("просрочена", "срочно (осталось <= 3 дня)", "скоро дедлайн (<= 7 дней)"):
                urgent_goals.append((g, status))

        if not urgent_goals:
            print("Напоминаний нет: все цели либо выполнены, либо дедлайны далеко.")
            return

        print("\n=== НАПОМИНАНИЯ ===")
        for g, status in urgent_goals:
            print("[{}] {}: прогресс {:.1f}%, дедлайн {}".format(
                status, g.name, g.progress_percent, g.due_date or "не установлен"))
            if g.due_date and g.due_date < today:
                days_overdue = (today - g.due_date).days
                print("  -> Просрочено на {} дн.".format(days_overdue))
            est = g.estimate_completion_date()
            if est:
                print("  -> Прогноз завершения: {}".format(est))


def parse_date(date_str: str) -> date:
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD или DD.MM.YYYY")


def print_menu():
    print("\n=== КОПИЛКА: управление накоплениями ===")
    print("1. Добавить цель (с дедлайном)")
    print("2. Показать все цели (с прогнозом и напоминаниями)")
    print("3. Изменить баланс цели")
    print("4. Установить/изменить дату завершения цели")
    print("5. Изменить категорию цели")
    print("6. Посмотреть историю изменений цели")
    print("7. Показать только напоминания")
    print("8. Удалить цель")
    print("9. Выход")


def main():
    piggy = PiggyBank()

    while True:
        print_menu()
        choice = input("Выберите действие (1-9): ").strip()

        if choice == "1":
            name = input("Название цели: ").strip()
            if not name:
                print("Название не может быть пустым.")
                continue
            try:
                target = float(input("Целевая сумма: "))
            except ValueError:
                print("Некорректное число.")
                continue

            print("Доступные категории: {}".format(", ".join(Goal.VALID_CATEGORIES)))
            category = input("Категория: ").strip()

            due_input = input("Дата завершения (YYYY-MM-DD или DD.MM.YYYY, можно оставить пустым): ").strip()
            due_date = None
            if due_input:
                try:
                    due_date = parse_date(due_input)
                except ValueError as e:
                    print(e)
                    continue

            piggy.add_goal(name, target, category, due_date)

        elif choice == "2":
            piggy.list_goals()

        elif choice == "3":
            name = input("Название цели для изменения баланса: ").strip()
            goal = piggy.find_goal_by_name(name)
            if goal is None:
                print("Цель не найдена.")
                continue
            try:
                delta = float(input("Сумма изменения (положительная для пополнения, отрицательная для снятия): "))
            except ValueError:
                print("Некорректное число.")
                continue
            goal.change_balance(delta)

        elif choice == "4":
            name = input("Название цели для установки даты завершения: ").strip()
            goal = piggy.find_goal_by_name(name)
            if goal is None:
                print("Цель не найдена.")
                continue
            due_input = input("Новая дата завершения (YYYY-MM-DD или DD.MM.YYYY): ").strip()
            try:
                new_due = parse_date(due_input)
                goal.set_due_date(new_due)
                print("Дата завершения обновлена.")
            except ValueError as e:
                print(e)

        elif choice == "5":
            name = input("Название цели для смены категории: ").strip()
            goal = piggy.find_goal_by_name(name)
            if goal is None:
                print("Цель не найдена.")
                continue
            print("Доступные категории: {}".format(", ".join(Goal.VALID_CATEGORIES)))
            new_cat = input("Новая категория: ").strip()
            goal.set_category(new_cat)

        elif choice == "6":
            name = input("Название цели для просмотра истории: ").strip()
            piggy.get_goal_history(name)

        elif choice == "7":
            piggy.show_reminders()

        elif choice == "8":
            name = input("Название цели для удаления: ").strip()
            piggy.remove_goal(name)

        elif choice == "9":
            print("До свидания!")
            break

        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()