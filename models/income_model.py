from database.database import Database

class IncomeModel(Database):
    def __init__(self):
        super().__init__()

    def add_income(self, income_data):
        query = """
        INSERT INTO receitas (data, descricao, categoria, valor)
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (
            income_data["data"],
            income_data["descricao"],
            income_data["categoria"],
            income_data["valor"]
        ))

    def get_all_incomes(self):
        query = "SELECT * FROM receitas"
        return self.fetch_all(query)