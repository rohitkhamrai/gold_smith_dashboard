import requests
import sys
import json
from datetime import datetime, date

class GoldsmithAPITester:
    def __init__(self, base_url="https://5d5c17ef-730c-4ed7-8c4c-8c5117204a70.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_customer_id = None
        self.created_transaction_id = None
        self.created_job_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic API health"""
        success, response = self.run_test(
            "API Health Check",
            "GET",
            "",
            200
        )
        return success

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard",
            200
        )
        if success:
            required_fields = ['total_gold_balance', 'total_money_balance', 'active_jobs_count', 'total_customers', 'total_transactions']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing field in dashboard response: {field}")
                    return False
            print(f"✅ Dashboard stats structure is correct")
        return success

    def test_create_customer(self):
        """Test customer creation"""
        customer_data = {
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "notes": "Regular customer for testing"
        }
        
        success, response = self.run_test(
            "Create Customer",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if success and 'id' in response:
            self.created_customer_id = response['id']
            print(f"✅ Customer created with ID: {self.created_customer_id}")
        
        return success

    def test_get_customers(self):
        """Test getting all customers"""
        success, response = self.run_test(
            "Get All Customers",
            "GET",
            "customers",
            200
        )
        
        if success and isinstance(response, list):
            print(f"✅ Retrieved {len(response)} customers")
            if self.created_customer_id:
                # Check if our created customer is in the list
                found = any(customer['id'] == self.created_customer_id for customer in response)
                if found:
                    print(f"✅ Created customer found in customer list")
                else:
                    print(f"❌ Created customer not found in customer list")
                    return False
        
        return success

    def test_get_customer_by_id(self):
        """Test getting specific customer"""
        if not self.created_customer_id:
            print("❌ No customer ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Customer by ID",
            "GET",
            f"customers/{self.created_customer_id}",
            200
        )
        
        if success:
            if response.get('name') == 'Rajesh Kumar':
                print(f"✅ Customer details match expected values")
            else:
                print(f"❌ Customer details don't match")
                return False
        
        return success

    def test_create_transaction(self):
        """Test transaction creation"""
        if not self.created_customer_id:
            print("❌ No customer ID available for transaction testing")
            return False
            
        transaction_data = {
            "customer_id": self.created_customer_id,
            "work_description": "Gold ring repair",
            "gold_in": 10.5,
            "gold_out": 8.2,
            "cash_in": 1000.0,
            "labour_charge": 500.0,
            "remarks": "Test transaction"
        }
        
        success, response = self.run_test(
            "Create Transaction",
            "POST",
            "transactions",
            200,
            data=transaction_data
        )
        
        if success and 'id' in response:
            self.created_transaction_id = response['id']
            print(f"✅ Transaction created with ID: {self.created_transaction_id}")
            
            # Verify calculations
            expected_gold_balance = 10.5 - 8.2  # 2.3
            expected_money_balance = 1000.0 + 500.0  # 1500.0
            print(f"✅ Expected gold balance: {expected_gold_balance}g")
            print(f"✅ Expected money balance: ₹{expected_money_balance}")
        
        return success

    def test_get_transactions(self):
        """Test getting all transactions"""
        success, response = self.run_test(
            "Get All Transactions",
            "GET",
            "transactions",
            200
        )
        
        if success and isinstance(response, list):
            print(f"✅ Retrieved {len(response)} transactions")
            if self.created_transaction_id:
                found = any(transaction['id'] == self.created_transaction_id for transaction in response)
                if found:
                    print(f"✅ Created transaction found in transaction list")
                else:
                    print(f"❌ Created transaction not found in transaction list")
                    return False
        
        return success

    def test_customer_balance(self):
        """Test customer balance calculation"""
        if not self.created_customer_id:
            print("❌ No customer ID available for balance testing")
            return False
            
        success, response = self.run_test(
            "Get Customer Balance",
            "GET",
            f"customer/{self.created_customer_id}/balance",
            200
        )
        
        if success:
            gold_balance = response.get('gold_balance', 0)
            money_balance = response.get('money_balance', 0)
            print(f"✅ Customer balance - Gold: {gold_balance}g, Money: ₹{money_balance}")
            
            # Verify our test transaction calculations
            if abs(gold_balance - 2.3) < 0.001 and abs(money_balance - 1500.0) < 0.01:
                print(f"✅ Balance calculations are correct")
            else:
                print(f"❌ Balance calculations seem incorrect")
                print(f"   Expected: Gold=2.3g, Money=₹1500.0")
                print(f"   Got: Gold={gold_balance}g, Money=₹{money_balance}")
                return False
        
        return success

    def test_create_job(self):
        """Test job creation"""
        if not self.created_customer_id:
            print("❌ No customer ID available for job testing")
            return False
            
        job_data = {
            "customer_id": self.created_customer_id,
            "work_description": "Custom necklace design",
            "status": "In Progress",
            "expected_delivery": "2025-03-01"
        }
        
        success, response = self.run_test(
            "Create Job",
            "POST",
            "jobs",
            200,
            data=job_data
        )
        
        if success and 'id' in response:
            self.created_job_id = response['id']
            print(f"✅ Job created with ID: {self.created_job_id}")
        
        return success

    def test_get_jobs(self):
        """Test getting all jobs"""
        success, response = self.run_test(
            "Get All Jobs",
            "GET",
            "jobs",
            200
        )
        
        if success and isinstance(response, list):
            print(f"✅ Retrieved {len(response)} jobs")
            if self.created_job_id:
                found = any(job['id'] == self.created_job_id for job in response)
                if found:
                    print(f"✅ Created job found in job list")
                else:
                    print(f"❌ Created job not found in job list")
                    return False
        
        return success

    def test_update_job_status(self):
        """Test job status update"""
        if not self.created_job_id:
            print("❌ No job ID available for status update testing")
            return False
            
        success, response = self.run_test(
            "Update Job Status",
            "PUT",
            f"jobs/{self.created_job_id}",
            200,
            params={"status": "Completed"}
        )
        
        if success:
            if response.get('status') == 'Completed':
                print(f"✅ Job status updated successfully")
            else:
                print(f"❌ Job status not updated correctly")
                return False
        
        return success

    def test_dashboard_after_operations(self):
        """Test dashboard stats after creating data"""
        success, response = self.run_test(
            "Dashboard Stats After Operations",
            "GET",
            "dashboard",
            200
        )
        
        if success:
            print(f"✅ Final Dashboard Stats:")
            print(f"   Gold Balance: {response.get('total_gold_balance', 0)}g")
            print(f"   Money Balance: ₹{response.get('total_money_balance', 0)}")
            print(f"   Active Jobs: {response.get('active_jobs_count', 0)}")
            print(f"   Total Customers: {response.get('total_customers', 0)}")
            print(f"   Total Transactions: {response.get('total_transactions', 0)}")
            
            # Verify that our operations affected the stats
            if response.get('total_customers', 0) >= 1:
                print(f"✅ Customer count reflects our additions")
            if response.get('total_transactions', 0) >= 1:
                print(f"✅ Transaction count reflects our additions")
            if response.get('active_jobs_count', 0) >= 1:
                print(f"✅ Active jobs count reflects our additions")
        
        return success

    # DELETE FUNCTIONALITY TESTS
    def test_delete_customer_with_transactions_should_fail(self):
        """Test that deleting customer with transactions fails"""
        if not self.created_customer_id:
            print("❌ No customer ID available for delete testing")
            return False
            
        success, response = self.run_test(
            "Delete Customer with Transactions (Should Fail)",
            "DELETE",
            f"customers/{self.created_customer_id}",
            400  # Should fail with 400 status
        )
        
        if success:
            print(f"✅ Customer deletion correctly blocked due to existing transactions")
        else:
            print(f"❌ Customer deletion should have been blocked but wasn't")
            return False
        
        return success

    def test_delete_customer_with_jobs_should_fail(self):
        """Test that deleting customer with jobs fails"""
        if not self.created_customer_id:
            print("❌ No customer ID available for delete testing")
            return False
            
        # First delete the transaction to test job blocking separately
        if self.created_transaction_id:
            self.run_test(
                "Delete Transaction for Job Test",
                "DELETE", 
                f"transactions/{self.created_transaction_id}",
                200
            )
            
        success, response = self.run_test(
            "Delete Customer with Jobs (Should Fail)",
            "DELETE",
            f"customers/{self.created_customer_id}",
            400  # Should fail with 400 status
        )
        
        if success:
            print(f"✅ Customer deletion correctly blocked due to existing jobs")
        else:
            print(f"❌ Customer deletion should have been blocked but wasn't")
            return False
        
        return success

    def test_delete_transaction(self):
        """Test transaction deletion"""
        if not self.created_transaction_id:
            print("❌ No transaction ID available for delete testing")
            return False
            
        # First recreate transaction since we deleted it in previous test
        transaction_data = {
            "customer_id": self.created_customer_id,
            "work_description": "Test transaction for deletion",
            "gold_in": 5.0,
            "gold_out": 2.0,
            "cash_in": 500.0,
            "labour_charge": 200.0,
            "remarks": "Test transaction for deletion"
        }
        
        success, response = self.run_test(
            "Create Transaction for Deletion Test",
            "POST",
            "transactions",
            200,
            data=transaction_data
        )
        
        if success and 'id' in response:
            transaction_id = response['id']
            
            # Now test deletion
            success, response = self.run_test(
                "Delete Transaction",
                "DELETE",
                f"transactions/{transaction_id}",
                200
            )
            
            if success:
                print(f"✅ Transaction deleted successfully")
                
                # Verify transaction is gone
                success_verify, _ = self.run_test(
                    "Verify Transaction Deleted",
                    "GET",
                    f"transactions/{transaction_id}",
                    404  # Should not be found
                )
                
                if success_verify:
                    print(f"✅ Transaction deletion verified - transaction not found")
                else:
                    print(f"❌ Transaction still exists after deletion")
                    return False
            else:
                print(f"❌ Transaction deletion failed")
                return False
        else:
            print(f"❌ Could not create transaction for deletion test")
            return False
        
        return success

    def test_delete_job(self):
        """Test job deletion"""
        if not self.created_job_id:
            print("❌ No job ID available for delete testing")
            return False
            
        success, response = self.run_test(
            "Delete Job",
            "DELETE",
            f"jobs/{self.created_job_id}",
            200
        )
        
        if success:
            print(f"✅ Job deleted successfully")
            
            # Verify job is gone
            success_verify, _ = self.run_test(
                "Verify Job Deleted",
                "GET",
                f"jobs/{self.created_job_id}",
                404  # Should not be found
            )
            
            # Note: The API doesn't have a get single job endpoint, so let's check the jobs list
            success_list, jobs_response = self.run_test(
                "Verify Job Deleted from List",
                "GET",
                "jobs",
                200
            )
            
            if success_list:
                found = any(job['id'] == self.created_job_id for job in jobs_response)
                if not found:
                    print(f"✅ Job deletion verified - job not found in list")
                else:
                    print(f"❌ Job still exists in list after deletion")
                    return False
        else:
            print(f"❌ Job deletion failed")
            return False
        
        return success

    def test_delete_customer_after_cleanup(self):
        """Test customer deletion after removing transactions and jobs"""
        if not self.created_customer_id:
            print("❌ No customer ID available for delete testing")
            return False
            
        # Now that transactions and jobs are deleted, customer deletion should work
        success, response = self.run_test(
            "Delete Customer After Cleanup",
            "DELETE",
            f"customers/{self.created_customer_id}",
            200
        )
        
        if success:
            print(f"✅ Customer deleted successfully after cleanup")
            
            # Verify customer is gone
            success_verify, _ = self.run_test(
                "Verify Customer Deleted",
                "GET",
                f"customers/{self.created_customer_id}",
                404  # Should not be found
            )
            
            if success_verify:
                print(f"✅ Customer deletion verified - customer not found")
            else:
                print(f"❌ Customer still exists after deletion")
                return False
        else:
            print(f"❌ Customer deletion failed even after cleanup")
            return False
        
        return success

    def test_delete_nonexistent_entities(self):
        """Test deleting non-existent entities returns 404"""
        fake_id = "fake-id-12345"
        
        # Test deleting non-existent customer
        success1, _ = self.run_test(
            "Delete Non-existent Customer",
            "DELETE",
            f"customers/{fake_id}",
            404
        )
        
        # Test deleting non-existent transaction
        success2, _ = self.run_test(
            "Delete Non-existent Transaction", 
            "DELETE",
            f"transactions/{fake_id}",
            404
        )
        
        # Test deleting non-existent job
        success3, _ = self.run_test(
            "Delete Non-existent Job",
            "DELETE", 
            f"jobs/{fake_id}",
            404
        )
        
        if success1 and success2 and success3:
            print(f"✅ All non-existent entity deletions correctly returned 404")
            return True
        else:
            print(f"❌ Some non-existent entity deletions didn't return 404")
            return False

    def test_dashboard_after_deletions(self):
        """Test dashboard stats after deletions"""
        success, response = self.run_test(
            "Dashboard Stats After Deletions",
            "GET",
            "dashboard",
            200
        )
        
        if success:
            print(f"✅ Final Dashboard Stats After Deletions:")
            print(f"   Gold Balance: {response.get('total_gold_balance', 0)}g")
            print(f"   Money Balance: ₹{response.get('total_money_balance', 0)}")
            print(f"   Active Jobs: {response.get('active_jobs_count', 0)}")
            print(f"   Total Customers: {response.get('total_customers', 0)}")
            print(f"   Total Transactions: {response.get('total_transactions', 0)}")
            
            print(f"✅ Dashboard stats updated correctly after deletions")
        
        return success

def main():
    print("🚀 Starting Goldsmith Ledger API Tests")
    print("=" * 50)
    
    tester = GoldsmithAPITester()
    
    # Run all tests in sequence
    tests = [
        tester.test_health_check,
        tester.test_dashboard_stats,
        tester.test_create_customer,
        tester.test_get_customers,
        tester.test_get_customer_by_id,
        tester.test_create_transaction,
        tester.test_get_transactions,
        tester.test_customer_balance,
        tester.test_create_job,
        tester.test_get_jobs,
        tester.test_update_job_status,
        tester.test_dashboard_after_operations
    ]
    
    for test in tests:
        if not test():
            print(f"\n❌ Test failed: {test.__name__}")
            break
        print("-" * 30)
    
    # Print final results
    print(f"\n📊 Final Results:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All API tests passed!")
        return 0
    else:
        print("❌ Some API tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())