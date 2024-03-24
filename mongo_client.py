import pymongo
from datetime import datetime as dt

class ExpenseMongoClient:
    def __init__(
            self,
            host: str,
            port: int,
            db_name: str = "Expenses_Bot",
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
            'date': dt.today().date().strftime("%Y-%m-%d")
            })
        return results

    def delete_expense(self, user_id:int, doc_id:str):
        result = self.collection.delete_one({
            'user_id' : user_id,
            '_id': doc_id,
        })
        return result.deleted_count
    
    
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

