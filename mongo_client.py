import pymongo
from datetime import datetime as dt



class ExpenseMongoClient:
    """
    A class for managing expenses in a MongoDB database.

    Attributes:
        host (str): The hostname of the MongoDB server.
        port (int): The port number of the MongoDB server.
        db_name (str): The name of the MongoDB database.
        collection_name (str): The name of the collection within the database.
    """

    def __init__(
            self,
            host: str,
            port: int,
            db_name: str = "Expenses_Bot",
            collection_name: str = "expenses",
    ):
        """
        Initializes the ExpenseMongoClient.

        Args:
            host (str): The hostname of the MongoDB server.
            port (int): The port number of the MongoDB server.
            db_name (str, optional): The name of the MongoDB database. Defaults to "Expenses_Bot".
            collection_name (str, optional): The name of the collection within the database. Defaults to "expenses".
        """

        self.client = pymongo.MongoClient(host, port)
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(collection_name)


    def add_expense(self, user_id: int, amount: int, category: str, description: str):
        """
        Adds a new expense to the database.

        Args:
            user_id (int): The ID of the user adding the expense.
            amount (int): The amount of the expense.
            category (str): The category of the expense.
            description (str): The description of the expense.

        Returns:
            pymongo.results.InsertOneResult: The result of the insertion operation.
        """

        results = self.collection.insert_one({
            "user_id": user_id,
            "amount": amount,
            "category": category,
            "description": description,
            'date': dt.today().date().strftime("%Y-%m-%d")
            })
        return results


    def delete_expense(self, user_id:int, doc_id:str):
        """
        Removes existence expense document from the database.

        Args:
            user_id (int): The ID of the user adding the expense.
            doc_id (int): document id with ObjectId type.

        """

        result = self.collection.delete_one({
            'user_id' : user_id,
            '_id': doc_id,
        })
        return result.deleted_count


    def get_expenses(self, user_id: int) -> list:
        """
        Returns a expense from the database.

        Args:
            user_id (int): The ID of the user adding the expense.


        Returns:
            The result of the find operation.
        """

        results = self.collection.find({'user_id': user_id})
        expenses = []
        for result in results:
            expenses.append({
                'document_id' : result["_id"],
                "amount": result["amount"],
                "category": result["category"],
                "description": result["description"],
                "date": result["date"],
            })
        return expenses


    def get_categories(self, user_id: int) -> list:
        """
        Returns all categories of the user.

        Args:
            user_id (int): The ID of the user.
        """

        categories = self.collection.distinct('category', {'user_id': user_id})
        return categories


    def get_expenses_by_category(self, user_id: int, category: str) -> list:
        """
        Returns each category documents from mongodb database.

        Args:
            user_id (int): The ID of the user.
            category (str): The name of the category.
        """

        results = self.collection.find({'user_id': user_id, 'category': category})
        cate = []
        for result in results:
            cate.append({
                'document_id' : result["_id"],
                "amount": result["amount"],
                "category": result["category"],
                "description": result["description"],
                "date": result["date"],
                })
        return cate


    def get_total_expense(self, user_id: int):
        """
        Returns total expense of user using aggregation functions of mongodb.

        Args:
            user_id (int): The ID of the user.
        """

        total_expense = self.collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])

        total_amount = 0
        for result in total_expense:
            total_amount = result["total"]

        return total_amount


    def get_total_expense_by_category(self, user_id: int) -> dict:
        """
        Returns total expense by each category using aggregation functions,
        of mongodb.

        Args:
            user_id (int): The ID of the user.
        """

        total_expenses = self.collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
        ])

        total_expense_by_category = {}
        for result in total_expenses:
            total_expense_by_category[result["_id"]] = result["total"]

        return total_expense_by_category


    def get_expenses_by_month(self, user_id: int,  month: int):
        """
        Retrieves expenses recorded within a specified month for a given user.

        Args:
            user_id (int): The ID of the user whose expenses are to be retrieved.
            month (int): The month for which expenses are to be retrieved (1 to 12).

        Returns:
            pymongo.cursor.Cursor: A cursor containing the expenses recorded within the specified month.
        """

        # Convert the month to a string with leading zero if necessary
        month_str = str(month).zfill(2)

        # Define the start and end dates for the specified month
        start_date = f'2024-{month_str}-01'
        end_date = f'2024-{month_str}-31'

        # Query the collection for expenses within the specified month
        expenses = self.collection.find({
            'user_id': user_id, 
            'date': {
                '$gte': start_date,
                '$lte': end_date
            }
        })

        return expenses


    def search_date(self, user_id: int, start_date: str, end_date: str):
        """
        Searches for expenses within a specified date range.

        Args:
            user_id (int): The ID of the user.
            start_date (str): The start date of the range in "YYYY-MM-DD" format.
            end_date (str): The end date of the range in "YYYY-MM-DD" format.

        Returns:
            pymongo.cursor.Cursor: A cursor containing the expenses within the specified date range.
        """

        # Convert the month to a string with leading zero if necessary
        start_date_str = str(start_date).zfill(2)
        end_date_str = str(end_date).zfill(2)

        # Query the collection for expenses within the specified duration
        expenses = self.collection.find({
            'user_id': user_id,
            'date': {
                '$gte': start_date_str,
                '$lte': end_date_str}
        })
        
        return expenses
