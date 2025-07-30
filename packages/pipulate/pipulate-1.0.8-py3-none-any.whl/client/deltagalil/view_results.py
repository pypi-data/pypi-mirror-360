import pandas as pd
import sqlite3
from tabulate import tabulate
import os

def view_results():
    """View and analyze the results from the URL status checker"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(script_dir, "url_status_results.csv")
    db_path = os.path.join(script_dir, "url_status.db")
    
    # Check if results file exists
    if not os.path.exists(results_path):
        print("No results file found. Run url_status_checker.py first.")
        return
        
    # Read results
    df = pd.read_csv(results_path)
    
    # Get status code counts
    status_counts = df['Status Code'].value_counts().sort_index()
    
    # Print summary
    print("\nURL Status Summary:")
    print(tabulate(
        [[code, count] for code, count in status_counts.items()],
        headers=['Status Code', 'Count'],
        tablefmt='grid'
    ))
    
    # Print total URLs processed
    print(f"\nTotal URLs processed: {len(df)}")
    
    # Print some example URLs for each status code
    print("\nExample URLs for each status code:")
    for status_code in status_counts.index:
        examples = df[df['Status Code'] == status_code]['Full URL'].head(3).tolist()
        print(f"\nStatus {status_code}:")
        for url in examples:
            print(f"  - {url}")
            
    # Check database for total processed
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM url_status")
        total_in_db = c.fetchone()[0]
        conn.close()
        print(f"\nTotal URLs in database: {total_in_db}")

if __name__ == "__main__":
    view_results() 