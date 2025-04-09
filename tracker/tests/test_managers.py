from django.test import TestCase

from tracker.choices import TransactionTextChoices
from tracker.models import Transaction
from tracker.tests.factories import TransactionFactory

INCOME = TransactionTextChoices.INCOME
EXPENSE = TransactionTextChoices.EXPENSE


class TransactionQuerySetTest(TestCase):
    def setUp(self):
        self.incomes = TransactionFactory.create_batch(3, type=INCOME, amount=300)
        self.expenses = TransactionFactory.create_batch(3, type=EXPENSE, amount=200)

    def test_get_income(self):
        income_qs = Transaction.objects.get_income()
        self.assertEqual(income_qs.count(), 3)
        self.assertTrue(all([t.type == INCOME for t in income_qs]))

    def test_get_expense(self):
        expense_qs = Transaction.objects.get_expense()
        self.assertEqual(expense_qs.count(), 3)
        self.assertTrue(all([t.type == EXPENSE for t in expense_qs]))
        
    def test_get_total_income_and_expense(self):
        totals = Transaction.objects.get_total_income_and_expense()
        total_incomes = totals["total_income"]
        total_expenses = totals["total_expense"]
        self.assertEqual(total_incomes, 900)
        self.assertEqual(total_expenses, 600)
    
    def test_get_net_income(self):
        totals = Transaction.objects.get_total_income_and_expense()
        total_incomes = totals["total_income"]
        total_expenses = totals["total_expense"]
        self.assertEqual(total_incomes, 900)
        self.assertEqual(total_expenses, 600)
        expected_net_income = total_incomes - total_expenses

        net_income = Transaction.objects.get_net_income()
        self.assertEqual(net_income, expected_net_income)
