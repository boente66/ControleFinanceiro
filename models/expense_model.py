from database.database import Database

class ExpenseModel(Database):
    def __init__(self):
        super().__init__()

    def add_expense(self, expense_data):
        query = """
        INSERT INTO despesas (data, descricao, categoria, valor)
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (
            expense_data["data"],
            expense_data["descricao"],
            expense_data["categoria"],
            expense_data["valor"]
        ))

    def get_all_expenses(self):
        query = "SELECT * FROM despesas"
        return self.fetch_all(query)