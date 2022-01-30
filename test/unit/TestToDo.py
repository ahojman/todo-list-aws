# from pprint import pprint
import warnings
import unittest
import boto3
from moto import mock_dynamodb2
import sys
import os
import json

@mock_dynamodb2
class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        print ('---------------------')
        print ('Start: setUp')
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<socket.socket.*>")
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message="callable is None.*")
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message="Using or importing.*")
        """Create the mock database and table"""
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
       
        self.is_local = 'true'
        self.uuid = "123e4567-e89b-12d3-a456-426614174000"
        self.text = "I'm an item on the ToDo list"

        from src.todoList import create_todo_table
        print(self.dynamodb)
        self.table = create_todo_table(self.dynamodb)
      
        print ('End: setUp')

    def tearDown(self):
        print ('---------------------')
        print ('Start: tearDown')
        """Delete mock database and table after test is run"""
        self.table.delete()
        print ('Table deleted succesfully')
        
        self.dynamodb = None
        print ('End: tearDown')
        
   
    def test_updateItem_noExists(self):
        print ('---------------------')
        print ('Start: test_updateItem_noExists')
        
        from src.todoList import update_item
        result = update_item(None,'Nuevo texto de prueba',False,self.dynamodb)
        print ('Response update_item' + str(result))
        print ('End: test_updateItem_noExists')
    
    
    def test_put_todo(self):
        print ('---------------------')
        print ('Start: test_put_todo')
        # Testing file functions
        from src.todoList import put_item
        # Table local
        response = put_item(self.text, self.dynamodb)
        print ('Response put_item:' + str(response))
        self.assertEqual(200, response['statusCode'])
        # Table mock
        #self.assertEqual(200, put_item(self.text, self.dynamodb)[
        #                 'ResponseMetadata']['HTTPStatusCode'])
        print ('End: test_put_todo')

    def test_put_todo_error(self):
        print ('---------------------')
        print ('Start: test_put_todo_error')
        # Testing file functions
        from src.todoList import put_item
        # Table mock
        self.assertRaises(Exception, put_item("", self.dynamodb))
        print ('End: test_put_todo_error')

    def test_get_todo(self):
        print ('---------------------')
        print ('Start: test_get_todo')
        from src.todoList import get_item
        from src.todoList import put_item

        responsePut = put_item(self.text, self.dynamodb)
        print ('Response put_item:' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        self.assertEqual(200, responsePut['statusCode'])
        responseGet = get_item(
                idItem,
                self.dynamodb)
        print ('Response Get:' + str(responseGet))
        self.assertEqual(
            self.text,
            responseGet['text'])
        print ('End: test_get_todo')
    
    def test_list_todo(self):
        print ('---------------------')
        print ('Start: test_list_todo')
        
        from src.todoList import put_item
        from src.todoList import get_items

        put_item(self.text, self.dynamodb)
        result = get_items(self.dynamodb)
        print ('Response GetItems' + str(result))
        self.assertTrue(len(result) == 1)
        self.assertTrue(result[0]['text'] == self.text)
        print ('End: test_list_todo')


    def test_update_todo(self):
        print ('---------------------')
        print ('Start: test_update_todo')
        
        from src.todoList import put_item
        from src.todoList import update_item
        from src.todoList import get_item
        
        updated_text = "I'm the UPDATED item on the ToDo List"
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        result = update_item(idItem, updated_text,
                            "false",
                            self.dynamodb)
        print ('Result Update Item:' + str(result))
        self.assertEqual(result['text'], updated_text)
        print ('End: test_update_todo')

    def test_translation(self):
        
        print ('---------------------')
        print ('Start: test_translation')
        
        from src.todoList import translate
        from src.todoList import put_item
        
        result = translate('id','fr')
        
        print (f"Response Error status {result['status_code']} message: {result['message']}")
        
        put_translation = put_item(self.text, self.dynamodb)
        
        idItem = json.loads(put_translation['body'])['id']
        
        result = translate(idItem,'ynh')
        
        print (f"Response Error 2 status {result['status_code']} message: {result['message']}")
        print ('End: test_translate')

    def test_update_todo_error(self):
        print ('---------------------')
        print ('Start: test_update_todo_error')
        from src.todoList import put_item
        from src.todoList import update_item
        updated_text = "I'm another different item on the ToDo List"
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        self.assertRaises(
            Exception,
            update_item(
                updated_text,
                "",
                "false",
                self.dynamodb))
        self.assertRaises(
            TypeError,
            update_item(
                "",
                self.uuid,
                "false",
                self.dynamodb))
        self.assertRaises(
            Exception,
            update_item(
                updated_text,
                self.uuid,
                "",
                self.dynamodb))
        print ('End: atest_update_todo_error')

    def test_delete_todo(self):
        print ('---------------------')
        print ('Start: test_delete_todo')
        from src.todoList import delete_item
        from src.todoList import put_item
        from src.todoList import get_items
        # Testing file functions
        # Table mock
        responsePut = put_item(self.text, self.dynamodb)
        print ('Response PutItem' + str(responsePut))
        idItem = json.loads(responsePut['body'])['id']
        print ('Id item:' + idItem)
        delete_item(idItem, self.dynamodb)
        print ('Item deleted succesfully')
        self.assertTrue(len(get_items(self.dynamodb)) == 0)
        print ('End: test_delete_todo')

    def test_delete_todo_error(self):
        print ('---------------------')
        print ('Start: test_delete_todo_error')
        from src.todoList import delete_item
        # Testing file functions
        self.assertRaises(TypeError, delete_item("", self.dynamodb))
        print ('End: test_delete_todo_error')



if __name__ == '__main__':
    unittest.main()