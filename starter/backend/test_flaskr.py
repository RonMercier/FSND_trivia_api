import os
import unittest
import json
from urllib import response
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'student', 'student', 'localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'this is a question',
            'answer': 'this is an answer',
            'category': '3',
            'difficulty': '4',
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # test get categories

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['categories'])

    def test_404_get_categories(self):
        response = self.client().get('/categories/111111')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    # test get questions
    def test_get_questions(self):
        response = self.client().get('/questions?page=1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_get_questions(self):
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    # test delete questions
    def test_delete_questions(self):
        question = Question(
            question=self.new_question['question'],
            answer=self.new_question['answer'],
            category=self.new_question['category'],
            difficulty=self.new_question['difficulty'])
        question.insert()

        response = self.client().delete('/questions/{}'.format(question.id))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # self.assertEqual(data['deleted'], question.id)

    def test_404_delete_questions(self):
        response = self.client().delete('/questions/1000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    # test add a new question
    def test_create_question(self):
        response = self.client().post('/add/questions', json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question Added')

    def test_422_create_question(self):
        response = self.client().post('/add/questions', json={
            'question': 'this is a question',
            'answer': 'this is an answer',
            'category': 'Science',
            'difficulty': '4',
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    # search question by category
    def test_search_questions(self):
        search_term = {'search_term': 'What is the largest lake in Canada?'}
        response = self.client().post('/questions', json=search_term)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(data['success'], True)

    def search_question_failure(self):
        search_term = {'search_term': ''}
        response = self.client().post('/questions/search', json=search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_search_question_by_category(self):
        response = self.client().get('/categories/3/questions?page=1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_search_question_by_category(self):
        response = self.client().get('/categories/10/questions?page=1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    # test get next question

    def test_get_next_question(self):
        response = self.client().post(
            '/play/quizzes', json={"previous_question": [1, 2, 3, 4],
                                   "quiz_category": {
                                       "type": "History", "id": 3
            }
            })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_get_next_question(self):
        response = self.client().post(
            '/play/quizzes', json={"previous_question": [
                2, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33
            ], "quiz_category": 3})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')


# Make the tests executable
if __name__ == "__main__":
    unittest.main()
