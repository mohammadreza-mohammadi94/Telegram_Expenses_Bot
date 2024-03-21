import pymongo


class ExpenseMongoClient:
    def __init__(
            self,
            host: str,
            port: int,
            db_name: str = "telegram_bot",
            collection_name: str = "expenses",
    ):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(collection_name)

    def add_expense(self, user_id: int, amount: int, category: str, description: str):
        results = self.collection.insert_one({
            "user_id": user_id,
            "amount": amount,
            "category": category,
            "description": description,
            })
        return results

    def get_expenses(self, user_id: int) -> list:
        results = self.collection.find({'user_id': user_id})
        expenses = []
        for result in results:
            expenses.append({
                "amount": result["amount"],
                "category": result["category"],
                "description": result["description"],
            })
        return expenses


    def get_categories(self, user_id: int) -> list:
        categories = self.collection.distinct('category', {'user_id': user_id})
        return categories

    def get_expenses_by_category(self, user_id: int, category: str) -> list:
        results = self.collection.find({'user_id': user_id, 'category': category})
        cate = []
        for result in results:
            cate.append({
                "amount": result["amount"],
                "category": result["category"],
                "description": result["description"],
                })
        return cate

    def get_total_expense(self, user_id: int):
        total_expense = self.collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])

        total_amount = 0
        for result in total_expense:
            total_amount = result["total"]

        return total_amount


    def get_total_expense_by_category(self, user_id: int) -> dict:
        total_expenses = self.collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
        ])

        total_expense_by_category = {}
        for result in total_expenses:
            total_expense_by_category[result["_id"]] = result["total"]

        return total_expense_by_category


if __name__ == "__main__":
    connection_uri = "mongodb+srv://jigsaw1313:Aramis2427@expenses.0cbt6ew.mongodb.net/"
    expense_mongo_client = ExpenseMongoClient(connection_uri, 27017)
    expense_mongo_client.add_expense(123, 100, "غذا", "ناهار")
    expense_mongo_client.add_expense(123, 200, "غذا", "شام")
    expense_mongo_client.add_expense(123, 300, "سفر", "پرواز")
    expense_mongo_client.add_expense(321, 400, "غذا", "ناهار")
    expense_mongo_client.add_expense(321, 500, "سفر", "پرواز")

    print("Expenses of 123")
    print(expense_mongo_client.get_expenses(123))

    print("Categories of 123")
    print(expense_mongo_client.get_categories(123))

    print("Total expense of 321")
    print(expense_mongo_client.get_total_expense(321))

    print("Total expense by category of 321")
    print(expense_mongo_client.get_total_expense_by_category(321))

    print("Expenses by category of 123")
    print(expense_mongo_client.get_expenses_by_category(123, "غذا"))
